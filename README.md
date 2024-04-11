# submit.py

This script automates the generation and submission of GEANT4 macros and Condor jobs for particle simulations.

## Purpose

The `submit.py` script simplifies the process of setting up and running particle simulations by:

- Generating GEANT4 macros with customizable parameters.
- Creating Condor submit files for parallel job execution.
- Submitting Condor jobs for each macro.

## Usage

To use the `submit.py` script, run it from the command line with the required parameters:
- `--macros_folder`: The path to the folder where generated GEANT4 macros will be saved.
- `--isotope`: The name of the isotope used in the simulation.
- `--position`: The position string specifying the position of the particle source.
- `--confine`: The name of the confinement for the particle source.
- `--num_events`: The number of events to be simulated in each macro.
- `--times`: The number of times to generate and submit the macro, allowing for multiple simulations with different parameters.

