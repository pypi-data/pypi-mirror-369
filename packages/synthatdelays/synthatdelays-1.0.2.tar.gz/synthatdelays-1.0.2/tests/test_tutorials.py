"""
Tests for running all tutorial files.

This test file parametrises over all tutorial files and runs them as tests
to ensure they execute without errors.
"""

import os
import glob
from unittest.mock import patch

import pytest
import importlib.util
import sys
import matplotlib

matplotlib.use(
    "Agg"
)  # Use non-interactive backend to avoid display issues during tests


def get_tutorial_files():
    """Get all tutorial Python files from the Tutorials directory."""
    # Assuming the tutorials are in a 'Tutorials' directory at the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tutorial_dir = os.path.join(project_root, "tutorials")

    # Get all Python files in the Tutorials directory
    tutorial_files = glob.glob(os.path.join(tutorial_dir, "Tutorial_*.py"))

    # Return relative paths for better test naming
    return [os.path.basename(f) for f in tutorial_files]


@pytest.mark.parametrize("tutorial_file", get_tutorial_files())
@patch("matplotlib.pyplot.show")  # Mock plt.show() to do nothing - showing no warnings
def test_tutorial_execution(mock_show, tutorial_file):
    """Test that each tutorial file can be executed without errors."""
    # Get the full path to the tutorial file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tutorial_path = os.path.join(project_root, "tutorials", tutorial_file)

    # Load the module from the file path
    spec = importlib.util.spec_from_file_location(
        f"tutorial_{tutorial_file.replace('.py', '')}", tutorial_path
    )
    tutorial_module = importlib.util.module_from_spec(spec)

    # Add the module to sys.modules
    sys.modules[spec.name] = tutorial_module

    try:
        # Execute the module
        spec.loader.exec_module(tutorial_module)
    except Exception as e:
        pytest.fail(f"Tutorial {tutorial_file} failed with error: {str(e)}")
