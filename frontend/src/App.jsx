import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import StatsBar from "./components/StatsBar";
import ExpenseTable from "./components/ExpenseTable";
import SubmitForm from "./components/SubmitForm";
import "./App.css";

const API = "http://localhost:8000";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState("all");

  const fetchData = useCallback(async () => {
    try {
      const url =
        activeFilter === "all"
          ? `${API}/expenses`
          : `${API}/expenses?status=${activeFilter}`;
      const [expRes, statsRes] = await Promise.all([
        axios.get(url),
        axios.get(`${API}/dashboard`),
      ]);
      setExpenses(expRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, [activeFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusUpdate = async (id, status) => {
    await axios.patch(`${API}/expenses/${id}/status`, { status });
    fetchData();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <h1>💼 Expense Automation Agent</h1>
          <span className="header-sub">AI-Powered • Auto-Routed • Real-Time</span>
        </div>
      </header>

      <main className="app-main">
        <StatsBar stats={stats} />

        <div className="content-grid">
          <div className="table-section">
            <div className="section-header">
              <h2>Expense Records</h2>
              <div className="filters">
                {["all", "pending", "approved", "rejected"].map((f) => (
                  <button
                    key={f}
                    className={`filter-btn ${activeFilter === f ? "active" : ""}`}
                    onClick={() => setActiveFilter(f)}
                  >
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="loading">Loading expenses...</div>
            ) : (
              <ExpenseTable
                expenses={expenses}
                onStatusUpdate={handleStatusUpdate}
              />
            )}
          </div>

          <div className="form-section">
            <h2>Submit Expense</h2>
            <SubmitForm onSubmitted={fetchData} />
          </div>
        </div>
      </main>
    </div>
  );
}