# -*- coding: utf-8 -*-
"""
Synth AT Delays

A library with a minimal model of operations between airports,
designed to synthesise realistic time series of delays and operations

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Union


@dataclass
class Options_Class:
    """
    Class encoding all the options for running a simulation.

    This class stores all configuration parameters for running a simulation,
    including aircraft and airport counts, timing parameters, delay models,
    and passenger connection settings.

    Attributes
    ----------
    numAircraft : int
        Number of aircraft in the simulation.
    numAirports : int
        Number of airports in the simulation.
    timeBetweenAirports : np.ndarray
        2D array of flight times between airports (hours).
    airportCapacity : np.ndarray
        1D array of airport capacities (operations per hour).
    turnAroundTime : float
        Time required for aircraft turnaround (hours).
    bufferTime : float
        Buffer time added to schedules (hours).
    routes : List[List[int]]
        List of routes for each aircraft, where each route is a list of airport indices.
    enRouteDelay : Optional[Callable]
        Function to calculate en-route delays.
    enRouteDelay_params : Optional[List]
        Parameters for the en-route delay function.
    airportDelay : Optional[Callable]
        Function to calculate airport delays.
    airportDelay_params : Optional[List]
        Parameters for the airport delay function.
    paxLinks : Optional[Callable]
        Function to create passenger connections.
    paxLinksProbability : Optional[float]
        Probability of creating passenger connections [0-1].
    paxLinksBtmLimit : Optional[float]
        Minimum connection time (hours).
    paxLinksTopLimit : Optional[float]
        Maximum connection time (hours).
    nightDuration : float
        Duration of night hours when no flights are scheduled (hours).
    simTime : float
        Total simulation time (days).
    analysisWindow : float
        Time window for analysis (minutes).
    verbose : bool
        Whether to print verbose output.
    rng : np.random.Generator
        Random number generator.
    """

    numAircraft: int = 0  # count
    numAirports: int = 0  # count
    timeBetweenAirports: np.ndarray = field(default=0)  # hours
    airportCapacity: np.ndarray = field(default=0)  # operations per hour
    turnAroundTime: float = 0.0  # hours
    bufferTime: float = 0.0  # hours
    routes: List[List[int]] = field(default_factory=list)

    enRouteDelay: Optional[Union[Callable, List[Callable]]] = None
    enRouteDelay_params: Optional[Union[List, List[List]]] = None

    airportDelay: Optional[Union[Callable, List[Callable]]] = None
    airportDelay_params: Optional[Union[List, List[List]]] = None

    paxLinks: Optional[List[List[int]]] = None
    paxLinksProbability: Optional[float] = None  # probability [0-1]
    paxLinksBtmLimit: Optional[float] = None  # hours
    paxLinksTopLimit: Optional[float] = None  # hours

    nightDuration: float = 0.0  # hours
    simTime: float = 0.0  # days

    analysisWindow: float = 60.0  # minutes

    verbose: bool = False
    rng: np.random.Generator = field(default_factory=np.random.default_rng)

    def set_seed(self, seed=None):
        """Set the random seed for reproducible results.

        Parameters
        ----------
        seed : int, optional
            The random seed to use. If None, a random seed will be used.

        Returns
        -------
        self
            Returns self for method chaining.
        """
        self.rng = np.random.default_rng(seed)
        return self

    def _check(self):
        if type(self.numAircraft) is not int:
            raise ValueError("The number of aircraft is not an integer")
        if self.numAircraft <= 0:
            raise ValueError("The number of aircraft must be positive")

        if type(self.routes) is not list:
            raise ValueError("Routes are not a list")
        if len(self.routes) != self.numAircraft:
            raise ValueError(
                "The number of aircraft (%d) must be equal to the number of routes (%d)"
                % (self.numAircraft, len(self.routes))
            )

        if type(self.numAirports) is not int:
            raise ValueError("The number of airports is not an integer")
        if self.numAirports <= 0:
            raise ValueError("The number of airports must be positive")

        if type(self.timeBetweenAirports) is not np.ndarray:
            raise ValueError("The time between airports is not a Numpy array")
        if self.timeBetweenAirports.ndim != 2:
            raise ValueError(
                "The time between airports is not a 2-d Numpy array, %d dimensions found"
                % self.timeBetweenAirports.ndim
            )
        if np.size(self.timeBetweenAirports) != self.numAirports**2:
            raise ValueError(
                "The time between airports has a wrong number of elements - "
                + " %d found, %d expected"
                % (np.size(self.timeBetweenAirports), self.numAirports**2)
            )
        if np.sum(self.timeBetweenAirports < 0.0) > 0:
            raise ValueError("The time between airports cannot be negative")

        if type(self.airportCapacity) is not np.ndarray:
            raise ValueError("The airport capacity is not a Numpy array")
        if self.airportCapacity.ndim != 1:
            raise ValueError(
                "The airport capacity is not a 1-d Numpy array, %d dimensions found"
                % self.airportCapacity.ndim
            )
        if np.size(self.airportCapacity) != self.numAirports:
            raise ValueError(
                "The airport capacity has a wrong number of elements - "
                + " %d found, %d expected"
                % (np.size(self.airportCapacity), self.numAirports)
            )


@dataclass
class Flight_Class:
    """
    Class encoding information about individual flights.

    This class stores information about individual flights, including scheduled
    and actual times, origin and destination airports, and aircraft assignment.

    Attributes
    ----------
    ac : int
        Aircraft index assigned to this flight.
    schedDepTime : float
        Scheduled departure time (hours).
    schedDuration : float
        Scheduled duration of the flight (hours).
    origAirp : int
        Origin airport index.
    destAirp : int
        Destination airport index.
    realDepTime : float
        Actual departure time (hours).
    realArrTime : float
        Actual arrival time (hours).
    dependence : Optional[object]
        Dependency (e.g., another flight).
    schedArrTime : float
        Scheduled arrival time (computed from departure time and duration).
    uniqueID : str
        Unique identifier for the flight (computed).
    """

    ac: int  # aircraft index
    schedDepTime: float  # hours
    schedDuration: float  # hours
    origAirp: int  # origin airport index
    destAirp: int  # destination airport index
    realDepTime: float = 0.0  # hours
    realArrTime: float = 0.0  # hours
    dependence: Optional[object] = None

    def __post_init__(self):
        """Initialize computed attributes after dataclass initialization."""
        self.schedArrTime = self.schedDepTime + self.schedDuration
        self._uniqueID = "%d-%f-%f-%d-%d" % (
            self.ac,
            self.schedDepTime,
            self.schedArrTime,
            self.origAirp,
            self.destAirp,
        )

    @property
    def uniqueID(self) -> str:
        """Unique identifier for the flight."""
        return f"{self.ac}-{self.schedDepTime}-{self.schedArrTime}-{self.origAirp}-{self.destAirp}"

    @property
    def delay(self) -> float:
        """Returns the flight delay in hours (actual arrival - scheduled arrival)."""
        return self.realArrTime - self.schedArrTime


@dataclass
class Aircraft_Class:
    """
    Class encoding the information about each aircraft.

    This class stores the state and history of an aircraft during simulation,
    including its current status, location, and scheduled operations.

    Attributes
    ----------
    status : int
        Status code of the aircraft (0=idle, 1=airborne, 2=turnaround).
    airport : int
        Current airport index where the aircraft is located.
    readyAt : float
        Time when the aircraft will be ready for the next operation (hours).
    arrivingAt : float
        Time when the aircraft will arrive at its destination (hours).
    executedFlights : List[Flight_Class]
        List of flights executed by this aircraft during the simulation.
    """

    status: int = 0  # status code (0=idle, 1=airborne, 2=turnaround)
    airport: int = 0  # current airport index
    readyAt: float = 0.0  # hours
    arrivingAt: float = 0.0  # hours
    executedFlights: List[Flight_Class] = field(default_factory=list)


@dataclass
class Airport_Class:
    """
    Class encoding information about the executed operations at a given airport.

    This class stores the operational state and history of an airport during simulation,
    including its capacity, last operation time, and all flights that have used it.

    Attributes
    ----------
    lastOp : float
        Time of the last operation at this airport (hours).
        Initialized to -10.0 to ensure the first operation can proceed.
    capacity : float
        Operational capacity of the airport (operations per hour).
    executedFlights : List[Flight_Class]
        List of flights that have used this airport during the simulation.
    """

    lastOp: float = -10.0  # hours
    capacity: float = 0.0  # operations per hour
    executedFlights: List[Flight_Class] = field(default_factory=list)


@dataclass
class Results_Class:
    """
    Class encoding the processed results of a simulation.

    This class stores the results of a simulation, including delay statistics
    and flight counts. Most attributes are initialised as scalar values but
    are populated with numpy arrays during analysis.

    Attributes
    ----------
    avgArrivalDelay : numpy.ndarray
        Average arrival delay per time window and airport (hours).
        Shape: (num_time_windows, num_airports)
    avgDepartureDelay : numpy.ndarray
        Average departure delay per time window and airport (hours).
        Shape: (num_time_windows, num_airports)
    numArrivalFlights : numpy.ndarray
        Number of arrival flights per time window and airport.
        Shape: (num_time_windows, num_airports)
    numDepartureFlights : numpy.ndarray
        Number of departure flights per time window and airport.
        Shape: (num_time_windows, num_airports)
    totalArrivalDelay : float
        Total arrival delay across all flights (hours).
    totalDepartureDelay : float
        Total departure delay across all flights (hours).
    """

    avgArrivalDelay: np.ndarray = 0  # Initialised as scalar, will be set to array
    avgDepartureDelay: np.ndarray = 0  # Initialised as scalar, will be set to array
    numArrivalFlights: np.ndarray = 0.0  # Initialised as scalar, will be set to array
    numDepartureFlights: np.ndarray = 0.0  # Initialised as scalar, will be set to array
    totalArrivalDelay: float = 0.0  # hours
    totalDepartureDelay: float = 0.0  # hours
