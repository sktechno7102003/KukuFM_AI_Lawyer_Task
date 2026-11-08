"""Structured case per issue type. The LLM fills these from a messy story; code decides what is missing."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Common(BaseModel):
    user_name: Optional[str] = Field(None, description="Full name of the person asking (needed only for the notice)")
    user_address: Optional[str] = Field(None, description="User's postal address (needed only for the notice)")
    city: Optional[str] = Field(None, description="City/state where this happened")
    proof_available: Optional[list[str]] = Field(None, description="Documents/evidence the user says they HAVE (agreement, receipts, screenshots, messages...)")
    communication_so_far: Optional[str] = Field(None, description="What the user has already asked/complained and what the other side replied")


class DepositCase(Common):
    landlord_name: Optional[str] = Field(None, description="Landlord's name")
    landlord_address: Optional[str] = Field(None, description="Landlord's postal address (for the notice)")
    monthly_rent: Optional[float] = Field(None, description="Monthly rent in INR")
    deposit_amount: Optional[float] = Field(None, description="Total security deposit paid in INR")
    amount_withheld: Optional[float] = Field(None, description="Amount of deposit still not returned in INR")
    move_out_date: Optional[str] = Field(None, description="Date the user vacated / handed over keys (YYYY-MM-DD or YYYY-MM)")
    written_agreement: Optional[bool] = Field(None, description="Is there a written rent agreement?")
    landlord_reason: Optional[str] = Field(None, description="Reason/deductions the landlord gives for not returning")


class ConsumerCase(Common):
    seller_or_platform: Optional[str] = Field(None, description="Company / seller / platform name")
    seller_address: Optional[str] = Field(None, description="Seller's address or registered office (for the notice)")
    product_or_service: Optional[str] = Field(None, description="What was bought")
    amount_paid: Optional[float] = Field(None, description="Price paid in INR")
    purchase_date: Optional[str] = Field(None, description="Date of purchase/booking (YYYY-MM-DD or YYYY-MM)")
    problem: Optional[str] = Field(None, description="What went wrong (defect, refund not received, not delivered...)")
    order_id: Optional[str] = Field(None, description="Order / booking / invoice number")
    complained_to_seller: Optional[bool] = Field(None, description="Has the user already complained to the seller/platform?")


class SalaryCase(Common):
    employer_name: Optional[str] = Field(None, description="Company / employer name")
    employer_address: Optional[str] = Field(None, description="Employer's office address (for the notice)")
    designation: Optional[str] = Field(None, description="User's job role")
    monthly_salary: Optional[float] = Field(None, description="Monthly salary in INR")
    unpaid_period: Optional[str] = Field(None, description="Which months/period are unpaid, e.g. 'Aug-Oct 2026'")
    amount_due: Optional[float] = Field(None, description="Total unpaid amount in INR")
    still_employed: Optional[bool] = Field(None, description="Is the user still working there?")
    last_working_day: Optional[str] = Field(None, description="Last working day if they left (YYYY-MM-DD)")


SCHEMAS: dict[str, type[BaseModel]] = {"deposit": DepositCase, "consumer": ConsumerCase, "salary": SalaryCase}

# What code requires before giving advice (kept short so we don't interrogate the user).
REQUIRED_FOR_ADVICE = {
    "deposit": ["deposit_amount", "move_out_date", "landlord_reason", "proof_available"],
    "consumer": ["seller_or_platform", "amount_paid", "purchase_date", "problem", "complained_to_seller"],
    "salary": ["amount_due", "unpaid_period", "still_employed", "proof_available"],
}
# Extra fields needed only to fill a legal notice (left as [PLACEHOLDER] if missing).
REQUIRED_FOR_DOC = {
    "deposit": ["user_name", "user_address", "landlord_name", "landlord_address"],
    "consumer": ["user_name", "user_address", "seller_or_platform", "seller_address", "order_id"],
    "salary": ["user_name", "user_address", "employer_name", "employer_address", "designation"],
}


def field_specs(issue: str) -> str:
    model = SCHEMAS[issue]
    return "\n".join(f"- {n} ({f.annotation}): {f.description}" for n, f in model.model_fields.items())


def clean_case(issue: str, data: dict) -> dict:
    """Validate the LLM's extraction through Pydantic; drop junk fields/values."""
    model = SCHEMAS[issue]
    safe = {k: v for k, v in data.items() if k in model.model_fields and v not in ("", [], "null", "unknown")}
    try:
        return model(**safe).model_dump(exclude_none=True)
    except Exception:
        out = {}
        for k, v in safe.items():  # keep fields that validate individually
            try:
                out.update(model(**{k: v}).model_dump(exclude_none=True))
            except Exception:
                pass
        return out


def missing(issue: str, case: dict, skipped: set[str], purpose: str = "advice") -> list[str]:
    req = (REQUIRED_FOR_ADVICE if purpose == "advice" else REQUIRED_FOR_DOC)[issue]
    return [f for f in req if case.get(f) in (None, "", []) and f not in skipped]
