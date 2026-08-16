"""
Route Optimization Service.
Uses Google OR-Tools to solve the Vehicle Routing Problem (VRP).
Follows Single Responsibility Principle — only handles route optimization logic.
"""
import logging
from typing import List, Tuple

from geopy.distance import geodesic
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from models.schemas import Location, RouteOptimizeResponse, RouteStop, VehicleRoute

logger = logging.getLogger(__name__)

# Scale factor: OR-Tools works with integers, so we convert km to metres*10 for precision
DISTANCE_SCALE = 1000


def build_distance_matrix(locations: List[Location]) -> List[List[int]]:
    """
    Builds a distance matrix (in scaled integer metres) between all locations.
    Uses geodesic (great-circle) distance — accurate for real-world coordinates.
    """
    n = len(locations)
    matrix = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                coord_i = (locations[i].latitude, locations[i].longitude)
                coord_j = (locations[j].latitude, locations[j].longitude)
                dist_km = geodesic(coord_i, coord_j).kilometers
                matrix[i][j] = int(dist_km * DISTANCE_SCALE)

    return matrix


def calculate_unoptimized_distance(locations: List[Location], depot_index: int) -> float:
    """
    Calculates the distance if locations are visited in their original (unoptimized) order.
    Used as a baseline to show improvement from optimization.
    """
    # Reorder so depot is first
    ordered = [locations[depot_index]] + [
        loc for i, loc in enumerate(locations) if i != depot_index
    ]

    total_km = 0.0
    for i in range(len(ordered) - 1):
        coord_a = (ordered[i].latitude, ordered[i].longitude)
        coord_b = (ordered[i + 1].latitude, ordered[i + 1].longitude)
        total_km += geodesic(coord_a, coord_b).kilometers

    # Return to depot
    coord_last = (ordered[-1].latitude, ordered[-1].longitude)
    coord_depot = (ordered[0].latitude, ordered[0].longitude)
    total_km += geodesic(coord_last, coord_depot).kilometers

    return round(total_km, 2)


def solve_vrp(
    locations: List[Location],
    depot_index: int,
    num_vehicles: int,
    vehicle_capacity: float = None,
) -> Tuple[List[List[int]], bool]:
    """
    Solves the Vehicle Routing Problem using OR-Tools.
    Returns (routes as lists of location indices per vehicle, success flag).
    """
    n = len(locations)
    distance_matrix = build_distance_matrix(locations)

    manager = pywrapcp.RoutingIndexManager(n, num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint if specified
    if vehicle_capacity is not None and vehicle_capacity > 0:
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return int(locations[from_node].demand or 0)

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [int(vehicle_capacity)] * num_vehicles,
            True,  # start cumul to zero
            "Capacity",
        )

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(10)

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        logger.warning("OR-Tools could not find a solution")
        return [], False

    # Extract routes
    routes = []
    for vehicle_id in range(num_vehicles):
        route = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # append end (depot)
        routes.append(route)

    return routes, True


def optimize_route(
    locations: List[Location],
    depot_index: int = 0,
    num_vehicles: int = 1,
    vehicle_capacity: float = None,
) -> RouteOptimizeResponse:
    """
    Main entry point: optimizes delivery routes for one or more vehicles.
    Returns a complete response with routes, distances, and improvement metrics.
    """
    if len(locations) < 2:
        raise ValueError("At least 2 locations are required (including depot).")

    if depot_index < 0 or depot_index >= len(locations):
        raise ValueError(f"depot_index must be between 0 and {len(locations) - 1}")

    raw_routes, success = solve_vrp(locations, depot_index, num_vehicles, vehicle_capacity)

    if not success:
        raise RuntimeError(
            "Could not find a valid route. Try increasing vehicle capacity or reducing stops."
        )

    vehicle_routes = []
    total_distance = 0.0

    for vehicle_id, route_indices in enumerate(raw_routes):
        if len(route_indices) <= 2:
            # Vehicle has no stops assigned (just depot -> depot)
            continue

        stops = []
        cumulative_km = 0.0
        total_demand = 0.0

        for order, loc_idx in enumerate(route_indices):
            loc = locations[loc_idx]

            if order == 0:
                distance_from_prev = 0.0
            else:
                prev_loc = locations[route_indices[order - 1]]
                coord_prev = (prev_loc.latitude, prev_loc.longitude)
                coord_curr = (loc.latitude, loc.longitude)
                distance_from_prev = round(geodesic(coord_prev, coord_curr).kilometers, 3)
                cumulative_km += distance_from_prev

            stops.append(RouteStop(
                order=order,
                location_id=loc.id,
                location_name=loc.name,
                latitude=loc.latitude,
                longitude=loc.longitude,
                distance_from_previous_km=distance_from_prev,
                cumulative_distance_km=round(cumulative_km, 3)
            ))
            total_demand += loc.demand or 0

        vehicle_routes.append(VehicleRoute(
            vehicle_id=vehicle_id,
            stops=stops,
            total_distance_km=round(cumulative_km, 2),
            total_demand_served=total_demand
        ))
        total_distance += cumulative_km

    unoptimized_distance = calculate_unoptimized_distance(locations, depot_index)
    distance_saved = round(unoptimized_distance - total_distance, 2)
    percent_improvement = round(
        (distance_saved / unoptimized_distance * 100) if unoptimized_distance > 0 else 0, 1
    )

    return RouteOptimizeResponse(
        success=True,
        routes=vehicle_routes,
        total_distance_km=round(total_distance, 2),
        unoptimized_distance_km=unoptimized_distance,
        distance_saved_km=max(distance_saved, 0),
        percent_improvement=max(percent_improvement, 0),
        message=f"Optimized {len(vehicle_routes)} route(s) across {len(locations) - 1} stops."
    )
