"""Offline tests (no API key needed) for the code-only safety layer: validator, red flags, language, date math."""
from datetime import date

from core import safety
from core.facts import compute
from core.validator import Report, Validator


def clean(text, issue="consumer", extra=""):
    rep = Report()
    return Validator(issue, extra).clean_text(text, rep), rep


def test_keeps_verified_citation():
    out, rep = clean("You can file within 2 years under Section 69 of the Consumer Protection Act, 2019.")
    assert "Section 69" in out and rep.clean


def test_removes_invented_section():
    out, rep = clean("Under Section 72A of the Consumer Protection Act, 2019 you get triple refund.")
    assert out == "" and rep.removed[0]["kind"] == "unverified_section"


def test_removes_subsection_not_in_kb():
    out, rep = clean("Section 2(47) defines unfair trade practice.")
    assert out == ""


def test_allows_subsection_when_base_verified():
    out, rep = clean("Section 17(2) needs payment in two working days.", issue="salary")
    assert out and rep.clean


def test_removes_case_law():
    for s in ["In Lucknow Development Authority v. M.K. Gupta the court awarded compensation.",
              "The Supreme Court has held that refunds are mandatory.", "See AIR 1994 SC 787."]:
        out, rep = clean(s)
        assert out == "" and rep.removed[0]["kind"] == "case_law", s


def test_removes_outdated_ipc_but_keeps_correction():
    out, rep = clean("File a case under IPC 420 for cheating.")
    assert out == "" and rep.removed[0]["kind"] == "outdated_law"
    out, rep = clean("IPC was replaced by the Bharatiya Nyaya Sanhita (BNS) from 1 July 2024.")
    assert out and rep.clean


def test_removes_repealed_wage_law():
    out, rep = clean("Under the Payment of Wages Act, 1936 salary is due by the 7th.", issue="salary")
    assert out == "" and rep.removed[0]["kind"] == "outdated_law"


def test_removes_unknown_act():
    out, rep = clean("You can also use the Civil Procedure Code to recover it.", issue="deposit")
    assert out == "" and rep.removed[0]["kind"] == "unverified_act"


def test_redacts_unverified_helpline_keeps_verified():
    out, rep = clean("Call the consumer helpline 1800-11-4000 or 1915.")
    assert "1915" in out and "1800" not in out and rep.removed[0]["kind"] == "unverified_number"


def test_amounts_and_order_ids_are_not_citations():
    out, rep = clean("You paid Rs. 25000 and your order 4521 was cancelled.")
    assert out and rep.clean


def test_unverified_link_redacted():
    out, rep = clean("File online at consumerforum-india.com or e-jagriti.gov.in.")
    assert "e-jagriti.gov.in" in out and "consumerforum-india.com" not in out


def test_notice_refs_allowed_when_in_users_document():
    out, rep = clean("The notice cites Section 138 of the Negotiable Instruments Act.", issue=None,
                     extra="...liable under Section 138 of the Negotiable Instruments Act, 1881...")
    assert out and rep.clean


def test_red_flags():
    assert safety.worst_tier(safety.scan("mera pati mujhe maarta hai")) == "critical"
    assert safety.worst_tier(safety.scan("मेरे पति मुझे मारते हैं, मारता है")) == "critical"
    assert safety.worst_tier(safety.scan("police ne bulaya hai kal")) == "lawyer"
    assert safety.worst_tier(safety.scan("I shared my OTP and lost money")) == "cyber"
    # Hinglish 'fir' (= then) must NOT trigger the FIR rule
    assert safety.worst_tier(safety.scan("fir bhi landlord ne paise nahi diye")) is None


def test_language_detection():
    assert safety.detect_language("मकान मालिक ने डिपॉज़िट वापस नहीं किया") == "hi"
    assert safety.detect_language("mera deposit wapas nahi kar raha landlord, kya karu") == "hinglish"
    assert safety.detect_language("My landlord won't return my deposit") == "en"


def test_deadline_math():
    facts, lawyer = compute("consumer", {"purchase_date": "2024-12-01", "amount_paid": 60_00_000}, date(2026, 11, 8))
    assert any("State Commission" in f for f in facts)
    assert len(lawyer) == 2  # near 2-year limit + above 50 lakh
    facts, lawyer = compute("deposit", {"move_out_date": "2026-08-01", "deposit_amount": 60000, "monthly_rent": 15000},
                            date(2026, 11, 8))
    assert any("4.0 months" in f for f in facts) and not lawyer


def test_unicode_hyphen_link_not_blocked():
    out, rep = clean("File online on the e‑Jagriti portal (e‑jagriti.gov.in).")
    assert "e-jagriti.gov.in" in out and rep.clean
