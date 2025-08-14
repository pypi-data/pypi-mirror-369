# -*- coding: utf-8 -*-
"""
Synth AT Delays - Priority Queue Module

This module provides functionality for managing aircraft priority queues at airports.
It handles the ordering of aircraft operations at each airport, ensuring that
aircraft are processed in the correct sequence based on their arrival in the queue.

The module implements a simple first-in-first-out (FIFO) queue system for each airport,
allowing aircraft to be added to queues, checked for priority status, and removed
when their operations are complete.

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""


def AddAircraftToQueue(AirportPriority, airport_index, aircraft_index):
    """
    Add an aircraft to the priority queue of an airport if it's not already in the queue.

    Parameters
    ----------
    AirportPriority : list
        List of priority queues for each airport.
    airport_index : int
        Index of the airport.
    aircraft_index : int
        Index of the aircraft to add to the queue.

    Returns
    -------
    list
        Updated list of priority queues.
    """
    if not isinstance(AirportPriority, list):
        raise TypeError("AirportPriority must be a list")

    if not isinstance(airport_index, int):
        raise TypeError("airport_index must be an integer")

    if airport_index < 0 or airport_index >= len(AirportPriority):
        raise ValueError(
            f"airport_index {airport_index} is out of range (0-{len(AirportPriority) - 1})"
        )

    if not isinstance(aircraft_index, int):
        raise TypeError("aircraft_index must be an integer")

    if aircraft_index < 0:
        raise ValueError("aircraft_index must be a non-negative integer")

    if aircraft_index not in AirportPriority[airport_index]:
        AirportPriority[airport_index].append(aircraft_index)

    return AirportPriority


def CheckPriority(AirportPriority, airport_index, aircraft_index):
    """
    Check if an aircraft is at the front of an airport's priority queue.

    Parameters
    ----------
    AirportPriority : list
        List of priority queues for each airport.
    airport_index : int
        Index of the airport.
    aircraft_index : int
        Index of the aircraft to check.

    Returns
    -------
    bool
        True if the aircraft is at the front of the queue, False otherwise.
    """
    if not isinstance(AirportPriority, list):
        raise TypeError("AirportPriority must be a list")

    if not isinstance(airport_index, int):
        raise TypeError("airport_index must be an integer")

    if airport_index < 0 or airport_index >= len(AirportPriority):
        raise ValueError(
            f"airport_index {airport_index} is out of range (0-{len(AirportPriority) - 1})"
        )

    if not isinstance(aircraft_index, int):
        raise TypeError("aircraft_index must be an integer")

    if aircraft_index < 0:
        raise ValueError("aircraft_index must be a non-negative integer")

    if not AirportPriority[airport_index]:
        raise ValueError(f"Priority queue for airport {airport_index} is empty")

    if AirportPriority[airport_index][0] == aircraft_index:
        return True

    return False


def RemoveAircraft(AirportPriority, airport_index, aircraft_index):
    """
    Remove the first aircraft from an airport's priority queue.

    Parameters
    ----------
    AirportPriority : list
        List of priority queues for each airport.
    airport_index : int
        Index of the airport.
    aircraft_index : int
        Index of the aircraft (not used in this function).

    Returns
    -------
    list
        Updated list of priority queues.
    """
    if not isinstance(AirportPriority, list):
        raise TypeError("AirportPriority must be a list")

    if not isinstance(airport_index, int):
        raise TypeError("airport_index must be an integer")

    if airport_index < 0 or airport_index >= len(AirportPriority):
        raise ValueError(
            f"airport_index {airport_index} is out of range (0-{len(AirportPriority) - 1})"
        )

    if not AirportPriority[airport_index]:
        raise ValueError(
            f"Cannot remove aircraft from empty queue for airport {airport_index}"
        )

    try:
        AirportPriority[airport_index].remove(AirportPriority[airport_index][0])
    except (IndexError, ValueError) as e:
        raise RuntimeError(f"Error removing aircraft from queue: {str(e)}")

    return AirportPriority
