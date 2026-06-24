export default function StatsBar({ stats }) {
  if (!stats) return <div className="stats-bar loading">Loading stats...</div>;

  const cards = [
    { label: "Total Submitted", value: stats.total, color: "#3b82f6" },
    { label: "Pending Review", value: stats.pending, color: "#f59e0b" },
    { label: "Auto Approved", value: stats.approved, color: "#10b981" },
    { label: "High Risk Flagged", value: stats.flagged, color: "#ef4444" },
    { label: "Rejected", value: stats.rejected, color: "#6b7280" },
    {
      label: "Total Amount",
      value: `₹${stats.total_amount.toLocaleString("en-IN")}`,
      color: "#8b5cf6",
    },
    {
      label: "Flagged Amount",
      value: `₹${stats.flagged_amount.toLocaleString("en-IN")}`,
      color: "#ef4444",
    },
  ];

  return (
    <div className="stats-bar">
      {cards.map((card) => (
        <div className="stat-card" key={card.label}>
          <div className="stat-value" style={{ color: card.color }}>
            {card.value}
          </div>
          <div className="stat-label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}