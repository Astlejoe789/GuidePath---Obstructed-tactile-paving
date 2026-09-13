"""Evidence inventory, not a quality score. Exit 2 if mandatory files are absent."""
import json
from pathlib import Path

def main():
    checks={
      'trained_checkpoint':Path('weights/best.pt').is_file(),
      'checkpoint_manifest':Path('weights/model_manifest.json').is_file(),
      'real_detector_metrics':any(Path('outputs/real').glob('**/summary.json')),
      'final_dataset_audit':Path('outputs/real/audit.json').is_file(),
      'real_api_response':Path('outputs/real/reason_response.json').is_file(),
      'observed_failures':Path('outputs/real/failure_review.md').is_file()}
    print(json.dumps({'checks':checks,'scope':'File presence only; manually verify contents and provenance.','complete':all(checks.values())},indent=2))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
