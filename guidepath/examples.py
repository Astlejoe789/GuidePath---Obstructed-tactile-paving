"""Synthetic structured fixtures for UI/software demonstrations, NEVER model results."""
from guidepath.reasoning import answer, DEFAULT

def scenarios():
    def det(i,name,box,confidence):return {'id':i,'class':name,'box':box,'confidence':confidence}
    paving=det(0,'tactile_paving',[280,30,420,410],.91)
    examples=[
      ('overlap','Possible overlap',[paving,det(1,'bicycle',[305,150,530,310],.87)]),
      ('beside','Bicycle beside paving',[paving,det(1,'bicycle',[450,150,675,310],.87)]),
      ('uncertain','Weak paving signal',[det(0,'tactile_paving',[280,30,420,410],.25),det(1,'bicycle',[305,150,530,310],.87)])]
    out=[]
    for id,title,ds in examples:
        result=answer('Is the tactile path blocked?',ds)
        out.append({'id':id,'title':title,'input_kind':'synthetic_fixture','model_inference':False,
          'label':'Illustrative fixture — not a trained-model prediction',
          'image_size':{'width':720,'height':440},'detections':ds,
          'thresholds':DEFAULT,'result':{**result,'detector_called':False,'would_call_detector':True,
          'llm_used':False,'llm_status':'demo_not_called','synthesis_mode':'deterministic_fixture'}})
    return out
