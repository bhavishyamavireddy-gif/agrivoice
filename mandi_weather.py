"""
mandi_weather.py
Bilingual (Telugu & English) Hyperlocal Mandi Pricing & Weather Alerts for North Andhra.
Covers Anakapalli (Jaggery & Groundnut), Palasa (Cashew), and Visakhapatnam APMC markets.
"""

from datetime import datetime
from typing import Dict, Any, List

class MandiWeatherService:
    """Provides bilingual real-time Mandi price feeds and rain advisories for North Andhra farmers."""

    MANDI_DATA = {
        "anakapalli": {
            "market_name_te": "అనకాపల్లి వ్యవసాయ మార్కెట్ యార్డ్ (APMC)",
            "market_name_en": "Anakapalli Agricultural Market Yard (APMC)",
            "district_te": "అనకాపల్లి",
            "district_en": "Anakapalli District",
            "rates": [
                {
                    "commodity_te": "బెల్లం - మొదటి రకం",
                    "commodity_en": "Jaggery - Grade 1",
                    "price_per_quintal": 4250,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "up",
                    "note_te": "డిమాండ్ బాగుంది, శుభ్రమైన నలుపు లేని బెల్లానికి మంచి రేటు",
                    "note_en": "Strong demand for clean, light-colored lump jaggery"
                },
                {
                    "commodity_te": "బెల్లం - రెండవ రకం",
                    "commodity_en": "Jaggery - Grade 2",
                    "price_per_quintal": 3800,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "stable",
                    "note_te": "సాధారణ ధర",
                    "note_en": "Normal steady price"
                },
                {
                    "commodity_te": "చెరకు (ఫ్యాక్టరీ మద్దతు ధర)",
                    "commodity_en": "Sugarcane (Factory FRP Rate)",
                    "price_per_quintal": 320,
                    "unit_te": "రూ. / క్వింటాల్ (టన్నుకు రూ. 3,200)",
                    "unit_en": "Rs / Quintal (Rs 3,200 per Ton)",
                    "trend": "stable",
                    "note_te": "ప్రభుత్వ మద్దతు ధర",
                    "note_en": "Government statutory price"
                },
                {
                    "commodity_te": "వరి - సాధారణ రకం",
                    "commodity_en": "Paddy - Common Variety",
                    "price_per_quintal": 2300,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "stable",
                    "note_te": "ప్రభుత్వ మద్దతు ధర రేటు",
                    "note_en": "MSP standard procurement rate"
                }
            ]
        },
        "palasa": {
            "market_name_te": "పలాస జీడిపిక్కల మార్కెట్",
            "market_name_en": "Palasa Raw Cashew Market",
            "district_te": "శ్రీకాకుళం",
            "district_en": "Srikakulam District",
            "rates": [
                {
                    "commodity_te": "జీడిపిక్కలు (80 కేజీల బస్తా)",
                    "commodity_en": "Raw Cashew Nuts (80kg Bag)",
                    "price_per_quintal": 11800,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "up",
                    "note_te": "పలాస ప్రాసెసింగ్ యూనిట్లలో మంచి డిమాండ్",
                    "note_en": "High procurement demand in Palasa processing mills"
                },
                {
                    "commodity_te": "వరి - గ్రేడ్-ఎ",
                    "commodity_en": "Paddy - Grade A",
                    "price_per_quintal": 2320,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "stable",
                    "note_te": "మంచి నాణ్యత గల ధాన్యం",
                    "note_en": "High-quality paddy"
                }
            ]
        },
        "vizag": {
            "market_name_te": "విశాఖపట్నం రైతు బజార్ & మార్కెట్",
            "market_name_en": "Visakhapatnam Rythu Bazar & Market",
            "district_te": "విశాఖపట్నం",
            "district_en": "Visakhapatnam District",
            "rates": [
                {
                    "commodity_te": "వేరుశనగ కాయలు",
                    "commodity_en": "Groundnut Pods",
                    "price_per_quintal": 6600,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "up",
                    "note_te": "నూనె గింజల డిమాండ్ స్థిరంగా ఉంది",
                    "note_en": "Steady oilseed crushing demand"
                },
                {
                    "commodity_te": "ఎండు మిరప",
                    "commodity_en": "Dry Red Chilli",
                    "price_per_quintal": 18500,
                    "unit_te": "రూ. / క్వింటాల్",
                    "unit_en": "Rs / Quintal",
                    "trend": "down",
                    "note_te": "నాణ్యమైన ఘాటు గల రకాలకు మెరుగైన ధర",
                    "note_en": "Pungent export varieties command higher premium"
                }
            ]
        }
    }

    WEATHER_DATA = {
        "anakapalli": {
            "forecast_te": "రాగల 24 గంటల్లో తేలికపాటి నుండి భారీ వర్షం పడే అవకాశం ఉంది.",
            "forecast_en": "Moderate to heavy rain expected across Anakapalli in the next 24 hours.",
            "rainfall_chance": "75%",
            "temperature": "29°C",
            "spray_advisory_te": "హెచ్చరిక: రేపు వర్షం సూచన ఉన్నందున పురుగుమందులు మరియు ఎరువులు ఎట్టి పరిస్థితుల్లోనూ పిచికారీ చేయవద్దు.",
            "spray_advisory_en": "Advisory: Do NOT spray pesticides or fertilizers today due to rain warning. Rain will wash away chemicals.",
            "safe_to_spray": False
        },
        "srikakulam": {
            "forecast_te": "వాతావరణం మేఘావృతమై ఉండి, సాయంత్రం జల్లులు కురిసే అవకాశం ఉంది.",
            "forecast_en": "Cloudy conditions with localized evening showers expected in Srikakulam.",
            "rainfall_chance": "40%",
            "temperature": "31°C",
            "spray_advisory_te": "ఉదయం పూట ఎండ ఉన్నప్పుడు మాత్రమే పిచికారీ చేయండి. సాయంత్రం ఆపండి.",
            "spray_advisory_en": "Safe for morning spraying under clear skies; stop spraying by afternoon.",
            "safe_to_spray": True
        },
        "visakhapatnam": {
            "forecast_te": "తీరప్రాంతంలో ఈదురు గాలులతో కూడిన సాధారణ వర్షం.",
            "forecast_en": "Coastal gusty winds with light showers across Visakhapatnam belt.",
            "rainfall_chance": "60%",
            "temperature": "30°C",
            "spray_advisory_te": "గాలులు ఎక్కువగా ఉన్నాయి. గాలి తీవ్రత తగ్గిన తర్వాతే పిచికారీ చేపట్టాలి.",
            "spray_advisory_en": "High wind drift warning. Spray only after wind speed subsides.",
            "safe_to_spray": False
        }
    }

    @classmethod
    def get_mandi_summary(cls, market_key: str = "anakapalli") -> Dict[str, Any]:
        """Returns market rates for the requested North Andhra market."""
        return cls.MANDI_DATA.get(market_key, cls.MANDI_DATA["anakapalli"])

    @classmethod
    def get_weather_summary(cls, location_key: str = "anakapalli") -> Dict[str, Any]:
        """Returns weather forecast and agricultural spraying advisory."""
        return cls.WEATHER_DATA.get(location_key, cls.WEATHER_DATA["anakapalli"])

    @classmethod
    def generate_missed_call_bulletin(cls, caller_phone: str, region: str = "anakapalli", lang: str = "both") -> Dict[str, Any]:
        """
        Creates bilingual audio voice scripts and SMS bulletins triggered by a missed call.
        """
        market = cls.get_mandi_summary(region)
        weather = cls.get_weather_summary(region)
        
        # Primary rates
        p_rate = market["rates"][0]
        
        # Telugu audio script
        audio_te = (
            f"అయ్యా నమస్కారం! అగ్రివాయిస్ మిస్డ్-కాల్ అలర్ట్. "
            f"నేటి {market['market_name_te']} ధర: {p_rate['commodity_te']} క్వింటాల్ రూ. {p_rate['price_per_quintal']}. "
            f"వాతావరణం: {weather['forecast_te']} {weather['spray_advisory_te']} "
            f"ఉచిత సలహాల కోసం 1800-AGRI-VOICE కు కాల్ చేయండి."
        )

        # English audio script
        audio_en = (
            f"Hello Farmer! AgriVoice Missed-Call Alert. "
            f"Today's {market['market_name_en']} price: {p_rate['commodity_en']} is Rs {p_rate['price_per_quintal']} per quintal. "
            f"Weather update: {weather['forecast_en']} {weather['spray_advisory_en']} "
            f"Call toll-free 1800-AGRI-VOICE anytime for advice."
        )

        # Combined bilingual script
        audio_bilingual = f"{audio_te}\n\n[In English]: {audio_en}"

        # Telugu SMS
        sms_te = (
            f"[అగ్రివాయిస్ అలర్ట్]\n"
            f"మార్కెట్: {market['district_te']}\n"
            f"{p_rate['commodity_te']}: రూ. {p_rate['price_per_quintal']}/క్వింటాల్\n"
            f"వర్షం సూచన: {weather['rainfall_chance']}\n"
            f"పిచికారీ: {'వర్షం ఉంది, మందు కొట్టవద్దు' if not weather['safe_to_spray'] else 'ఉదయం పిచికారీ చేయవచ్చు'}\n"
            f"ఉచిత కాల్: 1800-AGRI-VOICE"
        )

        # English SMS
        sms_en = (
            f"[AgriVoice Alert]\n"
            f"Market: {market['district_en']}\n"
            f"{p_rate['commodity_en']}: Rs {p_rate['price_per_quintal']}/Qtl\n"
            f"Rain Chance: {weather['rainfall_chance']}\n"
            f"Spray: {'DO NOT SPRAY (Rain Warning)' if not weather['safe_to_spray'] else 'Safe for morning spray'}\n"
            f"Free Call: 1800-AGRI-VOICE"
        )

        sms_bilingual = f"{sms_te}\n---\n{sms_en}"

        selected_audio = audio_en if lang == "en" else audio_te if lang == "te" else audio_bilingual
        selected_sms = sms_en if lang == "en" else sms_te if lang == "te" else sms_bilingual

        return {
            "caller_phone": caller_phone,
            "region": region,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio_script": selected_audio,
            "audio_te": audio_te,
            "audio_en": audio_en,
            "sms_text": selected_sms,
            "sms_te": sms_te,
            "sms_en": sms_en,
            "market": market,
            "weather": weather
        }
