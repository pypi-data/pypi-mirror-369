# -*- coding: utf-8 -*-
"""
Synth AT Delays

A library with a minimal model of operations between airports,
designed to synthesise realistic time series of delays and operations

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np

import synthatdelays.Classes as Classes


def AnalyseResults(
    inputData: list, Options: Classes.Options_Class
) -> Classes.Results_Class:
    """
    Function to compute the results of a simulation.

    Parameters
    ----------
    inputData : list of results
        List with all the individual results of the simulation, as yielded by ExecSimulation:
        (0) List of executed flights
        (1) List of all airports
        (2) List of all aircraft
    Options : Options_Class
        Object with the options of the simulation.

    Returns
    -------
    Results_Class
        Class with individual processed results. See the definition of the class for details.
    """

    (executedFlights, Airports, Aircraft) = inputData

    numAirports = Options.numAirports
    allResults = Classes.Results_Class()

    numWindows = int(24 * Options.simTime * 60.0 / Options.analysisWindow)
    avgArrivalDelay = np.zeros((numWindows, numAirports))
    avgDepartureDelay = np.zeros((numWindows, numAirports))
    numArrivalFlights = np.zeros((numWindows, numAirports))
    numDepartureFlights = np.zeros((numWindows, numAirports))
    totalArrivalDelay = 0.0
    totalDepartureDelay = 0.0

    for fl in executedFlights:
        arrDelay = (
            fl.realArrTime
            - fl.schedArrTime
            + np.random.uniform(-1.0 / 60.0, 1.0 / 60.0) / 2.0
        )
        depDelay = (
            fl.realDepTime
            - fl.schedDepTime
            + np.random.uniform(-1.0 / 60.0, 1.0 / 60.0) / 2.0
        )

        off = int(fl.realArrTime * 60.0 / Options.analysisWindow)
        avgArrivalDelay[off, fl.destAirp] += arrDelay
        numArrivalFlights[off, fl.destAirp] += 1.0
        totalArrivalDelay += arrDelay

        off = int(fl.realDepTime * 60.0 / Options.analysisWindow)
        avgDepartureDelay[off, fl.origAirp] += depDelay
        numDepartureFlights[off, fl.origAirp] += 1.0
        totalDepartureDelay += depDelay

    for k in range(numWindows):
        for l in range(numAirports):
            if numArrivalFlights[k, l] > 0:
                avgArrivalDelay[k, l] /= numArrivalFlights[k, l]
            if numDepartureFlights[k, l] > 0:
                avgDepartureDelay[k, l] /= numDepartureFlights[k, l]

    allResults.avgArrivalDelay = avgArrivalDelay
    allResults.avgDepartureDelay = avgDepartureDelay
    allResults.numArrivalFlights = numArrivalFlights
    allResults.numDepartureFlights = numDepartureFlights
    allResults.totalArrivalDelay = totalArrivalDelay
    allResults.totalDepartureDelay = totalDepartureDelay

    return allResults
