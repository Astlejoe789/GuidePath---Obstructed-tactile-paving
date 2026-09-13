"""Export annotated images and REAL predictions for manual failure analysis."""
import argparse,json
from pathlib import Path
from PIL import Image
from guidepath.reasoning import DEFAULT,assess
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--weights',required=True);p.add_argument('--images',required=True)
    p.add_argument('--output',required=True);p.add_argument('--split',choices=['val','test'],required=True)
    p.add_argument('--device',default='0');p.add_argument('--limit',type=int,default=0);p.add_argument('--config');a=p.parse_args()
    cfg={**DEFAULT,**(json.loads(Path(a.config).read_text()) if a.config else {})}
    from ultralytics import RTDETR
    m=RTDETR(a.weights);out=Path(a.output)
    out.mkdir(parents=True,exist_ok=False);rows=[]
    for path in sorted(Path(a.images).iterdir()):
        if path.suffix.lower() not in ('.jpg','.jpeg','.png'):continue
        if a.limit and len(rows)>=a.limit:break
        r=m.predict(str(path),conf=cfg['candidate_floor'],device=a.device,verbose=False)[0]
        ds=[{'id':i,'class':m.names[int(b.cls.item())],'confidence':float(b.conf.item()),
             'box':[float(x) for x in b.xyxy[0].tolist()]} for i,b in enumerate(r.boxes)]
        Image.fromarray(r.plot()[...,::-1]).save(out/(path.stem+'.jpg'))
        rows.append({'image_id':path.stem,'split':a.split,'truth':'REQUIRES_MANUAL_LABEL',
                     'detections':ds,'assessment':assess(ds,cfg),'root_cause':'REQUIRES_MANUAL_REVIEW'})
    (out/'cases.json').write_text(json.dumps(rows,indent=2))
