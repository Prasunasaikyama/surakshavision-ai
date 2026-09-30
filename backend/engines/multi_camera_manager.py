"""
SurakshaVision AI - Multi-Camera CCTV Stream & Zone Manager
Coordinates simulated CCTV feeds, stream telemetry, camera switching, and zone risk indicators.
"""

from typing import Dict, List, Any

class MultiCameraManager:
    def __init__(self):
        self.cameras = [
            {
                "id": 1,
                "cam_id": 1,
                "cam_code": "CAM-01",
                "name": "Zone A: Component Assembly Line",
                "location": "Zone A: Component Assembly Line",
                "zone_key": "zone_a",
                "feed_file": "feed_zone_a_compliant.jpg",
                "hazard_level": "Compliant",
                "status": "NORMAL",
                "fps": 30.0,
                "resolution": "1920x1080",
                "description": "Assembly line active. Workers properly equipped with Hard Hats and Hi-Vis Vests.",
                "summary": "Assembly line active. Workers properly equipped with Hard Hats and Hi-Vis Vests."
            },
            {
                "id": 2,
                "cam_id": 2,
                "cam_code": "CAM-02",
                "name": "Zone B: Heavy Hydraulic Press & Robotics",
                "location": "Zone B: Heavy Hydraulic Press & Robotics",
                "zone_key": "zone_b",
                "feed_file": "feed_zone_b_violation.jpg",
                "hazard_level": "Warning",
                "status": "VIOLATION_DETECTED",
                "fps": 29.8,
                "resolution": "1920x1080",
                "description": "Hydraulic press active. Worker detected without mandatory safety helmet.",
                "summary": "Hydraulic press active. Worker detected without mandatory safety helmet."
            },
            {
                "id": 3,
                "cam_id": 3,
                "cam_code": "CAM-03",
                "name": "Zone C: Chemical Storage & Acid Reactor",
                "location": "Zone C: Chemical Storage & Acid Reactor",
                "zone_key": "zone_c",
                "feed_file": "feed_zone_c_danger_zone.jpg",
                "hazard_level": "Danger",
                "status": "DANGER_ZONE_INTRUSION",
                "fps": 30.0,
                "resolution": "1920x1080",
                "description": "Chemical storage perimeter breach! Personnel inside red hazard exclusion geofence.",
                "summary": "Chemical storage perimeter breach! Personnel inside red hazard exclusion geofence."
            },
            {
                "id": 4,
                "cam_id": 4,
                "cam_code": "CAM-04",
                "name": "Zone D: Logistics Bay & High-Bay Storage",
                "location": "Zone D: Logistics Bay & High-Bay Storage",
                "zone_key": "zone_d",
                "feed_file": "feed_zone_d_worker_down.jpg",
                "hazard_level": "Emergency",
                "status": "WORKER_DOWN_EVENT",
                "fps": 30.0,
                "resolution": "1920x1080",
                "description": "High-bay warehouse aisle. Worker down detected with slip/fall profile.",
                "summary": "High-bay warehouse aisle. Worker down detected with slip/fall profile."
            }
        ]

    def get_all_cameras(self) -> List[Dict[str, Any]]:
        return self.cameras

    def get_camera_by_id(self, cam_id: int) -> Dict[str, Any]:
        return next((c for c in self.cameras if c["id"] == cam_id or c["cam_id"] == cam_id), self.cameras[0])
