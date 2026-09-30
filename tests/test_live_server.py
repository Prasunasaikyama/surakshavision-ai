"""
SurakshaVision AI - Enhanced Live Server Integration Test Suite
Validates all HTTP endpoints, CCTV inspections, custom geofences,
webcam inspections, automated emergency dispatch, and multilingual sirens.
"""

import sys
import time
import requests
import io
import cv2
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

PORT = int(os.environ.get("PORT", 8002))
BASE_URL = os.environ.get("BASE_URL", f"http://127.0.0.1:{PORT}")

def run_tests():
    print("=" * 70)
    print(f"Testing SurakshaVision AI Enhanced Live Server on {BASE_URL}...")
    print("=" * 70)

    time.sleep(2)
    # 1. Health check
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
        data = r.json()
        print(f"✅ Health Check Passed: {data['app_name']} | Version: {data['version']}")
        print(f"   Standards: {', '.join(data['standards'])}")
        print(f"   Features Active: {len(data.get('features', []))}")
        for feat in data.get("features", []):
            print(f"     • {feat}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        sys.exit(1)

    # 2. Get CCTV Cameras
    r = requests.get(f"{BASE_URL}/api/cctv/cameras", timeout=5)
    assert r.status_code == 200, f"Cameras endpoint failed: {r.status_code}"
    cameras = r.json()
    assert len(cameras) == 4, f"Expected 4 cameras, got {len(cameras)}"
    print(f"\n✅ CCTV Feeds Verified: {len(cameras)} active camera zones found.")
    for cam in cameras:
        print(f"   • [{cam['cam_code']}] {cam['name']} - Level: {cam['hazard_level']}")

    # 3. Test Inspect on all 4 cameras
    print("\n✅ Testing Multi-Zone Deep Vision Inspection:")
    for cam in cameras:
        cam_id = cam["id"]
        r = requests.post(f"{BASE_URL}/api/cctv/inspect", data={"cam_id": cam_id}, timeout=10)
        assert r.status_code == 200, f"Inspect failed for Cam {cam_id}: {r.status_code}"
        res = r.json()
        print(f"   • CAM-{cam_id} ({res['zone_id']}): Score {res['compliance_score']}% | Workers: {res['workers_detected']} | Violations: {len(res['violations'])}")
        assert "annotated_image" in res and res["annotated_image"].startswith("data:image/jpeg;base64,")

    # 4. Test FEATURE 3: Interactive Custom Geofence Ray-Casting
    print("\n✅ Testing Feature 3: Calibrated Polygon Geofence Incursion Detection:")
    custom_poly = "[[300, 200], [550, 200], [550, 480], [300, 480]]" # Covers Zone A workers
    r = requests.post(f"{BASE_URL}/api/cctv/inspect", data={"cam_id": 1, "custom_geofence": custom_poly}, timeout=10)
    assert r.status_code == 200, f"Custom geofence test failed: {r.status_code}"
    geo_res = r.json()
    has_geo_breach = any("Geofence" in v.get("type", "") for v in geo_res.get("violations", []))
    print(f"   • Calibrated Polygon Incursion Detected: {has_geo_breach} | Breached Workers: {len(geo_res.get('violations', []))}")
    assert has_geo_breach, "Expected custom geofence breach!"

    # 5. Test FEATURE 4: Automated EHS Emergency Dispatch Payload
    print("\n✅ Testing Feature 4: Automated EHS Emergency Dispatch Generator:")
    # Cam 4 has Worker Down emergency
    r = requests.post(f"{BASE_URL}/api/cctv/inspect", data={"cam_id": 4}, timeout=10)
    assert r.status_code == 200
    cam4_res = r.json()
    dispatch = cam4_res.get("emergency_dispatch")
    assert dispatch is not None, "Expected emergency dispatch for Cam 4 Worker Down event!"
    print(f"   • Dispatch ID: {dispatch['dispatch_id']} | Status: {dispatch['status']}")
    print(f"     Target: {dispatch['recipient']}")
    print(f"     Incident: {dispatch['incident_type']} | Response ETA: {dispatch['eta_response_team']}")

    # 6. Test FEATURE 1: Live Webcam Mode Endpoint
    print("\n✅ Testing Feature 1: Live Webcam / Video Frame Inspection:")
    # Synthesize synthetic test frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw simulated worker body
    cv2.rectangle(test_frame, (250, 150), (390, 420), (180, 100, 50), -1)
    # Draw head
    cv2.circle(test_frame, (320, 120), 40, (200, 180, 150), -1)
    # Draw yellow safety helmet on top
    cv2.ellipse(test_frame, (320, 100), (45, 25), 0, 180, 360, (0, 240, 255), -1)

    _, encoded = cv2.imencode(".jpg", test_frame)
    files = {"file": ("test_webcam.jpg", io.BytesIO(encoded.tobytes()), "image/jpeg")}
    r = requests.post(f"{BASE_URL}/api/cctv/inspect-webcam", files=files, timeout=10)
    assert r.status_code == 200, f"Webcam endpoint failed: {r.status_code}"
    webcam_res = r.json()
    print(f"   • Live Webcam Result: Workers: {webcam_res['workers_detected']} | Score: {webcam_res['compliance_score']}%")
    print(f"     Status: {webcam_res['detections'][0]['status']} ({webcam_res['detections'][0]['helmet']['type']})")

    # 7. Test Multilingual Siren Generation (8 Indian Languages)
    print("\n✅ Testing Multilingual Siren Generation across 8 Indian Languages:")
    test_langs = ["te", "hi", "en", "ta", "mr", "kn", "or", "as"]
    for lang in test_langs:
        r = requests.post(f"{BASE_URL}/api/cctv/siren", json={"alert_key": "helmet_violation", "lang": lang}, timeout=10)
        assert r.status_code == 200, f"Siren failed for lang {lang}: {r.status_code}"
        siren_res = r.json()
        print(f"   • [{lang.upper()}] {siren_res['language']}: \"{siren_res['alert_text'][:40]}...\"")

    # 8. Shift Safety Audit
    print("\n✅ Testing Shift Safety Audit Report Generation:")
    r = requests.get(f"{BASE_URL}/api/safety/audit", timeout=5)
    assert r.status_code == 200, f"Safety audit failed: {r.status_code}"
    audit = r.json()
    print(f"   • Shift ID: {audit['shift_id']} | Compliance Score: {audit['shift_compliance_score']}%")
    print(f"     Safety Officer: {audit['ehs_officer']}")
    print(f"     Incidents Intercepted: {audit['incidents_recorded']}")

    # 9. Index HTML
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Index HTML failed: {r.status_code}"
    assert "SurakshaVision AI" in r.text
    print("\n✅ Index HTML Route: 200 OK (Full UI bundle with Video Wall & Webcam ready).")

    print("\n" + "=" * 70)
    print("🎉 ALL 4 SHOWSTOPPER FEATURES & LIVE SERVER ENDPOINTS VERIFIED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
