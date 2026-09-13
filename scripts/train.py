"""Fine-tune or resume RT-DETR. Use --project on mounted Drive for durable outputs."""
import argparse, hashlib, json, platform, subprocess, sys, time
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data',required=True);p.add_argument('--epochs',type=int,default=30)
    p.add_argument('--batch',type=int,default=4);p.add_argument('--imgsz',type=int,default=640)
    p.add_argument('--device',default='0');p.add_argument('--workers',type=int,default=2)
    p.add_argument('--name',default='baseline');p.add_argument('--seed',type=int,default=42)
    p.add_argument('--project',default='runs/detect');p.add_argument('--resume',help='Your interrupted run last.pt')
    a=p.parse_args()
    import torch
    from ultralytics import RTDETR
    data=Path(a.data).resolve();audit=json.loads((data.parent/'audit.json').read_text())
    if audit['blocking_issues']:raise SystemExit('Resolve all audit blocking issues before training.')
    if a.resume:
        checkpoint=Path(a.resume).resolve()
        if not checkpoint.is_file():raise SystemExit('Resume checkpoint not found.')
        run=checkpoint.parent.parent
        cfg=dict(resume=True,data=str(data),device=a.device,batch=a.batch)
        model=RTDETR(str(checkpoint))
    else:
        run=Path(a.project).resolve()/a.name
        if run.exists():raise SystemExit('Run exists. Resume last.pt or use a NEW --name.')
        run.mkdir(parents=True)
        cfg=dict(data=str(data),epochs=a.epochs,batch=a.batch,imgsz=a.imgsz,device=a.device,
                 workers=a.workers,seed=a.seed,deterministic=False,project=str(run.parent),name=run.name,
                 exist_ok=True,save=True,save_period=-1)
        model=RTDETR('rtdetr-l.pt')
    metadata={'status':'started','config':cfg,'python':platform.python_version(),'torch':torch.__version__,
       'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
       'dataset_manifest_sha256':hashlib.sha256((data.parent/'manifest.json').read_bytes()).hexdigest(),
       'resume_from':a.resume,'note':'Fixed seed does not guarantee bitwise deterministic RT-DETR CUDA training.'}
    suffix=('resume_'+str(time.time_ns())) if a.resume else 'environment'
    meta_path=run/(suffix+'.json')
    meta_path.write_text(json.dumps(metadata,indent=2))
    (run/(suffix+'_pip-freeze.txt')).write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
    print('Output directory:',run,flush=True)
    print('Use a mounted Drive --project path to survive runtime deletion.',flush=True)
    start=time.perf_counter()
    try:
        model.train(**cfg);metadata['status']='completed'
    except BaseException:
        metadata['status']='interrupted_or_failed';raise
    finally:
        metadata['training_seconds_this_session']=time.perf_counter()-start
        meta_path.write_text(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
