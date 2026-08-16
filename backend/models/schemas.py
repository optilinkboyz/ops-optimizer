"""
Pydantic schemas for the Operations Optimizer.
Covers route optimization, staffing calculation, and scenario analysis.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ── Shared Models ──────────────────────────────────────────────────────────

class Location(BaseModel):
    """A single delivery/service location."""
    id: str
    name: str
    latitude: float
    longitude: float
    demand: Optional[float] = Field(default=1.0, description="Units to deliver/service")


# ── Route Optimization ────────────────────────────────────────────────────

class RouteOptimizeRequest(BaseModel):
    """Request to optimize a delivery route."""
    locations: List[Location] = Field(..., min_length=2)
    depot_index: int = Field(default=0, description="Index of the starting depot in the locations list")
    num_vehicles: int = Field(default=1, ge=1, le=20)
    vehicle_capacity: Optional[float] = Field(default=None, description="Max demand per vehicle (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "locations": [
                    {"id": "depot", "name": "Warehouse", "latitude": 47.0707, "longitude": 15.4395, "demand": 0},
                    {"id": "c1", "name": "Customer A", "latitude": 47.08, "longitude": 15.45, "demand": 5},
                    {"id": "c2", "name": "Customer B", "latitude": 47.06, "longitude": 15.42, "demand": 3}
                ],
                "depot_index": 0,
                "num_vehicles": 1
            }
        }


class RouteStop(BaseModel):
    """A single stop in an optimized route, in visiting order."""
    order: int
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    distance_from_previous_km: float
    cumulative_distance_km: float


class VehicleRoute(BaseModel):
    """One vehicle's complete route."""
    vehicle_id: int
    stops: List[RouteStop]
    total_distance_km: float
    total_demand_served: float


class RouteOptimizeResponse(BaseModel):
    """Response containing the optimized route(s)."""
    success: bool
    routes: List[VehicleRoute]
    total_distance_km: float
    unoptimized_distance_km: float
    distance_saved_km: float
    percent_improvement: float
    message: str


# ── Staffing / Queueing ────────────────────────────────────────────────────

class StaffingRequest(BaseModel):
    """Request to calculate optimal staffing using M/M/s queueing model."""
    arrival_rate: float = Field(..., gt=0, description="Average customers/orders arriving per hour (lambda)")
    service_rate: float = Field(..., gt=0, description="Average customers/orders one server can handle per hour (mu)")
    target_wait_time_minutes: Optional[float] = Field(
        default=5.0, description="Maximum acceptable average wait time in minutes"
    )
    max_servers_to_test: int = Field(default=20, ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "arrival_rate": 40,
                "service_rate": 12,
                "target_wait_time_minutes": 5
            }
        }


class StaffingScenario(BaseModel):
    """Queueing metrics for a specific number of servers."""
    num_servers: int
    utilization: float
    avg_wait_time_minutes: float
    avg_queue_length: float
    probability_of_waiting: float
    meets_target: bool


class StaffingResponse(BaseModel):
    """Response containing staffing recommendations."""
    success: bool
    recommended_servers: int
    scenarios: List[StaffingScenario]
    message: str


# ── What-If Scenario ────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    """Request to test a demand change scenario."""
    current_arrival_rate: float = Field(..., gt=0)
    service_rate: float = Field(..., gt=0)
    current_servers: int = Field(..., ge=1)
    demand_change_percent: float = Field(..., description="e.g. 20 for +20%, -15 for -15%")
    target_wait_time_minutes: Optional[float] = Field(default=5.0)


class WhatIfResponse(BaseModel):
    """Response comparing current vs projected scenario."""
    success: bool
    current_scenario: StaffingScenario
    projected_scenario: StaffingScenario
    new_arrival_rate: float
    additional_servers_needed: int
    message: str


# ── Error ───────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
