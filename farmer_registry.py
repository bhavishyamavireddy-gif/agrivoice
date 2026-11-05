"""
farmer_registry.py
Caller ID & Rural Farmer Profile Registry for North Andhra.
Maps phone numbers to registered villages, coordinates, crops, and language preferences.
"""

from typing import Dict, Any, Optional

FARMER_DATABASE = {
    "+919848022338": {
        "phone": "+919848022338",
        "name_te": "అప్పారావు",
        "name_en": "Apparao",
        "name_hi": "अप्पाराव",
        "village": "Kasimkota (కాశీంకోట)",
        "mandal": "Anakapalli",
        "district": "Anakapalli (అనకాపల్లి)",
        "latitude": 17.6534,
        "longitude": 82.9856,
        "primary_crop": "sugarcane",
        "crop_name_te": "చెరకు (Sugarcane)",
        "crop_name_en": "Sugarcane",
        "crop_name_hi": "गन्ना (Sugarcane)",
        "preferred_language": "te"
    },
    "+919440112233": {
        "phone": "+919440112233",
        "name_te": "రాజేష్ వర్మ",
        "name_en": "Rajesh Verma",
        "name_hi": "राजेश वर्मा",
        "village": "Pendurthi (పెందుర్తి)",
        "mandal": "Visakhapatnam Rural",
        "district": "Visakhapatnam (విశాఖపట్నం)",
        "latitude": 17.8286,
        "longitude": 83.2039,
        "primary_crop": "paddy",
        "crop_name_te": "వరి (Paddy)",
        "crop_name_en": "Paddy",
        "crop_name_hi": "धान / चावल (Paddy)",
        "preferred_language": "hi"
    },
    "+919866554433": {
        "phone": "+919866554433",
        "name_te": "సత్యనారాయణ",
        "name_en": "K. Satyam",
        "name_hi": "सत्यनारायण",
        "village": "Brahmana Tarla (బ్రాహ్మణ తర్లా)",
        "mandal": "Palasa",
        "district": "Srikakulam (శ్రీకాకుళం)",
        "latitude": 18.7667,
        "longitude": 84.4167,
        "primary_crop": "cashew",
        "crop_name_te": "జీడిమామిడి (Cashew)",
        "crop_name_en": "Cashew",
        "crop_name_hi": "काजू (Cashew)",
        "preferred_language": "te"
    },
    "+919123456789": {
        "phone": "+919123456789",
        "name_te": "జాన్ పీటర్",
        "name_en": "John Peter",
        "name_hi": "जॉन पीटर",
        "village": "Tagarapuvalasa (తగరపువలస)",
        "mandal": "Bheemunipatnam",
        "district": "Visakhapatnam (విశాఖపట్నం)",
        "latitude": 17.9300,
        "longitude": 83.4300,
        "primary_crop": "groundnut",
        "crop_name_te": "వేరుశనగ (Groundnut)",
        "crop_name_en": "Groundnut",
        "crop_name_hi": "मूंगफली (Groundnut)",
        "preferred_language": "en"
    }
}

class FarmerRegistry:
    """Provides Caller-ID lookup for rural feature phone farmers without apps or smartphones."""

    @classmethod
    def get_farmer_profile(cls, phone: str) -> Dict[str, Any]:
        """Looks up caller profile or generates a sensible regional default."""
        # Normalize phone
        clean_phone = phone.strip().replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            if len(clean_phone) == 10:
                clean_phone = "+91" + clean_phone

        if clean_phone in FARMER_DATABASE:
            return FARMER_DATABASE[clean_phone]

        # Default profile for unknown caller in Anakapalli belt
        return {
            "phone": phone,
            "name_te": "రైతు బాంధవుడు",
            "name_en": "Respected Farmer",
            "name_hi": "किसान भाई",
            "village": "Anakapalli Rural (అనకాపల్లి గ్రామీణం)",
            "mandal": "Anakapalli",
            "district": "Anakapalli",
            "latitude": 17.6896,
            "longitude": 83.0033,
            "primary_crop": "sugarcane",
            "crop_name_te": "చెరకు / వరి",
            "crop_name_en": "Sugarcane / Paddy",
            "crop_name_hi": "गन्ना / धान",
            "preferred_language": "te"
        }

    @classmethod
    def list_all_farmers(cls) -> Dict[str, Any]:
        """Returns demo farmers for easy testing on the dashboard."""
        return FARMER_DATABASE
