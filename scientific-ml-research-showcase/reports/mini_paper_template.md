# A Lightweight Synthetic Surrogate Modelling Workflow for Scientific Machine Learning

## Abstract

This report presents a lightweight synthetic scientific ML surrogate workflow. The task maps a two-channel synthetic input field to a plume-like target field using a compact CNN-based model. The goal is to demonstrate research engineering practice, not to report real scientific or PhD results.

## Motivation

Scientific simulations can be expensive to run repeatedly. Surrogate models provide a way to approximate simulation outputs for fast exploration. This project demonstrates the structure of such a workflow using synthetic data that can be generated locally and reproducibly.

## Synthetic Data Generation

The input contains:

- a smooth permeability-like random field
- a source/location Gaussian field

The target is a plume-like concentration field generated from a transparent formula influenced by the input fields. All data is synthetic demonstration data.

## Model

The default model is `mini_unet`, a lightweight encoder-decoder CNN with a skip connection. A smaller `small_cnn` baseline is also implemented.

## Experiment Setup

- Config file: `configs/config.yaml`
- Default samples: 96
- Image size: 32 x 32
- Default epochs: 5
- Device: CPU or CUDA automatically

## Metrics

The workflow reports:

- MAE
- RMSE
- Relative MAE
- Field correlation
- Simple SSIM-like score

## Results

Actual generated metrics are written to:

```text
outputs/metrics.csv
outputs/experiment_summary.md
```

Latest local test metrics:

| Metric | Value |
| --- | ---: |
| MAE | 0.051088 |
| RMSE | 0.081656 |
| Relative MAE | 0.280343 |
| Field correlation | 0.701694 |
| Simple SSIM-like score | 0.605504 |

These metrics are synthetic demonstration results only.

## Limitations

- Synthetic fields are simplified.
- The model is intentionally small.
- Results are not scientifically validated.
- No uncertainty quantification is included.
- No private PhD data is used.

## Reproducibility

Run:

```powershell
python .\scientific-ml-research-showcase\run_project.py
```

## Future Work

- Add public scientific benchmark data
- Add temporal fields
- Add uncertainty quantification
- Add longer experiment tracking
- Scale to Rāpoi/ECS only when needed
