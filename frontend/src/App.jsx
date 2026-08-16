/**
 * Operations & Supply Chain Optimizer
 * Main App Component — tab navigation between Route, Staffing, and What-If modules.
 */
import React, { useState } from "react";
import RouteOptimizer from "./components/RouteOptimizer";
import StaffingCalculator from "./components/StaffingCalculator";
import WhatIfScenario from "./components/WhatIfScenario";
import "./index.css";

const TABS = [
  { id: "route", label: "🗺️ Route Optimization", desc: "Minimize delivery distance" },
  { id: "staffing", label: "👥 Staffing Calculator", desc: "Optimal capacity planning" },
  { id: "whatif", label: "🔮 What-If Analysis", desc: "Test demand scenarios" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("route");
  const [staffingBaseline, setStaffingBaseline] = useState(null);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-logo">
            <span className="logo-icon">⚙️</span>
            <div>
              <h1 className="header-title">Operations Optimizer</h1>
              <p className="header-subtitle">Route Planning · Capacity Analysis · Scenario Testing</p>
            </div>
          </div>
        </div>
      </header>

      <nav className="tab-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-label">{tab.label}</span>
            <span className="tab-desc">{tab.desc}</span>
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === "route" && <RouteOptimizer />}
        {activeTab === "staffing" && (
          <StaffingCalculator onResultChange={setStaffingBaseline} />
        )}
        {activeTab === "whatif" && <WhatIfScenario baseline={staffingBaseline} />}
      </main>

      <footer className="app-footer">
        <p>
          Operations &amp; Supply Chain Optimizer &bull; Built with OR-Tools &amp; Queueing Theory &bull;{" "}
          <span className="footer-version">v1.0.0</span>
        </p>
      </footer>
    </div>
  );
}
