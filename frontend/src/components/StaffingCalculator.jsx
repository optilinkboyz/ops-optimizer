/**
 * StaffingCalculator Component
 * Handles staffing/capacity planning using M/M/s queueing theory.
 * Shows results as an interactive chart.
 */
import React, { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from "recharts";
import { calculateStaffing } from "../api";
import { SAMPLE_STAFFING } from "../sampleData";

export default function StaffingCalculator({ onResultChange }) {
  const [arrivalRate, setArrivalRate] = useState(SAMPLE_STAFFING.arrivalRate);
  const [serviceRate, setServiceRate] = useState(SAMPLE_STAFFING.serviceRate);
  const [targetWait, setTargetWait] = useState(SAMPLE_STAFFING.targetWaitMinutes);
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleCalculate = async () => {
    setIsCalculating(true);
    setError(null);
    try {
      const data = await calculateStaffing(arrivalRate, serviceRate, targetWait);
      setResult(data);
      if (onResultChange) {
        onResultChange({ arrivalRate, serviceRate, targetWait, recommended: data.recommended_servers });
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Calculation failed. Please try again.");
    } finally {
      setIsCalculating(false);
    }
  };

  const chartData = result
    ? result.scenarios.map((s) => ({
        servers: `${s.num_servers}`,
        waitTime: s.avg_wait_time_minutes === Infinity ? null : s.avg_wait_time_minutes,
        utilization: s.utilization,
        meetsTarget: s.meets_target,
      }))
    : [];

  return (
    <div className="module">
      <div className="module-controls">
        <div className="card">
          <h2 className="card-title">👥 Staffing Calculator</h2>
          <p className="card-subtitle">
            Uses M/M/s queueing theory (Erlang-C) to find the minimum staff needed.
          </p>

          <div className="input-group-vertical">
            <label>
              Arrival rate (customers/orders per hour)
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={arrivalRate}
                onChange={(e) => setArrivalRate(parseFloat(e.target.value) || 0)}
                className="text-input"
              />
            </label>

            <label>
              Service rate (per server, per hour)
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={serviceRate}
                onChange={(e) => setServiceRate(parseFloat(e.target.value) || 0)}
                className="text-input"
              />
            </label>

            <label>
              Target average wait time (minutes)
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={targetWait}
                onChange={(e) => setTargetWait(parseFloat(e.target.value) || 0)}
                className="text-input"
              />
            </label>
          </div>

          <button className="btn-primary full-width" onClick={handleCalculate} disabled={isCalculating}>
            {isCalculating ? <><div className="spinner-sm" /> Calculating...</> : "📊 Calculate Staffing"}
          </button>

          {error && <div className="error-banner">⚠️ {error}</div>}

          {result && (
            <div className="results-summary">
              <div className="stat-box highlight">
                <span className="stat-label">Recommended Staff</span>
                <span className="stat-value">{result.recommended_servers}</span>
              </div>
              <p className="result-message">{result.message}</p>
            </div>
          )}
        </div>
      </div>

      <div className="module-chart">
        <div className="card" style={{ height: "100%" }}>
          <h3 className="chart-title">Wait Time vs. Number of Staff</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={340}>
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e6ed" />
                <XAxis dataKey="servers" label={{ value: "Number of Staff", position: "bottom", offset: -5 }} />
                <YAxis label={{ value: "Avg Wait (min)", angle: -90, position: "insideLeft" }} />
                <Tooltip
                  formatter={(value, name) =>
                    name === "waitTime" ? [`${value} min`, "Avg Wait Time"] : [`${value}%`, "Utilization"]
                  }
                />
                <Legend />
                <ReferenceLine y={targetWait} stroke="#DC2626" strokeDasharray="4 4" label="Target" />
                <Bar dataKey="waitTime" fill="#2563EB" name="Avg Wait Time (min)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">
              <p>Run a calculation to see wait times across different staffing levels</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
