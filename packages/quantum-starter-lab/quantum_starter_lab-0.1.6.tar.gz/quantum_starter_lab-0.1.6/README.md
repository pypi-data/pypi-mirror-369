# quantum-starter-lab

[![PyPI version](https://img.shields.io/pypi/v/quantum-starter-lab.svg)](https://pypi.org/project/quantum-starter-lab/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub issues](https://img.shields.io/github/issues/Pranava-Kumar/quantum-starter-lab)](https://github.com/Pranava-Kumar/quantum-starter-lab/issues)
[![GitHub stars](https://img.shields.io/github/stars/Pranava-Kumar/quantum-starter-lab)](https://github.com/Pranava-Kumar/quantum-starter-lab/stargazers)

This package abstracts complex quantum frameworks, making it easy to experiment with entanglement, superposition, and more—perfect for students, educators, and researchers exploring noisy intermediate-scale quantum (NISQ) applications without building everything from scratch.

## Features:

Easy-to-Use API: Run quantum demos with minimal code.

Multiple Backends: Supports Qiskit Aer and Cirq Simulator (with plans for real hardware integration).

Noise Simulation: Apply realistic noise models (bit-flip, depolarizing, amplitude damping) to study error effects.

Visualization: Built-in plotting for circuit diagrams and result histograms.

Reproducibility: Seed support for consistent results.

Extensible: Modular IR (Intermediate Representation) for custom circuits.

Research Tools: Export results to JSON/CSV for analysis; upcoming VQE and QAOA for optimization studies.

Cross-Platform: Works on Windows, macOS, and Linux.

# Installation:

You can install quantum-starter-lab from PyPI using pip or uv (recommended for faster installs).

## Using uv (Preferred)
uv is a fast Python package manager.

uv venv  # Create a virtual environment

.venv\Scripts\activate  # Activate on Windows (or source .venv/bin/activate on Unix)

uv pip install quantum-starter-lab

## Using pip

python -m venv .venv

.venv\Scripts\activate

pip install quantum-starter-lab

# Development Installation

## Clone the repo and install in editable mode for contributing:

git clone https://github.com/Pranava-Kumar/quantum-starter-lab.git

cd quantum-starter-lab

uv venv

.venv\Scripts\activate

uv sync --all-extras --dev

uv pip install -e .

Requirements: Python >=3.10, Qiskit, Cirq, Matplotlib, NumPy.

# Quick Start
## After installation, run a simple demo:

from quantum_starter_lab.api import make_bell

### Run the Bell state demo

results = make_bell(backend="qiskit.aer", seed=42)

print(results)  # Prints explanation, counts, and probabilities

results.plot()  # Displays circuit and histogram


## Example Usage

Here's a complete script testing multiple functions (save as test_quantum_lab.py and run with uv run python test_quantum_lab.py):

import math

from quantum_starter_lab.api import make_bell, deutsch_jozsa, bernstein_vazirani, grover, teleportation

SEED = 42

BACKEND = "qiskit.aer"

### Bell state with noise

results_bell = make_bell(backend=BACKEND, noise_name="depolarizing", p=0.05, seed=SEED)

print("Bell Results:", results_bell)

results_bell.plot()  # View plot

### Deutsch-Jozsa

results_dj = deutsch_jozsa(n_qubits=3, oracle_type="balanced", backend=BACKEND, seed=SEED)

print("DJ Results:", results_dj)

### Bernstein-Vazirani

results_bv = bernstein_vazirani(n_qubits=4, secret_string="1011", backend=BACKEND, seed=SEED)

print("BV Results:", results_bv)

### Grover's search

results_grover = grover(n_qubits=3, marked_item="110", backend=BACKEND, seed=SEED)

print("Grover Results:", results_grover)

### Teleportation

results_tele = teleportation(initial_state_angle=math.pi, backend=BACKEND, seed=SEED)  # Teleport |1>

print("Teleportation Results:", results_tele)

Expected output includes printed results and plots for each demo.

### For research workflows, export data:

results.export_data("results.json")  # Upcoming feature in v0.2.0 

# Setup and Development

Virtual Environment: Use uv or venv as shown in Installation.

Running Tests: After development install, run make test (requires Makefile from repo).

Linting: make lint to check code style.

Building and Publishing: Use uv build and your GitHub workflow for releases.

For real hardware, install extras: uv pip install qiskit-ibm-provider and pass backend="ibm_q".

# Roadmap
v0.2.0: Enhanced parameters and data export.

v0.3.0: VQE and QAOA for research.

v1.0.0: Real hardware support and community contributions.

# Contributing
We welcome contributions! To get started:

Fork the repo.

Create a feature branch (git checkout -b feature/new-demo).

Commit changes (git commit -m "Add VQE function").

Push (git push origin feature/new-demo).

Open a Pull Request.

## See CONTRIBUTING.md for details. Report issues or suggest features on GitHub Issues.

# License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments
### Built with Qiskit and Cirq.
### Inspired by quantum education resources from IBM and Google.

# Contact
Author: Pranava Kumar (pranavakumar.it@gmail.com)

Project Link: https://github.com/Pranava-Kumar/quantum-starter-lab

For questions or collaboration, open an issue or reach out!
