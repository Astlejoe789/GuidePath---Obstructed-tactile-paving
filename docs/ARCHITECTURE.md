# Architecture

## Runtime: one handwritten decision layer

```mermaid
flowchart TD
  Q["Question + optional image"] --> R["Handwritten intent router"]
  R -->|Capability question| C["Local explanation; no detector"]
  R -->|Unsupported question| U["Explicit limitation; no detector"]
  R -->|Visual intent| V["Validate image and checkpoint"]
  V --> D["Fine-tuned RT-DETR"]
  D --> S["Classes, boxes, confidence"]
  S --> E["Counts + overlap + evidence IDs"]
  E --> L["Direct LLM HTTP: typed evidence plan"]
  L --> G{"Conclusion and facts valid?"}
  G -->|Yes| A["Render verified plain-language answer"]
  G -->|No / unavailable| F["Deterministic answer + fallback status"]
```

`/detect` ends after structured detection output. `/reason` uses the full branch. No LangChain, LangGraph, CrewAI or agent orchestration is used. The LLM can select/order verified facts and caveats; it cannot introduce visual facts or overrule the deterministic guardrail. This constrained plan trades linguistic flexibility for traceability. Live provider behavior still needs verification.

## Obstruction flow

```mermaid
flowchart TD
  D["Candidate detections"] --> P{"Confident paving visible?"}
  P -->|No| I["Insufficient information"]
  P -->|Yes| O{"Accepted obstacle-box overlap?"}
  O -->|Yes| M["Possible obstruction; cite pair IDs"]
  O -->|No| W{"Weak supported detections?"}
  W -->|Yes| I
  W -->|No| N["No supported obstruction detected"]
```

For obstacle box O and paving box P, the score is **area(O ∩ P) / area(O)**, not IoU and not physical blocked-path percentage. Provisional thresholds are 0.45 accepted confidence, 0.15 candidate floor and 0.10 overlap. Tune on validation evidence only, record the selected configuration, then freeze it before test evaluation.

## Training and evidence

```mermaid
flowchart TD
  W["Author WOTR archive"] --> A["VOC conversion + provenance audit"]
  A --> B{"Blocking issues?"}
  B -->|Yes| C["Explicit exclusions + fresh dataset"]
  C --> A2["Re-audit + manual location review"]
  B -->|No| A2
  A2 --> T["Train split: RT-DETR fine-tuning"]
  T --> V["Validation: model + rule decisions"]
  V --> F["Freeze checkpoint and thresholds"]
  F --> E["Held-out test + five observed failures"]
  E --> P["Weights hash + metrics + reproducible API"]
```

The 3D canvas is a separate teaching aid. It neither feeds nor consumes detector geometry; moving it changes only its conceptual scene.
