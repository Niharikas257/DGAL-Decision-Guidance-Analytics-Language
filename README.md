<!-- Project Badges -->
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Niharikas257/DGAL-Decision-Guidance-Analytics-Language/python-app.yml?branch=main)](https://github.com/Niharikas257/DGAL-Decision-Guidance-Analytics-Language/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub last commit](https://img.shields.io/github/last-commit/Niharikas257/DGAL-Decision-Guidance-Analytics-Language)](https://github.com/Niharikas257/DGAL-Decision-Guidance-Analytics-Language/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/Niharikas257/DGAL-Decision-Guidance-Analytics-Language)](https://github.com/Niharikas257/DGAL-Decision-Guidance-Analytics-Language)


# DGAL-Decision-Guidance-Analytics-Language
Python library for modeling and solving constraint-based optimization problems using Pyomo. Designed for supply chain, manufacturing, and service network decision analytics.

A Python library that abstracts and automates the process of defining and solving constraint-based optimization problems using [Pyomo](http://www.pyomo.org/). It is designed for use in decision guidance applications such as supply chain optimization, manufacturing flow modeling, transportation cost analysis, and hierarchical service network planning.

#Features

- Define optimization problems using JSON-style inputs with symbolic decision variables
- Support for real and integer variable types (`real?`, `int?`)
- Automated conversion of user-defined models into Pyomo-compatible structures
- Constraint chaining using logical `and`, `or`, and nested conditionals
- Built-in support for objective function formulation and solver selection (`GLPK`, `CBC`, etc.)
- Structured output reporting, including solver status, termination condition, and solution values
- Debugging and result tracking through Python's `logging` module

#Use Cases

This library was used to solve multiple decision models in the CS 787 – Decision Guidance Systems course at George Mason University, including:

- Supplier selection with quantity constraints
- Manufacturing input-output balancing with dependencies
- Transportation cost optimization across multi-location networks
- Combined supply chain optimization across supplier, manufacturer, and transportation layers
- Hierarchical service network modeling

#Technologies Used

- Python 3.x
- [Pyomo](https://pyomo.readthedocs.io/en/stable/)
- External solvers: `GLPK`, `CBC` (via Pyomo)
- JSON-based configuration
- Python logging/debugging tools

#Project Structure

dgal/ #Core DGAL Python implementation
└── dgal.py
solution/ # Assignment-related models and optimization scripts
├── ams.py # Analytic models (supplier, manuf, transp, etc.)
├── main.py # Entry point for running models with JSON input
├── optSupply.py # Optimization logic for supply model
├── optManuf.py # Optimization logic for manufacturing model
├── optTransp.py # Optimization logic for transportation model
example_input_output/
├── *.json # Sample input and expected output files
answers/ # Output results from optimizations

#How It Works

1. Define your model input using JSON with symbolic variables.
2. Create an analytic model in Python (e.g., cost computation, flow rules).
3. Define constraints and objectives using Python functions.
4. Call `dgal.optimize()` or `dgal.min()` / `dgal.max()` to solve.
5. Retrieve structured results and debug logs.



