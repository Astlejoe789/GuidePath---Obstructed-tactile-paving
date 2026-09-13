# Trained checkpoint required

No trained weights were uploaded to this workspace. Put your own fine-tuned RT-DETR `best.pt` here and keep its hash and actual run metadata. The required class order is tactile_paving, bicycle, motorcycle. The server checks class names and returns HTTP 503 when weights are missing; it never substitutes a stock model.

Weight files are ignored by git. Upload them separately as a GitHub Release asset (or another direct public download) and update docs/MODEL_CARD.md with the verified download URL and SHA256. Do not claim completion until a real /detect request succeeds.
