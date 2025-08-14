import pytest
import numpy as np
from unittest.mock import patch

import synthatdelays as satd


def test_AbsNormal():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(358)

    # Test with invalid parameters
    with pytest.raises(ValueError, match="The parameters must be a list"):
        satd.AD_AbsNormal(0, 0.0, "not a list", rng)

    with pytest.raises(ValueError, match="Three parameters are expected"):
        satd.AD_AbsNormal(0, 0.0, [], rng)

    with pytest.raises(
        ValueError, match="The first parameter must be a list of airports"
    ):
        satd.AD_AbsNormal(0, 0.0, [0, 0.0, 1.0], rng)

    with pytest.raises(
        ValueError, match="The standard deviation must be larger than zero"
    ):
        satd.AD_AbsNormal(0, 0.0, [[0], 1.0, 0.0], rng)

    with pytest.raises(
        ValueError, match="The standard deviation must be larger than zero"
    ):
        satd.AD_AbsNormal(0, 0.0, [[0], 1.0, -1.0], rng)

    # Test with valid parameters
    assert satd.AD_AbsNormal(0, 12.0, [[0], 1.0, 1.0], rng) > 0.0

    # Test with airport not in list
    assert satd.AD_AbsNormal(1, 12.0, [[0], 1.0, 1.0], rng) == 0.0

    # Test with -1 in airport list (all airports)
    assert satd.AD_AbsNormal(1, 12.0, [[-1], 1.0, 1.0], rng) > 0.0

    # Test that the result is always positive (absolute value)
    for _ in range(10):
        delay = satd.AD_AbsNormal(0, 12.0, [[0], -10.0, 1.0], rng)  # Negative mean
        assert delay >= 0.0


def test_AbsNormalAtHour():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(259)

    # Test with invalid parameters
    with pytest.raises(ValueError, match="The parameters must be a list"):
        satd.AD_AbsNormalAtHour(0, 0.0, "not a list", rng)

    with pytest.raises(ValueError, match="Three parameters are expected"):
        satd.AD_AbsNormalAtHour(0, 0.0, [], rng)

    with pytest.raises(
        ValueError, match="The first parameter must be a list of airports"
    ):
        satd.AD_AbsNormalAtHour(0, 0.0, [0, 12, 14, 1.0, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The start hour must be between 0 and 24"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], -1, 14, 1.0, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The start hour must be between 0 and 24"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 25, 14, 1.0, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The final hour must be between 0 and 24"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, -1, 1.0, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The final hour must be between 0 and 24"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, 25, 1.0, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The probability must be between 0 and 1"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, 14, -0.1, 1.0, 1.0], rng)

    with pytest.raises(ValueError, match="The probability must be between 0 and 1"):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, 14, 1.1, 1.0, 1.0], rng)

    with pytest.raises(
        ValueError, match="The standard deviation must be larger than zero"
    ):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, 14, 1.0, 1.0, 0.0], rng)

    with pytest.raises(
        ValueError, match="The standard deviation must be larger than zero"
    ):
        satd.AD_AbsNormalAtHour(0, 0.0, [[0], 12, 14, 1.0, 1.0, -1.0], rng)

    # Test with valid parameters
    assert satd.AD_AbsNormalAtHour(0, 13.0, [[0], 12, 14, 1.0, 1.0, 1.0], rng) > 0.0

    # Test with time outside the specified range
    assert satd.AD_AbsNormalAtHour(0, 11.0, [[0], 12, 14, 1.0, 1.0, 1.0], rng) == 0.0

    # Test with zero probability
    assert satd.AD_AbsNormalAtHour(0, 13.0, [[0], 12, 14, 0.0, 1.0, 1.0], rng) == 0.0

    # Test with airport not in list
    assert satd.AD_AbsNormalAtHour(1, 13.0, [[0], 12, 14, 1.0, 1.0, 1.0], rng) == 0.0

    # Test with -1 in airport list (all airports)
    assert satd.AD_AbsNormalAtHour(1, 13.0, [[-1], 12, 14, 1.0, 1.0, 1.0], rng) > 0.0

    # Test with time wrapping around 24 hours
    delay = satd.AD_AbsNormalAtHour(
        0, 25.0, [[0], 0, 2, 1.0, 1.0, 1.0], rng
    )  # 25 % 24 = 1
    assert delay > 0.0


@pytest.mark.parametrize("airport", ["EGLL", "LFPG", "EHAM", "EDDF", "LEMD"])
def test_real_delays(airport):
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test parameter validation
    with pytest.raises(ValueError, match="The parameters must be a list"):
        satd.AD_RealDelays(0, 0.0, "not a list", rng)

    with pytest.raises(ValueError, match="Three parameters are expected"):
        satd.AD_RealDelays(0, 0.0, [], rng)

    with pytest.raises(ValueError, match="Three parameters are expected"):
        satd.AD_RealDelays(0, 0.0, [[0], airport], rng)

    with pytest.raises(
        ValueError, match="The first parameter must be a list of airports"
    ):
        satd.AD_RealDelays(0, 0.0, [0, airport, 1.0], rng)

    # Test normal operation
    assert satd.AD_RealDelays(0, 12.0, [[0], airport, 1.0], rng) > 0.0
    assert satd.AD_RealDelays(99, 12.0, [[-1], airport, 1.0], rng) > 0.0
    assert satd.AD_RealDelays(1, 12.0, [[0], airport, 1.0], rng) == 0.0

    # Test with different amplitudes
    # Create a new RNG with the same seed for each test to ensure reproducibility
    rng1 = np.random.default_rng(42)
    delay1 = satd.AD_RealDelays(0, 12.0, [[0], airport, 1.0], rng1)

    rng2 = np.random.default_rng(42)
    delay2 = satd.AD_RealDelays(0, 12.0, [[0], airport, 2.0], rng2)

    # Use a more reasonable tolerance for floating point comparisons
    assert abs(delay2 - 2 * delay1) < 1e-6  # Should be approximately proportional

    # Test with different hours
    for hour in range(0, 24):
        delay = satd.AD_RealDelays(0, float(hour), [[0], airport, 1.0], rng)
        assert isinstance(delay, float)


def test_real_delays_unsupported_airport():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test with unsupported airport code
    with pytest.raises(ValueError, match="Unsupported airport code"):
        satd.AD_RealDelays(0, 12.0, [[0], "INVALID", 1.0], rng)

    with pytest.raises(ValueError, match="Unsupported airport code"):
        satd.AD_RealDelays(0, 12.0, [[-1], "XXXX", 1.0], rng)

    # Test with error message from AD_RealDelays
    with pytest.raises(
        ValueError, match="Error in AD_RealDelays: Unsupported airport code"
    ):
        satd.AD_RealDelays(0, 12.0, [[0], "ABCD", 1.0], rng)


@patch("synthatdelays.AirportDelay.load_airport_data")
def test_real_delays_file_not_found_error(mock_load_airport_data):
    """Test that FileNotFoundError in load_airport_data is properly handled."""
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Mock load_airport_data to raise FileNotFoundError
    mock_load_airport_data.side_effect = FileNotFoundError("Test file not found")

    # Test that the error is properly caught and re-raised as RuntimeError
    with pytest.raises(
        RuntimeError, match="Error loading data in AD_RealDelays: Test file not found"
    ):
        satd.AD_RealDelays(0, 12.0, [[0], "EGLL", 1.0], rng)


@patch("synthatdelays.AirportDelay.load_airport_data")
def test_real_delays_import_error(mock_load_airport_data):
    """Test that ImportError in load_airport_data is properly handled."""
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Mock load_airport_data to raise ImportError
    mock_load_airport_data.side_effect = ImportError("Test import error")

    # Test that the error is properly caught and re-raised as RuntimeError
    with pytest.raises(
        RuntimeError, match="Error loading data in AD_RealDelays: Test import error"
    ):
        satd.AD_RealDelays(0, 12.0, [[0], "EGLL", 1.0], rng)
