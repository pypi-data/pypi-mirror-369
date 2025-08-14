# -*- coding: utf-8 -*-
"""
Synth AT Delays - Auxiliary Functions Module

This module provides utility functions that support the main simulation process
in the Synth AT Delays library. It contains helper functions for flight scheduling,
delay application, aircraft management, and time series analysis.

Key functionalities include:
- Optimizing flight order for efficient processing
- Applying airport-specific delays to flights
- Applying en-route delays to flights
- Creating and managing aircraft clones for simulation scaling
- Time series analysis tools for delay propagation studies

These functions are primarily used internally by the main simulation module
but can also be used directly for custom simulation configurations.

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np

from synthatdelays.Classes import Options_Class, Flight_Class


def OptimiseFlightsOrder(Flights: list) -> list:
    """
    Sort the flights in the input array according to the
    scheduled departure time, to optimise subsequent calculations.

    Parameters
    ----------
    Flights : list
        List of flights to be processed.

    Returns
    -------
    list
        Sorted list of flights.

    Raises
    ------
    ValueError
        If the input is not a list or if the list is empty.
    """

    if not isinstance(Flights, list):
        raise ValueError("The input is not a list")

    numFlights = len(Flights)
    if numFlights == 0:
        raise ValueError("The list of flights is empty")

    # For smaller datasets, use list comprehension which is faster
    if numFlights < 1000:
        departure_times = np.array([flight.schedDepTime for flight in Flights])
        return [Flights[idx] for idx in np.argsort(departure_times)]

    # For larger datasets, use the original implementation which performs better
    Time = np.zeros((numFlights))

    for flight_idx in range(numFlights):
        Time[flight_idx] = Flights[flight_idx].schedDepTime

    sorted_indices = np.argsort(Time)

    newFlights = [Flights[idx] for idx in sorted_indices]

    return newFlights


def ApplyAirportDelay(
    Options: Options_Class, flight: Flight_Class, current_time: float
) -> float:
    """
    Apply the relevant airport delay to a flight, based on the
    information included in the Options of the simulation.

    Parameters
    ----------
    Options : Options_Class
        Class with the options of the current simulation.
    flight : Flight_Class
        Flight to which the delay has to be applied.
    current_time : float
        Current time in the simulation.

    Returns
    -------
    float
        Amount of delay to be applied.
    """

    if Options.airportDelay is None:
        return 0.0

    delay = 0.0

    if type(Options.airportDelay) == list:
        for delay_func_idx in range(len(Options.airportDelay)):
            delay += Options.airportDelay[delay_func_idx](
                flight.destAirp,
                current_time,
                Options.airportDelay_params[delay_func_idx],
                Options.rng,
            )

    else:
        delay = Options.airportDelay(
            flight.destAirp, current_time, Options.airportDelay_params, Options.rng
        )

    return delay


def ApplyEnRouteDelay(
    Options: Options_Class, flight: Flight_Class, current_time: float
) -> float:
    """
    Apply the relevant en-route delay to a flight, based on the
    information included in the Options of the simulation.

    Parameters
    ----------
    Options : Options_Class
        Class with the options of the current simulation.
    flight : Flight_Class
        Flight to which the delay has to be applied.
    current_time : float
        Current time in the simulation.

    Returns
    -------
    float
        Amount of delay to be applied.
    """

    if Options.enRouteDelay is None:
        return 0.0

    delay = 0.0
    flightTime = flight.schedDuration

    if type(Options.enRouteDelay) == list:
        for delay_func_idx in range(len(Options.enRouteDelay)):
            delay += Options.enRouteDelay[delay_func_idx](
                flight.origAirp,
                flight.destAirp,
                flightTime,
                current_time,
                Options.enRouteDelay_params[delay_func_idx],
                Options.rng,
            )

    else:
        delay = Options.enRouteDelay(
            flight.origAirp,
            flight.destAirp,
            flightTime,
            current_time,
            Options.enRouteDelay_params,
            Options.rng,
        )

    return delay


def CloneAircraft(
    Options: Options_Class, routeOffset: int, numNewAC: int
) -> Options_Class:
    """
    Auxiliary function to clone an existing route, and adding a number of aircraft to it.

    Parameters
    ----------
    Options : Options_Class
        Class with the options of the current simulation.
    routeOffset : int
        Offset to the route to be cloned.
    numNewAC : int
        Number of new aircraft to be added.

    Returns
    -------
    Options_Class
        Updated Options_Class.
    """

    if routeOffset < 0:
        raise ValueError("routeOffset cannot be smaller than zero")
    if routeOffset > len(Options.routes):
        raise ValueError("routeOffset cannot be larger than the number of routes")
    if numNewAC <= 0:
        raise ValueError("numNewAC must be larger than zero")

    Options.numAircraft += numNewAC

    route = Options.routes[routeOffset]

    # Use list extension instead of appending in a loop
    Options.routes.extend([route] * numNewAC)

    return Options


def GT(source_series, target_series, max_lag):
    """
    Function to compute the Granger Causality test between time series.

    Parameters
    ----------
    source_series : numpy.array
        Source time series.
    target_series : numpy.array
        Destination time series.
    max_lag : int
        Maximum temporal lag to be tested.

    Returns
    -------
    float
        Best (smallest) p-value for the causality source_series -> target_series.
    list
        List of all p-values as a function of the lag.
    """

    from statsmodels.tsa.tsatools import lagmat2ds
    from statsmodels.regression.linear_model import OLS
    from statsmodels.tools.tools import add_constant

    fullTS = np.array([target_series, source_series]).T

    allPValues = np.zeros((max_lag, 1))

    for lag_idx in range(1, max_lag + 1):
        dta = lagmat2ds(fullTS, lag_idx, trim="both", dropex=1)
        dtajoint = add_constant(dta[:, 1:], prepend=False)

        res2djoint = OLS(dta[:, 0], dtajoint).fit()

        rconstr = np.column_stack(
            (
                np.zeros((lag_idx - 1, lag_idx - 1)),
                np.eye(lag_idx - 1, lag_idx - 1),
                np.zeros((lag_idx - 1, 1)),
            )
        )
        rconstr = np.column_stack(
            (
                np.zeros((lag_idx, lag_idx)),
                np.eye(lag_idx, lag_idx),
                np.zeros((lag_idx, 1)),
            )
        )
        ftres = res2djoint.f_test(rconstr)
        allPValues[lag_idx - 1] = np.squeeze(ftres.pvalue)[()]

    return np.min(allPValues), allPValues
