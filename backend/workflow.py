from schemas import ExpenseCreate

# ── Thresholds ────────────────────────────────────────────────────────────────
AUTO_APPROVE_LIMIT = 2_000        # Under this → auto if low risk
MANAGER_LIMIT = 10_000           # Under this → manager review
DIRECTOR_LIMIT = 50_000          # Under this → director review
FINANCE_REVIEW_FLOOR = 50_000    # At or above → always finance_review

# Categories that always need a human eye regardless of amount
SENSITIVE_CATEGORIES = {"entertainment", "medical", "other"}

# ── Main routing function ─────────────────────────────────────────────────────
def determine_final_routing(expense: ExpenseCreate, ai_result: dict) -> dict:
    """
    Takes the raw expense and the AI's analysis.
    Applies hard business rules and returns the final routing decision.

    Business rules always override AI — AI is advisory, rules are mandatory.
    """

    amount = expense.amount
    ai_approval = ai_result.get("approval_level", "manager")
    ai_risk = ai_result.get("risk_flag", "medium")
    ai_category = ai_result.get("ai_category", "other")

    # Start with AI's recommendation
    final_approval = ai_approval
    final_status = "pending"
    override_notes = []

    # ── Rule 1: Hard amount overrides ─────────────────────────────────────────
    if amount >= FINANCE_REVIEW_FLOOR:
        final_approval = "finance_review"
        override_notes.append(f"Amount ₹{amount} exceeds ₹{FINANCE_REVIEW_FLOOR} limit — escalated to finance.")

    elif amount >= DIRECTOR_LIMIT and final_approval not in ("finance_review",):
        final_approval = "director"
        override_notes.append(f"Amount ₹{amount} requires director approval.")

    elif amount >= MANAGER_LIMIT and final_approval == "auto":
        final_approval = "manager"
        override_notes.append(f"Amount ₹{amount} exceeds auto-approve limit — routed to manager.")

    # ── Rule 2: High risk always escalates ────────────────────────────────────
    if ai_risk == "high" and final_approval == "auto":
        final_approval = "manager"
        override_notes.append("High risk flag overrides auto-approval.")

    if ai_risk == "high" and final_approval == "manager":
        final_approval = "director"
        override_notes.append("High risk flag escalated to director.")

    # ── Rule 3: Sensitive categories need at least manager review ─────────────
    if ai_category in SENSITIVE_CATEGORIES and final_approval == "auto":
        final_approval = "manager"
        override_notes.append(f"Category '{ai_category}' requires manual review.")

    # ── Rule 4: Category mismatch between employee and AI ─────────────────────
    submitted = expense.submitted_category.lower().strip()
    if submitted != ai_category and ai_risk == "low":
        # Upgrade risk to medium silently, don't block but do flag
        ai_result["risk_flag"] = "medium"
        ai_result["risk_reason"] = (
            ai_result.get("risk_reason", "") +
            f" Category mismatch: submitted '{submitted}', AI determined '{ai_category}'."
        )
        if final_approval == "auto":
            final_approval = "manager"
            override_notes.append(f"Category mismatch detected — routed to manager.")

    # ── Rule 5: Set final status ───────────────────────────────────────────────
    if final_approval == "auto":
        final_status = "approved"
    else:
        final_status = "pending"   # Awaiting human action

    # Append override notes to ai_notes if any rules fired
    if override_notes:
        existing = ai_result.get("ai_notes", "")
        ai_result["ai_notes"] = existing + " | Rules: " + " | ".join(override_notes)

    return {
        "ai_category": ai_result.get("ai_category"),
        "risk_flag": ai_result.get("risk_flag"),
        "risk_reason": ai_result.get("risk_reason"),
        "approval_level": final_approval,
        "status": final_status,
        "ai_notes": ai_result.get("ai_notes"),
    }


# ── Simple audit summary for logs ─────────────────────────────────────────────
def get_routing_summary(employee: str, amount: float, approval_level: str, status: str) -> str:
    return (
        f"Expense by {employee} | ₹{amount} | "
        f"Routed to: {approval_level.upper()} | Status: {status.upper()}"
    )