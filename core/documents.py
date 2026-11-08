"""Legal notice generator. The format, legal basis and demand are fixed by code (template + KB);
the LLM only writes the facts paragraphs, which are validated to contain no legal citations at all."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt
from jinja2 import Environment, FileSystemLoader

from . import kb, prompts
from .facts import compute, inr
from .schemas import REQUIRED_FOR_DOC, SCHEMAS, missing
from .validator import REF, Report, Validator

TPL = Environment(loader=FileSystemLoader(Path(__file__).resolve().parent.parent / "templates"), autoescape=False)

ISSUE_TEXT = {
    "deposit": dict(
        subject="Demand for refund of security deposit of {amt}",
        recipient=("landlord_name", "landlord_address"),
        demand="I hereby call upon you to refund the security deposit amount of {amt} withheld by you.",
        escalation="including filing a civil suit for recovery of the amount with interest and costs",
        lines={"DEP-2": "You agreed to refund the security deposit when I vacated. Withholding it is a breach of our agreement, entitling me to recover it with compensation."},
    ),
    "consumer": dict(
        subject="Notice for refund / compensation for deficiency in service and defective goods ({amt})",
        recipient=("seller_or_platform", "seller_address"),
        demand="I hereby call upon you to refund {amt} and compensate me for the inconvenience caused.",
        escalation="including filing a complaint before the District Consumer Disputes Redressal Commission",
        lines={"CON-1": "I purchased the goods/service for a price for my personal use and am a 'consumer'.",
               "CON-2": "Failure to provide the promised refund/product amounts to deficiency in service and/or a defect.",
               "CON-7": "As an e-commerce entity you are required to acknowledge complaints within 48 hours and redress them within one month."},
    ),
    "salary": dict(
        subject="Demand for payment of unpaid salary/wages of {amt}",
        recipient=("employer_name", "employer_address"),
        demand="I hereby call upon you to pay my outstanding salary/wages of {amt}.",
        escalation="including filing a claim before the authority under the Code on Wages, 2019 and/or a civil suit for recovery",
        lines={"SAL-1": "Wages must be paid within the time limits set by law, and within two working days of an employee leaving.",
               "SAL-2": "Unpaid wages can be claimed before the authority appointed under the Code.",
               "SAL-3": "Payment of agreed salary is a contractual obligation, and non-payment is a breach."},
    ),
}


def _ph(case: dict, field: str) -> str:
    v = case.get(field)
    return str(v) if v not in (None, "", []) else f"[PLACEHOLDER: {SCHEMAS_DESC(field)}]"


def SCHEMAS_DESC(field: str) -> str:
    for m in SCHEMAS.values():
        if field in m.model_fields:
            return m.model_fields[field].description.split("(")[0].strip()
    return field


def build_notice(conv) -> dict:
    issue, case = conv.issue, conv.case
    spec = ISSUE_TEXT[issue]
    amount = case.get("amount_withheld") or case.get("deposit_amount") or case.get("amount_paid") or case.get("amount_due")
    amt = inr(amount) if amount else "[PLACEHOLDER: amount]"
    facts, _ = compute(issue, case, conv.today)

    raw = conv.llm.chat(prompts.DOC_FACTS.format(issue=issue, case=json.dumps(case, ensure_ascii=False), facts=facts),
                        "Write the facts paragraphs.", name="doc_facts")
    v, rep = Validator(issue, conv.user_text()), Report()
    cleaned = v.clean_text(raw, rep)
    # Facts section must not contain ANY legal citation, verified or not: the legal basis is fixed by code.
    kept = []
    for line in cleaned.split("\n"):
        if REF.search(line):
            rep.add("citation_in_facts", line, "Legal citations are not allowed in the facts section.")
            continue
        kept.append(line)
    n, renum = 0, []
    for line in kept:  # renumber paragraphs after removals
        if re.match(r"^\s*\d+\.\s", line):
            n += 1
            line = re.sub(r"^\s*\d+\.", f"{n}.", line)
        renum.append(line)
    facts_text = "\n".join(renum).strip()
    conv._log_validation("document", rep)

    entries = kb.by_id(issue)
    basis = [{"cite": entries[i]["cite"], "notice_line": line} for i, line in spec["lines"].items() if i in entries]
    rname, raddr = spec["recipient"]
    md = TPL.get_template("notice.md.j2").render(
        today=conv.today.strftime("%d %B %Y"), sender_name=_ph(case, "user_name"), sender_address=_ph(case, "user_address"),
        recipient_name=_ph(case, rname), recipient_address=_ph(case, raddr), subject=spec["subject"].format(amt=amt),
        salutation="Dear Sir/Madam", facts=facts_text, legal_basis=basis, demand=spec["demand"].format(amt=amt),
        reply_days=conv.cfg.get("notice_reply_days", 15), escalation=spec["escalation"],
        proof=", ".join(case.get("proof_available") or []) or "[PLACEHOLDER: list your proof]",
    )
    miss = missing(issue, case, set(), purpose="doc")
    placeholders = sorted(set(re.findall(r"\[PLACEHOLDER: ([^\]]+)\]", md)))
    return {"markdown": md, "docx": to_docx(md), "missing": miss, "placeholders": placeholders, "removed": rep.removed}


def to_docx(md: str) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name, style.font.size = "Times New Roman", Pt(12)
    for line in md.split("\n"):
        p = doc.add_paragraph()
        line = re.sub(r"^- ", "• ", line)
        for part in re.split(r"(\*\*[^*]+\*\*)", line):
            if part.startswith("**") and part.endswith("**"):
                p.add_run(part[2:-2]).bold = True
            elif part:
                p.add_run(part)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
