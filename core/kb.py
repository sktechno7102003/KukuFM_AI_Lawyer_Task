"""Loads the curated, human-verified knowledge base. The LLM never gets law from anywhere else."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "knowledge"
ISSUES = ("deposit", "consumer", "salary")


@lru_cache
def load_issue(issue: str) -> dict:
    with open(KB_DIR / f"{issue}.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache
def common() -> dict:
    with open(KB_DIR / "common.json", encoding="utf-8") as f:
        return json.load(f)


def entries(issue: str | None) -> list[dict]:
    """Entries for an issue. For notice explanation (no single issue) we use all of them."""
    general = common().get("general_entries", [])
    if issue in ISSUES:
        return load_issue(issue)["entries"] + general
    seen, out = set(), []
    for e in [e for i in ISSUES for e in load_issue(i)["entries"]] + general:
        if e["id"] not in seen:
            seen.add(e["id"]); out.append(e)
    return out


def by_id(issue: str | None) -> dict[str, dict]:
    return {e["id"]: e for e in entries(issue)}


def prompt_block(issue: str | None) -> str:
    """Compact KB text given to the LLM. Only these entries may be cited."""
    lines = []
    for e in entries(issue):
        lines.append(
            f"[{e['id']}] {e['cite']} | {e['title']}\n  Summary: {e['summary']}\n"
            f"  Use when: {e['use_when']}" + (f"\n  Caveat: {e['caveat']}" if e.get("caveat") else "")
        )
    c = common()
    lines.append("Verified contacts (only these numbers may be given): " +
                 "; ".join(f"{x['name']}: {x['number']}" for x in c["contacts"]))
    return "\n".join(lines)


def contact_numbers() -> set[str]:
    return {c["number"] for c in common()["contacts"]}
