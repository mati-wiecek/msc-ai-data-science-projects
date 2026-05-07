# Genetic Algorithms for Portfolio Optimisation

## Overview

This project applies genetic algorithms to portfolio optimisation, exploring how evolutionary search can be used to find candidate asset allocations under risk-return constraints.

It demonstrates mathematical reasoning, optimisation logic, experiment design, and clear analysis of trade-offs.

## Problem

Portfolio optimisation is the task of selecting asset weights that balance expected return and risk. Traditional methods can be sensitive to assumptions, constraints, and objective functions.

A genetic algorithm offers a flexible search-based approach that can handle custom constraints and non-linear objectives.

## Approach

1. Represent a portfolio as a chromosome of asset weights.
2. Initialise a population of candidate portfolios.
3. Evaluate each portfolio using a fitness function.
4. Select stronger candidates for reproduction.
5. Apply crossover and mutation to create new portfolios.
6. Repeat over multiple generations.
7. Compare the best portfolio against baseline allocations.

## Technologies

- Python
- NumPy
- pandas
- matplotlib / seaborn
- Jupyter Notebook

## Fitness Function Ideas

Possible objectives include:

- Maximising expected return
- Minimising volatility
- Maximising Sharpe ratio
- Penalising portfolios that violate allocation constraints

## Repository Structure

```text
genetic-algorithms-portfolio-optimisation/
  README.md
  requirements.txt
  notebooks/
  src/
  reports/
    figures/
```

## Reproducibility

Suggested setup:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

The final version should include data source notes, random seed control, and plots showing convergence over generations.

## Results to Include

- Fitness score over generations
- Best portfolio allocation
- Risk-return comparison against baseline portfolios
- Sensitivity analysis for mutation rate or population size

## Status

README and project structure prepared. Implementation, experiment notebook, and final plots should be added next.
