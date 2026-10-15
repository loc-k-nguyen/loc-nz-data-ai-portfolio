# Reproducibility Checklist

- [x] Synthetic data only
- [x] No private PhD data
- [x] Config file committed: `configs/config.yaml`
- [x] Random seed configured
- [x] CPU-compatible run
- [x] Training command documented
- [x] Evaluation command documented
- [x] Metrics written to `outputs/`
- [x] Plots written to `outputs/`
- [x] Model metadata written to `models/`
- [x] Limitations documented
- [ ] Optional longer run documented separately
- [ ] Optional Rāpoi/ECS run documented only if actually performed

Commands:

```powershell
python .\scientific-ml-research-showcase\run_project.py
python -m compileall .\scientific-ml-research-showcase
```

