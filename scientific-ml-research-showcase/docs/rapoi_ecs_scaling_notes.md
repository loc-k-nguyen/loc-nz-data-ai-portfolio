# Rāpoi / ECS Scaling Notes

This file is documentation only. No jobs are submitted by this project.

## When To Use Rāpoi/ECS

Use server resources only when local runs are too slow or when experiments require:

- larger synthetic datasets
- larger image sizes
- deeper CNN/U-Net models
- longer training runs
- repeated sweeps

## What Would Need To Change

- Increase `num_samples`, `image_size`, and `epochs` in `configs/config.yaml`.
- Add explicit logging paths.
- Save checkpoints periodically.
- Record environment details.
- Sync only code, configs, and non-private artifacts.

## Placeholder Future Commands

These are examples only and should be adapted before use:

```bash
python scientific-ml-research-showcase/src/train.py
python scientific-ml-research-showcase/src/evaluate.py
```

## GPU / CPU Notes

The current config uses `device: auto`, so it uses CUDA if available and CPU otherwise. CPU is sufficient for the default portfolio run.

## Reproducibility Precautions

- Commit config files before running.
- Record git commit hash.
- Record package versions.
- Do not copy private data.
- Do not include credentials or private paths in reports.

