"""
SurakshaVision AI - Multilingual Industrial Siren & Voice Alert Engine
Synthesizes real-time factory floor spoken safety sirens and hazard alarms in 8 Indian Languages.
"""

import hashlib
import base64
from pathlib import Path
from gtts import gTTS

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIO_CACHE_DIR = BASE_DIR / "data" / "audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 8 Indian Languages configuration
LANG_CONFIG = {
    "te": {"name": "Telugu", "gtts": "te", "native": "తెలుగు"},
    "hi": {"name": "Hindi", "gtts": "hi", "native": "हिन्दी"},
    "en": {"name": "English", "gtts": "en", "native": "English"},
    "ta": {"name": "Tamil", "gtts": "ta", "native": "தமிழ்"},
    "mr": {"name": "Marathi", "gtts": "mr", "native": "मराठी"},
    "kn": {"name": "Kannada", "gtts": "kn", "native": "ಕನ್ನಡ"},
    "or": {"name": "Odia", "gtts": "hi", "native": "ଓଡ଼ିଆ"},
    "as": {"name": "Assamese", "gtts": "bn", "native": "অসমীয়া"}
}

SAFETY_ALERTS = {
    "helmet_violation": {
        "en": "Warning: Worker in Zone B is not wearing a safety helmet. Please equip hard hat immediately.",
        "hi": "चेतावनी: जोन बी में कर्मचारी ने सुरक्षा हेलमेट नहीं पहना है। कृपया तुरंत हेलमेट पहनें।",
        "te": "హెచ్చరిక: జోన్ బి లో కార్మికుడు సేఫ్టీ హెల్మెట్ ధరించలేదు. దయచేసి వెంటనే హెల్మెట్ ధరించండి.",
        "ta": "எச்சரிக்கை: மண்டலம் பி-யில் உள்ள தொழிலாளி பாதுகாப்பு தலைக்கவசம் அணியவில்லை. உடனே அணியவும்.",
        "mr": "इशारा: झोन बी मधील कामगाराने सेफ्टी हेल्मेट घातलेले नाही. कृपया ताबडतोब हेल्मेट घाला.",
        "kn": "ಎಚ್ಚರಿಕೆ: ವಲಯ ಬಿ ಯಲ್ಲಿರುವ ಕಾರ್ಮಿಕರು ಸುರಕ್ಷತಾ ಹೆಲ್ಮೆಟ್ ಧರಿಸಿಲ್ಲ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ಹೆಲ್ಮೆಟ್ ಧರಿಸಿ.",
        "or": "ଚେତାବନୀ: ଜୋନ ବି ରେ ଥିବା କର୍ମଚାରୀ ହେଲମେଟ ପିନ୍ଧି ନାହାଁନ୍ତି। ଦୟାକରି ତୁରନ୍ତ ହେଲମେଟ ପିନ୍ଧନ୍ତୁ।",
        "as": "সতৰ্কবাণী: জ'ন বি-ৰ কৰ্মীজনে সুৰক্ষা হেলমেট পিন্ধা নাই। অনুগ্ৰহ কৰি ততালিকে হেলমেট পিন্ধক।"
    },
    "danger_zone": {
        "en": "Danger: Unauthorized worker intrusion detected inside Chemical Hazard Red Zone. Evacuate immediately!",
        "hi": "खतरा: रासायनिक लाल खतरे के क्षेत्र में अनधिकृत प्रवेश! कृपया तुरंत बाहर निकलें!",
        "te": "ప్రమాదం: రసాయన ఎరుపు ప్రమాదకర జోన్ లోకి అనుమతి లేని ప్రవేశం గుర్తించబడింది. వెంటనే బయటకు రండి!",
        "ta": "ஆபத்து: ரசாயன அபாய சிவப்பு மண்டலத்திற்குள் அத்துமீறல்! உடனே வெளியேறவும்!",
        "mr": "धोका: रासायनिक धोक्याच्या लाल क्षेत्रात अनधिकृत प्रवेश! त्वरित बाहेर पडा!",
        "kn": "ಅಪಾಯ: ರಾಸಾಯನಿಕ ಅಪಾಯದ ಕೆಂಪು ವಲಯದೊಳಗೆ ಅನಧಿಕೃತ ಪ್ರವೇಶ! ತಕ್ಷಣ ಹೊರಬನ್ನಿ!",
        "or": "ବିପଦ: ରାସାୟନିକ ଲାଲ ବିପଦପୂର୍ଣ୍ଣ ଅଞ୍ଚଳ ଭିତରକୁ ଅନଧିକୃତ ପ୍ରବେଶ! ତୁରନ୍ତ ବାହାରି ଯାଆନ୍ତୁ!",
        "as": "বিপদ: ৰাসায়নিক ৰঙা বিপজ্জনক অঞ্চলৰ ভিতৰত অনুপ্ৰৱেশ! অনুগ্ৰহ কৰি ততালিকে ওলাই আহক!"
    },
    "worker_down": {
        "en": "Emergency: Worker down detected in Zone D logistics bay. Medical response team dispatched.",
        "hi": "आपातकाल: जोन डी में कर्मचारी के गिरने की घटना! चिकित्सा दल को सूचित कर दिया गया है।",
        "te": "అత్యవసరం: జోన్ డి లో కార్మికుడు కింద పడిపోయినట్లు గుర్తించబడింది. వైద్య బృందం బయలుదేరింది.",
        "ta": "அவசரம்: மண்டலம் டி-யில் தொழிலாளி கீழே விழுந்துள்ளார்! மருத்துவக் குழு விரைந்துள்ளது.",
        "mr": "आणीबाणी: झोन डी मध्ये कामगार खाली पडल्याची घटना! वैद्यकीय पथकाला पाचारण केले आहे.",
        "kn": "ತುರ್ತು ಪರಿಸ್ಥಿತಿ: ವಲಯ ಡಿ ಯಲ್ಲಿ ಕಾರ್ಮಿಕರು ಬಿದ್ದಿರುವುದು ಪತ್ತೆಯಾಗಿದೆ! ವೈದ್ಯಕೀಯ ತಂಡ ಹೊರಟಿದೆ.",
        "or": "ଜରୁରୀକାଳୀନ: ଜୋନ ଡି ରେ କର୍ମଚାରୀ ଖସି ପଡ଼ିଥିବା ଚିହ୍ନଟ ହୋଇଛି! ଡାକ୍ତରୀ ଦଳକୁ ଖବର ଦିଆଯାଇଛି।",
        "as": "জৰুৰীকালীন: জ'ন ডি-ত কৰ্মী পিছলি পৰা ঘটনা চিনাক্ত! চিকিৎসা দলক খবৰ দিয়া হৈছে।"
    }
}

class MultilingualSirenEngine:
    def __init__(self):
        pass

    def get_alert_speech(self, alert_key: str = "helmet_violation", lang: str = "te") -> dict:
        """Synthesizes high-priority emergency siren announcement in worker's native language."""
        # Whitelist input parameters
        clean_alert_key = alert_key if alert_key in SAFETY_ALERTS else "helmet_violation"
        clean_lang = lang if lang in LANG_CONFIG else "te"
        gtts_lang = LANG_CONFIG[clean_lang]["gtts"]

        alert_dict = SAFETY_ALERTS[clean_alert_key]
        text = alert_dict.get(clean_lang, alert_dict["en"])

        # Cache key using SHA-256 for secure deterministic caching
        cache_key = hashlib.sha256(f"siren_{clean_lang}_{clean_alert_key}".encode("utf-8")).hexdigest()[:32]
        cache_file = AUDIO_CACHE_DIR / f"{cache_key}.mp3"

        if not cache_file.exists():
            try:
                tts = gTTS(text=text, lang=gtts_lang, tld="co.in", timeout=3.5)
                tts.save(str(cache_file))
            except Exception as err:
                try:
                    # Fallback to English
                    tts = gTTS(text=alert_dict["en"], lang="en", tld="co.in", timeout=3.5)
                    tts.save(str(cache_file))
                except Exception as fallback_err:
                    # Look for any existing cached mp3 file as safety fallback
                    existing = list(AUDIO_CACHE_DIR.glob("*.mp3"))
                    if existing:
                        cache_file = existing[0]

        audio_bytes = b""
        if cache_file.exists():
            with open(cache_file, "rb") as f:
                audio_bytes = f.read()

        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

        return {
            "alert_key": clean_alert_key,
            "lang": clean_lang,
            "language": LANG_CONFIG[clean_lang]["name"],
            "language_name": LANG_CONFIG[clean_lang]["name"],
            "native_name": LANG_CONFIG[clean_lang]["native"],
            "spoken_text": text,
            "alert_text": text,
            "audio_base64": f"data:audio/mp3;base64,{b64_audio}",
            "audio_url": f"data:audio/mp3;base64,{b64_audio}"
        }
