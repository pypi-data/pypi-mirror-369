import pytest
import numpy as np
from unittest.mock import patch

import synthatdelays as satd
from synthatdelays.SynthATDelays import create_flight_copy, ExecSimulation
from synthatdelays.Classes import Flight_Class


def test_create_flight_copy():
    """Test the create_flight_copy function."""
    # Create a flight
    flight = Flight_Class(1, 10.0, 2.0, 0, 1)
    flight.realDepTime = 10.5
    flight.realArrTime = 12.5
    flight.dependence = "test-dependency"

    # Create a copy
    copy = create_flight_copy(flight)

    # Verify the copy has the same attributes
    assert copy.ac == flight.ac
    assert copy.schedDepTime == flight.schedDepTime
    assert copy.schedDuration == flight.schedDuration
    assert copy.origAirp == flight.origAirp
    assert copy.destAirp == flight.destAirp
    assert copy.realDepTime == flight.realDepTime
    assert copy.realArrTime == flight.realArrTime
    assert copy.dependence == flight.dependence
    assert copy.uniqueID == flight.uniqueID


def test_ExecSimulation_verbose():
    """Test ExecSimulation with verbose output enabled."""
    # Create a simple scenario
    Options = satd.Scenario_RandomConnectivity(2, 2, 0.5)
    Options.simTime = 1  # Must be an integer for range() function
    Options.verbose = True

    # Run simulation with verbose=True to cover print statements
    with patch("builtins.print") as mock_print:
        ExecSimulation(Options)

        # Verify that print was called for verbose output lines
        mock_print.assert_any_call("Checking options ...")
        mock_print.assert_any_call("Initialising system ...")
        mock_print.assert_any_call("Optimising flights ...")
        mock_print.assert_any_call("Creating pax links between flights ...")
        mock_print.assert_any_call("Starting simulation ...")
        mock_print.assert_any_call("\tDay 0 of 1")


def test_ExecSimulation_night_hours():
    """Test ExecSimulation with night hours to cover line 138."""
    # Create a scenario with night hours
    Options = satd.Scenario_RandomConnectivity(2, 2, 0.5)
    Options.simTime = 1  # Must be an integer for range() function
    Options.nightDuration = 6.0  # 6 hours of night time

    # Run simulation
    result = ExecSimulation(Options)

    # Verify we got results
    assert len(result) == 3
    executedFlights, Airports, Aircraft = result
    assert isinstance(executedFlights, list)
    assert isinstance(Airports, list)
    assert isinstance(Aircraft, list)


def test_ExecSimulation_route_with_negative_one():
    """Test ExecSimulation with a route containing -1 to cover line 157."""
    # Create a scenario with a route containing -1
    Options = satd.Scenario_RandomConnectivity(3, 1, 0.5)
    Options.simTime = 1  # Must be an integer for range() function
    Options.routes = [[0, 1, -1, 2]]  # Route with -1 to reset to first airport

    # Run simulation
    result = ExecSimulation(Options)

    # Verify we got results
    assert len(result) == 3
    executedFlights, Airports, Aircraft = result
    assert isinstance(executedFlights, list)
    assert isinstance(Airports, list)
    assert isinstance(Aircraft, list)


def test_ExecSimulation_flight_origAirp_mismatch():
    """Test ExecSimulation with flight origin airport mismatch to cover line 201."""
    # Create a basic scenario
    Options = satd.Scenario_RandomConnectivity(3, 1, 0.5)
    Options.simTime = 1  # Must be an integer for range() function

    # Modify the routes to ensure we'll hit the condition on line 201
    # The aircraft starts at airport 0, but we'll create a flight from airport 1
    Options.routes = [[0, 1]]

    # Create a custom flight with mismatched origin airport
    with patch("synthatdelays.PaxLinking.LinkPassengers") as mock_link:
        # Return a custom flight list with mismatched origin airport
        def custom_link(opts, flights):
            # Add a flight with mismatched origin airport
            flight = Flight_Class(
                0, 0.1, 1.0, 1, 2
            )  # Aircraft is at 0, flight starts at 1
            return [flight]

        mock_link.side_effect = custom_link

        # Run simulation
        result = ExecSimulation(Options)

        # Verify we got results
        assert len(result) == 3
        executedFlights, Airports, Aircraft = result
        assert isinstance(executedFlights, list)
        assert isinstance(Airports, list)
        assert isinstance(Aircraft, list)


def test_ExecSimulation_flight_dependence():
    """Test ExecSimulation with flight dependence to cover line 206."""
    # Create a basic scenario
    Options = satd.Scenario_RandomConnectivity(2, 2, 0.5)
    Options.simTime = 1  # Must be an integer for range() function

    # Mock PaxLinking.CheckForDependence to return False for the first call, then True
    call_count = [0]

    def mock_check_dependence(flight, executed_flights):
        call_count[0] += 1
        # Return False for the first call to trigger the break on line 206
        return call_count[0] > 1

    with patch(
        "synthatdelays.PaxLinking.CheckForDependence", side_effect=mock_check_dependence
    ):
        # Run simulation
        result = ExecSimulation(Options)

        # Verify we got results
        assert len(result) == 3
        executedFlights, Airports, Aircraft = result
        assert isinstance(executedFlights, list)
        assert isinstance(Airports, list)
        assert isinstance(Aircraft, list)


def test_ExecSimulation_arriving_time_correction():
    """Test ExecSimulation with arriving time correction to cover line 250."""
    # Create a basic scenario
    Options = satd.Scenario_RandomConnectivity(2, 1, 0.5)
    Options.simTime = 1  # Must be an integer for range() function

    # Mock ApplyEnRouteDelay and ApplyAirportDelay to return negative values
    # This will trigger the condition on line 250
    with (
        patch("synthatdelays.AuxFunctions.ApplyEnRouteDelay", return_value=-1.0),
        patch("synthatdelays.AuxFunctions.ApplyAirportDelay", return_value=-1.0),
    ):
        # Run simulation
        result = ExecSimulation(Options)

        # Verify we got results
        assert len(result) == 3
        executedFlights, Airports, Aircraft = result
        assert isinstance(executedFlights, list)
        assert isinstance(Airports, list)
        assert isinstance(Aircraft, list)


def test_ExecSimulation_aircraft_states():
    """Test ExecSimulation with different aircraft states to cover lines 192->257 and 265->280."""
    # Create a basic scenario with more simulation time to ensure flights are executed
    Options = satd.Scenario_RandomConnectivity(2, 1, 0.5)
    Options.simTime = 5  # Increase simulation time to ensure flights are executed

    # Modify the routes to ensure flights are executed
    Options.routes = [[0, 1]]

    # Set small values for flight times to ensure flights are completed
    Options.timeBetweenAirports = np.ones((2, 2)) * 0.5  # Short flight times
    Options.turnAroundTime = 0.1  # Quick turnaround
    Options.bufferTime = 0.1  # Small buffer

    # Run simulation
    result = ExecSimulation(Options)

    # Verify we got results
    assert len(result) == 3
    executedFlights, Airports, Aircraft = result

    # Check that we have executed flights and aircraft
    assert len(Aircraft) == 1

    # Verify that the aircraft went through different states
    # At least one flight should have been executed
    assert len(Aircraft[0].executedFlights) > 0
