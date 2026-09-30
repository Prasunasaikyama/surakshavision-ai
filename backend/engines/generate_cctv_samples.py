"""
SurakshaVision AI - Industrial CCTV Camera Feed Synthesizer
Generates realistic industrial factory CCTV feeds for PPE compliance, restricted zone intrusion, and worker slip/fall detection.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FEEDS_DIR = BASE_DIR / "data" / "cctv_feeds"
FEEDS_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size=18, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "calibri.ttf", "segoeui.ttf"]
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()

def draw_cctv_telemetry(draw, cam_id, zone_name, w, h):
    # Industrial CCTV overlay header
    time_str = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S.24")
    overlay_font = get_font(16, bold=True)
    draw.text((25, 20), f"CAM-{cam_id:02d} [LIVE]  //  {zone_name.upper()}", fill=(0, 255, 120), font=overlay_font)
    draw.text((w - 280, 20), f"REC ●  {time_str}", fill=(240, 50, 50), font=overlay_font)
    draw.text((25, h - 35), "ISO-45001 EHS SAFETY COMPLIANCE MONITOR  |  FPS: 30.0", fill=(180, 180, 180), font=get_font(13))

def create_zone_a_compliant():
    # Zone A: Assembly Floor - 2 Fully Compliant Workers (Helmet + Vest)
    w, h = 900, 560
    img = Image.new("RGB", (w, h), color=(35, 42, 54)) # Factory floor gray-blue
    draw = ImageDraw.Draw(img)

    # Factory floor lines and machinery background
    draw.line([(0, 360), (w, 360)], fill=(70, 80, 95), width=2)
    # Machinery silhouettes
    draw.rectangle([60, 180, 260, 360], fill=(45, 55, 70), outline=(80, 95, 115), width=2)
    draw.rectangle([640, 150, 840, 360], fill=(45, 55, 70), outline=(80, 95, 115), width=2)
    # Yellow floor safety walkway lines
    draw.line([(0, 480), (w, 480)], fill=(230, 190, 30), width=4)
    draw.line([(0, 420), (w, 420)], fill=(230, 190, 30), width=4)

    # Worker 1 (Left): Fully Compliant
    # Yellow Hard Hat
    draw.ellipse([320, 210, 370, 240], fill=(245, 210, 20), outline=(210, 170, 10), width=2)
    # Face
    draw.ellipse([330, 235, 360, 265], fill=(225, 180, 150))
    # Hi-Vis Orange/Yellow Vest
    draw.rectangle([315, 265, 375, 370], fill=(245, 130, 20), outline=(230, 230, 230), width=2)
    # Silver reflective stripes on vest
    draw.line([(315, 290), (375, 290)], fill=(230, 230, 230), width=3)
    draw.line([(315, 330), (375, 330)], fill=(230, 230, 230), width=3)
    # Pants & Boots
    draw.rectangle([320, 370, 342, 470], fill=(40, 50, 70))
    draw.rectangle([348, 370, 370, 470], fill=(40, 50, 70))
    draw.rectangle([316, 465, 344, 480], fill=(20, 20, 20))
    draw.rectangle([346, 465, 374, 480], fill=(20, 20, 20))

    # Worker 2 (Center-Right): Fully Compliant
    # Hard Hat
    draw.ellipse([500, 220, 545, 248], fill=(245, 210, 20), outline=(210, 170, 10), width=2)
    # Face
    draw.ellipse([510, 243, 538, 270], fill=(215, 170, 140))
    # Hi-Vis Green Vest
    draw.rectangle([495, 270, 550, 375], fill=(50, 205, 50), outline=(230, 230, 230), width=2)
    draw.line([(495, 300), (550, 300)], fill=(230, 230, 230), width=3)
    draw.line([(495, 340), (550, 340)], fill=(230, 230, 230), width=3)
    # Pants
    draw.rectangle([500, 375, 520, 470], fill=(35, 45, 60))
    draw.rectangle([525, 375, 545, 470], fill=(35, 45, 60))

    draw_cctv_telemetry(draw, 1, "Zone A: Component Assembly Line", w, h)
    img.save(FEEDS_DIR / "feed_zone_a_compliant.jpg", quality=92)
    print("Saved feed_zone_a_compliant.jpg")

def create_zone_b_violation():
    # Zone B: Heavy Machinery - Worker Missing Helmet Violation!
    w, h = 900, 560
    img = Image.new("RGB", (w, h), color=(38, 40, 48))
    draw = ImageDraw.Draw(img)

    # Heavy Robotic Arm & Warning Hazard Area
    draw.rectangle([100, 140, 300, 400], fill=(50, 55, 65), outline=(240, 160, 20), width=2)
    draw.text((120, 160), "HYDRAULIC PRESS #4", fill=(240, 160, 20), font=get_font(15, bold=True))
    draw.line([(0, 420), (w, 420)], fill=(70, 75, 85), width=2)

    # Worker (Center): Wearing Vest, but NO HELMET (Hair visible)
    # Dark hair / No Helmet!
    draw.ellipse([460, 210, 505, 245], fill=(30, 25, 25))
    draw.ellipse([465, 235, 500, 265], fill=(225, 175, 140))
    # Hi-Vis Orange Vest
    draw.rectangle([450, 265, 515, 380], fill=(245, 130, 20), outline=(230, 230, 230), width=2)
    draw.line([(450, 300), (515, 300)], fill=(230, 230, 230), width=3)
    # Pants
    draw.rectangle([455, 380, 480, 480], fill=(45, 50, 65))
    draw.rectangle([485, 380, 510, 480], fill=(45, 50, 65))

    # Flashing Warning Sign in Background
    draw.rectangle([620, 180, 840, 260], fill=(180, 20, 20), outline=(255, 255, 255), width=2)
    draw.text((640, 195), "SAFETY HELMET AREA", fill=(255, 255, 255), font=get_font(16, bold=True))
    draw.text((640, 220), "HARD HAT MANDATORY", fill=(255, 230, 50), font=get_font(14, bold=True))

    draw_cctv_telemetry(draw, 2, "Zone B: Heavy Hydraulic Press & Robotics", w, h)
    img.save(FEEDS_DIR / "feed_zone_b_violation.jpg", quality=92)
    print("Saved feed_zone_b_violation.jpg")

def create_zone_c_danger_zone():
    # Zone C: Chemical Storage / High-Voltage Intrusion
    w, h = 900, 560
    img = Image.new("RGB", (w, h), color=(30, 35, 45))
    draw = ImageDraw.Draw(img)

    # Chemical storage tanks
    draw.rectangle([80, 120, 260, 380], fill=(60, 70, 85), outline=(100, 115, 135), width=2)
    draw.text((100, 140), "SULFURIC ACID TANK", fill=(255, 220, 50), font=get_font(14, bold=True))

    # RED EXCLUSION DANGER ZONE on Floor
    draw.rectangle([400, 300, 850, 480], fill=(60, 15, 20), outline=(240, 30, 30), width=4)
    # Diagonal hazard stripes
    for x in range(410, 840, 40):
        draw.line([(x, 300), (x+30, 480)], fill=(200, 20, 20), width=2)
    draw.text((430, 315), "DANGER ZONE: RESTRICTED ENTRY ONLY (HIGH VOLTAGE / ACID)", fill=(255, 80, 80), font=get_font(14, bold=True))

    # Worker walking directly inside the Red Restricted Zone
    # White Helmet
    draw.ellipse([540, 250, 580, 280], fill=(240, 240, 240), outline=(200, 200, 200), width=2)
    draw.ellipse([548, 275, 574, 300], fill=(215, 170, 140))
    # Grey overalls (No high-vis vest)
    draw.rectangle([535, 300, 585, 390], fill=(90, 95, 110))
    draw.rectangle([540, 390, 558, 460], fill=(60, 65, 75))
    draw.rectangle([562, 390, 580, 460], fill=(60, 65, 75))

    draw_cctv_telemetry(draw, 3, "Zone C: Chemical Storage & High-Voltage", w, h)
    img.save(FEEDS_DIR / "feed_zone_c_danger_zone.jpg", quality=92)
    print("Saved feed_zone_c_danger_zone.jpg")

def create_zone_d_worker_down():
    # Zone D: Loading Dock / Warehouse - Worker Fallen / Slip Incident
    w, h = 900, 560
    img = Image.new("RGB", (w, h), color=(32, 38, 48))
    draw = ImageDraw.Draw(img)

    # Warehouse shelving and pallets
    draw.rectangle([80, 100, 340, 350], fill=(50, 60, 75), outline=(90, 105, 125), width=2)
    draw.text((100, 120), "AISLE 4 - HIGH BAY STORAGE", fill=(200, 210, 225), font=get_font(15, bold=True))
    draw.rectangle([600, 120, 850, 320], fill=(50, 60, 75), outline=(90, 105, 125), width=2)

    # Wet floor puddle simulation
    draw.ellipse([420, 410, 620, 460], fill=(25, 45, 65), outline=(60, 110, 160), width=2)
    draw.text((460, 430), "WET FLOOR", fill=(80, 160, 240), font=get_font(12, bold=True))

    # Fallen Worker (Horizontal posture on ground - Slip / Fall)
    # Hard Hat rolled off
    draw.ellipse([340, 430, 380, 460], fill=(245, 210, 20), outline=(200, 160, 10), width=2)
    # Worker head on ground
    draw.ellipse([420, 415, 455, 445], fill=(215, 170, 140))
    # Worker torso horizontal
    draw.rectangle([455, 410, 570, 450], fill=(245, 130, 20), outline=(230, 230, 230), width=2)
    draw.line([(490, 410), (490, 450)], fill=(230, 230, 230), width=3)
    # Legs sprawled
    draw.line([(570, 420), (660, 410)], fill=(45, 55, 75), width=18)
    draw.line([(570, 440), (650, 455)], fill=(45, 55, 75), width=18)

    draw_cctv_telemetry(draw, 4, "Zone D: Logistics Bay & High-Bay Warehouse", w, h)
    img.save(FEEDS_DIR / "feed_zone_d_worker_down.jpg", quality=92)
    print("Saved feed_zone_d_worker_down.jpg")

if __name__ == "__main__":
    create_zone_a_compliant()
    create_zone_b_violation()
    create_zone_c_danger_zone()
    create_zone_d_worker_down()
    print("All industrial CCTV scenarios synthesized successfully!")
