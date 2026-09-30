"""
SurakshaVision AI - Backend Test Suite
Tests PPE Detector, Safety Auditor, Multilingual Siren, Camera Manager & API routes.
"""

import sys
import io
from pathlib import Path
import cv2

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_tests():
    print("=== Testing SurakshaVision AI Backend Engines ===")

    # 1. Test PPE Detector on Zone A
    print("[1/5] Testing IndustrialPPEDetector (Zone A: Compliant)...")
    from backend.engines.ppe_detector import IndustrialPPEDetector
    detector = IndustrialPPEDetector()
    img_a = cv2.imread(str(PROJECT_ROOT / "data" / "cctv_feeds" / "feed_zone_a_compliant.jpg"))
    res_a = detector.analyze_frame(img_a, "zone_a")
    assert res_a["safety_score_percentage"] == 100.0
    assert len(res_a["detections"]) == 2
    print(f"  -> Zone A Safety Score: {res_a['safety_score_percentage']}%, Workers: {res_a['total_workers']}")

    # 2. Test PPE Detector on Zone B (Helmet Violation)
    print("[2/5] Testing IndustrialPPEDetector (Zone B: Violation)...")
    img_b = cv2.imread(str(PROJECT_ROOT / "data" / "cctv_feeds" / "feed_zone_b_violation.jpg"))
    res_b = detector.analyze_frame(img_b, "zone_b")
    assert len(res_b["violations"]) > 0
    print(f"  -> Zone B Violations Detected: {len(res_b['violations'])}, Alert: {res_b['alerts'][0]}")

    # 3. Test Safety Auditor Engine
    print("[3/5] Testing SafetyAuditorEngine...")
    from backend.engines.safety_auditor import SafetyAuditorEngine
    auditor = SafetyAuditorEngine()
    audit_report = auditor.generate_shift_audit_report("JSW Steel Works")
    assert audit_report["metrics"]["overall_shift_safety_score"] > 80
    assert len(audit_report["incidents"]) == 3
    print(f"  -> Audit ID: {audit_report['report_id']}, Shift Score: {audit_report['metrics']['overall_shift_safety_score']}%")

    # 4. Test Multilingual Siren in 8 Indian Languages
    print("[4/5] Testing MultilingualSirenEngine in 8 languages...")
    from backend.engines.multilingual_siren import MultilingualSirenEngine
    siren = MultilingualSirenEngine()
    for lang in ["te", "hi", "en", "ta", "mr", "kn", "or", "as"]:
        alert = siren.get_alert_speech("helmet_violation", lang=lang)
        assert "audio_base64" in alert
        print(f"  -> Siren generated in {alert['language_name']} ({alert['native_name']})")

    # 5. Test FastAPI App routes
    print("[5/5] Testing FastAPI App initialization...")
    from backend.main import app
    assert len(app.routes) >= 6
    print(f"  -> FastAPI App operational with {len(app.routes)} routes!")

    print("\n>>> ALL SURAKSHAVISION BACKEND TESTS PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    run_tests()
