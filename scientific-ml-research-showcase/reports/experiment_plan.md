# Experiment Plan

## Research Question

Can a lightweight CNN-based surrogate learn a deterministic synthetic mapping from 2D scientific input fields to a plume-like output field?

## Purpose

Demonstrate scientific ML workflow competence without exposing private research data.

## Data

- Data type: synthetic demonstration fields
- Inputs: permeability-like field and source/location field
- Target: plume-like concentration field
- Config: `configs/config.yaml`
- Private data used: no

## Method

- Generate deterministic synthetic data from a random seed.
- Split into train, validation, and test sets.
- Train a small `mini_unet` by default.
- Evaluate MAE, RMSE, relative MAE, field correlation, and a simple SSIM-like score.
- Save plots and summaries.

## Success Criteria

- The workflow runs locally.
- Metrics and plots are generated.
- Reports clearly state synthetic data limitations.
- No private data or thesis claims are used.

## Current Run

- Model: `mini_unet`
- Samples: 96
- Image size: 32 x 32
- Epochs: 10
- Test RMSE: 0.081656
- Test field correlation: 0.701694

## Reporting Rules

- Report generated metrics only as synthetic demonstration results.
- Do not claim scientific validity.
- Do not claim PhD experiment reproduction.
