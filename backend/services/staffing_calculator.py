"""
Staffing Calculator Service.
Uses M/M/s queueing theory to determine optimal staffing levels.
Follows Single Responsibility Principle — only handles queueing calculations.

M/M/s Model:
- M = Markovian (Poisson) arrivals
- M = Markovian (exponential) service times
- s = number of servers

Reference: Standard Erlang-C queueing formulas.
"""
import logging
import math
from typing import List

from models.schemas import StaffingScenario

logger = logging.getLogger(__name__)


def erlang_c(num_servers: int, traffic_intensity: float) -> float:
    """
    Calculates the Erlang-C probability that an arriving customer must wait
    (i.e., all servers are busy).

    num_servers (s): number of servers
    traffic_intensity (a): arrival_rate / service_rate (offered load in Erlangs)
    """
    if num_servers <= traffic_intensity:
        # System is unstable — infinite queue growth
        return 1.0

    # Calculate Erlang B first (probability of blocking in a loss system)
    erlang_b = 1.0
    for k in range(1, num_servers + 1):
        erlang_b = (traffic_intensity * erlang_b) / (k + traffic_intensity * erlang_b)

    # Convert Erlang B to Erlang C
    rho = traffic_intensity / num_servers
    erlang_c_prob = erlang_b / (1 - rho * (1 - erlang_b))

    return min(erlang_c_prob, 1.0)


def calculate_mms_metrics(
    arrival_rate: float,
    service_rate: float,
    num_servers: int
) -> StaffingScenario:
    """
    Calculates key M/M/s queueing metrics for a given number of servers.

    arrival_rate (lambda): customers/orders arriving per hour
    service_rate (mu): customers/orders one server can handle per hour
    num_servers (s): number of servers being tested
    """
    traffic_intensity = arrival_rate / service_rate  # offered load in Erlangs
    utilization = traffic_intensity / num_servers

    if utilization >= 1.0:
        # System is unstable at this server count — infinite wait
        return StaffingScenario(
            num_servers=num_servers,
            utilization=round(min(utilization, 1.0) * 100, 1),
            avg_wait_time_minutes=float('inf'),
            avg_queue_length=float('inf'),
            probability_of_waiting=1.0,
            meets_target=False
        )

    prob_wait = erlang_c(num_servers, traffic_intensity)

    # Average wait time in queue (Wq) using Erlang-C formula
    avg_wait_hours = prob_wait / (num_servers * service_rate - arrival_rate)
    avg_wait_minutes = avg_wait_hours * 60

    # Average queue length (Lq) using Little's Law: Lq = lambda * Wq
    avg_queue_length = arrival_rate * avg_wait_hours

    return StaffingScenario(
        num_servers=num_servers,
        utilization=round(utilization * 100, 1),
        avg_wait_time_minutes=round(avg_wait_minutes, 2),
        avg_queue_length=round(avg_queue_length, 2),
        probability_of_waiting=round(prob_wait, 3),
        meets_target=False  # set by caller based on target
    )


def find_optimal_staffing(
    arrival_rate: float,
    service_rate: float,
    target_wait_time_minutes: float = 5.0,
    max_servers_to_test: int = 20
) -> tuple[int, List[StaffingScenario]]:
    """
    Tests increasing numbers of servers until the target wait time is met.
    Returns the recommended number of servers and all tested scenarios.
    """
    traffic_intensity = arrival_rate / service_rate

    # Minimum servers needed just for stability (utilization < 100%)
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

        # Stop testing once we've found the optimal and shown 2 more for context
        if recommended is not None and s >= recommended + 2:
            break

    if recommended is None:
        # Target not achievable within max_servers_to_test — recommend the last tested
        recommended = scenarios[-1].num_servers
        logger.warning(
            f"Target wait time of {target_wait_time_minutes}min not achievable "
            f"within {max_servers_to_test} servers tested."
        )

    return recommended, scenarios
