"""Post-generation citation validator. Pure code, no LLM.

Every sentence the LLM writes is checked before the user sees it:
  1. Case law (X v. Y, AIR 1999, SCC, 'Supreme Court held') -> removed. We never cite judgments.
  2. Repealed / replaced laws (IPC, CrPC, Payment of Wages Act, e-Daakhil...) -> removed + correction note.
  3. Section / Rule / Article numbers not present in the verified KB (or in the user's own document) -> removed.
  4. Act names not in the KB -> removed.
  5. Phone numbers in helpline-like sentences that aren't verified contacts -> redacted.
  6. Web domains not on the allow-list -> redacted.
Everything removed is logged and shown to the user as a transparency note.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import kb

SENT_SPLIT = re.compile(r"(?<=[.!?।])\s+|\n+")

CASE_LAW = [
    r"\b[A-Z][\w.&']+(?:\s+[A-Z][\w.&']+)*\s+(?:v\.|vs\.?|versus)\s+[A-Z]",
    r"\bAIR\s+\d{4}\b", r"\(\d{4}\)\s*\d+\s*SCC", r"\b\d{4}\s+SCC\b", r"\bSCC\s+\d+", r"\bSCR\b",
    r"\b(?:Supreme Court|High Court|SC|HC|NCDRC|National Commission)\s+(?:has\s+)?(?:held|ruled|observed|said|decided)",
    r"\blandmark (?:case|judgment|judgement|ruling)\b", r"\bin the case of\b", r"\bprecedent\b",
]
# Case-sensitive on purpose: 'Rs. 5000' or 'order 4521' must not look like a legal reference.
REF = re.compile(r"(?<![A-Za-z])(?:[Ss]ections?|SECTION|[Ss]ec\.?|S\.|[Rr]ule|[Aa]rticle|Art\.|धारा|नियम)\s*"
                 r"(\d+[A-Z]?(?:\s*\(\s*[0-9a-zA-Z]+\s*\))*)")
ACT = re.compile(r"((?:[A-Z][A-Za-z()&'\-]*\s+){0,8}?(?:Act|Code|Rules|Sanhita|Adhiniyam))\b(?:,?\s*(\d{4}))?")
PHONE_CTX = re.compile(r"helpline|call|dial|phone|number|toll|whatsapp|contact|हेल्पलाइन|कॉल|नंबर|फ़ोन|फोन", re.I)
NUMBER = re.compile(r"(?<![\w₹.,])(\+?\d(?:[\d -]{1,14}\d)?)(?![\w,]|\.\d)")
DOMAIN = re.compile(r"\b(?:https?://)?(?:www\.)?((?:[a-z0-9-]+\.)+(?:gov\.in|nic\.in|co\.in|org\.in|in|com|org|net|io))\b", re.I)
# Generic phrases that look like act names but are fine to mention.
GENERIC_ACT_OK = {"labour code", "labour codes", "rent control act", "state rent act", "the act", "this act", "an act",
                  "consumer act", "contract act"}


ABBREV = re.compile(r"(?:\b(?:v|vs|Rs|No|Sec|S|Art|Mr|Mrs|Ms|Dr|Ltd|Pvt|Co|St|e\.g|i\.e|[A-Z])\.|^\s*\d+\.)$")


def split_sentences(line: str) -> list[str]:
    """Split on sentence ends, but not after abbreviations like 'v.', 'Rs.', 'M.K.' (so 'A v. B' stays whole)."""
    parts, buf = [], ""
    for piece in re.split(r"(?<=[.!?।])\s+", line):
        buf = f"{buf} {piece}" if buf else piece
        if not ABBREV.search(buf):
            parts.append(buf); buf = ""
    if buf:
        parts.append(buf)
    return parts


def norm_ref(r: str) -> str:
    return re.sub(r"\s+", "", r).lower()


@dataclass
class Report:
    removed: list[dict] = field(default_factory=list)

    def add(self, kind: str, text: str, detail: str = ""):
        self.removed.append({"kind": kind, "text": text.strip(), "detail": detail})

    @property
    def clean(self) -> bool:
        return not self.removed


class Validator:
    def __init__(self, issue: str | None, extra_text: str = ""):
        """extra_text: user-provided material (their own messages / pasted notice). Refs and numbers that
        appear there may be repeated back (e.g. explaining 'the notice cites Section 138')."""
        self.entries = kb.entries(issue)
        self.common = kb.common()
        corpus = " ".join(f"{e['section']} {e['cite']} {e['summary']}" for e in self.entries)
        self.allowed_refs = {norm_ref(m) for m in REF.findall(corpus + " " + extra_text)}
        self.allowed_acts = {a.lower() for e in self.entries for a in [e["act"], *e["act_aliases"]] if a}
        self.allowed_acts |= {m[0].strip().lower() for m in ACT.findall(extra_text)}
        self.allowed_numbers = kb.contact_numbers() | set(re.findall(r"\d{3,}", extra_text))
        self.allowed_domains = self.common["allowed_domains"]
        self.extra_text = extra_text

    # ------------------------------------------------------------- checks
    def _ref_ok(self, ref: str) -> bool:
        n = norm_ref(ref)
        if n in self.allowed_refs:
            return True
        base = n.split("(")[0]
        return "(" in n and base in self.allowed_refs  # 17(2) ok if 17 is verified; 2(47) not ok if only 2(7) is

    def _act_ok(self, name: str) -> bool:
        n = re.sub(r"^(the|under|of|and|in|as per|per)\s+", "", name.strip().lower())
        if n in GENERIC_ACT_OK or len(n.split()) < 2:
            return True
        return any(a in n or n in a for a in self.allowed_acts)

    def check_sentence(self, s: str, rep: Report) -> str | None:
        for rx in CASE_LAW:
            if re.search(rx, s):
                rep.add("case_law", s, "We never cite court judgments: they are the most commonly invented legal facts.")
                return None
        for r in self.common["repealed_or_replaced"]:
            if re.search(r["pattern"], s, flags=re.I) and not re.search(r["replacement_pattern"], s, flags=re.I):
                rep.add("outdated_law", s, f"{r['name']} has been replaced by {r['replaced_by']}.")
                return None
        for ref in REF.findall(s):
            if not self._ref_ok(ref):
                rep.add("unverified_section", s, f"'{ref.strip()}' is not in the verified knowledge base.")
                return None
        for name, _year in ACT.findall(s):
            if not self._act_ok(name):
                rep.add("unverified_act", s, f"'{name.strip()}' is not in the verified knowledge base.")
                return None
        if PHONE_CTX.search(s):
            def redact(m):
                num = re.sub(r"\D", "", m.group(1))
                before = s[max(0, m.start() - 5):m.start()]
                if len(num) < 3 or num in self.allowed_numbers or re.search(r"(Rs\.?|₹|INR)\s*$", before) \
                        or (len(num) == 4 and 1900 <= int(num) <= 2099):
                    return m.group(0)
                rep.add("unverified_number", s, f"Phone number {m.group(1)} is not a verified contact.")
                return "[number removed: unverified]"
            s = NUMBER.sub(redact, s)

        def dom(m):
            d = m.group(1).lower()
            if any(d == a or d.endswith("." + a) for a in self.allowed_domains):
                return m.group(0)
            rep.add("unverified_link", s, f"Website {d} is not on the verified list.")
            return "[link removed]"
        s = DOMAIN.sub(dom, s)
        return s

    def clean_text(self, text: str, rep: Report) -> str:
        """Validate a block of text sentence by sentence, preserving line breaks."""
        # Models often emit non-breaking/unicode hyphens (e‑jagriti) and spaces, which break regex checks.
        text = re.sub(r"[‐‑‒–−]", "-", text).replace(" ", " ").replace(" ", " ")
        out_lines = []
        for line in text.split("\n"):
            if not line.strip():
                out_lines.append(line)
                continue
            parts = split_sentences(line)
            kept = [k for k in (self.check_sentence(p, rep) for p in parts) if k]
            if kept:
                out_lines.append(" ".join(kept))
        return "\n".join(out_lines).strip()

    def clean_points(self, points: list[dict], rep: Report, valid_ids: set[str]) -> list[dict]:
        """Points are {text, kb_ids}. Drop unknown KB ids; validate text."""
        out = []
        for p in points or []:
            if isinstance(p, str):
                p = {"text": p, "kb_ids": []}
            ids = [i for i in p.get("kb_ids", []) or [] if i in valid_ids]
            bad = [i for i in p.get("kb_ids", []) or [] if i not in valid_ids]
            if bad:
                rep.add("unknown_kb_id", p.get("text", ""), f"Cited unknown source id(s) {bad}.")
            txt = self.clean_text(p.get("text", ""), rep)
            if txt:
                out.append({"text": txt, "kb_ids": ids})
        return out


def describe(rep: Report) -> list[str]:
    msgs = {
        "case_law": "removed a statement citing a court case (I never cite judgments)",
        "outdated_law": "removed a reference to an old/replaced law",
        "unverified_section": "removed a statement citing a section not in my verified sources",
        "unverified_act": "removed a statement citing a law not in my verified sources",
        "unverified_number": "removed an unverified phone number",
        "unverified_link": "removed an unverified website link",
        "unknown_kb_id": "dropped a reference to a source that doesn't exist",
    }
    out = []
    for r in rep.removed:
        m = msgs.get(r["kind"], r["kind"])
        if r["kind"] == "outdated_law":
            m += f" ({r['detail']})"
        out.append(m)
    return sorted(set(out))
