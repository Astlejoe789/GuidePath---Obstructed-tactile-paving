# Model card — checkpoint pending

- Architecture: Ultralytics RT-DETR-L initialized from `rtdetr-l.pt`, then fine-tuned on the documented three-class dataset.
- Intended use: photographic review of supported paving–obstacle relationships.
- Checkpoint: **not included or verified**. Add your actual `best.pt` and generated `weights/model_manifest.json`.
- Metrics, latency and final epoch count: **not measured in this delivered environment**.
- Training recipe: `scripts/train.py`; requested starting experiment 30 epochs, batch 4, 640 pixels, seed 42. Dataset manifest hash, actual configuration, environment and elapsed session time are saved with the run. CUDA RT-DETR uses `deterministic=False`; a seed is not a bitwise reproducibility guarantee.
- Confidence values refer to detections, not actual obstruction probabilities. Thresholds are provisional.
- Limitations: box geometry, weak/occluded paving, lighting, class confusion, unsupported obstacles, location leakage and domain shift.
- Required evidence: real per-class mAP50 and mAP50–95, precision/recall and confusion plots; selected/frozen thresholds; five real model failures; live API examples linked to the checkpoint SHA-256.
