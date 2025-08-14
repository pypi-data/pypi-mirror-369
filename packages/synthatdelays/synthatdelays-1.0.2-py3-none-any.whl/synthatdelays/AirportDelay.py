# -*- coding: utf-8 -*-
"""
Synth AT Delays

A library with a minimal model of operations between airports,
designed to synthesise realistic time series of delays and operations

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np
from .data import load_airport_data


def AD_AbsNormal(Airport: int, time: float, params: list, rng):
    """
    Airport delay function, returning the absolute value of numbers drawn from a normal distribution.

    Parameters
    ----------
    Airport : int
        Destination airport of the processed flight.
    time : float
        Time of the landing (in hours since the start of the simulation).
    params : list
        Specific parameters of the function.
        (0) List of affected airports; -1 for all airports.
        (1) Mean of the normal distribution (hours).
        (2) Standard deviation of the normal distribution (hours).
    rng : numpy.random.Generator
        Random number generator to use for generating random values.

    Returns
    -------
    float
        Amount of delay to be applied (hours).
    """

    if type(params) is not list:
        raise ValueError("The parameters must be a list")
    if len(params) != 3:
        raise ValueError("Three parameters are expected, got %d" % len(params))
    if type(params[0]) is not list:
        raise ValueError("The first parameter must be a list of airports")
    if params[2] <= 0.0:
        raise ValueError("The standard deviation must be larger than zero")

    delay = 0.0

    validAirport = False
    if -1 in params[0] or Airport in params[0]:
        validAirport = True

    if not validAirport:
        return delay

    delay = np.abs(rng.normal(params[1], params[2]))

    return delay


def AD_AbsNormalAtHour(Airport: int, time: float, params: list, rng):
    """
    Airport delay function, returning the absolute value of numbers drawn from a normal distribution, applied only in a specific temporal range.

    Parameters
    ----------
    Airport : int
        Destination airport of the processed flight.
    time : float
        Time of the landing (in hours since the start of the simulation).
    params : list
        Specific parameters of the function.
        (0) List of affected airports; -1 for all airports.
        (1) Start hour of the delay (in hours, between 0 and 24).
        (2) Final hour of the delay (in hours, between 0 and 24).
        (3) Probability of generating the delay, between 0 and 1 (dimensionless).
        (4) Mean of the normal distribution (hours).
        (5) Standard deviation of the normal distribution (hours).
    rng : numpy.random.Generator
        Random number generator to use for generating random values.

    Returns
    -------
    float
        Amount of delay to be applied (hours).
    """

    if type(params) is not list:
        raise ValueError("The parameters must be a list")
    if len(params) != 6:
        raise ValueError("Three parameters are expected, got %d" % len(params))
    if type(params[0]) is not list:
        raise ValueError("The first parameter must be a list of airports")
    if params[1] < 0.0 or params[1] > 24.0:
        raise ValueError("The start hour must be between 0 and 24")
    if params[2] < 0.0 or params[2] > 24.0:
        raise ValueError("The final hour must be between 0 and 24")
    if params[3] < 0.0 or params[3] > 1.0:
        raise ValueError("The probability must be between 0 and 1")
    if params[5] <= 0.0:
        raise ValueError("The standard deviation must be larger than zero")

    delay = 0.0

    validAirport = False
    if -1 in params[0] or Airport in params[0]:
        validAirport = True

    if not validAirport:
        return delay

    btmTime = params[1]
    topTime = params[2]

    if np.mod(time, 24.0) > btmTime and np.mod(time, 24.0) < topTime:
        if rng.uniform(0.0, 1.0) < params[3]:
            delay = np.abs(rng.normal(params[4], params[5]))

    return delay


def AD_RealDelays(Airport: int, time: float, params: list, rng):
    """
    Airport delay function, returning random values as observed from operations at different airports. Values are synthetically generated, see: https://doi.org/10.5281/zenodo.15046397

    Parameters
    ----------
    Airport : int
        Destination airport of the processed flight.
    time : float
        Time of the landing (in hours since the start of the simulation).
    params : list
        Specific parameters of the function.
        (0) List of affected airports; -1 for all airports.
        (1) ICAO code of the reference airport. Supported airports include London Heathrow ('EGLL'); Paris Charles de Gaulle ('LFPG'); Amsterdam ('EHAM'); Frankfurt ('EDDF'); and Madrid ('LEMD')
        (2) Amplitude of the delay, where 1 correspond to the original data (dimensionless scaling factor).
    rng : numpy.random.Generator
        Random number generator to use for generating random values.

    Returns
    -------
    float
        Amount of delay to be applied (hours).
    """

    if type(params) is not list:
        raise ValueError("The parameters must be a list")
    if len(params) != 3:
        raise ValueError("Three parameters are expected, got %d" % len(params))
    if type(params[0]) is not list:
        raise ValueError("The first parameter must be a list of airports")

    delay = 0.0

    validAirport = False
    if -1 in params[0] or Airport in params[0]:
        validAirport = True

    if not validAirport:
        return delay

    # Loading of the delay data.
    # Original data can be found at: https://doi.org/10.5281/zenodo.15046397
    try:
        targetData = load_airport_data(params[1])
    except ValueError as e:
        # Re-raise with more context about the function
        raise ValueError(f"Error in AD_RealDelays: {str(e)}")
    except (FileNotFoundError, ImportError) as e:
        # Re-raise with more context about the function
        raise RuntimeError(f"Error loading data in AD_RealDelays: {str(e)}")

    hour = int(np.mod(time, 24.0))
    delay = targetData[rng.integers(100), hour]
    delay *= params[2]

    return delay
