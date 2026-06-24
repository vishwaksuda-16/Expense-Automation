const RISK_COLORS = {
  low: { bg: "#d1fae5", text: "#065f46" },
  medium: { bg: "#fef3c7", text: "#92400e" },
  high: { bg: "#fee2e2", text: "#991b1b" },
};

const STATUS_COLORS = {
  approved: { bg: "#d1fae5", text: "#065f46" },
  pending: { bg: "#fef3c7", text: "#92400e" },
  rejected: { bg: "#fee2e2", text: "#991b1b" },
};

const APPROVAL_LABELS = {
  auto: "⚡ Auto",
  manager: "👤 Manager",
  director: "🏢 Director",
  finance_review: "🔍 Finance",
};

function Badge({ value, colorMap }) {
  const style = colorMap[value] || { bg: "#f3f4f6", text: "#374151" };
  return (
    <span
      className="badge"
      style={{ backgroundColor: style.bg, color: style.text }}
    >
      {value}
    </span>
  );
}

export default function ExpenseTable({ expenses, onStatusUpdate }) {
  if (expenses.length === 0) {
    return <div className="empty">No expenses found. Submit one to get started.</div>;
  }

  return (
    <div className="table-wrapper">
      <table className="expense-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Employee</th>
            <th>Amount</th>
            <th>Submitted As</th>
            <th>AI Category</th>
            <th>Risk</th>
            <th>Route</th>
            <th>Status</th>
            <th>AI Notes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((exp) => (
            <tr key={exp.id} className={exp.risk_flag === "high" ? "row-flagged" : ""}>
              <td>{exp.id}</td>
              <td>{exp.employee}</td>
              <td className="amount">₹{exp.amount.toLocaleString("en-IN")}</td>
              <td>{exp.submitted_category}</td>
              <td>{exp.ai_category || "—"}</td>
              <td>
                <Badge value={exp.risk_flag || "—"} colorMap={RISK_COLORS} />
              </td>
              <td>{APPROVAL_LABELS[exp.approval_level] || exp.approval_level}</td>
              <td>
                <Badge value={exp.status} colorMap={STATUS_COLORS} />
              </td>
              <td className="notes" title={exp.ai_notes}>
                {exp.ai_notes ? exp.ai_notes.slice(0, 60) + (exp.ai_notes.length > 60 ? "…" : "") : "—"}
              </td>
              <td className="actions">
                {exp.status === "pending" && (
                  <>
                    <button
                      className="btn-approve"
                      onClick={() => onStatusUpdate(exp.id, "approved")}
                    >
                      ✓
                    </button>
                    <button
                      className="btn-reject"
                      onClick={() => onStatusUpdate(exp.id, "rejected")}
                    >
                      ✕
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}