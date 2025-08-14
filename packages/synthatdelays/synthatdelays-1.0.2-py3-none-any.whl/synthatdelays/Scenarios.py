# -*- coding: utf-8 -*-
"""
Synth AT Delays

A library with a minimal model of operations between airports,
designed to synthesise realistic time series of delays and operations

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np

import synthatdelays as satd
from synthatdelays.Classes import Options_Class


def Scenario_RandomConnectivity(
    numAirports: int, numAircraft: int, bufferTime: float, seed: int = 0
) -> Options_Class:
    """
    Scenario composed of a set of airports, randomly connected by a set of independent flights,
    and with random and homogeneous enroute delays.

    Parameters
    ----------
    numAirports : int
        Number of simulated airports.
    numAircraft : int
        Number of simulated aircraft.
    bufferTime : float
        Buffer time between subsequent operations, in hours.
    seed : int, optional
        Seed for random number generation to use.
        Default: 0.

    Returns
    -------
    Options_Class
        Set of options for executing the scenario.
    """

    if numAirports <= 0:
        raise ValueError("The number of airports must be positive")
    if numAircraft <= 0:
        raise ValueError("The number of aircraft must be positive")
    if bufferTime < 0.0:
        raise ValueError("The buffer time cannot be negative")

    from synthatdelays.EnRouteDelay import ERD_Normal

    Options = satd.Classes.Options_Class()
    Options.set_seed(seed)

    Options.numAircraft = numAircraft
    Options.numAirports = numAirports
    Options.timeBetweenAirports = Options.rng.uniform(
        0.8, 2.2, (numAirports, numAirports)
    )
    Options.airportCapacity = np.ones(Options.numAirports) * 30.0
    Options.turnAroundTime = 0.5
    Options.bufferTime = bufferTime

    Options.routes = []
    for _ in range(numAircraft):
        # Ensure we get Python int values, not numpy integers
        airport1 = int(Options.rng.integers(numAirports))
        airport2 = int(Options.rng.integers(numAirports))
        Options.routes.append([airport1, airport2])

    Options.enRouteDelay = ERD_Normal
    Options.enRouteDelay_params = [[-1], [-1], 0.0, 0.05]

    Options.simTime = 100

    return Options


def Scenario_IndependentOperationsWithTrends(
    activateTrend: bool, seed: int = 0
) -> Options_Class:
    """
    Scenario composed of two groups of two airports. Flights connect airports between
    a same group, but not across groups; hence, no propagations can happen in the
    latter case. Still, when delays are activated according to the hour of the day,
    the temporal organisation (i.e. the presence of trends, or of non-stationarities)
    give rise to spurious causality relations between them.

    Parameters
    ----------
    activateTrend : bool
        If true, delays are added at 12:00 and 14:00, thus generating spurious causalities.
    seed : int, optional
        Seed for random number generation to use.
        Default: 0.

    Returns
    -------
    Options_Class
        Set of options for executing the scenario.
    """

    import synthatdelays as satd
    import synthatdelays.AuxFunctions as Aux
    from synthatdelays.EnRouteDelay import ERD_Normal
    from synthatdelays.AirportDelay import AD_AbsNormalAtHour

    Options = satd.Classes.Options_Class()
    Options.set_seed(seed)
    Options.numAircraft = 2
    Options.numAirports = 4
    Options.timeBetweenAirports = np.ones((Options.numAirports, Options.numAirports))
    Options.airportCapacity = np.ones((Options.numAirports)) * 30.0
    Options.turnAroundTime = 0.2
    Options.bufferTime = 1.0
    Options.routes = [[0, 1], [2, 3]]

    for k in range(0, 2):
        Options = Aux.CloneAircraft(Options, k, 2)

    Options.simTime = 100
    Options.analysisWindow = 60 * 1

    Options.enRouteDelay = []
    Options.enRouteDelay_params = []
    Options.enRouteDelay.append(ERD_Normal)
    Options.enRouteDelay_params.append([[0, 1], [0, 1], 0.0, 0.05])
    Options.enRouteDelay.append(ERD_Normal)
    Options.enRouteDelay_params.append([[2, 3], [2, 3], 0.0, 0.05])

    if activateTrend:
        Options.airportDelay = []
        Options.airportDelay_params = []
        Options.airportDelay.append(AD_AbsNormalAtHour)
        Options.airportDelay_params.append([[0], 11.0, 13.0, 0.5, 0.2, 0.1])
        Options.airportDelay.append(AD_AbsNormalAtHour)
        Options.airportDelay_params.append([[2], 12.0, 14.0, 0.5, 0.2, 0.1])

    return Options
