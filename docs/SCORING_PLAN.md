# Evidence mapped to RAP's rubric

The goal is to make each scored claim easy to verify. No rank or selection probability can be promised.

| Weight | Component | Evidence to produce | Current status |
|---|---|---|---|
| 25% | Hidden-set performance | Fine-tuned checkpoint, robust preprocessing, held-out testing | Needs real training and external evaluation |
| 15% | Dataset quality | Source, mapping, class counts, reviewed boxes, leakage checks | Converter tested; original audit summary shared; final cleanup and scene review pending |
| 10% | Evaluation honesty | Saved detector metrics, class counts and clear limitations | Evaluation scripts built; results pending |
| 15% | Failure analysis | Five actual image IDs with evidence and root causes | Exporter built; real cases pending |
| 15% | Reasoning | Routes, evidence IDs, abstentions, actual direct LLM call | Logic tested; live LLM call pending |
| 10% | Code and reproduction | API, instructions, environment and training manifest | Software checked; model integration pending |
| 10% | Bonus engineering | Container, reachable deployment, logs, error handling | Code included; deployment pending |

Highest-value next work: recover the checkpoint if it exists, otherwise complete a real baseline on the audited data, then review measured failures. No software test or UI screenshot replaces the required model evidence.

Verbal defence prompts:
- Why RT-DETR and why these three classes?
- How does `blind_road` map to the labels?
- Why is detection confidence not obstruction confidence?
- What does the overlap denominator mean?
- When can diagonal paving cause a false alarm?
- What does no obstruction detected exclude?
- How did you prevent leakage and choose thresholds?
- What did the LLM actually do, and why constrain it?
- Which failure surprised you, and what evidence supports your diagnosis?
