"""
dialect_processor.py
Trilingual (Telugu, Hindi, English) Speech & Dialect Adaptation Engine.
Features auto-detection of spoken language and semantic mapping for rural agricultural terms.
"""

import re
from typing import Dict, List, Tuple, Any

# Regional phonetic mappings and colloquial vocabulary for North Andhra Telugu
TELUGU_DIALECT_DICTIONARY = {
    # Pronouns & Interrogatives
    "యెట్నున్నావ్": "ఎలా ఉన్నావు",
    "ఎట్టాగ": "ఎలా",
    "ఎట్టా": "ఎలా",
    "ఎట్టాగ ఉంది": "ఎలా ఉంది",
    "ఎట్టాగుంది": "ఎలా ఉంది",
    "యాడ": "ఎక్కడ",
    "యాడ ఉంటారు": "ఎక్కడ ఉంటారు",
    "యాడికి": "ఎక్కడికి",
    "ఏటి": "ఏమిటి",
    "ఏటయ్యింది": "ఏమైంది",
    "ఏటి సంగతులు": "ఏమిటి విశేషాలు",
    
    # Severity & Quantifiers
    "జాస్తిగా": "ఎక్కువగా",
    "దిట్టంగా": "ఎక్కువగా",
    "మస్తుగా": "బాగా",
    "కొద్దిగా": "కొంచం",
    "సూడండి": "చూడండి",
    "సెప్పండి": "చెప్పండి",
    "సేను": "చేను",
    "సేల్లో": "చేనులో",
    "తోట్లో": "తోటలో",
    
    # Agricultural Symptoms & Pests in Dialect
    "సీతాకోక": "గొంగళి పురుగు / పురుగు",
    "కంబళి": "గొంగళి పురుగు",
    "పుర్గు": "పురుగు",
    "దోమ కాటు": "దోమ ఉధృతి",
    "మోడు వారిపోతాంది": "ఎండిపోతోంది",
    "మోడు వారిపోయింది": "ఎండిపోయింది",
    "మాడిపోతుంది": "ఎండిపోతుంది",
    "కాటు పడింది": "తెగులు సోకింది",
    "జబ్బు చేసింది": "తెగులు సోకింది",
    "రాలతాంది": "రాలిపోతోంది",
    "కుళ్లుతాంది": "కుళ్లిపోతోంది",
    "సుడి": "సుడి దోమ",
    "పిడక తెగులు": "అగ్గి తెగులు",
    "అగ్గి మచ్చలు": "అగ్గి తెగులు",
    "ఎర్ర కుళ్లు": "ఎర్ర కుళ్లు తెగులు",
    "చెరకు పిప్పి": "ఎర్ర కుళ్లు తెగులు",
    "టీ దోమ": "టీ దోమ",
    "జిగురు కారుతుంది": "జిగురు తెగులు",
    "తిక్కా మచ్చలు": "తిక్కా తెగులు"
}

# Crop alias mapping across Telugu, Hindi, and English
CROP_ALIASES = {
    # Paddy / Rice
    "వరి": "paddy",
    "వరి చేను": "paddy",
    "వరి పంట": "paddy",
    "బియ్యం": "paddy",
    "దాన్యం": "paddy",
    "paddy": "paddy",
    "rice": "paddy",
    "धान": "paddy",
    "चावल": "paddy",
    "धान की फसल": "paddy",
    
    # Sugarcane
    "చెరకు": "sugarcane",
    "చెరుకు": "sugarcane",
    "చెరుకు తోట": "sugarcane",
    "sugarcane": "sugarcane",
    "cane": "sugarcane",
    "गन्ना": "sugarcane",
    "गन्ने": "sugarcane",
    "ईख": "sugarcane",
    "गन्ने की फसल": "sugarcane",
    
    # Cashew
    "జీడి": "cashew",
    "జీడిమామిడి": "cashew",
    "జీడితోట": "cashew",
    "cashew": "cashew",
    "cashewnut": "cashew",
    "काजू": "cashew",
    "काजू की फसल": "cashew",
    
    # Groundnut / Peanut
    "వేరుశనగ": "groundnut",
    "శనగ": "groundnut",
    "పల్లీలు": "groundnut",
    "groundnut": "groundnut",
    "peanut": "groundnut",
    "मूंगफली": "groundnut",
    "मूंगफली की फसल": "groundnut",
    
    # Tomato & Chilli
    "టమాటా": "tomato",
    "tomato": "tomato",
    "टमाटर": "tomato",
    "మిర్చి": "chilli",
    "మిరప": "chilli",
    "chilli": "chilli",
    "मिर्च": "chilli"
}

class DialectProcessor:
    """Trilingual speech and dialect adaptation engine for Telugu, Hindi, and English."""

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Automatically detects whether the farmer is speaking in Telugu, Hindi, or English.
        Uses Unicode script ranges and phonetic markers.
        """
        if not text:
            return "te"

        telugu_count = len(re.findall(r'[\u0C00-\u0C7F]', text))
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
        latin_count = len(re.findall(r'[a-zA-Z]', text))

        # Check native scripts
        if telugu_count > devanagari_count and telugu_count > 0:
            return "te"
        if devanagari_count > telugu_count and devanagari_count > 0:
            return "hi"
        if latin_count > 0:
            # Check for Romanized Hindi / Telugu phrases
            text_lower = text.lower()
            hindi_romanized = ["namaste", "kisan", "kisaan", "fasal", "khet", "ganna", "dhan", "kaju", "dawa", "barish", "bhai", "kya"]
            if any(w in text_lower for w in hindi_romanized):
                return "hi"

            telugu_romanized = ["namaskaram", "rythu", "chepandi", "enti", "cheyali", "mandu", "varsham"]
            if any(w in text_lower for w in telugu_romanized):
                return "te"

            return "en"

        return "te"

    @staticmethod
    def normalize_text(text: str) -> str:
        """Converts spoken regional dialect phrases into standardized tokens."""
        if not text:
            return ""

        normalized = text.strip()
        sorted_terms = sorted(TELUGU_DIALECT_DICTIONARY.items(), key=lambda x: len(x[0]), reverse=True)
        for dialect_term, standard_term in sorted_terms:
            normalized = normalized.replace(dialect_term, standard_term)

        return normalized

    @staticmethod
    def extract_crop(text: str) -> Tuple[str, str, str, str]:
        """
        Detects crop name from speech transcript in Telugu, Hindi, or English.
        Returns (crop_key, name_te, name_en, name_hi).
        """
        text_lower = text.lower()
        for alias, crop_key in CROP_ALIASES.items():
            if alias.lower() in text_lower:
                crop_meta = {
                    "paddy": ("వరి", "Paddy (Rice)", "धान (Paddy)"),
                    "sugarcane": ("చెరకు", "Sugarcane", "गन्ना (Sugarcane)"),
                    "cashew": ("జీడిమామిడి", "Cashew", "काजू (Cashew)"),
                    "groundnut": ("వేరుశనగ", "Groundnut", "मूंगफली (Groundnut)"),
                    "tomato": ("టమాటా", "Tomato", "टमाटर (Tomato)"),
                    "chilli": ("మిరప", "Chilli", "मिर्च (Chilli)")
                }
                te_name, en_name, hi_name = crop_meta.get(crop_key, ("", "", ""))
                return crop_key, te_name, en_name, hi_name

        return "", "", "", ""

    @staticmethod
    def extract_intent(text: str) -> str:
        """Determines top-level caller intent without button presses in Telugu, Hindi, or English."""
        text_norm = DialectProcessor.normalize_text(text).lower()

        # Mandi / Market price intent
        mandi_keywords = [
            "ధర", "రేటు", "మార్కెట్", "మండి", "బెల్లం రేటు", "అమ్మకం", "ఖరీదు",
            "mandi", "market", "price", "rate", "cost", "jaggery", "quintal",
            "मंडी", "भाव", "दाम", "कीमत", "गुड़ का भाव", "रेट"
        ]
        if any(w in text_norm for w in mandi_keywords):
            return "MANDI_PRICE"

        # Weather / Rain intent
        weather_keywords = [
            "వర్షం", "వాన", "మబ్బు", "గాలులు", "తుఫాను", "వాతావరణం",
            "weather", "rain", "rainfall", "forecast", "storm", "wind", "spray",
            "मौसम", "बारिश", "वर्षा", "हवा", "तूफान", "छिड़काव"
        ]
        if any(w in text_norm for w in weather_keywords):
            return "WEATHER_QUERY"

        # Greeting / General query
        greeting_keywords = [
            "నమస్కారం", "హలో", "బాగున్నారా", "ఎవరయ్యా",
            "hello", "hi", "namaste", "good morning",
            "नमस्ते", "प्रणाम", "हेलो", "राम राम"
        ]
        if any(w in text_norm for w in greeting_keywords):
            return "GREETING"

        # Default to crop diagnosis
        diagnosis_keywords = [
            "పంట", "చేను", "తోట", "ఆకులు", "పురుగు", "తెగులు", "మందు", "ఎండి", "కుళ్లి", "మచ్చలు",
            "crop", "leaf", "leaves", "disease", "pest", "insect", "rot", "blast", "dry", "spots",
            "फसल", "पौधा", "पत्ती", "पत्तियां", "कीड़ा", "रोग", "बीमारी", "दवा", "सड़न", "धब्बे", "सूख"
        ]
        if any(w in text_norm for w in diagnosis_keywords):
            return "CROP_DIAGNOSIS"

        return "GENERAL_ADVISORY"
