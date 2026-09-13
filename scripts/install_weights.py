"""Install YOUR trusted fine-tuned checkpoint, verify classes, record SHA256."""
import argparse,hashlib,json,shutil
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--sha256');a=p.parse_args()
    source=Path(a.source).resolve()
    if not source.is_file():raise SystemExit('Checkpoint not found.')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if a.sha256 and digest!=a.sha256:raise SystemExit('Checksum mismatch.')
    from ultralytics import RTDETR
    from guidepath.reasoning import CLASSES
    m=RTDETR(str(source))
    if [m.names[i] for i in range(len(m.names))]!=CLASSES:raise SystemExit('Checkpoint class mapping mismatch.')
    out=Path('weights/best.pt');out.parent.mkdir(exist_ok=True)
    if source!=out.resolve():
        if out.exists():raise SystemExit('weights/best.pt exists. Preserve or move it before replacing.')
        shutil.copy2(source,out)
    Path('weights/model_manifest.json').write_text(json.dumps({'sha256':digest,'class_names':CLASSES,
         'installed_path':'weights/best.pt','model_type':'RT-DETR','accuracy':'Not measured by this installation check'},indent=2))
    print('Installed trained checkpoint. SHA256:',digest)
if __name__=='__main__':main()
