# Run and check the API

Run all commands from the project root while the server is running. Use `curl.exe` instead of `curl` in Windows PowerShell. Local file `photo.jpg` must be your own permitted image.

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/demo/scenarios
curl -X POST http://127.0.0.1:8000/demo/reason -F "scenario=beside" -F "question=Is the tactile path blocked?"
curl -X POST http://127.0.0.1:8000/reason -F "question=What can GuidePath do?"
curl -X POST http://127.0.0.1:8000/detect -F "image=@photo.jpg"
curl -X POST http://127.0.0.1:8000/reason -F "image=@photo.jpg" -F "question=Is the tactile path blocked?"
```

Detection returns `detections` (ID, class, confidence and `[x1,y1,x2,y2]` pixel box), image size after EXIF rotation, timing, thresholds and `model_inference: true`. Timing includes first model load on the initial call; measure warm inference separately if reporting latency.

Reasoning returns intent, detector-called flag, answer, status, supporting overlap pairs when relevant, and `llm_used` / `llm_status`. `no_obstruction_detected` means no supported overlap was detected, not that a path is safe. Counts are detections, not guarantees of true counts.

| Check | Expected behavior |
|---|---|
| Capability question without image | 200; no detector or LLM call |
| Unsupported safety/clearance question | 200; explicit limitation, no detector |
| Visual question without image | 422 |
| Invalid image bytes | 400 |
| Upload over 10 MiB or decoded image over 20 MP | 413 |
| Valid image but missing checkpoint | 503; no fabricated detections |
| Configured provider returns invalid evidence | Deterministic fallback with explicit LLM status |
| `/demo/*` | Labelled synthetic fixtures; `model_inference: false` |

The checked-in `outputs/examples` are actual responses from software fixture endpoints, not trained-model predictions. Save real `/detect` and `/reason` JSON under `outputs/real` after connecting the checkpoint and provider. Never place API keys in screenshots, notebooks or response artifacts.
