import pytest
from synthatdelays import PriorityQueue as PQ


def test_add_aircraft_to_queue_normal():
    """Test normal operation of AddAircraftToQueue."""
    airport_priority = [[], [], []]
    result = PQ.AddAircraftToQueue(airport_priority, 1, 5)
    assert result[1] == [5]

    # Add another aircraft
    result = PQ.AddAircraftToQueue(result, 1, 7)
    assert result[1] == [5, 7]

    # Adding same aircraft again should not duplicate
    result = PQ.AddAircraftToQueue(result, 1, 5)
    assert result[1] == [5, 7]


def test_add_aircraft_to_queue_errors():
    """Test error handling in AddAircraftToQueue."""
    airport_priority = [[], [], []]

    # Test invalid AirportPriority type
    with pytest.raises(TypeError, match="AirportPriority must be a list"):
        PQ.AddAircraftToQueue("not a list", 1, 5)

    # Test invalid airport_index type
    with pytest.raises(TypeError, match="airport_index must be an integer"):
        PQ.AddAircraftToQueue(airport_priority, "not an int", 5)

    # Test invalid airport_index range
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.AddAircraftToQueue(airport_priority, 3, 5)

    # Test negative airport_index
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.AddAircraftToQueue(airport_priority, -1, 5)

    # Test invalid aircraft_index type
    with pytest.raises(TypeError, match="aircraft_index must be an integer"):
        PQ.AddAircraftToQueue(airport_priority, 1, "not an int")

    # Test negative aircraft_index
    with pytest.raises(
        ValueError, match="aircraft_index must be a non-negative integer"
    ):
        PQ.AddAircraftToQueue(airport_priority, 1, -5)


def test_check_priority_normal():
    """Test normal operation of CheckPriority."""
    airport_priority = [[1, 2], [5, 7], []]

    # Test aircraft at front of queue
    assert PQ.CheckPriority(airport_priority, 0, 1) is True

    # Test aircraft not at front of queue
    assert PQ.CheckPriority(airport_priority, 0, 2) is False

    # Test aircraft not in queue
    assert PQ.CheckPriority(airport_priority, 0, 3) is False


def test_check_priority_errors():
    """Test error handling in CheckPriority."""
    airport_priority = [[1, 2], [5, 7], []]

    # Test invalid AirportPriority type
    with pytest.raises(TypeError, match="AirportPriority must be a list"):
        PQ.CheckPriority("not a list", 1, 5)

    # Test invalid airport_index type
    with pytest.raises(TypeError, match="airport_index must be an integer"):
        PQ.CheckPriority(airport_priority, "not an int", 5)

    # Test invalid airport_index range
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.CheckPriority(airport_priority, 3, 5)

    # Test negative airport_index
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.CheckPriority(airport_priority, -1, 5)

    # Test invalid aircraft_index type
    with pytest.raises(TypeError, match="aircraft_index must be an integer"):
        PQ.CheckPriority(airport_priority, 1, "not an int")

    # Test negative aircraft_index
    with pytest.raises(
        ValueError, match="aircraft_index must be a non-negative integer"
    ):
        PQ.CheckPriority(airport_priority, 1, -5)

    # Test empty queue
    with pytest.raises(ValueError, match="Priority queue for airport .* is empty"):
        PQ.CheckPriority(airport_priority, 2, 5)


def test_remove_aircraft_normal():
    """Test normal operation of RemoveAircraft."""
    airport_priority = [[1, 2], [5, 7], [9]]

    # Remove first aircraft from queue
    result = PQ.RemoveAircraft(airport_priority, 0, 0)  # aircraft_index is not used
    assert result[0] == [2]

    # Remove another aircraft
    result = PQ.RemoveAircraft(result, 0, 0)
    assert result[0] == []


def test_remove_aircraft_errors():
    """Test error handling in RemoveAircraft."""
    airport_priority = [[1, 2], [5, 7], []]

    # Test invalid AirportPriority type
    with pytest.raises(TypeError, match="AirportPriority must be a list"):
        PQ.RemoveAircraft("not a list", 1, 5)

    # Test invalid airport_index type
    with pytest.raises(TypeError, match="airport_index must be an integer"):
        PQ.RemoveAircraft(airport_priority, "not an int", 5)

    # Test invalid airport_index range
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.RemoveAircraft(airport_priority, 3, 5)

    # Test negative airport_index
    with pytest.raises(ValueError, match="airport_index .* is out of range"):
        PQ.RemoveAircraft(airport_priority, -1, 5)

    # Test empty queue
    with pytest.raises(ValueError, match="Cannot remove aircraft from empty queue"):
        PQ.RemoveAircraft(airport_priority, 2, 5)


def test_remove_aircraft_exception():
    """Test exception handling in RemoveAircraft."""

    # Create a mock list that will raise an exception when remove is called
    class MockList(list):
        def remove(self, item):
            raise ValueError("Mock exception")

    # Create a priority queue with our mock list
    airport_priority = [MockList([1])]

    # Test that the exception is caught and re-raised as RuntimeError
    with pytest.raises(RuntimeError, match="Error removing aircraft from queue"):
        PQ.RemoveAircraft(airport_priority, 0, 0)
