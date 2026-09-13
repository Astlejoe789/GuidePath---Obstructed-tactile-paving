# GuidePath memo worksheet — incomplete, not submission-ready

Keep the final rendered memo at or below two pages. Replace every placeholder with measured evidence.

1. Domain and data (about 150 words): Why a maintenance photo-inspection task? Cite WOTR, acquisition date/version/hash and exact class mapping. Explain the restricted obstacle coverage. State label review findings and actual image/instance counts. Note the pivot from the earlier paving-only dataset candidate to WOTR because it includes obstacle annotations.
2. Splits and evaluation (about 150 words plus compact metrics table): Actual train/val/test counts, group policy, duplicate findings, held-out scope, per-class mAP/precision/recall and limitations. Describe threshold selection using validation only. Include overlap-vs-co-occurrence comparison and abstention rate if completed.
3. Five observed failures (compact five-row table): For EACH give image ID, expected behaviour, actual prediction/confidence, evidence for likely root cause and a specific proposed fix. Do not claim an untested fix works. Attach full images in repository evidence rather than overcrowding the memo.
4. Reasoning (about 100 words): Routes, spatial rule, validated LLM evidence-plan synthesis, rejected malformed output, and an actual insufficient-information example. Describe limits of the LLM component candidly.
5. Reproduction pointer: Repository command, weights path/checksum, environment lock, GPU, duration and hyperparameters. State remaining domain-shift and geometry limitations.

Do not fill this worksheet with hypothetical results. Do not quote a dataset's hosted-model metrics as your own RT-DETR result.
