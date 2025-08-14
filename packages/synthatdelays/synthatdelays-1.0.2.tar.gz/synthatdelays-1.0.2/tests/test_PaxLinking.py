import pytest
from unittest.mock import patch

import synthatdelays as satd


def test_LinkPassengers_none():
    """Test LinkPassengers when Options.paxLinks is None (line 36)."""
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = None  # Set paxLinks to None

    scheduledFlights = []
    fl1 = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    scheduledFlights.append(fl1)

    fl2 = satd.Flight_Class(0, 14.0, 1.0, 1, 2)
    scheduledFlights.append(fl2)

    # Should return scheduledFlights unchanged when paxLinks is None
    result = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    assert result is scheduledFlights
    assert result[1].dependence is None


def test_LinkPassengers():
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 0.0
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 1.0

    scheduledFlights = []

    fl = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    fl.schedArrTime = fl.schedDepTime + fl.schedDuration
    scheduledFlights.append(fl)

    fl = satd.Flight_Class(0, 14.0, 1.0, 1, 2)
    scheduledFlights.append(fl)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    assert scheduledFlights[1].dependence is not None

    fl = satd.Flight_Class(0, 17.0, 1.0, 1, 2)
    scheduledFlights[1] = fl

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    assert scheduledFlights[1].dependence is None


def test_LinkPassengers_early_termination():
    """Test early termination when deltaTime < paxLinksBtmLimit (line 51->44)."""
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 1.0  # Set minimum connection time
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 1.0

    scheduledFlights = []

    # First flight arrives at 13.0
    fl1 = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    scheduledFlights.append(fl1)

    # Second flight departs at 13.5 (deltaTime = 0.5, which is < paxLinksBtmLimit)
    fl2 = satd.Flight_Class(0, 13.5, 1.0, 1, 2)
    scheduledFlights.append(fl2)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    # Should not create a dependency due to early termination
    assert scheduledFlights[1].dependence is None


def test_LinkPassengers_airport_compatibility():
    """Test airport compatibility check (line 66)."""
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 0.0
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 1.0

    scheduledFlights = []

    # First flight arrives at airport 2
    fl1 = satd.Flight_Class(0, 12.0, 1.0, 0, 2)
    scheduledFlights.append(fl1)

    # Second flight departs from airport 1 (not matching fl1's destination)
    fl2 = satd.Flight_Class(0, 14.0, 1.0, 1, 2)
    scheduledFlights.append(fl2)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    # Should not create a dependency due to airport mismatch
    assert scheduledFlights[1].dependence is None


def test_LinkPassengers_valid_route():
    """Test valid route check (line 70)."""
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    # Only route [0, 1, 2] is valid
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 0.0
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 1.0

    scheduledFlights = []

    # First flight from 0 to 1
    fl1 = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    scheduledFlights.append(fl1)

    # Second flight from 1 to 3 (not a valid route as per paxLinks)
    fl2 = satd.Flight_Class(0, 14.0, 1.0, 1, 3)
    scheduledFlights.append(fl2)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    # Should not create a dependency due to invalid route
    assert scheduledFlights[1].dependence is None


@patch("numpy.random.uniform")
def test_LinkPassengers_probability(mock_uniform):
    """Test probability check (line 74)."""
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 0.0
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 0.3  # 30% probability

    # Mock uniform to return a value higher than probability
    mock_uniform.return_value = 0.5  # > 0.3, so should skip

    scheduledFlights = []

    # First flight from 0 to 1
    fl1 = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    scheduledFlights.append(fl1)

    # Second flight from 1 to 2 (valid route)
    fl2 = satd.Flight_Class(0, 14.0, 1.0, 1, 2)
    scheduledFlights.append(fl2)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    # Should not create a dependency due to probability check
    assert scheduledFlights[1].dependence is None

    # Now test with a value lower than probability
    mock_uniform.return_value = 0.2  # < 0.3, so should create dependency
    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    # Should create a dependency now
    assert scheduledFlights[1].dependence is not None


def test_CheckForDependence():
    """Test CheckForDependence function with various scenarios."""
    # Test with no dependency
    targetFlight = satd.Flight_Class(0, 12.0, 1.5, 0, 1)
    targetFlight.dependence = None
    assert satd.PaxLinking.CheckForDependence(targetFlight, []) == True

    # Test with dependency but empty executed flights
    depFlight = satd.Flight_Class(1, 12.0, 1.5, 1, 0)
    targetFlight.dependence = depFlight.uniqueID
    assert satd.PaxLinking.CheckForDependence(targetFlight, []) == False

    # Test with dependency and matching executed flight
    depFlight.realArrTime = 11.5
    assert satd.PaxLinking.CheckForDependence(targetFlight, [depFlight]) == True

    # Test with dependency and multiple executed flights (to cover lines 109->108)
    # Create several flights that don't match the dependency
    otherFlights = []
    for i in range(3):
        flight = satd.Flight_Class(i + 2, 10.0, 1.0, i, i + 1)
        otherFlights.append(flight)

    # Add the dependent flight at the end
    executedFlights = otherFlights + [depFlight]

    # Check that it finds the dependency even when it's not the first flight
    assert satd.PaxLinking.CheckForDependence(targetFlight, executedFlights) == True

    # Test with dependency but no matching flight in executed flights
    nonMatchingFlights = otherFlights.copy()  # Only contains flights that don't match
    assert satd.PaxLinking.CheckForDependence(targetFlight, nonMatchingFlights) == False
