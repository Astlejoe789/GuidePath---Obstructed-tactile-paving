"""Create a fresh converted dataset using explicit exclusions; preserve the original."""
import argparse,csv,json
from pathlib import Path
from scripts.prepare_wotr import prepare

def cleanup(audit_dir,source,output):
    original=Path(audit_dir);out=Path(output)
    if out.exists():raise ValueError('Output exists; choose a new directory.')
    audit=json.loads((original/'audit.json').read_text());rows=json.loads((original/'manifest.json').read_text())
    unknown=[x for x in audit['blocking_issues'] if not x.startswith(('Invalid selected-class box:','Exact duplicate pixels:'))]
    if unknown:raise ValueError(f'Inspect unexpected issues first: {unknown}')
    invalid={x.split(':',1)[1].strip() for x in audit['blocking_issues'] if x.startswith('Invalid selected-class box:')}
    kept=[];removed=[];hashes={};priority={'test':0,'val':1,'train':2}
    for row in sorted(rows,key=lambda r:(priority[r['split']],r['image_id'])):
        reason='invalid_selected_class_box' if row['image_id'] in invalid else 'exact_duplicate' if row['sha256_pixels'] in hashes else None
        if reason:
            removed.append({'image_id':row['image_id'],'split':row['split'],'reason':reason,
                            'retained_duplicate':hashes.get(row['sha256_pixels'])});continue
        hashes[row['sha256_pixels']]=row['image_id'];kept.append(row)
    out.parent.mkdir(parents=True,exist_ok=True)
    splitfile=out.parent/(out.name+'_splits.csv')
    with splitfile.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['image_id','split','group']);writer.writeheader()
        for r in kept:writer.writerow({'image_id':r['image_id'],'split':r['split'],'group':'exact_pixels_'+r['sha256_pixels']})
    result=prepare(source,out,splitfile)
    result['grouping_scope']='exact duplicate pixels only; NOT a location/sequence independence guarantee'
    (out/'audit.json').write_text(json.dumps(result,indent=2))
    (out/'cleanup_report.json').write_text(json.dumps({'before':len(rows),'after':len(kept),'removed':removed,
      'policy':'Exclude invalid images; prefer test then val then train for identical pixels.',
      'limitation':'Near duplicates and location/sequence leakage still need manual review.'},indent=2))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit-dir',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    r=cleanup(a.audit_dir,a.source,a.output);print(json.dumps(r,indent=2))
    if r['blocking_issues']:raise SystemExit(2)
