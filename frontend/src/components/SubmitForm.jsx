import { useState } from "react";
import axios from "axios";

const CATEGORIES = [
  "Travel", "Meals", "Accommodation", "Supplies",
  "Equipment", "Entertainment", "Training", "Software", "Medical", "Other",
];

const EMPTY_FORM = {
  employee: "",
  amount: "",
  submitted_category: "Travel",
  description: "",
  receipt_ref: "",
};

export default function SubmitForm({ onSubmitted }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!form.employee || !form.amount || !form.description) {
      setError("Employee, amount, and description are required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    setResult(null);
    try {
      const res = await axios.post("http://localhost:8000/expenses", {
        ...form,
        amount: parseFloat(form.amount),
      });
      setResult(res.data);
      setForm(EMPTY_FORM);
      onSubmitted();
    } catch (err) {
      setError(err.response?.data?.detail || "Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const riskColor = { low: "#10b981", medium: "#f59e0b", high: "#ef4444" };

  return (
    <div className="submit-form">
      <div className="form-group">
        <label>Employee Name</label>
        <input
          name="employee"
          value={form.employee}
          onChange={handleChange}
          placeholder="e.g. Vishwak"
        />
      </div>

      <div className="form-group">
        <label>Amount (₹)</label>
        <input
          name="amount"
          type="number"
          value={form.amount}
          onChange={handleChange}
          placeholder="e.g. 4500"
          min="1"
        />
      </div>

      <div className="form-group">
        <label>Category</label>
        <select name="submitted_category" value={form.submitted_category} onChange={handleChange}>
          {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          placeholder="e.g. Flight to Delhi for client meeting"
          rows={3}
        />
      </div>

      <div className="form-group">
        <label>Receipt Ref (optional)</label>
        <input
          name="receipt_ref"
          value={form.receipt_ref}
          onChange={handleChange}
          placeholder="e.g. BOOKING_REF_123"
        />
      </div>

      {error && <div className="form-error">{error}</div>}

      <button
        className="submit-btn"
        onClick={handleSubmit}
        disabled={submitting}
      >
        {submitting ? "⏳ Processing..." : "🚀 Submit & Analyze"}
      </button>

      {/* AI Result Panel */}
      {result && (
        <div className="ai-result">
          <div className="ai-result-header">⚡ AI Decision</div>
          <div className="ai-result-grid">
            <div className="ai-field">
              <span className="ai-label">Category</span>
              <span className="ai-value">{result.ai_category}</span>
            </div>
            <div className="ai-field">
              <span className="ai-label">Risk</span>
              <span className="ai-value" style={{ color: riskColor[result.risk_flag] }}>
                ● {result.risk_flag?.toUpperCase()}
              </span>
            </div>
            <div className="ai-field">
              <span className="ai-label">Routed To</span>
              <span className="ai-value">{result.approval_level}</span>
            </div>
            <div className="ai-field">
              <span className="ai-label">Status</span>
              <span className="ai-value">{result.status}</span>
            </div>
          </div>
          <div className="ai-reason">
            <strong>Risk Reason:</strong> {result.risk_reason}
          </div>
          <div className="ai-notes-full">
            <strong>AI Notes:</strong> {result.ai_notes}
          </div>
        </div>
      )}
    </div>
  );
}