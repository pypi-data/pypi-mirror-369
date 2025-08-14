# Synthetic Air Transport Delays

[![PyPI version](https://img.shields.io/pypi/v/synthatdelays)](https://pypi.org/project/synthatdelays/)
[![Python Version](https://img.shields.io/pypi/pyversions/synthatdelays)](https://pypi.org/project/synthatdelays/)
[![Coverage](https://gitlab.com/MZanin/synth-at-delays/badges/main/coverage.svg)](https://gitlab.com/MZanin/synth-at-delays/-/jobs)
[![License](https://img.shields.io/pypi/l/synthatdelays)](https://gitlab.com/MZanin/synth-at-delays/-/blob/main/LICENSE)
[![GitLab](https://img.shields.io/badge/GitLab-MZanin%2Fsynth--at--delays-orange?logo=gitlab)](https://gitlab.com/MZanin/synth-at-delays)

Welcome to Synth-AT-Delays, a Python package designed to produce synthetic delay information from highly tuneable scenarios. Compared to other options, these scenarios are not aimed at mimicking the behaviour of the real system; but rather to test specific conditions and hypotheses, and how subsequent analyses are able to capture these. You may use this package to create a hypothetical system composed of a few airports, and generate time series representing the evolution of the average delays when changing their capacity. Similarly, different events and conditions can be simulated, e.g. the appearance of delays in specific routes, the dependence of different flights from the same crew, or the length of the buffer time between subsequent operations. 


## Setup

This package can be installed from PyPI using pip:

```bash
pip install synthatdelays
```

This will automatically install all the necessary dependencies as specified in the
`pyproject.toml` file.


## Getting started

Information about how to set up a simulation and extract results is available in the wiki: [Go to the wiki](https://gitlab.com/MZanin/synth-at-delays/-/wikis/home).

A good starting point are also the [Tutorial files](https://gitlab.com/MZanin/synth-at-delays/-/wikis/Home/Tutorials), which guide you in scenarios of increasing complexity.


## Change log

See the [Version History](https://gitlab.com/MZanin/synth-at-delays/-/wikis/Home/Version-History) section of the Wiki for details.

