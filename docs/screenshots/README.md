# Screenshot provenance

These are real browser captures of the running interface, not generated renderings or trained-model results.

1. `01_review_workspace.png`: synthetic overlap fixture with computed 51.1% obstacle-box overlap.
2. `02_beside_paving.png`: synthetic bicycle beside paving, no accepted overlap.
3. `03_uncertainty.png`: weak paving fixture, insufficient information.
4. `04_interactive_3d.png`: conceptual Canvas 3D view with rotation/movement controls; no real depth estimate.
5. `05_missing_weights_guardrail.png`: a real upload of the supplied Colab screenshot receives an explicit missing-checkpoint error. This is API/UI error evidence, not a street detection result.
6. `06_mobile.png`: responsive demo layout at 390 pixels wide.

Reproduce after starting the API on port 8000:

```bash
npm install --no-save playwright
npx playwright install chromium
node scripts/capture_ui.cjs
```

This optional capture dependency is not required to run the app. Captures overwrite these screenshot files. Install outputs in `node_modules` are git-ignored.
