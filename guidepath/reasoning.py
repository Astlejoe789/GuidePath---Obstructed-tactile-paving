"""Image-plane evidence only. Thresholds are provisional until validated."""
from collections import Counter
import re
CLASSES = ["tactile_paving", "bicycle", "motorcycle"]
ALIASES = {"tactile_paving": ["tactile paving", "tactile path", "paving"],
           "bicycle": ["bicycle", "bicycles", "bike", "bikes"],
           "motorcycle": ["motorcycle", "motorcycles", "motorbike", "motorbikes"]}
DEFAULT = {"confidence": 0.45, "candidate_floor": 0.15, "overlap": 0.10}

def route(question):
    q = " ".join(question.lower().split())
    if q in ("hi", "hello", "help") or any(x in q for x in ["what can you", "what can guidepath", "capabilities", "how do you work", "what is guidepath"]):
        return "capabilities", None
    if any(x in q for x in ["safe", "clearance", "metres", "meters", "navigate", "walk through", "helmet", "dogs", "people", "person", "pedestrian", "car ", "cars", "barrier", "boxes", "pole"]):
        return "unsupported", None
    if re.search(r"\b(blocked|blocking|obstruct|obstructed|obstruction|obstacles?|clear)\b", q):
        return "obstruction", None
    if any(x in q for x in ["is there", "are there", "can you see", "where is", "where are"]):
        found = [c for c, terms in ALIASES.items()
                 if any(re.search(r"\b" + re.escape(t) + r"\b", q) for t in terms)]
        if len(found) == 1:
            return ("location" if q.startswith("where") else "presence"), found[0]
        return "unsupported", None
    if "most common" in q:
        return "most_common", None
    if "how many" in q or re.search(r"\bcount\b", q):
        found = [c for c, terms in ALIASES.items()
                 if any(re.search(r"\b" + re.escape(t) + r"\b", q) for t in terms)]
        if len(found) == 1:
            return "count", found[0]
        if "objects" in q and not found:
            return "count", None
        return "unsupported", None
    if any(x in q for x in ["what objects", "list objects", "what is visible", "what do you detect"]):
        return "list", None
    return "unsupported", None

def intersection(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))

def area(a):
    return max(0,a[2]-a[0])*max(0,a[3]-a[1])

def assess(detections, config=None):
    cfg = config or DEFAULT
    strong = [d for d in detections if d["confidence"] >= cfg["confidence"]]
    weak = [d for d in detections if cfg["candidate_floor"] <= d["confidence"] < cfg["confidence"]]
    paving = [d for d in strong if d["class"] == "tactile_paving"]
    obstacles = [d for d in strong if d["class"] in CLASSES[1:]]
    evidence=[]
    for o in obstacles:
        for p in paving:
            ratio=intersection(o["box"],p["box"])/max(area(o["box"]),1e-9)
            if ratio >= cfg["overlap"]:
                evidence.append({"obstacle_id":o["id"], "paving_id":p["id"],
                                 "overlap_fraction_of_obstacle_box":round(ratio,4)})
    # An accepted overlap is a review candidate even if other detections are weak.
    if not paving:
        status="insufficient_information"
        text="Insufficient information: tactile paving was not detected confidently."
    elif evidence:
        status="possible_obstruction"
        n=len({e["obstacle_id"] for e in evidence})
        text=f"{n} detected bicycle/motorcycle object(s) overlap a tactile-paving box and may obstruct it."
    elif any(d["class"] in CLASSES for d in weak):
        status="insufficient_information"
        text="Insufficient information: low-confidence detections make the visible assessment uncertain."
    else:
        status="no_obstruction_detected"
        text="No supported bicycle or motorcycle obstruction was detected on the visible paving."
    return {"status":status,"evidence":evidence,"answer":text,
            "limitation":"Bounding-box overlap does not establish physical blockage, clearance, or route safety. Other obstacle classes are unsupported."}

def answer(question, detections, config=None):
    cfg=config or DEFAULT
    intent,target=route(question)
    if intent=="capabilities":
        return {"intent":intent,"detector_called":False,"status":"answered",
                "answer":"GuidePath detects tactile paving, bicycles and motorcycles, counts supported detections, and flags possible image-plane overlap."}
    if intent=="unsupported":
        return {"intent":intent,"detector_called":False,"status":"insufficient_information",
                "answer":"Insufficient information or unsupported question. Ask about supported object counts or possible tactile-paving obstructions; I cannot establish route safety or physical clearance."}
    if intent=="obstruction":
        return {"intent":intent,"detector_called":True,**assess(detections,cfg)}
    strong=[d for d in detections if d["confidence"]>=cfg["confidence"]]
    counts=Counter(d["class"] for d in strong)
    if not strong:
        return {"intent":intent,"detector_called":True,"status":"insufficient_information",
                "answer":"Insufficient information: no supported objects were detected confidently.","counts":{}}
    if target and any(d["class"] == target and cfg["candidate_floor"] <= d["confidence"] < cfg["confidence"] for d in detections):
        return {"intent":intent,"detector_called":True,"status":"insufficient_information", "counts":dict(counts),
                "answer":"Insufficient information: weak target detections make this class-specific answer uncertain."}
    if intent=="count":
        n=counts[target] if target else sum(counts.values())
        text=f"I detected {n} {target or 'supported object'} instance(s) above the configured threshold. This is a detection count, not proof of the true count."
    elif intent=="presence":
        text=(f"I detected {counts[target]} {target} instance(s)." if counts[target] else
              f"No {target} was detected above the threshold. This does not prove absence.")
    elif intent=="location":
        selected=[d for d in strong if d["class"]==target]
        text=("Detected image-plane locations: "+"; ".join(f"ID {d['id']}: {d['box']}" for d in selected)
              if selected else f"No confident {target} location is available.")
    elif intent=="most_common":
        n=max(counts.values()); names=sorted(k for k,v in counts.items() if v==n)
        text=f"Most common detected class(es): {', '.join(names)}; {n} detection(s) each."
    else:
        text="Supported detections: "+", ".join(f"{k}: {v}" for k,v in sorted(counts.items()))+"."
    return {"intent":intent,"detector_called":True,"status":"answered","counts":dict(counts),"answer":text}
