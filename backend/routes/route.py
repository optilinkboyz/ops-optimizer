"""
Route optimization route.
Accepts a list of locations and returns optimized delivery routes.
"""
import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ErrorResponse, RouteOptimizeRequest, RouteOptimizeResponse
from services.route_optimizer import optimize_route

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/route", tags=["Route Optimization"])


@router.post(
    "/optimize",
    response_model=RouteOptimizeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Optimize delivery route(s)",
    description="Given a list of locations and a depot, returns the optimal visiting order to minimise total distance."
)
async def optimize(request: RouteOptimizeRequest):
    """
    Solves the Vehicle Routing Problem for the given locations.
    Returns optimized route(s), total distance, and improvement vs unoptimized order.
    """
    logger.info(
        f"Route optimization request: {len(request.locations)} locations, "
        f"{request.num_vehicles} vehicle(s)"
    )

    try:
        result = optimize_route(
            locations=request.locations,
            depot_index=request.depot_index,
            num_vehicles=request.num_vehicles,
            vehicle_capacity=request.vehicle_capacity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in route optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during optimization.")

    logger.info(
        f"Optimization complete: {result.percent_improvement}% improvement, "
        f"{result.distance_saved_km}km saved"
    )

    return result
