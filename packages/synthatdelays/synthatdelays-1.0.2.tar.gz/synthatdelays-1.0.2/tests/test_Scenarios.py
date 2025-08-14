import pytest

import synthatdelays as satd


def test_Scenario_RandomConnectivity_invalid_inputs():
    """Test that Scenario_RandomConnectivity raises appropriate errors for invalid inputs."""
    # Test invalid numAirports (line 44)
    with pytest.raises(ValueError, match="The number of airports must be positive"):
        satd.Scenario_RandomConnectivity(0, 5, 0.5)

    with pytest.raises(ValueError, match="The number of airports must be positive"):
        satd.Scenario_RandomConnectivity(-1, 5, 0.5)

    # Test invalid numAircraft (line 46)
    with pytest.raises(ValueError, match="The number of aircraft must be positive"):
        satd.Scenario_RandomConnectivity(3, 0, 0.5)

    with pytest.raises(ValueError, match="The number of aircraft must be positive"):
        satd.Scenario_RandomConnectivity(3, -2, 0.5)

    # Test invalid bufferTime (line 48)
    with pytest.raises(ValueError, match="The buffer time cannot be negative"):
        satd.Scenario_RandomConnectivity(3, 5, -0.1)


@pytest.mark.parametrize("numAirports", [2, 3, 4])
@pytest.mark.parametrize("numAircraft", [5, 10, 15, 20])
def test_Scenario_RandomConnectivity(numAirports, numAircraft):
    """Test the Random Connectivity scenario by design."""

    Options = satd.Scenario_RandomConnectivity(numAirports, numAircraft, 0.5)
    Options.simTime = 2
    satd.ExecSimulation(Options)


def test_Scenario_IndependentOperationsWithTrends():
    """Test the Trends scenario by design."""

    Options = satd.Scenario_IndependentOperationsWithTrends(True)
    Options.simTime = 2
    satd.ExecSimulation(Options)

    Options = satd.Scenario_IndependentOperationsWithTrends(False)
    Options.simTime = 2
    satd.ExecSimulation(Options)
