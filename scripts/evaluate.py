import argparse, json, hashlib
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument("--weights",required=True);p.add_argument("--data",required=True)
    p.add_argument("--split",choices=["val","test"],default="test");p.add_argument("--device",default="0")
    p.add_argument("--name",default="final_test");a=p.parse_args()
    from ultralytics import RTDETR
    model=RTDETR(a.weights)
    out=Path("runs/evaluation")/a.name
    if out.exists(): raise SystemExit("Use a new --name; do not overwrite evaluation evidence.")
    result=model.val(data=a.data,split=a.split,device=a.device,plots=True,save_json=True,
                     project="runs/evaluation",name=a.name)
    per_class = {}
    for j, class_id in enumerate(result.box.ap_class_index):
        per_class[model.names[int(class_id)]] = {"precision": float(result.box.p[j]), "recall": float(result.box.r[j]), "map50": float(result.box.ap50[j]), "map50_95": float(result.box.ap[j])}
    summary={"weights_sha256":hashlib.sha256(Path(a.weights).read_bytes()).hexdigest(),"per_class":per_class,"split":a.split,"weights":a.weights,"metrics":result.results_dict,
             "per_class_map50_95":{model.names[i]:float(v) for i,v in enumerate(result.box.maps)},
             "note":"Ultralytics per-class maps may use aggregate fallback for classes without targets; consult audit counts."}
    (Path(result.save_dir)/"summary.json").write_text(json.dumps(summary,indent=2))
if __name__=="__main__": main()
