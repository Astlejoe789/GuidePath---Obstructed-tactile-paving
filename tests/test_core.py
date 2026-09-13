import io,json
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from guidepath import api,llm
from guidepath.reasoning import answer,assess,route

def d(i,name,box,confidence=.9):return {'id':i,'class':name,'box':box,'confidence':confidence}
paving=d(0,'tactile_paving',[0,0,100,100])

def test_missing_paving_abstains():assert assess([d(1,'bicycle',[0,0,20,20])])['status']=='insufficient_information'
def test_overlap_flags():assert assess([paving,d(1,'bicycle',[10,10,30,30])])['status']=='possible_obstruction'
def test_beside_not_flagged():assert assess([paving,d(1,'bicycle',[110,0,150,30])])['status']=='no_obstruction_detected'
def test_weak_obstacle_abstains():assert assess([paving,d(1,'bicycle',[10,10,30,30],.25)])['status']=='insufficient_information'
def test_shared_border_not_overlap():assert assess([paving,d(1,'motorcycle',[100,0,150,30])])['status']=='no_obstruction_detected'
def test_duplicate_paving_does_not_double_count():
    r=assess([paving,d(2,'tactile_paving',[0,0,90,90]),d(1,'bicycle',[10,10,30,30])]);assert r['answer'].startswith('1 ')
def test_unsupported_class():assert route('How many dogs are there?')[0]=='unsupported'
def test_ambiguous_count():assert route('How many bicycles and motorcycles?')[0]=='unsupported'
def test_safety_abstains():assert route('Is it safe to walk through?')[0]=='unsupported'
def test_count_is_detection_count():assert 'detected 1' in answer('How many bicycles?', [d(1,'bicycle',[0,0,10,10])])['answer']
def test_tie():assert 'bicycle, motorcycle' in answer('Most common object?', [d(1,'bicycle',[0,0,10,10]),d(2,'motorcycle',[0,0,10,10])])['answer']

@pytest.fixture
def client():return TestClient(api.app)
def image_bytes():
    b=io.BytesIO();Image.new('RGB',(10,10)).save(b,format='PNG');return b.getvalue()
def test_capabilities_skips_detector(client,monkeypatch):
    def fail(_):raise AssertionError('Detector should not be called')
    monkeypatch.setattr(api,'detect_image',fail)
    r=client.post('/reason',data={'question':'What can GuidePath do?'});assert r.status_code==200 and not r.json()['detector_called']
def test_missing_image(client):assert client.post('/reason',data={'question':'Is the path blocked?'}).status_code==422
def test_bad_image(client):assert client.post('/detect',files={'image':('x.jpg',b'bad','image/jpeg')}).status_code==400
def test_missing_weights(client,monkeypatch):
    monkeypatch.setenv('GUIDEPATH_WEIGHTS','/missing/weights.pt');monkeypatch.setattr(api,'_model',None)
    assert client.post('/detect',files={'image':('x.png',image_bytes(),'image/png')}).status_code==503
def test_reason_with_injected_detections(client,monkeypatch):
    monkeypatch.setattr(api,'detect_image',lambda _: {'detections':[paving,d(1,'bicycle',[10,10,30,30])]})
    monkeypatch.delenv('LLM_API_KEY',raising=False)
    r=client.post('/reason',data={'question':'Is the path blocked?'},files={'image':('x.png',image_bytes(),'image/png')})
    assert r.status_code==200 and r.json()['status']=='possible_obstruction' and not r.json()['llm_used']
def test_llm_rejects_invented_ids(monkeypatch):
    for k in ['LLM_API_URL','LLM_API_KEY','LLM_MODEL']:monkeypatch.setenv(k,'https://example.invalid')
    class Response:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return json.dumps({'choices':[{'message':{'content':'{"caveat_ids":["safe_to_walk"]}'}}]}).encode()
    monkeypatch.setattr(llm,'urlopen',lambda *a,**kw:Response())
    r=llm.enrich('Is it clear?',{'answer':'Original evidence.','status':'possible_obstruction'});assert r['answer']=='Original evidence.' and not r['llm_used']
def test_llm_valid_output(monkeypatch):
    for k in ['LLM_API_URL','LLM_API_KEY','LLM_MODEL']:monkeypatch.setenv(k,'https://example.invalid')
    class Response:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return json.dumps({'choices':[{'message':{'content':'{"conclusion":"possible_obstruction","fact_ids":[],"caveat_ids":["geometry"]}'}}]}).encode()
    monkeypatch.setattr(llm,'urlopen',lambda *a,**kw:Response())
    assert llm.enrich('Is it blocked?',{'answer':'Possible overlap.','status':'possible_obstruction'})['llm_used']
