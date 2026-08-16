/**
 * API Service
 * Centralized axios calls to the Operations Optimizer backend.
 */
import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8002";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

/**
 * Optimize a delivery route.
 * @param {Array} locations - [{id, name, latitude, longitude, demand}]
 * @param {number} depotIndex
 * @param {number} numVehicles
 * @param {number|null} vehicleCapacity
 */
export const optimizeRoute = async (
  locations,
  depotIndex = 0,
  numVehicles = 1,
  vehicleCapacity = null
) => {
  const response = await api.post("/route/optimize", {
    locations,
    depot_index: depotIndex,
    num_vehicles: numVehicles,
    vehicle_capacity: vehicleCapacity,
  });
  return response.data;
};

/**
 * Calculate optimal staffing.
 * @param {number} arrivalRate
 * @param {number} serviceRate
 * @param {number} targetWaitMinutes
 */
export const calculateStaffing = async (
  arrivalRate,
  serviceRate,
  targetWaitMinutes = 5
) => {
  const response = await api.post("/staffing/calculate", {
    arrival_rate: arrivalRate,
    service_rate: serviceRate,
    target_wait_time_minutes: targetWaitMinutes,
  });
  return response.data;
};

/**
 * Run a what-if demand scenario.
 * @param {number} currentArrivalRate
 * @param {number} serviceRate
 * @param {number} currentServers
 * @param {number} demandChangePercent
 * @param {number} targetWaitMinutes
 */
export const runWhatIfScenario = async (
  currentArrivalRate,
  serviceRate,
  currentServers,
  demandChangePercent,
  targetWaitMinutes = 5
) => {
  const response = await api.post("/scenario/whatif", {
    current_arrival_rate: currentArrivalRate,
    service_rate: serviceRate,
    current_servers: currentServers,
    demand_change_percent: demandChangePercent,
    target_wait_time_minutes: targetWaitMinutes,
  });
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};
