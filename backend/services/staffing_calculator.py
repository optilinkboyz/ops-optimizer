"""
Staffing Calculator Service.
Uses M/M/s queueing theory to determine optimal staffing levels.

M/M/s Model — Erlang-C formulas.
"""
import logging
import math
from typing import List

from models.schemas import StaffingScenario

logger = logging.getLogger(__name__)

# Used instead of float('inf') — JSON cannot serialize Infinity
UNSTABLE_WAIT_TIME = 999999.0
UNSTABLE_QUEUE_LENGTH = 999999.0


def erlang_c(num_servers: int, traffic_intensity: float) -> float:
    """Calculates the Erlang-C probability that an arriving customer must wait."""
    if num_servers <= traffic_intensity:
        return 1.0

    erlang_b = 1.0
    for k in range(1, num_servers + 1):
        erlang_b = (traffic_intensity * erlang_b) / (k + traffic_intensity * erlang_b)

    rho = traffic_intensity / num_servers
    erlang_c_prob = erlang_b / (1 - rho * (1 - erlang_b))

    return min(erlang_c_prob, 1.0)


def calculate_mms_metrics(
    arrival_rate: float,
    service_rate: float,
    num_servers: int
) -> StaffingScenario:
    """Calculates key M/M/s queueing metrics for a given number of servers."""
    traffic_intensity = arrival_rate / service_rate
    utilization = traffic_intensity / num_servers

    if utilization >= 1.0:
        # System is unstable — use large finite number instead of infinity
        # (JSON does not support Infinity, so we cap the value)
        return StaffingScenario(
            num_servers=num_servers,
            utilization=round(min(utilization, 1.0) * 100, 1),
            avg_wait_time_minutes=UNSTABLE_WAIT_TIME,
            avg_queue_length=UNSTABLE_QUEUE_LENGTH,
            probability_of_waiting=1.0,
            meets_target=False
        )

    prob_wait = erlang_c(num_servers, traffic_intensity)
    avg_wait_hours = prob_wait / (num_servers * service_rate - arrival_rate)
    avg_wait_minutes = avg_wait_hours * 60
    avg_queue_length = arrival_rate * avg_wait_hours

    return StaffingScenario(
        num_servers=num_servers,
        utilization=round(utilization * 100, 1),
        avg_wait_time_minutes=round(avg_wait_minutes, 2),
        avg_queue_length=round(avg_queue_length, 2),
        probability_of_waiting=round(prob_wait, 3),
        meets_target=False
    )


def find_optimal_staffing(
    arrival_rate: float,
    service_rate: float,
    target_wait_time_minutes: float = 5.0,
    max_servers_to_test: int = 20
) -> tuple[int, List[StaffingScenario]]:
    """Tests increasing numbers of servers until the target wait time is met."""
    traffic_intensity = arrival_rate / service_rate
    min_servers = math.floor(traffic_intensity) + 1

    scenarios = []
    recommended = None

    for s in range(min_servers, min_servers + max_servers_to_test):
        scenario = calculate_mms_metrics(arrival_rate, service_rate, s)
        meets_target = scenario.avg_wait_time_minutes <= target_wait_time_minutes
        scenario.meets_target = meets_target

        scenarios.append(scenario)

        if meets_target and recommended is None:
            recommended = s

        if recommended is not None and s >= recommended + 2:
            break

    if recommended is None:
        recommended = scenarios[-1].num_servers
        logger.warning(
            f"Target wait time of {target_wait_time_minutes}min not achievable "
            f"within {max_servers_to_test} servers tested."
        )

    return recommended, scenarios
