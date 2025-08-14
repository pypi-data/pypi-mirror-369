# -*- coding: utf-8 -*-
"""
Synth AT Delays - Main Simulation Module

This is the core module of the Synth AT Delays library, which provides a minimal
but realistic model of operations between airports. It is designed to synthesize
time series of delays and operations that mimic real-world air traffic patterns.

The module implements a discrete event simulation that models:
- Aircraft movements between airports following predefined routes
- Airport capacity constraints and turnaround times
- En-route and airport-specific delays
- Passenger connections between flights

The simulation takes a set of configuration options and produces detailed results
about flight operations, including departure and arrival times, delays, and aircraft
utilization. These results can be used for further analysis of air traffic patterns
and delay propagation through the network.

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np


import synthatdelays.Classes as Classes
import synthatdelays.AuxFunctions as Aux
import synthatdelays.PriorityQueue as PQ
import synthatdelays.PaxLinking as PaxLinking

CONST_AC_IS_IDLE = 0
CONST_AC_IS_AIRBORNE = 1
CONST_AC_IS_IN_TURNAROUND = 2


def create_flight_copy(flight):
    """
    Create a lightweight copy of a Flight_Class object without using deepcopy.

    Parameters
    ----------
    flight : Flight_Class
        The flight object to copy.

    Returns
    -------
    Flight_Class
        A new Flight_Class object with the same attributes.
    """
    new_flight = Classes.Flight_Class(
        flight.ac,
        flight.schedDepTime,
        flight.schedDuration,
        flight.origAirp,
        flight.destAirp,
    )
    new_flight.realDepTime = flight.realDepTime
    new_flight.realArrTime = flight.realArrTime
    new_flight.dependence = flight.dependence
    # uniqueID is already set in the constructor

    return new_flight


def ExecSimulation(Options):
    """
    Main function of the simulation. Takes as input the options, and yields a set of results
    for subsequent analysis.

    Parameters
    ----------
    Options : Options_Class
        Input options defining the simulation.

    Returns
    -------
    list
        List with all the individual results of the simulation:
        (0) List of executed flights
        (1) List of all airports
        (2) List of all aircraft
    """

    # ------------------------------------------
    # Check if initial options are coherent

    if Options.verbose:
        print("Checking options ...")

    Options._check()

    # ------------------------------------------
    # Initialising internal variables

    if Options.verbose:
        print("Initialising system ...")

    executedFlights = []
    inProgressFlights = []
    scheduledFlights = []

    Airports = []
    for airport_idx in range(Options.numAirports):
        newAP = Classes.Airport_Class()
        newAP.capacity = Options.airportCapacity[airport_idx]
        Airports.append(newAP)

    AirportPriority = []
    for airport_idx in range(Options.numAirports):
        AirportPriority.append([])

    Aircraft = []
    for aircraft_idx in range(Options.numAircraft):
        newAC = Classes.Aircraft_Class()
        newAC.airport = Options.routes[aircraft_idx][0]
        Aircraft.append(newAC)

    # ------------------------------------------
    # Creating aircraft routes

    for aircraft_idx in range(Options.numAircraft):
        lastArrTime = Options.rng.uniform(
            0.01, 24.0
        )  # hours (initial arrival time between 0.01 and 24 hours)
        numStopAirports = len(Options.routes[aircraft_idx])
        lastAirportIndex = 0
        nextAirportIndex = 1
        while (
            lastArrTime < 24 * Options.simTime
        ):  # hours (simulation time in days converted to hours)
            newDepTime = (
                lastArrTime + Options.turnAroundTime + Options.bufferTime
            )  # hours
            while (
                np.mod(newDepTime, 24) < Options.nightDuration
            ):  # check if departure is during night hours
                newDepTime += 1.0  # hours (increment by 1 hour)

            departureAirport = Options.routes[aircraft_idx][lastAirportIndex]
            arrivalAirport = Options.routes[aircraft_idx][nextAirportIndex]
            Flight = Classes.Flight_Class(
                aircraft_idx,
                newDepTime,
                Options.timeBetweenAirports[departureAirport, arrivalAirport],
                departureAirport,
                arrivalAirport,
            )
            scheduledFlights.append(Flight)

            lastArrTime = Flight.schedArrTime
            lastAirportIndex = nextAirportIndex
            nextAirportIndex += 1
            if nextAirportIndex >= numStopAirports:
                nextAirportIndex = 0
            if Options.routes[aircraft_idx][nextAirportIndex] == -1:
                nextAirportIndex = 0

    # ------------------------------------------
    # Sort flights by time of departure, to
    # speed up calculations

    if Options.verbose:
        print("Optimising flights ...")
    scheduledFlights = Aux.OptimiseFlightsOrder(scheduledFlights)

    # ------------------------------------------
    # Creating connecting passengers

    if Options.verbose:
        print("Creating pax links between flights ...")
    scheduledFlights = PaxLinking.LinkPassengers(Options, scheduledFlights)

    # ------------------------------------------
    # Start of the simulation

    if Options.verbose:
        print("Starting simulation ...")

    for timeStep in range(
        60 * 24 * Options.simTime
    ):  # minutes (simulation time in days converted to minutes)
        currentTime = timeStep / 60.0  # hours (convert from minutes to hours)

        if (
            np.mod(timeStep, 60 * 24) == 0 and Options.verbose
        ):  # check if it's the start of a new day (60 min * 24 hours)
            print("\tDay %d of %d" % (timeStep / 60 / 24, Options.simTime))

        for aircraft_idx in range(Options.numAircraft):
            if Aircraft[aircraft_idx].status == CONST_AC_IS_IDLE:
                for flight in scheduledFlights:
                    # Check that flight is the next scheduled flight
                    # of the aircraft aircraft_idx

                    if flight.ac != aircraft_idx:
                        continue
                    if flight.schedDepTime > currentTime:
                        break
                    if flight.origAirp != Aircraft[aircraft_idx].airport:
                        continue

                    # Check if the aircraft has to wait for another
                    # flight; if so, skip to the next aircraft
                    if not PaxLinking.CheckForDependence(flight, executedFlights):
                        break

                    # Add the aircraft to the priority queue of the airport
                    AirportPriority = PQ.AddAircraftToQueue(
                        AirportPriority, flight.origAirp, aircraft_idx
                    )
                    if (
                        Airports[flight.origAirp].lastOp
                        + 1.0 / Airports[flight.origAirp].capacity
                        > currentTime
                    ):  # hours (time between operations = 1/capacity)
                        break

                    if not PQ.CheckPriority(
                        AirportPriority, flight.origAirp, aircraft_idx
                    ):
                        break

                    AirportPriority = PQ.RemoveAircraft(
                        AirportPriority, flight.origAirp, aircraft_idx
                    )

                    inProgressFlights.append(flight)
                    scheduledFlights.remove(flight)
                    flight.realDepTime = currentTime  # hours
                    Aircraft[aircraft_idx].status = CONST_AC_IS_AIRBORNE
                    flightTime = Options.timeBetweenAirports[
                        flight.origAirp, flight.destAirp
                    ]  # hours
                    Aircraft[aircraft_idx].arrivingAt = (
                        currentTime + flightTime
                    )  # hours

                    # Apply enroute and arrival airport delays
                    Aircraft[aircraft_idx].arrivingAt += Aux.ApplyEnRouteDelay(
                        Options, flight, currentTime
                    )  # hours
                    Aircraft[aircraft_idx].arrivingAt += Aux.ApplyAirportDelay(
                        Options, flight, currentTime
                    )  # hours

                    # Ensures that the aircraft cannot
                    # arrive before departing
                    if Aircraft[aircraft_idx].arrivingAt <= currentTime:
                        Aircraft[aircraft_idx].arrivingAt = (
                            currentTime + 1.0 / 60.0
                        )  # hours (add 1 minute)

                    Airports[flight.origAirp].lastOp = currentTime
                    break

            if (
                Aircraft[aircraft_idx].status == CONST_AC_IS_AIRBORNE
                and Aircraft[aircraft_idx].arrivingAt <= currentTime
            ):
                Aircraft[aircraft_idx].status = CONST_AC_IS_IN_TURNAROUND
                Aircraft[aircraft_idx].readyAt = (
                    currentTime + Options.turnAroundTime
                )  # hours
                for flight in inProgressFlights:
                    if flight.ac == aircraft_idx:
                        flight.realArrTime = currentTime  # hours
                        executedFlights.append(flight)
                        inProgressFlights.remove(flight)
                        Aircraft[aircraft_idx].airport = flight.destAirp

                        Aircraft[aircraft_idx].executedFlights.append(
                            create_flight_copy(flight)
                        )
                        Airports[flight.destAirp].executedFlights.append(
                            create_flight_copy(flight)
                        )
                        break

            if (
                Aircraft[aircraft_idx].status == CONST_AC_IS_IN_TURNAROUND
                and Aircraft[aircraft_idx].readyAt <= currentTime
            ):
                Aircraft[aircraft_idx].status = CONST_AC_IS_IDLE

    return (executedFlights, Airports, Aircraft)
