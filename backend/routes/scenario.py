"""
What-if scenario route.
Compares current staffing to a projected scenario with changed demand.
"""
import logging

from fastapi import APIRouter, HTTPException

from models.schemas import ErrorResponse, WhatIfRequest, WhatIfResponse
from services.staffing_calculator import calculate_mms_metrics, find_optimal_staffing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenario", tags=["What-If Scenario Analysis"])


@router.post(
    "/whatif",
    response_model=WhatIfResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Run a what-if demand scenario",
    description="Compares your current staffing against a projected scenario (e.g. +20% demand) and recommends how many additional staff are needed."
)
async def whatif_scenario(request: WhatIfRequest):
    """
    Calculates current vs projected queueing metrics based on a demand change percentage.
    Useful for answering: 'What happens if demand increases 20%?'
    """
    logger.info(
        f"What-if request: current_rate={request.current_arrival_rate}, "
        f"change={request.demand_change_percent}%, current_servers={request.current_servers}"
    )

    if request.current_arrival_rate <= 0 or request.service_rate <= 0:
        raise HTTPException(status_code=400, detail="Arrival rate and service rate must be positive.")

    try:
        # Current scenario
        current = calculate_mms_metrics(
            request.current_arrival_rate, request.service_rate, request.current_servers
        )
        target = request.target_wait_time_minutes or 5.0
        current.meets_target = current.avg_wait_time_minutes <= target

        # Projected scenario with demand change
        new_arrival_rate = request.current_arrival_rate * (1 + request.demand_change_percent / 100)

        if new_arrival_rate <= 0:
            raise HTTPException(status_code=400, detail="Demand change results in zero or negative arrival rate.")

        projected = calculate_mms_metrics(
            new_arrival_rate, request.service_rate, request.current_servers
        )
        projected.meets_target = projected.avg_wait_time_minutes <= target

        # If projected scenario doesn't meet target, find how many servers WOULD be needed
        additional_needed = 0
        if not projected.meets_target:
            recommended, _ = find_optimal_staffing(
                new_arrival_rate, request.service_rate, target, max_servers_to_test=30
            )
            additional_needed = max(0, recommended - request.current_servers)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"What-if calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred running the scenario.")

    direction = "increase" if request.demand_change_percent >= 0 else "decrease"
    message = (
        f"With a {abs(request.demand_change_percent)}% demand {direction}, "
        f"your current {request.current_servers} staff "
        f"{'still meet' if projected.meets_target else 'would NOT meet'} the target wait time."
    )
    if additional_needed > 0:
        message += f" You would need {additional_needed} additional staff."

    return WhatIfResponse(
        success=True,
        current_scenario=current,
        projected_scenario=projected,
        new_arrival_rate=round(new_arrival_rate, 2),
        additional_servers_needed=additional_needed,
        message=message
    )
