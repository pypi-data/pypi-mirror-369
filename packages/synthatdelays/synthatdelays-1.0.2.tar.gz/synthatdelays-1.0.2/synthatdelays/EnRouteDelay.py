# -*- coding: utf-8 -*-
"""
Synth AT Delays - En-Route Delay Module

This module provides functions for simulating delays that occur during the en-route
phase of flights between airports. It implements different delay models that can be
applied to flights based on their departure and destination airports.

The module includes functions for:
- Normal distribution delays proportional to flight duration
- Exponential distribution delays simulating large disruptions in the system

Each function validates its input parameters and provides clear error messages
to help users understand and correct any issues with their simulation setup.

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np


def ERD_Normal(depAirport, destAirport, flightTime, time, params, rng):
    """
    Enroute delay function, returning random values from a normal distribution, and proportional to the duration of the flight.

    Parameters
    ----------
    depAirport : int
        Departure airport of the processed flight.
    destAirport : int
        Destination airport of the processed flight.
    flightTime : float
        Duration of the flight, in hours.
    time : float
        Time of the landing (in hours since the start of the simulation).
    params : list
        Specific parameters of the function.
        (0) List of affected departure airports. If -1, all airports are accepted.
        (1) List of affected arrival airports. If -1, all airports are accepted.
        (2) Mean of the normal distribution (dimensionless, as a fraction of flight time).
        (3) Standard deviation of the normal distribution (dimensionless, as a fraction of flight time).
    rng : numpy.random.Generator
        Random number generator to use for generating random values.

    Returns
    -------
    float
        Amount of delay to be applied (hours).
    """
    if type(params) is not list:
        raise ValueError("The parameters must be a list")
    if len(params) != 4:
        raise ValueError("Four parameters are expected, got %d" % len(params))
    if type(params[0]) is not list:
        raise ValueError("The first parameter must be a list of departure airports")
    if type(params[1]) is not list:
        raise ValueError("The second parameter must be a list of arrival airports")
    if params[3] <= 0.0:
        raise ValueError("The standard deviation must be larger than zero")

    if depAirport not in params[0] and -1 not in params[0]:
        return 0.0
    if destAirport not in params[1] and -1 not in params[1]:
        return 0.0

    delay = flightTime * rng.normal(params[2], params[3])
    return delay


def ERD_Disruptions(depAirport, destAirport, flightTime, time, params, rng):
    """
    Enroute delay function, returning random values from an exponential distribution, simulating large disruptions in the system.

    Parameters
    ----------
    depAirport : int
        Departure airport of the processed flight.
    destAirport : int
        Destination airport of the processed flight.
    flightTime : float
        Duration of the flight, in hours.
    time : float
        Time of the landing (in hours since the start of the simulation).
    params : list
        Specific parameters of the function.
        (0) List of affected departure airports. If -1, all airports are accepted.
        (1) List of affected arrival airports. If -1, all airports are accepted.
        (2) Probability of generating the delay, between zero and one (dimensionless).
        (3) Scale parameter of the exponential distribution (hours).
    rng : numpy.random.Generator
        Random number generator to use for generating random values.

    Returns
    -------
    float
        Amount of delay to be applied (hours).
    """
    if type(params) is not list:
        raise ValueError("The parameters must be a list")
    if len(params) != 4:
        raise ValueError("Four parameters are expected, got %d" % len(params))
    if type(params[0]) is not list:
        raise ValueError("The first parameter must be a list of departure airports")
    if type(params[1]) is not list:
        raise ValueError("The second parameter must be a list of arrival airports")
    if params[2] < 0.0 or params[2] > 1.0:
        raise ValueError("The probability must be between 0 and 1, got %f" % params[2])
    if params[3] <= 0.0:
        raise ValueError("The scale parameter must be larger than zero")

    if depAirport not in params[0] and -1 not in params[0]:
        return 0.0
    if destAirport not in params[1] and -1 not in params[1]:
        return 0.0

    delay = 0.0

    if rng.uniform() < params[2]:
        delay += rng.exponential(params[3])

    return delay
