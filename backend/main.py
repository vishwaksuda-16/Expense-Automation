from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, create_tables, Expense
from schemas import ExpenseCreate, ExpenseResponse, DashboardStats, StatusUpdate
from agent import analyze_expense
from workflow import determine_final_routing, get_routing_summary

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Expense Automation Agent",
    description="AI-powered expense processing, risk flagging, and approval routing",
    version="1.0.0"
)

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_tables()
    logger.info("Database tables ready.")


# ── POST /expenses ─────────────────────────────────────────────────────────────
# The core endpoint — full pipeline: validate → AI → rules → save → return
@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
def submit_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Submit a new expense. Triggers the full AI + rules pipeline automatically.
    """
    logger.info(f"New expense from {expense.employee} — ₹{expense.amount}")

    # Step 1: Send to Groq AI for analysis
    ai_result = analyze_expense(
        employee=expense.employee,
        amount=expense.amount,
        submitted_category=expense.submitted_category,
        description=expense.description
    )
    logger.info(f"AI result: {ai_result}")

    # Step 2: Apply business rules on top of AI decision
    final = determine_final_routing(expense, ai_result)
    logger.info(get_routing_summary(expense.employee, expense.amount, final["approval_level"], final["status"]))

    # Step 3: Save to database
    db_expense = Expense(
        employee=expense.employee,
        amount=expense.amount,
        submitted_category=expense.submitted_category,
        description=expense.description,
        receipt_ref=expense.receipt_ref,
        ai_category=final["ai_category"],
        risk_flag=final["risk_flag"],
        risk_reason=final["risk_reason"],
        approval_level=final["approval_level"],
        status=final["status"],
        ai_notes=final["ai_notes"],
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    return db_expense


# ── GET /expenses ──────────────────────────────────────────────────────────────
# Fetch all expenses — optional filters by status or risk
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    status: str = None,
    risk_flag: str = None,
    approval_level: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)
    if status:
        query = query.filter(Expense.status == status)
    if risk_flag:
        query = query.filter(Expense.risk_flag == risk_flag)
    if approval_level:
        query = query.filter(Expense.approval_level == approval_level)
    return query.order_by(Expense.created_at.desc()).all()


# ── GET /expenses/{id} ─────────────────────────────────────────────────────────
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


# ── PATCH /expenses/{id}/status ────────────────────────────────────────────────
# Manager/director manually approves or rejects a pending expense
@app.patch("/expenses/{expense_id}/status", response_model=ExpenseResponse)
def update_expense_status(
    expense_id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db)
):
    allowed_statuses = {"approved", "rejected", "pending"}
    if update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed_statuses}")

    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.status = update.status
    if update.notes:
        expense.ai_notes = (expense.ai_notes or "") + f" | Manual: {update.notes}"
    db.commit()
    db.refresh(expense)
    logger.info(f"Expense #{expense_id} manually updated to '{update.status}'")
    return expense


# ── GET /dashboard ─────────────────────────────────────────────────────────────
# Aggregated stats for the frontend dashboard
@app.get("/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    total = db.query(Expense).count()
    pending = db.query(Expense).filter(Expense.status == "pending").count()
    approved = db.query(Expense).filter(Expense.status == "approved").count()
    flagged = db.query(Expense).filter(Expense.risk_flag == "high").count()
    rejected = db.query(Expense).filter(Expense.status == "rejected").count()

    total_amount = db.query(func.sum(Expense.amount)).scalar() or 0.0
    flagged_amount = db.query(func.sum(Expense.amount)).filter(Expense.risk_flag == "high").scalar() or 0.0

    return DashboardStats(
        total=total,
        pending=pending,
        approved=approved,
        flagged=flagged,
        rejected=rejected,
        total_amount=total_amount,
        flagged_amount=flagged_amount
    )


# ── GET /health ────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Expense Automation Agent"}