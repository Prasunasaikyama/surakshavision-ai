# SurakshaVision AI - System Architecture & Technical Specification

## 1. Architectural Topology Overview

SurakshaVision AI operates as an on-premise, edge-first Computer Vision Command Center. The system ingests standard industrial CCTV RTSP camera streams, runs frame decoding and deep learning safety models on an edge device (NVIDIA Jetson, Intel NUC, or on-premise GPU workstation), and serves a low-latency web dashboard with real-time audio siren broadcasting and automated ISO 45001 EHS shift reports.

```
+-----------------------------------------------------------------------------------+
|                           INDUSTRIAL PLANT FLOOR (ZONE A-D)                      |
|                                                                                   |
|  [CAM-01: Assembly]   [CAM-02: Press]   [CAM-03: Reactor]   [CAM-04: Logistics]  |
+--------------------------+-------------------+------------------+-----------------+
                           | RTSP / TCP-IP (H.264/H.265)          |
                           v                                      v
+-----------------------------------------------------------------------------------+
|                        SURAKSHAVISION AI EDGE ENGINE CORE                         |
|                                                                                   |
|  1. OpenCV Video Capture & Frame Buffer Pool (30 FPS Ring Buffer)                 |
|  2. YOLOv8 / Contour Person Detector (Human Bounding Box Proposals)               |
|  3. Anatomical RoI Slicer (Head RoI = Upper 28%, Torso RoI = Middle 50%)          |
|  4. Multi-Spectrum PPE Classifier (ANSI Hard Hats & ISO Hi-Vis Vests)             |
|  5. Polygon Ray-Casting Geofence Engine (Restricted Danger Zone Interlocking)     |
|  6. Kinematic Aspect-Ratio Fall Detector (Worker Down / Slip-Trip Interception)   |
+--------------------------+--------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------------------------------+
|                           FASTAPI ASYNCHRONOUS BACKEND                            |
|                                                                                   |
|  • /api/health          - System liveness, standards, and active camera count     |
|  • /api/cctv/cameras    - Multi-camera inventory, zone telemetry, and hazard tier  |
|  • /api/cctv/inspect    - Deep frame inference, bounding box overlay, base64 img |
|  • /api/cctv/siren      - Spoken emergency siren synthesizer (8 Indian Languages)  |
|  • /api/safety/audit    - Certified ISO 45001 & OSHA 1910 Shift Report Generator  |
+--------------------------+--------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------------------------------+
|                       CLIENT INDUSTRIAL COMMAND DASHBOARD                         |
|                                                                                   |
|  • Step 1: Zone Camera Selector (Dynamic Cam Cards with Telemetry Badges)         |
|  • Step 2: Live CCTV Inspection & Multilingual Siren Alarm (Telugu, Hindi, etc.)  |
|  • Step 3: ISO 45001 Shift Safety Audit Certificate (Print-Ready EHS Card)        |
|  • Accurate Geolocation: Centroid Distance Matching (Telangana Centroid Lock)     |
+-----------------------------------------------------------------------------------+
```

---

## 2. API Contract Specification

### 2.1 Health Check
- **Endpoint:** `GET /api/health`
- **Response:**
```json
{
  "status": "healthy",
  "app_name": "SurakshaVision AI (सुरक्षाविजन AI)",
  "version": "1.0.0",
  "supported_languages": { ... },
  "standards": ["ISO 45001:2018", "OSHA 29 CFR 1910", "Factories Act 1948 (India)"],
  "active_cameras": 4
}
```

### 2.2 Get Active CCTV Feeds
- **Endpoint:** `GET /api/cctv/cameras`
- **Response:**
```json
[
  {
    "id": 1,
    "cam_code": "CAM-01",
    "name": "Zone A: Component Assembly Line",
    "location": "Zone A: Component Assembly Line",
    "hazard_level": "Compliant",
    "fps": 30.0,
    "resolution": "1920x1080",
    "description": "Assembly line active. Workers properly equipped with Hard Hats and Hi-Vis Vests."
  },
  ...
]
```

### 2.3 Inspect Camera Feed Frame
- **Endpoint:** `POST /api/cctv/inspect`
- **Payload:** Form-data (`cam_id`: int, optional `file`: binary image)
- **Response:**
```json
{
  "zone_id": "zone_a",
  "workers_detected": 2,
  "compliant_workers": 2,
  "helmets_detected": 2,
  "vests_detected": 2,
  "compliance_score": 100,
  "violations": [],
  "alerts": [],
  "annotated_image": "data:image/jpeg;base64,...",
  "camera_metadata": { ... }
}
```

### 2.4 Trigger Multilingual Emergency Siren
- **Endpoint:** `POST /api/cctv/siren`
- **Payload:**
```json
{
  "alert_key": "helmet_violation",
  "lang": "te"
}
```
- **Response:**
```json
{
  "alert_key": "helmet_violation",
  "lang": "te",
  "language": "Telugu",
  "native_name": "తెలుగు",
  "alert_text": "హెచ్చరిక: హెల్మెట్ లేదా రక్షణ దుస్తులు ధరించలేదు. దయచేసి వెంటనే భద్రతా నిబంధనలను పాటించండి.",
  "audio_url": "data:audio/mp3;base64,..."
}
```

### 2.5 Generate ISO 45001 Shift Audit Report
- **Endpoint:** `GET /api/safety/audit`
- **Response:**
```json
{
  "report_id": "SVR-EHS-20260927-004",
  "shift_id": "SHIFT-B-20260927",
  "plant_name": "Suraksha Industrial Works - Unit 4, Hyderabad",
  "audit_timestamp": "2026-09-27 15:00:00",
  "ehs_officer": "Dr. K. Srinivas Rao (Safety Director)",
  "shift_compliance_score": 94,
  "total_workers_scanned": 28,
  "incidents_recorded": 3,
  "incidents": [ ... ],
  "status": "CONDITIONALLY CERTIFIED - 3 CORRECTIVE ACTIONS IMPLEMENTED"
}
```

---

## 3. Client Localization & Geolocation System

### Indian State Centroid Matching Algorithm
The client determines regional language preference without third-party cloud trackers using Euclidean nearest-neighbor centroid matching:
$$\arg\min_{i} \left( (lat_{user} - lat_i)^2 + (lon_{user} - lon_i)^2 \right)$$

Supported States and Languages:
- **Telangana ($17.3850^\circ\text{ N}, 78.4867^\circ\text{ E}$):** Telugu (`te`)
- **Andhra Pradesh ($16.5062^\circ\text{ N}, 80.6480^\circ\text{ E}$):** Telugu (`te`)
- **Karnataka ($12.9716^\circ\text{ N}, 77.5946^\circ\text{ E}$):** Kannada (`kn`)
- **Tamil Nadu ($13.0827^\circ\text{ N}, 80.2707^\circ\text{ E}$):** Tamil (`ta`)
- **Maharashtra ($19.7515^\circ\text{ N}, 75.7139^\circ\text{ E}$):** Marathi (`mr`)
- **Odisha ($20.2961^\circ\text{ N}, 85.8245^\circ\text{ E}$):** Odia (`or`)
- **Assam ($26.1445^\circ\text{ N}, 91.7362^\circ\text{ E}$):** Assamese (`as`)
- **North India ($28.6139^\circ\text{ N}, 77.2090^\circ\text{ E}$):** Hindi (`hi`)

Manual dropdown controls allow instant user override with real-time UI re-rendering.
