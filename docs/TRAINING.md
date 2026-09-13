# Fine-tune, recover and evaluate

Use a GPU environment and install `requirements.txt`. The supplied notebook handles Colab upload, Drive mounting and source-folder discovery. Download WOTR from https://github.com/kxzr/WOTR. If gdown is denied, use the author's browser download or published alternative and upload the archive to Drive; rerunning preparation cannot repair a missing download.

## Prepare and audit

```bash
python -m scripts.prepare_wotr --source data/raw/WOTR --output data/guidepath_original
python -m scripts.clean_dataset --source data/raw/WOTR --audit-dir data/guidepath_original --output data/guidepath_clean
```

The first command exits 2 when its saved audit contains blocking issues. Read that audit. Run cleanup only for the supported invalid-box/exact-duplicate issues. A fresh output path is mandatory. If there were no blocking issues, use the original dataset. Review sample image/label overlays and location groups. Do not start training by suppressing the audit check.

## Fine-tune

```bash
python -m scripts.train --data data/guidepath_clean/data.yaml --epochs 30 --batch 4 --imgsz 640 --name baseline --project runs/detect
```

On Colab use `--project /content/drive/MyDrive/GuidePath/runs/detect` after mounting Drive. Keep the dataset on the local runtime for reading speed. Last/best checkpoints are saved by training to the Drive run directory after epochs; interruption before a checkpoint finishes can still lose progress. Resume from the newest readable `last.pt`.

For a short integration experiment use `--epochs 1 --name smoke`. Raising batch to 8 may improve throughput if GPU memory permits; lower it after an out-of-memory error and use a fresh run name. It is not guaranteed faster, and one epoch does not establish final performance. Do not promise training a 13,928-image dataset within 3–5 minutes.

## Runtime disconnected

Reconnect a GPU, reinstall dependencies and restore/reprepare the same data. Locate the saved checkpoint in Drive. Then:

```bash
python -m scripts.train --data data/guidepath_clean/data.yaml --resume /content/drive/MyDrive/GuidePath/runs/detect/baseline/weights/last.pt --batch 4 --device 0
```

Resume uses the checkpoint's training schedule, not a new `--epochs` budget. A completed one-epoch checkpoint is not an interrupted 30-epoch run. If the runtime was deleted and nothing was saved outside it, those checkpoints cannot be recovered from the notebook alone. The installed Ultralytics version governs resume support; preserve the run's pip-freeze record.

## Evaluate and inspect real cases

```bash
python -m scripts.evaluate --weights runs/detect/baseline/weights/best.pt --data data/guidepath_clean/data.yaml --split val --name baseline_val
python -m scripts.collect_cases --weights runs/detect/baseline/weights/best.pt --images data/guidepath_clean/images/val --split val --output runs/cases_val
```

Review `cases.json` with its images. Fill truth and root cause from inspection, not from the model answer. Tune confidence/overlap on validation only. Save thresholds in `thresholds.json` and freeze the checkpoint. Then run evaluation on `--split test --name final_test`, and collect test cases to a fresh directory. `--limit` is for quick inspection, not a representative performance estimate.

For reasoning evaluation, manually label image-level `truth` as `possible_obstruction`, `no_obstruction_detected` or `insufficient_information`. These labels concern visible image evidence, not physical safety. Use a single split:

```bash
python -m scripts.reasoning_eval --input runs/cases_val/cases.json --split val --config thresholds.json --output runs/reasoning_val.json
```

The evaluator compares the spatial rule with a co-occurrence baseline and reports abstention. Unreviewed placeholder truths deliberately fail. Its metrics are not detector mAP.

Install the selected checkpoint with `python -m scripts.install_weights --source YOUR/best.pt`. Preserve evaluation `summary.json`, plots, CSV, final audit/manifest/cleanup report, environment JSON, pip-freeze, five manually explained failures and real API responses. The notebook export cell packages these local/Drive outputs. All final performance claims must refer to these actual outputs.
