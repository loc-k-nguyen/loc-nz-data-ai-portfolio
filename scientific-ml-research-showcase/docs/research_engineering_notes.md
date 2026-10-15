# Research Engineering Notes

## What This Project Demonstrates

- Scientific ML surrogate framing
- Synthetic data generation
- Configuration-driven experiments
- PyTorch Dataset and model implementation
- Field-level regression metrics
- Reproducible training and evaluation
- Research-style reporting with limitations

## Why It Is Relevant To Scientific ML

Many scientific ML projects involve learning mappings between input fields, parameters, and simulation outputs. This project demonstrates the structure of that workflow in a controlled synthetic setting.

## Connection To PhD Skills

This project connects to PhD-style skills such as experiment design, surrogate modelling, numerical field interpretation, reproducibility, and scientific reporting. It does not use or reveal private thesis data.

## What Is Intentionally Simplified

- Synthetic formula instead of real simulator
- Small image size
- Small CNN
- Short local training
- No uncertainty quantification
- No temporal sequence modelling

## How It Could Scale To Rāpoi/ECS

The same structure could be scaled by increasing sample count, model size, image size, and training epochs. Server training would require explicit environment setup, logging, artifact synchronization, and reproducibility notes.

## Interview Talking Points

- Why synthetic data was used
- How the field-to-field task mirrors surrogate modelling structure
- Why metrics alone are not enough for scientific validity
- How the workflow could be adapted to public scientific benchmarks
- How to scale responsibly without exposing private data

