# -*- coding: utf-8 -*-
"""
Synth AT Delays - Passenger Linking Module

This module provides functionality for creating connections between flights,
simulating passenger transfers between aircraft. It handles the creation of
dependencies between flights and checking if dependent flights have been completed.

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np
from typing import List, Any


def LinkPassengers(Options: Any, scheduledFlights: List) -> List:
    """
    Create links between compatible flights to simulate connecting passengers.

    Pre-compute valid routes and cache flight details for better performance.

    Parameters
    ----------
    Options : Any
        Options class containing passenger linking parameters
    scheduledFlights : List
        List of scheduled flights to process

    Returns
    -------
    List
        Updated list of scheduled flights with dependencies
    """
    if Options.paxLinks is None:
        return scheduledFlights

    # Pre-compute valid routes for faster lookup
    valid_routes = set()
    for route in Options.paxLinks:
        valid_routes.add((route[0], route[1], route[2]))

    # Original nested loop structure with optimizations
    for fl1 in range(len(scheduledFlights)):
        # Cache flight 1 details outside the inner loop
        fl1_flight = scheduledFlights[fl1]
        fl1_orig_airp = fl1_flight.origAirp
        fl1_dest_airp = fl1_flight.destAirp
        fl1_sched_dep_time = fl1_flight.schedDepTime

        for fl2 in range(len(scheduledFlights)):
            # Get flight 2 details
            fl2_flight = scheduledFlights[fl2]

            # Calculate time difference
            deltaTime = fl1_sched_dep_time - fl2_flight.schedArrTime

            # Early termination conditions
            if deltaTime < Options.paxLinksBtmLimit:
                break
            if deltaTime > Options.paxLinksTopLimit:
                continue

            # Check airport compatibility
            if fl2_flight.destAirp != fl1_orig_airp:
                continue

            # Check if this is a valid route using the pre-computed set
            if (fl2_flight.origAirp, fl1_orig_airp, fl1_dest_airp) not in valid_routes:
                continue

            # Apply probability check
            if np.random.uniform() > Options.paxLinksProbability:
                continue

            # Create dependency
            scheduledFlights[fl1].dependence = fl2_flight.uniqueID
            break

    return scheduledFlights


def CheckForDependence(fl: Any, executedFlights: List) -> bool:
    """
    Check if the flight connected to the current one has already landed.

    This function uses the original implementation which performs better
    for typical workloads based on our benchmarks.

    Parameters
    ----------
    fl : Any
        Flight to check for dependencies
    executedFlights : List
        List of flights that have already been executed

    Returns
    -------
    bool
        True if the flight has no dependencies or if its dependent flight
        has already been executed, False otherwise
    """
    # If there's no dependency, return True immediately
    if fl.dependence is None:
        return True

    # Linear search
    for depFl in range(len(executedFlights)):
        if executedFlights[depFl].uniqueID == fl.dependence:
            return True

    return False
