# Five observed failures — fill after real inference

Do not submit hypothetical cases as observations. Run `scripts.collect_cases`, inspect images against labels and record at least five actual failures. Candidate investigation categories: diagonal paving, small/distant tiles, occlusion, lighting/shadows, bicycle–motorcycle confusion. These are hypotheses until found.

| Image ID / split | Observed truth | Actual prediction | Failure and likely cause | Evidence file | Proposed fix and validation test |
|---|---|---|---|---|---|

For each case distinguish detector failure from relation-rule failure. Record uncertainty if physical blockage cannot be judged from the photo. Include enough context to reproduce inference: checkpoint SHA-256, thresholds, image ID and split. Do not cherry-pick these examples as aggregate performance evidence.
