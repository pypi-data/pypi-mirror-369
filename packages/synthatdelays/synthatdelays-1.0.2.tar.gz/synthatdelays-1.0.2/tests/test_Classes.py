import pytest
import numpy as np

import synthatdelays as satd
from synthatdelays.Classes import (
    Flight_Class,
    Aircraft_Class,
    Airport_Class,
    Results_Class,
    Options_Class,
)


def test_Options_empty():
    Options = satd.Options_Class()

    with pytest.raises(ValueError):
        Options._check()


@pytest.mark.parametrize(
    "invalid_value,error_message",
    [
        ("not an integer", "The number of aircraft is not an integer"),
        (0, "The number of aircraft must be positive"),
        (-1, "The number of aircraft must be positive"),
    ],
)
def test_Options_numAircraft(invalid_value, error_message):
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAircraft = invalid_value
    with pytest.raises(ValueError, match=error_message):
        Options._check()


@pytest.mark.parametrize(
    "invalid_value,error_message",
    [
        ("not a list", "Routes are not a list"),
        (
            [[0, 1], [1, 2]],
            "The number of aircraft .* must be equal to the number of routes",
        ),
    ],
)
def test_Options_routes(invalid_value, error_message):
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.routes = invalid_value
    with pytest.raises(ValueError, match=error_message):
        Options._check()


@pytest.mark.parametrize(
    "invalid_value,error_message",
    [
        ("not an integer", "The number of airports is not an integer"),
        (0, "The number of airports must be positive"),
        (-1, "The number of airports must be positive"),
    ],
)
def test_Options_numAirports(invalid_value, error_message):
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAirports = invalid_value
    with pytest.raises(ValueError, match=error_message):
        Options._check()


@pytest.mark.parametrize(
    "invalid_value,error_message",
    [
        ("not an array", "The time between airports is not a Numpy array"),
        (
            np.random.uniform(1.0, 2.0, (4,)),
            "The time between airports is not a 2-d Numpy array",
        ),
        (
            np.random.uniform(1.0, 2.0, (3, 3)),
            "The time between airports has a wrong number of elements",
        ),
        (
            np.random.uniform(-2.0, -1.0, (4, 4)),
            "The time between airports cannot be negative",
        ),
    ],
)
def test_Options_timeBetweenAirports(invalid_value, error_message):
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.timeBetweenAirports = invalid_value
    with pytest.raises(ValueError, match=error_message):
        Options._check()


@pytest.mark.parametrize(
    "invalid_value,error_message",
    [
        ("not an array", "The airport capacity is not a Numpy array"),
        (
            np.random.uniform(1.0, 2.0, (4, 4)),
            "The airport capacity is not a 1-d Numpy array",
        ),
        (
            np.random.uniform(1.0, 2.0, (3,)),
            "The airport capacity has a wrong number of elements",
        ),
    ],
)
def test_Options_airportCapacity(invalid_value, error_message):
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.airportCapacity = invalid_value
    with pytest.raises(ValueError, match=error_message):
        Options._check()


def test_Options_set_seed():
    """Test that set_seed method properly sets the random number generator."""
    # Test with specific seed
    options1 = Options_Class().set_seed(42)
    options2 = Options_Class().set_seed(42)

    # Generate random numbers from both instances
    rand1 = options1.rng.random(10)
    rand2 = options2.rng.random(10)

    # With the same seed, they should generate identical sequences
    np.testing.assert_array_equal(rand1, rand2)

    # Test with different seeds
    options3 = Options_Class().set_seed(123)
    rand3 = options3.rng.random(10)

    # With different seeds, they should generate different sequences
    with pytest.raises(AssertionError):
        np.testing.assert_array_equal(rand1, rand3)

    # Test method chaining
    options4 = Options_Class()
    result = options4.set_seed(42)
    assert result is options4, "set_seed should return self for method chaining"

    # Test with None seed (should still work but we can't test determinism)
    options5 = Options_Class().set_seed(None)
    assert isinstance(options5.rng, np.random.Generator)


@pytest.mark.parametrize(
    "ac,sched_dep,sched_dur,orig,dest,expected_arr,expected_id",
    [
        (1, 10.0, 2.0, 0, 1, 12.0, "1-10.0-12.0-0-1"),
        (2, 15.5, 3.5, 1, 2, 19.0, "2-15.5-19.0-1-2"),
        (0, 0.0, 1.0, 0, 0, 1.0, "0-0.0-1.0-0-0"),
    ],
)
def test_Flight_Class_initialization(
    ac, sched_dep, sched_dur, orig, dest, expected_arr, expected_id
):
    """Test Flight_Class initialization with various parameters."""
    flight = Flight_Class(ac, sched_dep, sched_dur, orig, dest)

    # Test basic attributes
    assert flight.ac == ac
    assert flight.schedDepTime == sched_dep
    assert flight.schedDuration == sched_dur
    assert flight.origAirp == orig
    assert flight.destAirp == dest

    # Test computed attributes
    assert flight.schedArrTime == expected_arr
    assert flight.uniqueID == expected_id

    # Test default values
    assert flight.realDepTime == 0.0
    assert flight.realArrTime == 0.0
    assert flight.dependence is None


@pytest.mark.parametrize(
    "real_dep,real_arr,sched_arr,expected_delay",
    [
        (10.0, 12.0, 12.0, 0.0),  # On time
        (11.0, 13.5, 12.0, 1.5),  # Delayed
        (9.0, 11.0, 12.0, -1.0),  # Early
    ],
)
def test_Flight_Class_delay(real_dep, real_arr, sched_arr, expected_delay):
    """Test the delay property of Flight_Class."""
    flight = Flight_Class(1, 10.0, 2.0, 0, 1)
    flight.realDepTime = real_dep
    flight.realArrTime = real_arr
    flight.schedArrTime = sched_arr

    assert flight.delay == expected_delay


@pytest.mark.parametrize(
    "status,airport,ready_at,arriving_at",
    [
        (0, 0, 0.0, 0.0),  # Default values
        (1, 2, 10.5, 12.5),  # Custom values
        (2, 3, 15.0, 0.0),  # Turnaround status
    ],
)
def test_Aircraft_Class_initialization(status, airport, ready_at, arriving_at):
    """Test Aircraft_Class initialization with various parameters."""
    aircraft = Aircraft_Class(status, airport, ready_at, arriving_at)

    assert aircraft.status == status
    assert aircraft.airport == airport
    assert aircraft.readyAt == ready_at
    assert aircraft.arrivingAt == arriving_at
    assert aircraft.executedFlights == []


def test_Aircraft_Class_executed_flights():
    """Test adding executed flights to an Aircraft_Class instance."""
    aircraft = Aircraft_Class()

    # Create some flights
    flight1 = Flight_Class(0, 10.0, 2.0, 0, 1)
    flight2 = Flight_Class(0, 13.0, 1.5, 1, 2)

    # Add flights to executed flights
    aircraft.executedFlights.append(flight1)
    aircraft.executedFlights.append(flight2)

    assert len(aircraft.executedFlights) == 2
    assert aircraft.executedFlights[0] == flight1
    assert aircraft.executedFlights[1] == flight2


@pytest.mark.parametrize(
    "last_op,capacity",
    [
        (-10.0, 0.0),  # Default values
        (15.5, 30.0),  # Custom values
    ],
)
def test_Airport_Class_initialization(last_op, capacity):
    """Test Airport_Class initialization with various parameters."""
    airport = Airport_Class(last_op, capacity)

    assert airport.lastOp == last_op
    assert airport.capacity == capacity
    assert airport.executedFlights == []


def test_Airport_Class_executed_flights():
    """Test adding executed flights to an Airport_Class instance."""
    airport = Airport_Class()

    # Create some flights
    flight1 = Flight_Class(0, 10.0, 2.0, 0, 1)
    flight2 = Flight_Class(1, 11.0, 1.5, 0, 2)

    # Add flights to executed flights
    airport.executedFlights.append(flight1)
    airport.executedFlights.append(flight2)

    assert len(airport.executedFlights) == 2
    assert airport.executedFlights[0] == flight1
    assert airport.executedFlights[1] == flight2


@pytest.mark.parametrize(
    "avg_arr,avg_dep,num_arr,num_dep,total_arr,total_dep",
    [
        (0, 0, 0.0, 0.0, 0.0, 0.0),  # Default values
        (
            np.zeros((5, 3)),
            np.ones((5, 3)),
            np.zeros((5, 3)),
            np.ones((5, 3)),
            10.5,
            15.2,
        ),  # Custom values
    ],
)
def test_Results_Class_initialization(
    avg_arr, avg_dep, num_arr, num_dep, total_arr, total_dep
):
    """Test Results_Class initialization with various parameters."""
    results = Results_Class(avg_arr, avg_dep, num_arr, num_dep, total_arr, total_dep)

    assert results.avgArrivalDelay is avg_arr
    assert results.avgDepartureDelay is avg_dep
    assert results.numArrivalFlights is num_arr
    assert results.numDepartureFlights is num_dep
    assert results.totalArrivalDelay == total_arr
    assert results.totalDepartureDelay == total_dep
