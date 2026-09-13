# Data card

Source: https://github.com/kxzr/WOTR — use the author's published archive. Record the downloaded archive hash and reviewed usage terms in your final submission. The dataset itself is not included here.

VOC labels map `blind_road` or `tactile_paving` to class 0 `tactile_paving`; `bicycle` to 1; `motorcycle` to 2. Other classes are omitted. Images without selected labels remain negative/background images. Difficult selected objects are included and counted in the manifest. VOC left/top coordinates are converted from 1-based inclusive to zero-based bounds before YOLO normalization.

| Original split | Images | Paving instances | Bicycle instances | Motorcycle instances |
|---|---:|---:|---:|---:|
| train | 9056 | 1596 | 4012 | 8059 |
| val | 2338 | 371 | 987 | 1887 |
| test | 2534 | 409 | 992 | 2202 |

These numbers are from the user-shared original audit, not a new run or the final cleaned dataset. There were 34 blocking flags, not necessarily 34 images. Only a partial flag listing was shared. The complete original and final audit files are not available in this package.

`prepare_wotr.py` preserves official splits unless a reviewed CSV (`image_id,split,group`) is supplied. It blocks invalid boxes, dimensions, empty classes/splits, duplicate image IDs, exact pixel duplicates and provided groups crossing splits. `clean_dataset.py` handles only invalid-box and exact-pixel flags, creates fresh outputs, records every removal and prefers test > val > train for duplicate retention. Unknown issue types require inspection. It does not silently repair coordinates.

The automatic cleanup groups by exact pixel hash only. It must not be described as scene-independent. Review similar locations, sequences and near duplicates; if a reviewed split is needed, create it before training and re-audit. Freeze the manifest; use validation for choices and test only after freezing them. Dataset shift to local campuses, paving textures, lighting and camera angles remains unmeasured.
