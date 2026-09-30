"""
SurakshaVision AI - 1-Click Production Server Launcher
Real-Time Industrial Safety Vision, PPE Compliance & Hazard Prevention
Port: 8002
"""

import os
import sys
import webbrowser
import threading
import time
import uvicorn

PORT = int(os.environ.get("PORT", 8002))
HOST = os.environ.get("HOST", "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1")
IS_HEADLESS = bool(os.environ.get("RENDER") or os.environ.get("HEADLESS"))

def open_browser():
    if not IS_HEADLESS:
        time.sleep(1.5)
        try:
            webbrowser.open(f"http://127.0.0.1:{PORT}")
        except Exception:
            pass

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 72)
    print(" 🛡️  SurakshaVision AI (सुरक्षाविजन AI) - Industrial Safety Vision")
    print("    Standard: ISO 45001:2018 | OSHA 29 CFR 1910 | Factories Act 1948")
    print("    Local Languages: Telugu, Hindi, English, Tamil, Marathi, Kannada, Odia, Assamese")
    print("    Offline Edge AI: Zero Cloud API Dependencies")
    print("=" * 72)
    print(f" 🚀 Launching server at: http://{HOST}:{PORT}")
    print("=" * 72)

    # Launch browser automatically if interactive desktop
    if not IS_HEADLESS:
        threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI server
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)
