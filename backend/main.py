"""
SurakshaVision AI - Main FastAPI Application Server
Real-Time Industrial Safety Vision, PPE Compliance Monitoring & Workplace Hazard Prevention.
"""

import os
import cv2
import json
import numpy as np
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.engines.ppe_detector import IndustrialPPEDetector
from backend.engines.safety_auditor import SafetyAuditorEngine
from backend.engines.multilingual_siren import MultilingualSirenEngine, LANG_CONFIG
from backend.engines.multi_camera_manager import MultiCameraManager

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
DATA_DIR = BASE_DIR / "data"

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB payload protection limit

app = FastAPI(
    title="SurakshaVision AI API",
    description="Real-Time Computer Vision for Industrial Safety, PPE Compliance & Hazard Prevention",
    version="1.0.0"
)

# Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=*, microphone=*"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

async def read_and_validate_image(file: UploadFile) -> np.ndarray:
    """Safely reads, validates size and decodes an uploaded image frame."""
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Uploaded image exceeds 10MB payload limit.")
    if len(contents) < 16:
        raise HTTPException(status_code=400, detail="Empty or invalid image file uploaded.")
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Corrupted image: unable to decode into BGR frame.")
    return img_bgr

def safe_parse_geofence(custom_geofence_str: Optional[str]) -> Optional[List[List[int]]]:
    """Validates and parses custom polygonal geofence vertices safely."""
    if not custom_geofence_str:
        return None
    try:
        pts = json.loads(custom_geofence_str)
        if isinstance(pts, list) and len(pts) >= 3:
            cleaned = []
            for p in pts:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    cleaned.append([int(p[0]), int(p[1])])
            return cleaned if len(cleaned) >= 3 else None
    except Exception:
        return None
    return None

# Engine Singletons
ppe_detector = IndustrialPPEDetector()
safety_auditor = SafetyAuditorEngine()
siren_engine = MultilingualSirenEngine()
camera_manager = MultiCameraManager()

class SirenRequest(BaseModel):
    alert_key: str = "helmet_violation"
    lang: str = "te"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>SurakshaVision AI is running.</h1>")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": "SurakshaVision AI (सुरक्षाविजन AI)",
        "version": "1.0.0",
        "supported_languages": LANG_CONFIG,
        "standards": ["ISO 45001:2018", "OSHA 29 CFR 1910", "Factories Act 1948 (India)"],
        "active_cameras": len(camera_manager.get_all_cameras()),
        "features": [
            "Real-Time PPE Inspection (Helmets & Hi-Vis Vests)",
            "Dynamic 4-Camera Video Wall (SCADA Control Room Grid)",
            "Interactive Calibrated Polygon Geofence Exclusion Zones",
            "Live Laptop Webcam / Mobile Video AI Testing Mode",
            "8 Indian Languages Acoustic Emergency Siren Alerts",
            "Automated EHS Emergency SMS/LoRaWAN Dispatch Simulator",
            "Certified ISO 45001 & OSHA 1910 Shift Audit Cards"
        ]
    }

@app.get("/api/cctv/cameras")
async def get_cctv_cameras():
    """Returns list of active CCTV cameras with telemetry and hazard states."""
    return camera_manager.get_all_cameras()

@app.post("/api/cctv/inspect")
async def inspect_cctv_frame(
    cam_id: Optional[int] = Form(1),
    file: Optional[UploadFile] = File(None),
    custom_geofence: Optional[str] = Form(None),
    zone_id: Optional[str] = Form(None)
):
    """
    Inspects a camera feed for PPE compliance, danger zone intrusions,
    custom exclusion geofences, and slips/falls.
    """
    cam_info = camera_manager.get_camera_by_id(cam_id or 1)
    zone_key = zone_id or (cam_info["zone_key"] if cam_info else "zone_a")

    img_bgr = None
    if file:
        img_bgr = await read_and_validate_image(file)
    else:
        sample_path = DATA_DIR / "cctv_feeds" / cam_info["feed_file"]
        if sample_path.exists():
            img_bgr = cv2.imread(str(sample_path))

    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Unable to load camera feed frame.")

    geofence_pts = safe_parse_geofence(custom_geofence)

    analysis = ppe_detector.analyze_frame(img_bgr, zone_id=zone_key, custom_geofence=geofence_pts)
    analysis["camera_metadata"] = cam_info
    return analysis

@app.post("/api/cctv/inspect-webcam")
async def inspect_webcam_frame(
    file: UploadFile = File(...),
    custom_geofence: Optional[str] = Form(None)
):
    """
    Inspects live user webcam video stream for hard hats, hi-vis vests, posture, and falls.
    """
    img_bgr = await read_and_validate_image(file)
    geofence_pts = safe_parse_geofence(custom_geofence)

    analysis = ppe_detector.analyze_frame(img_bgr, zone_id="webcam", custom_geofence=geofence_pts)
    analysis["camera_metadata"] = {
        "id": 0,
        "cam_code": "LIVE-WEBCAM",
        "name": "Live Examiner / Field Webcam Inspection",
        "location": "Local Inspection Workspace",
        "hazard_level": "Live Edge Stream",
        "fps": 30.0,
        "resolution": f"{img_bgr.shape[1]}x{img_bgr.shape[0]}"
    }
    return analysis

@app.post("/api/cctv/siren")
async def trigger_safety_siren(req: SirenRequest):
    """Synthesizes high-priority factory floor voice alarm in worker's native language."""
    res = siren_engine.get_alert_speech(req.alert_key, req.lang or "te")
    return res

@app.get("/api/safety/audit")
async def get_safety_audit():
    """Generates certified ISO 45001 / OSHA 1910 Shift Safety Compliance Report."""
    return safety_auditor.generate_shift_audit_report()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
