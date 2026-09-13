# Example output provenance

The three `*_fixture.json` files are actual responses from `/demo/scenarios`, computed from authored synthetic detections. They contain no trained-model output. `capabilities_response.json` is an actual `/reason` response to a non-visual capability question; it skips detection and the LLM.

Expected fixture states: overlap → possible_obstruction; beside → no_obstruction_detected; uncertain → insufficient_information. These demonstrate software behavior, not detector accuracy. Real inference outputs belong in `outputs/real` after training.
