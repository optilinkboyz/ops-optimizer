import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";
import Papa from "papaparse";
import { optimizeRoute } from "../api";
import { SAMPLE_LOCATIONS, SAMPLE_CSV_TEMPLATE } from "../sampleData";

const defaultIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const depotIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [30, 46],
  iconAnchor: [15, 46],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: "depot-marker",
});

export default function RouteOptimizer() {
  const [locations, setLocations] = useState(SAMPLE_LOCATIONS);
  const [numVehicles, setNumVehicles] = useState(1);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const mapCenter = [47.0707, 15.4395];

  const handleCsvUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const parsed = results.data.map((row) => ({
            id: String(row.id),
            name: String(row.name),
            latitude: parseFloat(row.latitude),
            longitude: parseFloat(row.longitude),
            demand: parseFloat(row.demand) || 0,
          }));

          if (parsed.length < 2) {
            setError("CSV must contain at least 2 locations (depot + 1 customer).");
            return;
          }

          setLocations(parsed);
          setResult(null);
          setError(null);
        } catch (err) {
          setError("Could not parse CSV. Please check the format matches the template.");
        }
      },
      error: () => setError("Failed to read CSV file."),
    });
    e.target.value = "";
  };

  const downloadTemplate = () => {
    const blob = new Blob([SAMPLE_CSV_TEMPLATE], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "route_locations_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setError(null);
    try {
      const data = await optimizeRoute(locations, 0, numVehicles);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Optimization failed. Please try again.");
    } finally {
      setIsOptimizing(false);
    }
  };

  const useSampleData = () => {
    setLocations(SAMPLE_LOCATIONS);
    setResult(null);
    setError(null);
  };

  const routeColors = ["#2563EB", "#DC2626", "#059669", "#D97706", "#7C3AED"];

  return (
    <div className="module">
      <div className="module-controls">
        <div className="card">
          <h2 className="card-title">📍 Delivery Locations</h2>
          <p className="card-subtitle">
            {locations.length} locations loaded ({locations.length - 1} customers + 1 depot)
          </p>

          <div className="btn-row">
            <button className="btn-secondary" onClick={useSampleData}>
              🎲 Use Sample Data
            </button>
            <label className="btn-secondary file-label">
              📤 Upload CSV
              <input type="file" accept=".csv" onChange={handleCsvUpload} style={{ display: "none" }} />
            </label>
            <button className="btn-text" onClick={downloadTemplate}>
              ⬇ Download Template
            </button>
          </div>

          <div className="input-row">
            <label>
              Number of vehicles:
              <input
                type="number"
                min="1"
                max="10"
                value={numVehicles}
                onChange={(e) => setNumVehicles(parseInt(e.target.value) || 1)}
                className="number-input"
              />
            </label>
          </div>

          <button className="btn-primary full-width" onClick={handleOptimize} disabled={isOptimizing}>
            {isOptimizing ? <><div className="spinner-sm" /> Optimizing...</> : "🚀 Optimize Route"}
          </button>

          {error && <div className="error-banner">⚠️ {error}</div>}

          {result && (
            <div className="results-summary">
              <div className="stat-box">
                <span className="stat-label">Optimized Distance</span>
                <span className="stat-value">{result.total_distance_km} km</span>
              </div>
              <div className="stat-box highlight">
                <span className="stat-label">Distance Saved</span>
                <span className="stat-value">{result.distance_saved_km} km</span>
              </div>
              <div className="stat-box highlight">
                <span className="stat-label">Improvement</span>
                <span className="stat-value">{result.percent_improvement}%</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="module-map">
        <MapContainer center={mapCenter} zoom={12} style={{ height: "100%", width: "100%", borderRadius: "12px" }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {locations.map((loc, i) => (
            <Marker
              key={loc.id}
              position={[loc.latitude, loc.longitude]}
              icon={i === 0 ? depotIcon : defaultIcon}
            >
              <Popup>
                <strong>{loc.name}</strong>
                {i === 0 ? " (Depot)" : ` — Demand: ${loc.demand}`}
              </Popup>
            </Marker>
          ))}
          {result &&
            result.routes.map((route, idx) => (
              <Polyline
                key={route.vehicle_id}
                positions={route.stops.map((s) => [s.latitude, s.longitude])}
                color={routeColors[idx % routeColors.length]}
                weight={4}
                opacity={0.8}
              />
            ))}
        </MapContainer>
      </div>
    </div>
  );
}
