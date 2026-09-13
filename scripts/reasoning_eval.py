"""Evaluate cached REAL detections against manually labelled image assessments.
Input JSON list: {image_id, split, truth, detections}. No invented observations.
Tune on val; use the same thresholds on test. Compare overlap rules with an
'always flag when both paving and an obstacle exist' baseline.
"""
import argparse,json
from collections import Counter
from pathlib import Path
from guidepath.reasoning import assess,DEFAULT,CLASSES

def evaluate(rows,cfg):
    confusion=Counter();baseline=Counter();total=len(rows);abstain=0
    for r in rows:
        truth=r['truth'];pred=assess(r['detections'],cfg)['status']
        if truth not in ('possible_obstruction','no_obstruction_detected','insufficient_information'):
            raise ValueError('Invalid truth label')
        confusion[(truth,pred)]+=1;abstain+=pred=='insufficient_information'
        strong=[d for d in r['detections'] if d['confidence']>=cfg['confidence']]
        names={d['class'] for d in strong}
        b=('insufficient_information' if CLASSES[0] not in names else
           'possible_obstruction' if names.intersection(CLASSES[1:]) else 'no_obstruction_detected')
        baseline[(truth,b)]+=1
    def summarize(c):
        positive='possible_obstruction';negative='no_obstruction_detected'
        tp=c[(positive,positive)];fp=c[(negative,positive)];fn=c[(positive,negative)]+c[(positive,'insufficient_information')]
        return {'confusion':[{'truth':t,'predicted':p,'count':n} for (t,p),n in sorted(c.items())],
                'precision_on_decidable_truth':tp/(tp+fp) if tp+fp else None,
                'recall_abstentions_count_as_misses':tp/(tp+fn) if tp+fn else None}
    return {'n':total,'thresholds':cfg,'abstention_rate':abstain/total if total else None,
            'spatial_rule':summarize(confusion),'cooccurrence_baseline':summarize(baseline)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    p.add_argument('--split',choices=['val','test'],required=True);p.add_argument('--config');a=p.parse_args()
    rows=json.loads(Path(a.input).read_text())
    if not rows or any(r['split']!=a.split for r in rows): raise SystemExit('Use a nonempty single-split file.')
    cfg={**DEFAULT,**(json.loads(Path(a.config).read_text()) if a.config else {})}
    Path(a.output).write_text(json.dumps(evaluate(rows,cfg),indent=2))
