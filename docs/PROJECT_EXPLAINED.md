# Why GuidePath?

Tactile paving provides a physical cue for pedestrians with visual impairments. A visible bicycle or motorcycle may obstruct that cue. GuidePath's intended user is a campus or facilities reviewer inspecting photographs and deciding which locations need follow-up.

## Before and after: proposed workflow, not measured impact

| Stage | Basic object detector / manual review | GuidePath approach |
|---|---|---|
| Observation | See a paving box and bicycle box | Preserve IDs, confidence and exact image coordinates |
| Interpretation | Assume co-occurrence means obstruction | Compare spatial overlap and expose the calculation |
| Weak evidence | Risk producing a confident statement | Return insufficient information |
| Explanation | Generic generated caption | Render only validated facts selected by the LLM |
| Follow-up | Reviewer restarts the investigation | Save the response JSON and inspect the cited evidence |

## What is different in this submission?

The contribution is an application-specific engineering design: a non-COCO paving class, an audited dataset, a spatial relation rule, explicit abstention and bounded LLM synthesis. RT-DETR, bounding-box overlap and language models are existing techniques. No claim of first-in-the-world novelty or superiority to another candidate is made.

The dataset investigation is concrete: the shared audit had 34 blocking flags, including exact cross-split duplicates. Excluding leakage and retaining an audit trail is more defensible than presenting an inflated metric. Remaining location leakage is acknowledged.

## Decisions and trade-offs

| Decision | Reason | Cost / test needed |
|---|---|---|
| RT-DETR-L fine-tuning | Meets the required model family and adapts to tactile paving | GPU time; final quality must be measured |
| Three supported classes | Direct paving–obstacle relation with available labels | Misses cars, poles, boxes and other hazards |
| Keep background images | Teach the detector when supported objects are absent | Review false positives and class imbalance |
| Exclude invalid-box images | Avoid silently teaching partial or corrupted target labels | Loses valid instances on those images; report exclusions |
| Prefer test copy during exact deduplication | Prevent a test image from also training the model | Reduces train size; does not cure near duplicates |
| Rules compute evidence, LLM composes a typed plan | Makes the language step inspectable and rejects invented observations | Restricted language and provider integration still needed |
| Separate 3D explanation | Helps a reviewer understand position and perspective | Does not measure real depth or clearance |

## Social value and how to measure it

Potential value: help facilities teams notice supported obstructions earlier and make photographic review more consistent. It is not a navigation aid. A pilot should measure confirmed useful alerts, false alerts per reviewed image, reviewer time, missed supported obstructions and abstention coverage. Compare a manual workflow and a simple co-occurrence baseline on the same reviewed cases. No percentage improvement is asserted before that study.

Future work follows observed failures: paving masks for diagonal paths; local images for domain shift; more obstacle labels for wider coverage. Each extension needs new labels and an evaluation, not just a new UI feature.

## Interview explanation

“I chose tactile paving because recognizing an object is not enough to explain an accessibility concern. I convert and audit WOTR, fine-tune RT-DETR on three classes, then link each potential overlap to detector IDs. The handwritten router avoids unnecessary inference. A constrained LLM selects supporting facts, and validation prevents invented evidence. I measure detector quality separately from reasoning behavior and report what remains unverified.”

Use this explanation only after understanding the implementation. Be precise about the training and evaluation you personally completed.
