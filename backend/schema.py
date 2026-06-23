from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── What the client sends when submitting an expense ──────────────────────────
class ExpenseCreate(BaseModel):
    employee: str = Field(..., example="Vishwak")
    amount: float = Field(..., gt=0, example=4500.00)
    submitted_category: str = Field(..., example="Travel")
    description: str = Field(..., example="Flight to Delhi for client meeting")
    receipt_ref: Optional[str] = Field(None, example="BOOKING_REF_123")


# ── What the API sends back after processing ──────────────────────────────────
class ExpenseResponse(BaseModel):
    id: int
    employee: str
    amount: float
    submitted_category: str
    ai_category: Optional[str]
    description: str
    receipt_ref: Optional[str]

    risk_flag: Optional[str]
    risk_reason: Optional[str]
    approval_level: Optional[str]
    status: str
    ai_notes: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Summary stats for the dashboard ───────────────────────────────────────────
class DashboardStats(BaseModel):
    total: int
    pending: int
    approved: int
    flagged: int
    rejected: int
    total_amount: float
    flagged_amount: float


# ── For manually updating an expense status (manager action) ──────────────────
class StatusUpdate(BaseModel):
    status: str = Field(..., example="approved")
    notes: Optional[str] = Field(None, example="Verified with manager")