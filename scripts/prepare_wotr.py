"""Convert official VOC splits, preserving provenance and auditing exact leakage.
Optional CSV columns: image_id,split,group. Use for a manually reviewed group split.
Near duplicates still require visual/location review; exact hashes do not certify independence.
"""
import argparse, csv, hashlib, json, shutil
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image
import yaml
from guidepath.reasoning import CLASSES
ALIASES={'blind_road':'tactile_paving','tactile_paving':'tactile_paving',
         'bicycle':'bicycle','motorcycle':'motorcycle'}

def prepare(source,output,split_csv=None):
    source=Path(source);out=Path(output)
    if out.exists(): raise ValueError('Output already exists; choose a fresh directory.')
    entries=[]; issues=[]; groups={}
    image_index={}
    for path in (source/'JPEGImages').iterdir():
        if path.suffix.lower() in ('.jpg','.jpeg','.png'):
            image_index.setdefault(path.stem,[]).append(path)
    if split_csv:
        for r in csv.DictReader(open(split_csv,newline='')):
            if r['split'] not in ('train','val','test') or not r['group'].strip():
                raise ValueError('Each row needs train/val/test and a nonempty group.')
            entries.append((r['image_id'],r['split'],r['group']))
    else:
        for split in ('train','val','test'):
            for line in (source/'ImageSets'/'Main'/f'{split}.txt').read_text().splitlines():
                if line.strip(): entries.append((line.split()[0],split,None))
    out.mkdir(parents=True)
    rows=[];seen_ids={};seen_hash={};counts={s:Counter() for s in ('train','val','test')}
    for image_id,split,group in entries:
        if Path(image_id).name!=image_id: raise ValueError('Image IDs must be basenames.')
        if image_id in seen_ids:
            issues.append(f'Duplicate image ID {image_id}: {seen_ids[image_id]} and {split}')
            continue
        seen_ids[image_id]=split
        if group:
            if group in groups and groups[group]!=split: issues.append(f'Group crosses splits: {group}')
            groups[group]=split
        xml=source/'Annotations'/f'{image_id}.xml'
        tree=ET.parse(xml).getroot()
        candidates=image_index.get(image_id,[])
        if len(candidates)!=1: raise ValueError(f'Expected exactly one image for {image_id}')
        img_path=candidates[0]
        with Image.open(img_path) as im:
            rgb=im.convert('RGB');w,h=rgb.size
            digest=hashlib.sha256(f'{w}x{h}'.encode()+rgb.tobytes()).hexdigest()
        xml_w=int(tree.findtext('size/width'));xml_h=int(tree.findtext('size/height'))
        if (w,h)!=(xml_w,xml_h): issues.append(f'Image/XML size mismatch: {image_id}')
        if digest in seen_hash:
            old_id,old_split=seen_hash[digest]
            issues.append(f'Exact duplicate pixels: {old_id} ({old_split}), {image_id} ({split})')
        seen_hash[digest]=(image_id,split)
        labels=[];difficult=0
        for obj in tree.findall('object'):
            name=ALIASES.get(obj.findtext('name','').strip())
            if name is None: continue
            difficult+=int(obj.findtext('difficult','0'))
            b=obj.find('bndbox')
            # VOC is 1-based inclusive: convert left/top to zero-based boundaries.
            x1=float(b.findtext('xmin'))-1;y1=float(b.findtext('ymin'))-1
            x2=float(b.findtext('xmax'));y2=float(b.findtext('ymax'))
            if not (0<=x1<x2<=w and 0<=y1<y2<=h):
                issues.append(f'Invalid selected-class box: {image_id}');continue
            labels.append(f'{CLASSES.index(name)} {(x1+x2)/2/w:.8f} {(y1+y2)/2/h:.8f} {(x2-x1)/w:.8f} {(y2-y1)/h:.8f}')
            counts[split][name]+=1
        ip=out/'images'/split/(image_id+img_path.suffix.lower());lp=out/'labels'/split/(image_id+'.txt')
        ip.parent.mkdir(parents=True,exist_ok=True);lp.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(img_path,ip);lp.write_text('\n'.join(labels)+'\n' if labels else '')
        rows.append({'image_id':image_id,'split':split,'group':group,'sha256_pixels':digest,
                     'image':str(ip.resolve()),'selected_instances':len(labels),'difficult_included':difficult})
    for split in counts:
        if not any(r['split']==split for r in rows): issues.append(f'Empty split: {split}')
        for name in CLASSES:
            if counts[split][name]==0: issues.append(f'No {name} annotations in {split}')
    audit={'source':'https://github.com/kxzr/WOTR','classes':CLASSES,'counts':counts,
           'images_per_split':dict(Counter(r['split'] for r in rows)),
           'negative_images':dict(Counter(r['split'] for r in rows if not r['selected_instances'])),
           'blocking_issues':issues,'group_manifest_supplied':bool(split_csv),
           'warnings':['Near-duplicate and location leakage require manual review.',
                       'Selected difficult objects are included rather than silently ignored.',
                       'Verify dataset terms separately from the repository code licence.',
                       'Images without selected classes are retained as background.']}
    (out/'manifest.json').write_text(json.dumps(rows,indent=2))
    (out/'audit.json').write_text(json.dumps(audit,indent=2))
    (out/'data.yaml').write_text(yaml.safe_dump({'path':str(out.resolve()),'train':'images/train',
         'val':'images/val','test':'images/test','names':dict(enumerate(CLASSES))},sort_keys=False))
    return audit
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    p.add_argument('--split-csv');a=p.parse_args();result=prepare(a.source,a.output,a.split_csv)
    print(json.dumps(result,indent=2))
    if result['blocking_issues']: raise SystemExit(2)
