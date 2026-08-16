/**
 * Sample data for demo purposes.
 * Real Graz-area coordinates so the map demo looks realistic.
 */

export const SAMPLE_LOCATIONS = [
  { id: "depot", name: "Warehouse (Graz Centre)", latitude: 47.0707, longitude: 15.4395, demand: 0 },
  { id: "c1", name: "Liebenau", latitude: 47.0468, longitude: 15.4558, demand: 5 },
  { id: "c2", name: "Puntigam", latitude: 47.0289, longitude: 15.4343, demand: 3 },
  { id: "c3", name: "Wetzelsdorf", latitude: 47.0504, longitude: 15.4120, demand: 4 },
  { id: "c4", name: "Jakomini", latitude: 47.0619, longitude: 15.4487, demand: 2 },
  { id: "c5", name: "Gries", latitude: 47.0654, longitude: 15.4280, demand: 6 },
  { id: "c6", name: "St. Leonhard", latitude: 47.0780, longitude: 15.4550, demand: 3 },
];

export const SAMPLE_CSV_TEMPLATE = `id,name,latitude,longitude,demand
depot,Warehouse,47.0707,15.4395,0
c1,Customer A,47.0468,15.4558,5
c2,Customer B,47.0289,15.4343,3
c3,Customer C,47.0504,15.4120,4`;

export const SAMPLE_STAFFING = {
  arrivalRate: 40,
  serviceRate: 12,
  targetWaitMinutes: 5,
};
