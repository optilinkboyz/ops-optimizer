"""
Staffing calculation route.
Uses M/M/s queueing theory to recommend optimal staffing levels.
"""
import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ErrorResponse, StaffingRequest, StaffingResponse
from services.staffing_calculator import find_optimal_staffing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/staffing", tags=["Staffing / Capacity Planning"])


@router.post(
    "/calculate",
    response_model=StaffingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Calculate optimal staffing level",
    description="Given arrival rate, service rate, and a target wait time, recommends the minimum number of staff/servers needed."
)
async def calculate_staffing(request: StaffingRequest):
    """
    Uses M/M/s queueing theory to find the minimum number of servers
    that achieves the target average wait time.
    """
    logger.info(
        f"Staffing request: arrival_rate={request.arrival_rate}, "
        f"service_rate={request.service_rate}, target={request.target_wait_time_minutes}min"
    )

    if request.arrival_rate <= 0 or request.service_rate <= 0:
        raise HTTPException(status_code=400, detail="Arrival rate and service rate must be positive.")

    try:
        recommended, scenarios = find_optimal_staffing(
            arrival_rate=request.arrival_rate,
            service_rate=request.service_rate,
            target_wait_time_minutes=request.target_wait_time_minutes or 5.0,
            max_servers_to_test=request.max_servers_to_test,
        )
    except Exception as e:
        logger.error(f"Staffing calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred calculating staffing levels.")

    logger.info(f"Recommended staffing: {recommended} servers")

    return StaffingResponse(
        success=True,
        recommended_servers=recommended,
        scenarios=scenarios,
        message=(
            f"Recommended {recommended} staff to achieve an average wait time under "
            f"{request.target_wait_time_minutes} minutes."
        )
    )
