"""Deterministic calculations. Dates, deadlines and forum by amount are computed in code, never by the LLM."""
from __future__ import annotations

import re
from datetime import date, datetime


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            d = datetime.strptime(s, fmt).date()
            return d
        except ValueError:
            pass
    m = re.match(r"(\d{4})-(\d{2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    return None


def inr(x) -> str:
    try:
        return f"Rs {float(x):,.0f}"
    except (TypeError, ValueError):
        return str(x)


def compute(issue: str, case: dict, today: date | None = None) -> tuple[list[str], list[str]]:
    """Return (facts, lawyer_reasons). Facts are plain English strings shown to user and LLM."""
    today = today or date.today()
    facts, lawyer = [], []

    if issue == "deposit":
        d = parse_date(case.get("move_out_date"))
        if d:
            days = (today - d).days
            if days < 0:
                facts.append(f"Move-out date {d.isoformat()} is in the future; refund isn't due yet.")
            else:
                facts.append(f"It has been about {days} days since you moved out ({d.isoformat()}).")
                if days > 3 * 365 - 90:
                    lawyer.append("You are close to (or past) the general 3-year limit for a money recovery case.")
        rent, dep = case.get("monthly_rent"), case.get("deposit_amount")
        if rent and dep and float(rent) > 0:
            months = float(dep) / float(rent)
            facts.append(f"Your deposit was {months:.1f} months' rent (the Model Tenancy Act caps it at 2, where adopted).")
        if case.get("amount_withheld") or dep:
            facts.append(f"Amount to claim: {inr(case.get('amount_withheld') or dep)}.")

    elif issue == "consumer":
        d = parse_date(case.get("purchase_date"))
        if d:
            days = (today - d).days
            left = 730 - days
            facts.append(f"Purchase was about {days} days ago ({d.isoformat()}). Consumer complaints must be filed within 2 years of the problem arising.")
            if left < 90:
                lawyer.append("You are close to (or past) the 2-year limit for a consumer complaint.")
        amt = case.get("amount_paid")
        if amt is not None:
            a = float(amt)
            forum = "District Commission" if a <= 50_00_000 else ("State Commission" if a <= 2_00_00_000 else "National Commission")
            fee = "no filing fee (up to Rs 5 lakh)" if a <= 5_00_000 else "a small filing fee applies"
            facts.append(f"Amount paid {inr(a)} -> {forum}; {fee}.")
            if a > 50_00_000:
                lawyer.append("Claims above Rs 50 lakh go to the State/National Commission; a lawyer is strongly advised.")

    elif issue == "salary":
        d = parse_date(case.get("last_working_day"))
        if d:
            facts.append(f"Last working day {d.isoformat()}: final wages are due within 2 working days of leaving under the Code on Wages.")
            if (today - d).days > 3 * 365 - 90:
                lawyer.append("You are close to (or past) the 3-year limit for a wage claim.")
        if case.get("amount_due"):
            facts.append(f"Amount to claim: {inr(case['amount_due'])}.")
        if case.get("still_employed") is True:
            facts.append("You are still employed: monthly salary is due before the 7th of the following month.")
    return facts, lawyer
