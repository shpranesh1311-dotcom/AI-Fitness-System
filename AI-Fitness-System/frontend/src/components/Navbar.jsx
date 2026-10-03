import React from "react";

const TABS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "food", label: "Food & Nutrition" },
  { key: "activity", label: "Activity" },
  { key: "recommendations", label: "AI Recommendations" },
  { key: "progress", label: "Progress" },
  { key: "profile", label: "Profile" },
];

export default function Navbar({ active, onChange, userName, onLogout }) {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="navbar-logo">🥗</span>
        <span>AI Fitness &amp; Nutrition</span>
      </div>
      <nav className="navbar-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`navbar-tab ${active === tab.key ? "active" : ""}`}
            onClick={() => onChange(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <div className="navbar-user">
        {userName && <span className="navbar-username">👤 {userName}</span>}
        {userName && (
          <button className="btn-link" onClick={onLogout}>
            Switch user
          </button>
        )}
      </div>
    </header>
  );
}
