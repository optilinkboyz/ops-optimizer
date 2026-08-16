import React, { useState, useEffect } from "react";
import { runWhatIfScenario } from "../api";

const UNSTABLE_THRESHOLD = 100000; // matches backend's UNSTABLE_WAIT_TIME cap

function formatWaitTime(minutes) {
  if (minutes >= UNSTABLE_THRESHOLD) {
    return "∞ (system overloaded)";
  }
  return `${minutes} min`;
}

export default function WhatIfScenario({ baseline }) {
  const [currentServers, setCurrentServers] = useState(4);
  const [demandChange, setDemandChange] = useState(20);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (baseline?.recommended) {
      setCurrentServers(baseline.recommended);
    }
  }, [baseline]);

  const handleRun = async () => {
    if (!baseline) {
      setError("Please run the Staffing Calculator first to establish a baseline.");
      return;
    }

    setIsRunning(true);
    setError(null);
    try {
      const data = await runWhatIfScenario(
        baseline.arrivalRate,
        baseline.serviceRate,
        currentServers,
        demandChange,
        baseline.targetWait
      );
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Scenario calculation failed.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="module">
      <div className="module-controls full-span">
        <div className="card">
          <h2 className="card-title">🔮 What-If Scenario Analysis</h2>
          <p className="card-subtitle">
            Test how demand changes affect wait times and staffing needs.
          </p>

          {!baseline && (
            <div className="info-banner">
              💡 Run the Staffing Calculator first to set a baseline for this scenario.
            </div>
          )}

          <div className="input-group-vertical">
            <label>
              Current number of staff
              <input
                type="number"
                min="1"
                value={currentServers}
                onChange={(e) => setCurrentServers(parseInt(e.target.value) || 1)}
                className="text-input"
              />
            </label>

            <label>
              Demand change: <strong>{demandChange > 0 ? "+" : ""}{demandChange}%</strong>
              <input
                type="range"
                min="-50"
                max="100"
                step="5"
                value={demandChange}
                onChange={(e) => setDemandChange(parseInt(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>-50%</span>
                <span>0%</span>
                <span>+100%</span>
              </div>
            </label>
          </div>

          <button className="btn-primary full-width" onClick={handleRun} disabled={isRunning || !baseline}>
            {isRunning ? <><div className="spinner-sm" /> Running...</> : "▶ Run Scenario"}
          </button>

          {error && <div className="error-banner">⚠️ {error}</div>}
        </div>
      </div>

      {result && (
        <div className="module-comparison full-span">
          <div className="comparison-grid">
            <div className="card comparison-card">
              <h3 className="comparison-title">Current Scenario</h3>
              <div className="comparison-stat">
                <span>Arrival Rate</span>
                <strong>{baseline.arrivalRate}/hr</strong>
              </div>
              <div className="comparison-stat">
                <span>Staff</span>
                <strong>{currentServers}</strong>
              </div>
              <div className="comparison-stat">
                <span>Avg Wait</span>
                <strong>{formatWaitTime(result.current_scenario.avg_wait_time_minutes)}</strong>
              </div>
              <div className={`status-badge ${result.current_scenario.meets_target ? "good" : "bad"}`}>
                {result.current_scenario.meets_target ? "✅ Meets Target" : "❌ Below Target"}
              </div>
            </div>

            <div className="comparison-arrow">→</div>

            <div className={`card comparison-card ${!result.projected_scenario.meets_target ? "warning" : ""}`}>
              <h3 className="comparison-title">
                Projected ({demandChange > 0 ? "+" : ""}{demandChange}% demand)
              </h3>
              <div className="comparison-stat">
                <span>Arrival Rate</span>
                <strong>{result.new_arrival_rate}/hr</strong>
              </div>
              <div className="comparison-stat">
                <span>Staff</span>
                <strong>{currentServers}</strong>
              </div>
              <div className="comparison-stat">
                <span>Avg Wait</span>
                <strong>{formatWaitTime(result.projected_scenario.avg_wait_time_minutes)}</strong>
              </div>
              <div className={`status-badge ${result.projected_scenario.meets_target ? "good" : "bad"}`}>
                {result.projected_scenario.meets_target ? "✅ Meets Target" : "❌ Below Target"}
              </div>
            </div>
          </div>

          <div className="recommendation-banner">
            <strong>💡 Recommendation:</strong> {result.message}
          </div>
        </div>
      )}
    </div>
  );
}
