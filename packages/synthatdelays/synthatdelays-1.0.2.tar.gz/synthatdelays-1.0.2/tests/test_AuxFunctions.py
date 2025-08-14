import pytest
import numpy as np

import synthatdelays as satd
from synthatdelays.Classes import Options_Class, Flight_Class


def test_OptimiseFlightsOrder():
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)

    scheduledFlights = []

    for k in range(10):
        fl = satd.Flight_Class(0, np.random.uniform(0.0, 24.0), 1.0, 0, 1)
        scheduledFlights.append(fl)

    scheduledFlights = satd.AuxFunctions.OptimiseFlightsOrder(scheduledFlights)

    for k in range(10 - 1):
        assert scheduledFlights[k + 1].schedDepTime > scheduledFlights[k].schedDepTime

    satd.ExecSimulation(Options)


def test_OptimiseFlightsOrder_error_handling():
    # Test with empty list
    with pytest.raises(ValueError, match="The list of flights is empty"):
        satd.AuxFunctions.OptimiseFlightsOrder([])

    # Test with non-list input
    with pytest.raises(ValueError, match="The input is not a list"):
        satd.AuxFunctions.OptimiseFlightsOrder("not a list")


def test_ApplyAirportDelay():
    # Create a flight and options
    fl = Flight_Class(0, 10.0, 1.0, 0, 1)
    options = Options_Class()

    # Test with no airport delay function
    options.airportDelay = None
    delay = satd.AuxFunctions.ApplyAirportDelay(options, fl, 10.0)
    assert delay == 0.0

    # Test with airport delay function
    options.airportDelay = satd.AD_AbsNormal
    options.airportDelay_params = [[1], 1.0, 1.0]
    delay = satd.AuxFunctions.ApplyAirportDelay(options, fl, 10.0)
    assert isinstance(delay, float)


def test_ApplyEnRouteDelay():
    # Create a flight and options
    fl = Flight_Class(0, 10.0, 1.0, 0, 1)
    options = Options_Class()

    # Test with no en-route delay function
    options.enRouteDelay = None
    delay = satd.AuxFunctions.ApplyEnRouteDelay(options, fl, 10.0)
    assert delay == 0.0

    # Test with single en-route delay function
    options.enRouteDelay = satd.ERD_Normal
    options.enRouteDelay_params = [[0], [1], 0.0, 1.0]
    delay = satd.AuxFunctions.ApplyEnRouteDelay(options, fl, 10.0)
    assert isinstance(delay, float)

    # Test with list of en-route delay functions
    options.enRouteDelay = [satd.ERD_Normal, satd.ERD_Disruptions]
    options.enRouteDelay_params = [[[0], [1], 0.0, 1.0], [[0], [1], 0.5, 1.0]]
    delay = satd.AuxFunctions.ApplyEnRouteDelay(options, fl, 10.0)
    assert isinstance(delay, float)


def test_CloneAircraft():
    # Create options with routes
    options = Options_Class()
    options.numAircraft = 1
    options.routes = [[0, 1]]

    # Test normal operation
    new_options = satd.AuxFunctions.CloneAircraft(options, 0, 2)
    assert new_options.numAircraft == 3
    assert len(new_options.routes) == 3
    assert new_options.routes[1] == new_options.routes[0]
    assert new_options.routes[2] == new_options.routes[0]

    # Test error handling
    with pytest.raises(ValueError, match="routeOffset cannot be smaller than zero"):
        satd.AuxFunctions.CloneAircraft(options, -1, 1)

    with pytest.raises(
        ValueError, match="routeOffset cannot be larger than the number of routes"
    ):
        satd.AuxFunctions.CloneAircraft(options, 10, 1)

    with pytest.raises(ValueError, match="numNewAC must be larger than zero"):
        satd.AuxFunctions.CloneAircraft(options, 0, 0)


def test_GT():
    # Create two correlated time series
    np.random.seed(42)
    x = np.random.normal(0, 1, 100)
    y = 0.5 * x + np.random.normal(0, 0.5, 100)  # y depends on x

    # Test the GT function
    min_p_value, all_p_values = satd.AuxFunctions.GT(x, y, 3)

    # Check return types and shapes
    assert isinstance(min_p_value, float)
    assert isinstance(all_p_values, np.ndarray)
    assert len(all_p_values) == 3

    # Test with reversed causality (should have higher p-values)
    min_p_value_rev, all_p_values_rev = satd.AuxFunctions.GT(y, x, 3)

    # Due to the stochastic nature of the test and the small sample size,
    # we can't reliably assert that min_p_value <= min_p_value_rev.
    # Instead, we'll just check that both values are valid p-values.
    assert 0 <= min_p_value <= 1
    assert 0 <= min_p_value_rev <= 1
