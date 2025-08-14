"""
Data loading utilities for synthatdelays package.

This module provides functions for loading airport delay data files.
"""

from functools import lru_cache

import importlib.resources

from numpy import load, ndarray

# List of supported airports
SUPPORTED_AIRPORTS = ["EGLL", "LFPG", "EHAM", "EDDF", "LEMD"]


@lru_cache(maxsize=10)
def load_airport_data(airport_code: str) -> ndarray:
    """
    Load delay data for a specific airport.

    Parameters
    ----------
    airport_code : str
        ICAO code of the airport. Supported airports include:
        - London Heathrow ('EGLL')
        - Paris Charles de Gaulle ('LFPG')
        - Amsterdam ('EHAM')
        - Frankfurt ('EDDF')
        - Madrid ('LEMD')

    Returns
    -------
    np.ndarray
        Numpy array containing the delay data.

    Raises
    ------
    ValueError
        If the airport code is not supported.
    FileNotFoundError
        If the data file for the airport cannot be found.
    ImportError
        If there is an error importing the data file.

    Notes
    -----
    Loading of the delay data.
    Original data can be found at: https://doi.org/10.5281/zenodo.15046397
    """
    if airport_code not in SUPPORTED_AIRPORTS:
        raise ValueError(
            f"Unsupported airport code: {airport_code}. Supported airports are: {', '.join(SUPPORTED_AIRPORTS)}"
        )

    try:
        with importlib.resources.path(
            "synthatdelays.data", f"realDelays{airport_code}.npz"
        ) as data_path:
            data = load(data_path)
            return data["delays"]
    except (FileNotFoundError, ImportError) as e:
        raise e
    except KeyError as e:
        raise KeyError(
            f"Could not find 'delays' data in the file for airport {airport_code}: {str(e)}"
        )
