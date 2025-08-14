import pytest
import numpy as np

import synthatdelays as satd
from synthatdelays import EnRouteDelay


def test_ERD_Normal():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test with invalid airport parameters
    assert satd.ERD_Normal(0, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng) == 0.0
    assert satd.ERD_Normal(1, 0, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng) == 0.0

    # Test with valid parameters
    delay = satd.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    # Test with -1 in airport lists (all airports)
    delay = satd.ERD_Normal(0, 1, 1.0, 0.0, [[-1], [1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    delay = satd.ERD_Normal(1, 0, 1.0, 0.0, [[1], [-1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    # Test proportionality to flight time
    # Create new RNGs with the same seed for each test to ensure reproducibility
    rng1 = np.random.default_rng(42)
    delay1 = satd.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.5, 0.1], rng1)

    rng2 = np.random.default_rng(42)
    delay2 = satd.ERD_Normal(1, 1, 2.0, 0.0, [[1], [1], 0.5, 0.1], rng2)

    assert abs(delay2 - 2 * delay1) < 1e-10  # Should be exactly proportional


def test_ERD_Normal_errors():
    """Test error handling in ERD_Normal."""
    rng = np.random.default_rng(42)

    # Test invalid params type
    with pytest.raises(ValueError, match="The parameters must be a list"):
        EnRouteDelay.ERD_Normal(1, 1, 1.0, 0.0, "not a list", rng)

    # Test incorrect number of parameters
    with pytest.raises(ValueError, match="Four parameters are expected"):
        EnRouteDelay.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.0], rng)

    # Test invalid first parameter type
    with pytest.raises(
        ValueError, match="The first parameter must be a list of departure airports"
    ):
        EnRouteDelay.ERD_Normal(1, 1, 1.0, 0.0, ["not a list", [1], 0.0, 1.0], rng)

    # Test invalid second parameter type
    with pytest.raises(
        ValueError, match="The second parameter must be a list of arrival airports"
    ):
        EnRouteDelay.ERD_Normal(1, 1, 1.0, 0.0, [[1], "not a list", 0.0, 1.0], rng)

    # Test invalid standard deviation
    with pytest.raises(
        ValueError, match="The standard deviation must be larger than zero"
    ):
        EnRouteDelay.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.0, 0.0], rng)


def test_ERD_Disruptions():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test with invalid airport parameters
    assert satd.ERD_Disruptions(0, 1, 1.0, 0.0, [[1], [1], 0.5, 1.0], rng) == 0.0
    assert satd.ERD_Disruptions(1, 0, 1.0, 0.0, [[1], [1], 0.5, 1.0], rng) == 0.0

    # Test with valid parameters but zero probability
    delay = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng)
    assert delay == 0.0

    # Test with valid parameters and 100% probability
    delay = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 1.0, 1.0], rng)
    assert delay > 0.0

    # Test with -1 in airport lists (all airports)
    delay = satd.ERD_Disruptions(0, 1, 1.0, 0.0, [[-1], [1], 0.5, 1.0], rng)
    assert isinstance(delay, float)

    delay = satd.ERD_Disruptions(1, 0, 1.0, 0.0, [[1], [-1], 0.5, 1.0], rng)
    assert isinstance(delay, float)

    # Test that flight time doesn't affect the delay (unlike ERD_Normal)
    # Create new RNGs with the same seed for each test to ensure reproducibility
    rng1 = np.random.default_rng(42)
    delay1 = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 1.0, 2.0], rng1)

    rng2 = np.random.default_rng(42)
    delay2 = satd.ERD_Disruptions(1, 1, 2.0, 0.0, [[1], [1], 1.0, 2.0], rng2)

    assert delay1 == delay2  # Should be the same regardless of flight time


def test_ERD_Disruptions_errors():
    """Test error handling in ERD_Disruptions."""
    rng = np.random.default_rng(42)

    # Test invalid params type
    with pytest.raises(ValueError, match="The parameters must be a list"):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, "not a list", rng)

    # Test incorrect number of parameters
    with pytest.raises(ValueError, match="Four parameters are expected"):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 0.5], rng)

    # Test invalid first parameter type
    with pytest.raises(
        ValueError, match="The first parameter must be a list of departure airports"
    ):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, ["not a list", [1], 0.5, 1.0], rng)

    # Test invalid second parameter type
    with pytest.raises(
        ValueError, match="The second parameter must be a list of arrival airports"
    ):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], "not a list", 0.5, 1.0], rng)

    # Test invalid probability range (negative)
    with pytest.raises(ValueError, match="The probability must be between 0 and 1"):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], -0.1, 1.0], rng)

    # Test invalid probability range (greater than 1)
    with pytest.raises(ValueError, match="The probability must be between 0 and 1"):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 1.1, 1.0], rng)

    # Test invalid scale parameter
    with pytest.raises(
        ValueError, match="The scale parameter must be larger than zero"
    ):
        EnRouteDelay.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 0.5, 0.0], rng)
