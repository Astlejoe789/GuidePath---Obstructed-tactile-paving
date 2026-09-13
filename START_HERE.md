# Start here — ASTLE JOE A S

1. Extract the archive and open the inner `guidepath` folder in VS Code or a terminal.
2. Follow the first three commands in README to install UI dependencies and start the server.
3. Open http://127.0.0.1:8000. Compare the three demo cases and try the 3D controls.
4. Run `python -m pip install -r requirements-dev.txt` and `python -m pytest -q`.
5. To complete the assignment, recover or train your RT-DETR checkpoint with `GuidePath_Colab.ipynb`. Copy your `best.pt` through `scripts.install_weights`, then evaluate and collect real failure cases.
6. Configure the LLM in `.env`, upload a real image and save its answer JSON. Check `model_inference: true` and `llm_used: true`.
7. Read `docs/GITHUB_UPLOAD.md` to publish to your own repository. Put large weights in a GitHub Release and record the download URL and SHA-256.

**What you can demonstrate now:** interface, evidence rules, explicit uncertainty, API routing, mocked provider validation, interactive explanatory 3D.
**What is not supplied:** a verified final model, real performance scores or a deployed service. A polished document is supporting evidence, not a substitute for these deliverables.
