import json
import pytest
from fastapi.testclient import TestClient
from guidepath import api,llm
from guidepath.examples import scenarios
from guidepath.reasoning import answer

def test_three_fixtures_labelled_and_different():
    data=scenarios()
    assert [d['result']['status'] for d in data]==['possible_obstruction','no_obstruction_detected','insufficient_information']
    assert all(d['model_inference'] is False and d['input_kind']=='synthetic_fixture' for d in data)

def test_demo_question_never_calls_model(monkeypatch):
    monkeypatch.setattr(api,'get_model',lambda:pytest.fail('Demo must not load detector'))
    r=TestClient(api.app).post('/demo/reason',data={'scenario':'overlap','question':'How many bicycles?'})
    assert r.status_code==200
    assert r.json()['result']['counts']['bicycle']==1
    assert r.json()['model_inference'] is False
    assert r.json()['result']['detector_called'] is False

def test_invalid_demo_id():
    assert TestClient(api.app).post('/demo/reason',data={'scenario':'bad','question':'How many bicycles?'}).status_code==404

def test_static_home_and_assets():
    client=TestClient(api.app)
    assert '3D explanation' in client.get('/').text
    assert client.get('/static/app.js').status_code==200

def test_location_and_weak_presence():
    assert answer('Where is the tactile paving?',scenarios()[0]['detections'])['intent']=='location'
    assert answer('Is there tactile paving?',scenarios()[2]['detections'])['status']=='insufficient_information'

def test_llm_fact_ledger_and_validation():
    ds=scenarios()[0]['detections'];r=answer('Is the path blocked?',ds)
    facts=llm.facts_for('Is the path blocked?',r,ds)
    assert '51.1%' in facts['overlap:1:0']
    plan={'conclusion':r['status'],'fact_ids':['overlap:1:0'],'caveat_ids':['geometry']}
    assert '51.1%' in llm.render_plan(plan,facts,r)
    for change in ({'conclusion':'safe'},{'fact_ids':['invented']},{'fact_ids':[]},{'caveat_ids':['safe_to_walk']}):
        with pytest.raises(ValueError):llm.render_plan({**plan,**change},facts,r)

def test_llm_provider_roundtrip_with_mock(monkeypatch):
    for k,v in {'LLM_API_URL':'https://example.invalid/chat','LLM_API_KEY':'mock-only','LLM_MODEL':'mock'}.items():monkeypatch.setenv(k,v)
    ds=scenarios()[0]['detections'];r=answer('How many bicycles?',ds)
    class Response:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def read(self,*a):return json.dumps({'choices':[{'message':{'content':json.dumps({'conclusion':'answered','fact_ids':['count:bicycle'],'caveat_ids':['coverage']})}}]}).encode()
    def request(req,**kwargs):
        assert 'count:bicycle' in req.data.decode()
        return Response()
    monkeypatch.setattr(llm,'urlopen',request)
    result=llm.enrich('How many bicycles?',r,ds)
    assert result['llm_used'] and 'bicycle: 1' in result['answer']
