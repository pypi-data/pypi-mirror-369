import numpy as np

from synthatdelays.Classes import Options_Class


def test_set_seed_method_exists():
    """Test that the set_seed method exists in Options_Class."""
    options = Options_Class()
    assert hasattr(options, "set_seed"), "Options_Class should have a set_seed method"
    assert callable(options.set_seed), "set_seed should be a callable method"


def test_rng_attribute_exists():
    """Test that the rng attribute exists in Options_Class."""
    options = Options_Class()
    assert hasattr(options, "rng"), "Options_Class should have an rng attribute"


def test_set_seed_reproducibility():
    """Test that setting the same seed produces the same random numbers."""
    options1 = Options_Class()
    options1.set_seed(42)

    options2 = Options_Class()
    options2.set_seed(42)

    # Generate random numbers with both instances
    random_numbers1 = [options1.rng.uniform(0, 1) for _ in range(10)]
    random_numbers2 = [options2.rng.uniform(0, 1) for _ in range(10)]

    # They should be identical
    assert random_numbers1 == random_numbers2, (
        "Same seed should produce same random numbers"
    )


def test_different_seeds_different_results():
    """Test that different seeds produce different random numbers."""
    options1 = Options_Class()
    options1.set_seed(42)

    options2 = Options_Class()
    options2.set_seed(43)

    # Generate random numbers with both instances
    random_numbers1 = [options1.rng.uniform(0, 1) for _ in range(10)]
    random_numbers2 = [options2.rng.uniform(0, 1) for _ in range(10)]

    # They should be different
    assert random_numbers1 != random_numbers2, (
        "Different seeds should produce different random numbers"
    )


def test_rng_methods():
    """Test that the rng attribute has the expected methods."""
    options = Options_Class()
    options.set_seed(0)

    # Test various random number generation methods
    assert hasattr(options.rng, "normal"), "RNG should have normal method"
    assert hasattr(options.rng, "uniform"), "RNG should have uniform method"
    assert hasattr(options.rng, "exponential"), "RNG should have exponential method"
    assert hasattr(options.rng, "integers"), "RNG should have integers method"

    # Test that the methods work as expected
    assert isinstance(options.rng.normal(0, 1), float)
    assert 0 <= options.rng.uniform(0, 1) <= 1
    assert options.rng.exponential(1) >= 0
    assert isinstance(options.rng.integers(0, 10), np.integer)


def test_default_rng_initialization():
    """Test that the rng is initialized by default."""
    options = Options_Class()

    # Should have an rng attribute even without calling set_seed
    assert hasattr(options, "rng"), "Options_Class should initialize rng by default"

    # Should be able to generate random numbers
    assert isinstance(options.rng.normal(0, 1), float)
