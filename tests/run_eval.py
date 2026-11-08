"""Run every test case end-to-end, save unedited raw outputs, and score them automatically.

Usage:  python tests/run_eval.py                 # all cases, model from config.yaml / env
        python tests/run_eval.py --only 13 07     # cases whose id starts with these
        LLM_PROVIDER=gemini python tests/run_eval.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import safety  # noqa: E402
from core.documents import build_notice  # noqa: E402
from core.engine import Conversation  # noqa: E402
from core.llm import LLM  # noqa: E402

TODAY = date(2026, 11, 8)  # fixed so date math is reproducible


def assistant_text(conv: Conversation) -> str:
    return "\n".join(m["content"] for m in conv.history if m["role"] == "assistant")


def escalation_of(conv: Conversation) -> str:
    for m in conv.history:
        if m.get("kind") == "escalation":
            return "cyber" if "1930" in m["content"] else "critical"
    return "none"


def reply_language(conv: Conversation) -> str | None:
    """Language of the main LLM-written replies (headings/templates excluded as far as possible)."""
    texts = []
    for m in conv.history:
        if m["role"] != "assistant":
            continue
        meta = m.get("meta") or {}
        if m.get("kind") == "advice" and meta.get("advice"):
            a = meta["advice"]
            texts.append(a["summary"] + " " + " ".join(p["text"] for p in a["points"]))
        elif m.get("kind") in ("question", "followup"):
            texts.append(m["content"])
    return safety.detect_language(" ".join(texts)) if texts else None


def check(case: dict, conv: Conversation, notice: dict | None) -> dict:
    exp = case.get("expect", {})
    out = assistant_text(conv) + ("\n" + notice["markdown"] if notice else "")
    res = {}
    if "issue" in exp:
        res["issue"] = conv.issue == exp["issue"]
    if "escalation" in exp:
        res["escalation"] = escalation_of(conv) == exp["escalation"]
    if "stage" in exp:
        res["stage"] = conv.stage == exp["stage"]
    if "lawyer" in exp:
        got = bool(conv.lawyer_reasons) or bool((conv.advice or {}).get("needs_lawyer")) or conv.police_court
        res["lawyer"] = got == exp["lawyer"]
    if "language" in exp and exp.get("stage") != "escalated":
        lang = reply_language(conv)
        res["language"] = lang is None or lang == exp["language"]
    for rx in exp.get("must_not_contain", []):
        res[f"not:{rx[:20]}"] = not re.search(rx, out, flags=re.I)
    # Universal check: nothing that reached the user cites case law (the validator must have caught it all).
    res["no_case_law"] = not re.search(r"\bAIR\s+\d{4}|\(\d{4}\)\s*\d+\s*SCC|\b[A-Z]\w+ v\. [A-Z]", out)
    return res


def run_case(case: dict, llm_factory) -> tuple[Conversation, dict | None, str | None]:
    conv = Conversation(llm_factory(), today=TODAY)
    notice, err = None, None
    try:
        for turn in case["turns"]:
            conv.handle(turn)
        for action in case.get("actions", []):
            if action == "notice" and conv.issue:
                notice = build_notice(conv)
            elif action.startswith("practice:") and conv.issue:
                conv.start_practice()
                conv.handle(action.split(":", 1)[1])
    except Exception:
        err = traceback.format_exc()
    return conv, notice, err


def write_raw(case: dict, conv: Conversation, notice: dict | None, err: str | None, res: dict, outdir: Path,
              seconds: float = 0):
    data = {"test_case": case, "result": res, "error": err, "seconds": seconds, **conv.to_dict()}
    if notice:
        data["notice"] = {k: v for k, v in notice.items() if k != "docx"}
        (outdir / f"{case['id']}_notice.docx").write_bytes(notice["docx"])
    (outdir / f"{case['id']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    md = [f"# {case['id']} ({case['category']})", f"Model: `{conv.llm.provider}/{conv.llm.model}`", ""]
    for m in conv.history:
        who = "🧑 USER" if m["role"] == "user" else f"🤖 ASSISTANT ({m.get('kind', '')})"
        md += [f"## {who}", m["content"], ""]
    if notice:
        md += ["## 📝 GENERATED NOTICE", notice["markdown"], ""]
    if conv.validation_log:
        md += ["## 🛡️ VALIDATOR REMOVED", "```json", json.dumps(conv.validation_log, ensure_ascii=False, indent=2), "```"]
    if err:
        md += ["## ❌ ERROR", "```", err, "```"]
    md += ["## ✅ AUTO-CHECKS", json.dumps(res, indent=2)]
    (outdir / f"{case['id']}.md").write_text("\n".join(md), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--provider"); ap.add_argument("--model")
    ap.add_argument("--out", default=str(ROOT / "outputs"))
    args = ap.parse_args()

    cases = yaml.safe_load(open(ROOT / "tests" / "test_cases.yaml", encoding="utf-8"))
    if args.only:
        cases = [c for c in cases if any(c["id"].startswith(p) for p in args.only)]
    probe = LLM.from_config(args.provider, args.model)
    outdir = Path(args.out) / f"{probe.provider}__{probe.model.replace('/', '_')}"
    outdir.mkdir(parents=True, exist_ok=True)

    for case in cases:
        t0 = time.time()
        conv, notice, err = run_case(case, lambda: LLM.from_config(args.provider, args.model))
        res = check(case, conv, notice) if not err else {"error": False}
        write_raw(case, conv, notice, err, res, outdir, round(time.time() - t0, 1))
        failed = [k for k, v in res.items() if not v]
        print(f"{'✅' if not failed else '❌'} {case['id']:<34} {'PASS' if not failed else 'FAIL: ' + ', '.join(failed)}", flush=True)

    # Summary is rebuilt from ALL saved case files, so partial re-runs (--only) keep a complete summary.
    rows, totals, caught = [], {"calls": 0, "pt": 0, "ct": 0, "sec": 0.0}, {}
    for f in sorted(outdir.glob("[0-9]*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "test_case" not in d:  # file from an older runner version
            continue
        for c in d["llm_calls"]:
            totals["calls"] += 1; totals["pt"] += c["prompt_tokens"]; totals["ct"] += c["completion_tokens"]; totals["sec"] += c["seconds"]
        for v in d["validation_log"]:
            for r in v["removed"]:
                caught[r["kind"]] = caught.get(r["kind"], 0) + 1
        failed = [k for k, v in d["result"].items() if not v]
        rows.append((d["test_case"]["id"], d["test_case"]["category"], d["issue"] or "-", d["language"] or "-", d["stage"],
                     (d["advice"] or {}).get("confidence", "-"), sum(len(v["removed"]) for v in d["validation_log"]),
                     "PASS" if not failed else "FAIL: " + ", ".join(failed), d.get("seconds", "-")))

    n = len(rows); passed = sum(r[7] == "PASS" for r in rows)
    md = [f"# Eval summary: {probe.provider}/{probe.model}", f"Run date (fixed 'today' for date math): {TODAY}", "",
          f"**{passed}/{n} cases passed all automatic checks.**", "",
          "| Case | Category | Issue | Lang | Final stage | Confidence | Validator removals | Result | Secs |",
          "|---|---|---|---|---|---|---|---|---|"]
    md += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    md += ["", "## Hallucinations caught by the validator (removed before the user saw them)", ""]
    md += [f"- {k}: {v}" for k, v in sorted(caught.items())] or ["- none"]
    md += ["", "## Cost / volume", "",
           f"- LLM calls: {totals['calls']} ({totals['calls']/max(n,1):.1f} per conversation)",
           f"- Tokens: {totals['pt']:,} prompt + {totals['ct']:,} completion ({(totals['pt']+totals['ct'])/max(n,1):,.0f} per conversation)",
           f"- Total model time: {totals['sec']:.0f}s"]
    (outdir / "eval_summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[3:4]))
    print(f"Raw outputs: {outdir}")


if __name__ == "__main__":
    main()
