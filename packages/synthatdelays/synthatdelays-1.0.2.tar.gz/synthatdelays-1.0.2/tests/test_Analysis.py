import pytest
import numpy as np

import synthatdelays as satd


@pytest.mark.parametrize("numAirports", [2, 4])
@pytest.mark.parametrize("numAircraft", [5, 10])
@pytest.mark.parametrize("simTime", [2, 4])
def test_Analysis(numAirports, numAircraft, simTime):
    Options = satd.Scenario_RandomConnectivity(numAirports, numAircraft, 0.5)
    Options.simTime = simTime
    (executedFlights, Airports, Aircraft) = satd.ExecSimulation(Options)
    allResults = satd.AnalyseResults((executedFlights, Airports, Aircraft), Options)

    assert np.size(allResults.avgArrivalDelay, 1) == numAirports
    assert np.size(allResults.avgArrivalDelay, 0) == simTime * 24

    assert np.size(allResults.avgDepartureDelay, 1) == numAirports
    assert np.size(allResults.avgDepartureDelay, 0) == simTime * 24

    assert np.size(allResults.numArrivalFlights, 1) == numAirports
    assert np.size(allResults.numArrivalFlights, 0) == simTime * 24

    assert np.size(allResults.numDepartureFlights, 1) == numAirports
    assert np.size(allResults.numDepartureFlights, 0) == simTime * 24

    assert len(Airports) == numAirports
    assert len(Aircraft) == numAircraft
