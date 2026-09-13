# Verification report — current package

- **29 software tests passed** in Python 3.12.14. See `outputs/verification/pytest.txt` and `environment.json`.
- Tests include routing, uncertainty, overlap boundaries, supported counts, class confusion/ties, image errors, missing weights, mocked LLM plans and rejection, VOC boundary conversion, duplicate/group leakage and explicit cleanup provenance.
- Tests use synthetic detections/images and a mocked provider where appropriate. They do not establish model accuracy or live LLM behavior.
- Six actual Chromium screenshots were captured from the running FastAPI UI. Browser interactions checked fixture switching, a count question, 3D controls, missing-weight handling and mobile rendering. See `browser_checks.json`.
- Python sources and every notebook code cell compile. GPU training and the full Colab notebook were not executed here.
- Both PDF reports were rendered and visually checked; the technical memo remains two pages.
- One dependency deprecation warning comes from Starlette's anyio alias; tests pass.
- No trained checkpoint, measured detector performance, live LLM call, Docker build, public deployment or actual model failure cases were verified in this environment.

Training writes a separate resolved pip-freeze and hardware/configuration record in the actual GPU runtime. These development versions are not a claim that GPU training was verified with them.
