import io, json, logging, os, threading, time, warnings
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()
from guidepath.reasoning import CLASSES, DEFAULT, route, answer
from guidepath.llm import enrich
app=FastAPI(title="GuidePath",version="0.2.0",description="Research prototype: image-plane obstruction candidates only.")
log=logging.getLogger("guidepath")
logging.basicConfig(level=logging.INFO)
_model=None
_lock=threading.Lock()
CONFIG=dict(DEFAULT)
if os.getenv("GUIDEPATH_CONFIG"):
    CONFIG.update(json.loads(Path(os.environ["GUIDEPATH_CONFIG"]).read_text()))
if not 0 < CONFIG["candidate_floor"] < CONFIG["confidence"] < 1 or not 0 < CONFIG["overlap"] <= 1:
    raise ValueError("Invalid GuidePath thresholds")

def get_model():
    global _model
    if _model is None:
        path=Path(os.getenv("GUIDEPATH_WEIGHTS","weights/best.pt"))
        if not path.is_file():
            raise HTTPException(503,"Trained weights are missing. Run training and set GUIDEPATH_WEIGHTS.")
        try:
            from ultralytics import RTDETR
        except ImportError:
            raise HTTPException(503,"Install requirements.txt to enable real inference.")
        try:
            candidate=RTDETR(str(path))
        except Exception:
            raise HTTPException(503,"The checkpoint could not be loaded. Verify its format and training environment.")
        names=[candidate.names[i] for i in range(len(candidate.names))]
        if names!=CLASSES:
            raise HTTPException(503,"Checkpoint classes do not match the GuidePath dataset.")
        _model=candidate
    return _model

def decode(upload):
    raw=upload.file.read(10*1024*1024+1)
    if len(raw)>10*1024*1024:
        raise HTTPException(413,"Maximum image upload is 10 MiB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error",Image.DecompressionBombWarning)
            img=Image.open(io.BytesIO(raw))
            if img.width*img.height>20_000_000:
                raise HTTPException(413,"Maximum decoded image size is 20 megapixels.")
            img=ImageOps.exif_transpose(img).convert("RGB")
            img.load()
            return img
    except HTTPException:
        raise
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError,Image.DecompressionBombWarning):
        raise HTTPException(400,"Upload a valid supported image.")

def detect_image(img):
    start=time.perf_counter()
    with _lock:
        model=get_model()
        r=model.predict(img,conf=CONFIG["candidate_floor"],imgsz=int(os.getenv("GUIDEPATH_IMGSZ","640")),device=os.getenv("GUIDEPATH_DEVICE","cpu"),verbose=False)[0]
    ds=[]
    for i,b in enumerate(r.boxes):
        ds.append({"id":i,"class":model.names[int(b.cls.item())],
                   "confidence":round(float(b.conf.item()),6),
                   "box":[round(float(v),2) for v in b.xyxy[0].tolist()]})
    elapsed=round(1000*(time.perf_counter()-start),2)
    log.info("inference_ms=%s detections=%s",elapsed,len(ds))
    return {"image_size":{"width":img.width,"height":img.height},"box_format":"xyxy_pixels_after_exif_rotation",
            "detections":ds,"inference_ms":elapsed,"thresholds":CONFIG,"input_kind":"uploaded_image","model_inference":True}

@app.get("/health")
def health():
    return {"status":"ok","weights_present":Path(os.getenv("GUIDEPATH_WEIGHTS","weights/best.pt")).is_file(),
            "model_loaded":_model is not None,"llm_configured":all(os.getenv(x) for x in ("LLM_API_URL","LLM_API_KEY","LLM_MODEL"))}

@app.post("/detect")
def detect(image:UploadFile=File(...)):
    return detect_image(decode(image))

@app.post("/reason")
def reason(question:str=Form(...,min_length=1,max_length=1000),image:UploadFile|None=File(None)):
    intent,_=route(question)
    if intent in ("capabilities","unsupported"):
        return {**answer(question,[]),"llm_used":False,"llm_status":"not_needed"}
    if image is None:
        raise HTTPException(422,"This question requires an image.")
    result=detect_image(decode(image))
    return {**enrich(question,answer(question,result["detections"],CONFIG),result["detections"],CONFIG),**result}


STATIC=Path(__file__).parent/'static'
app.mount('/static', StaticFiles(directory=str(STATIC)), name='static')

@app.get('/', include_in_schema=False)
def home():
    return FileResponse(STATIC/'index.html')

@app.get('/demo/scenarios', tags=['Illustrative demo'])
def demo_scenarios():
    from guidepath.examples import scenarios
    return scenarios()

@app.post('/demo/reason', tags=['Illustrative demo'])
def demo_reason(scenario:str=Form(...), question:str=Form(...,min_length=1,max_length=1000)):
    from guidepath.examples import scenarios
    item=next((x for x in scenarios() if x['id']==scenario),None)
    if item is None:raise HTTPException(404,'Unknown demo scenario')
    result=answer(question,item['detections'])
    return {**item, 'result':{**result,'would_call_detector':result['detector_called'],
        'detector_called':False,'llm_used':False,'llm_status':'demo_not_called',
        'synthesis_mode':'deterministic_fixture'}}
