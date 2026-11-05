"""
agri_doctor.py
Trilingual (Telugu, Hindi, English) Multi-Turn AI Agricultural Doctor.
Conducts one-by-one diagnostic dialog (Crop -> Symptoms -> Duration -> Severity -> Prescription).
Responds strictly in the farmer's detected language and dynamically tracks language switches.
"""

from typing import Dict, Any, Optional, Tuple
from dialect_processor import DialectProcessor
from weather_service import WeatherService
from gemini_client import GeminiClient

# Comprehensive Trilingual Agro-Pathology Knowledge Base
CROP_PATHOLOGY_KB = {
    "paddy": {
        "crop_name_te": "వరి",
        "crop_name_en": "Paddy (Rice)",
        "crop_name_hi": "धान (चावल)",
        "diseases": [
            {
                "disease_id": "paddy_blast",
                "name_te": "అగ్గి తెగులు / పిడక తెగులు (Blast Disease)",
                "name_en": "Paddy Blast Disease (Pyricularia oryzae)",
                "name_hi": "धान का झुलसा रोग (Paddy Blast)",
                "keywords": [
                    "అగ్గి", "మచ్చలు", "కండె", "ఆకులు ఎండి", "పిడక", "గోధుమ",
                    "blast", "spindle", "brown spot", "lesions", "dry",
                    "झुलसा", "धब्बे", "पत्तियां सूख", "भूरे धब्बे", "ब्लास्ट"
                ],
                "symptoms_desc_te": "ఆకులపై నూలుకండె ఆకారంలో గోధుమ రంగు మచ్చలు ఏర్పడి, మధ్యలో బూడిద రంగులో ఉంటాయి.",
                "symptoms_desc_en": "Spindle-shaped brown lesions on leaves with grayish centers.",
                "symptoms_desc_hi": "पत्तियों पर आंख या नाव के आकार के भूरे धब्बे बनते हैं जिनका केंद्र राख के रंग का होता है।",
                "chemical_te": "ట్రైసైక్లాజోల్ 75% WP (Tricyclazole) - 16 లీటర్ల చేతి పంపు నీటికి 10 గ్రాములు లేదా ఐసోప్రోథియోలేన్ 25 మిల్లీలీటర్లు కలిపి పిచికారీ చేయాలి.",
                "chemical_en": "Tricyclazole 75% WP @ 10 grams per 16-liter knapsack sprayer tank (0.6g/L water).",
                "chemical_hi": "ट्राइसाइक्लाजोल 75% डब्ल्यूपी (Tricyclazole) - 16 लीटर नैपसैक पंप में 10 ग्राम मिलाकर सुबह के समय छिड़काव करें।",
                "organic_te": "వేప నూనె 5 మిల్లీలీటర్లు లీటరు నీటికి లేదా పులిసిన మజ్జిగ ద్రావణం పిచికారీ చేయండి.",
                "organic_en": "Spray 5ml Neem oil per liter of water or sour buttermilk solution.",
                "organic_hi": "नीम का तेल 5 मिली प्रति लीटर पानी या खट्टी छाछ का छिड़काव करें।",
                "precautions_te": "చేనులో యూరియా ఎరువు అధికంగా వాడకూడదు. పొలంలో నీరు నిలువ లేకుండా చూడండి.",
                "precautions_en": "Avoid excess urea nitrogen fertilizer. Drain stagnant water.",
                "precautions_hi": "खेत में यूरिया का अधिक उपयोग न करें और अतिरिक्त पानी निकाल दें।"
            },
            {
                "disease_id": "paddy_bph",
                "name_te": "సుడి దోమ (Brown Plant Hopper)",
                "name_en": "Brown Plant Hopper (BPH)",
                "name_hi": "भूरा फुदका / भूरा माहू (BPH)",
                "keywords": [
                    "దోమ", "సుడి", "గుండ్రంగా", "ఎండిపోవడం", "మొదలు",
                    "bph", "hopper", "brown plant hopper", "circular",
                    "फुदका", "माहू", "तने के पास", "गोलाकार सूखा"
                ],
                "symptoms_desc_te": "పైరు మొదళ్ళ వద్ద గోధుమ రంగు దోమలు చేరి రసం పీల్చడం వల్ల పైరు గుండ్రటి వలయాలుగా ఎండిపోతుంది.",
                "symptoms_desc_en": "Brown hoppers suck sap at stem base causing circular patches of hopper burn.",
                "symptoms_desc_hi": "पौधे के निचले तने पर भूरे रंग के कीड़े रस चूसते हैं जिससे फसल गोलाकार घेरे में सूख जाती है।",
                "chemical_te": "పైమెట్రోజైన్ 50% WDG ఎకరాకు 120 గ్రాములు లేదా దినోటెఫ్యూరాన్ 20% SG ఎకరాకు 80 గ్రాములు పిచికారీ చేయాలి. మందు దుబ్బు మొదళ్లకు తగలాలి.",
                "chemical_en": "Pymetrozine 50% WDG @ 120g/acre or Dinotefuran 20% SG @ 80g/acre, directed strictly at the plant base.",
                "chemical_hi": "पाइमेट्रोज़ीन 50% डब्ल्यूडीजी 120 ग्राम प्रति एकड़ या डिनोटेफ्यूरॉन 80 ग्राम प्रति एकड़ सीधे तने की जड़ पर छिड़कें।",
                "organic_te": "చేనులో నీటిని వెంటనే తీసివేసి 2-3 రోజులు ఆరబెట్టాలి. గాలి సోకేలా అల్లికలు చేయాలి.",
                "organic_en": "Drain field water completely for 2-3 days for aeration.",
                "organic_hi": "खेत से पानी निकालकर 2-3 दिन धूप और हवा लगने दें।",
                "precautions_te": "పిచికారీని ఆకులపై కాకుండా దుబ్బు మొదళ్ళ వద్ద చేయాలి.",
                "precautions_en": "Direct the spray nozzle towards the root base, not upper foliage.",
                "precautions_hi": "दवा का छिड़काव पत्तियों के ऊपर नहीं, बल्कि तने की जड़ पर करें।"
            }
        ]
    },
    "sugarcane": {
        "crop_name_te": "చెరకు (అనకాపల్లి)",
        "crop_name_en": "Sugarcane (Anakapalli)",
        "crop_name_hi": "गन्ना (अनकापल्ली)",
        "diseases": [
            {
                "disease_id": "sugarcane_red_rot",
                "name_te": "ఎర్ర కుళ్లు తెగులు (Red Rot)",
                "name_en": "Sugarcane Red Rot (Colletotrichum falcatum)",
                "name_hi": "गन्ने का लाल सड़न रोग (Red Rot)",
                "keywords": [
                    "ఎర్ర", "కుళ్లు", "వాసన", "ఆకులు ఎండి", "గడలు", "పిప్పి",
                    "red rot", "red", "alcohol smell", "cane", "stalk rot",
                    "लाल सड़न", "शराब जैसी गंध", "गन्ना अंदर से लाल", "सड़न"
                ],
                "symptoms_desc_te": "ఆకులు పసుపు రంగులోకి మారి ఎండిపోతాయి. చెరకు గడ లోపల ఎరుపు రంగుగా మారి, తెల్లటి అడ్డ మచ్చలు మరియు మద్యం లాంటి వాసన వస్తుంది.",
                "symptoms_desc_en": "Leaves wither and dry. Splitting the cane stalk reveals red tissue with white cross patches and an alcoholic odor.",
                "symptoms_desc_hi": "ऊपर की पत्तियां पीली होकर सूखती हैं। गन्ने को चीरने पर अंदर लाल रंग और शराब जैसी दुर्गंध आती है।",
                "chemical_te": "విత్తన ముక్కలను కార్బండజిమ్ 0.1% ద్రావణంలో 15 నిమిషాలు నానబెట్టాలి. నేల తడపడానికి కాపర్ ఆక్సిక్లోరైడ్ 3 గ్రాములు లీటరు నీటికి వాడండి.",
                "chemical_en": "Dip seed sets in Carbendazim 0.1% for 15 minutes before planting. Drench soil with Copper Oxychloride @ 3g/L.",
                "chemical_hi": "कार्बेन्डाजिम 0.1% (1 ग्राम प्रति लीटर) में बीज के टुकड़ों को 15 मिनट भिगोएं। कॉपर ऑक्सीक्लोराइड 3 ग्राम/लीटर से मिट्टी तर करें।",
                "organic_te": "తెగులు సోకిన పిలకలను దుంపలతో సహా పెరికి కాల్చివేయాలి. పంట మార్పిడి చేపట్టండి.",
                "organic_en": "Uproot and burn diseased clumps. Rotate with paddy.",
                "organic_hi": "रोगी पौधों को जड़ सहित उखाड़कर जला दें और फसल चक्र अपनाएं।",
                "precautions_te": "ఆ గడలను బెల్లం తయారీకి వాడితే బెల్లం నల్లబడి నాణ్యత దెబ్బతింటుంది.",
                "precautions_en": "Do NOT use affected canes for jaggery making as it darkens and spoils quality.",
                "precautions_hi": "रोगग्रस्त गन्ने का उपयोग गुड़ बनाने में न करें, इससे गुड़ की गुणवत्ता खराब होती है।"
            }
        ]
    },
    "cashew": {
        "crop_name_te": "జీడిమామిడి (పలాస)",
        "crop_name_en": "Cashew (Palasa/Srikakulam)",
        "crop_name_hi": "काजू (पलासा)",
        "diseases": [
            {
                "disease_id": "cashew_tea_mosquito",
                "name_te": "టీ దోమ మరియు కొమ్మ ఎండు తెగులు (Tea Mosquito Bug)",
                "name_en": "Tea Mosquito Bug (Helopeltis antonii)",
                "name_hi": "चाय मच्छर कीट (Tea Mosquito Bug)",
                "keywords": [
                    "టీ దోమ", "దోమ", "పూత", "చిగుళ్లు", "జిగురు",
                    "tea mosquito", "mosquito", "flower blight", "gum", "resin",
                    "चाय मच्छर", "मच्छर", "फूल सूखना", "गोंद"
                ],
                "symptoms_desc_te": "లేత చిగుళ్ళు, పూత రెమ్మలపై దోమ కుట్టడం వల్ల నల్లటి మచ్చలు ఏర్పడి జిగురు కారుతుంది. పూత మాడిపోతుంది.",
                "symptoms_desc_en": "Black necrotic lesions on tender shoots and flower panicles with gum exudation; blossom blight.",
                "symptoms_desc_hi": "नई कोपलों और फूलों पर काले धब्बे पड़ते हैं, गोंद जैसा रिसाव होता है और फूल जलकर सूख जाते हैं।",
                "chemical_te": "లాంబ్డా సైహలోథ్రిన్ 5% EC 1 మిల్లీలీటరు లీటరు నీటికి (16 లీటర్ల పంపుకు 16 మి.లీ.) లేదా ప్రొఫెనోఫాస్ 1.5 మి.లీ. పిచికారీ చేయాలి.",
                "chemical_en": "Lambda-cyhalothrin 5% EC @ 1ml/L (16ml per 16L knapsack sprayer pump) at flowering.",
                "chemical_hi": "लैम्ब्डा-साइहलोथ्रिन 5% ईसी 1 मिली प्रति लीटर (16 लीटर पंप में 16 मिली) का छिड़काव करें।",
                "organic_te": "పూత దశలో 5% వేప గింజల కషాయం పిచికారీ చేయండి.",
                "organic_en": "Spray 5% Neem Seed Kernel Extract (NSKE) during flowering.",
                "organic_hi": "फूल आने के समय 5% नीम के बीज का काढ़ा (एनएसकेई) छिड़कें।",
                "precautions_te": "పూత రాలే సమయంలో మరియు పిందె కట్టే సమయంలో రెండు దఫాలుగా పిచికారీ చేయాలి.",
                "precautions_en": "Spray once at vegetative flushing and once during panicle emergence.",
                "precautions_hi": "नई पत्तियां आने और फूल खिलने के समय दो बार छिड़काव करें।"
            }
        ]
    },
    "groundnut": {
        "crop_name_te": "వేరుశనగ",
        "crop_name_en": "Groundnut (Peanut)",
        "crop_name_hi": "मूंगफली",
        "diseases": [
            {
                "disease_id": "groundnut_tikka",
                "name_te": "తిక్కా ఆకుమచ్చ తెగులు (Tikka Leaf Spot)",
                "name_en": "Tikka Leaf Spot (Cercospora arachidicola)",
                "name_hi": "टिक्का पत्ती धब्बा रोग (Tikka Disease)",
                "keywords": [
                    "తిక్కా", "ఆకుమచ్చ", "నల్లటి", "పసుపు రంగు అంచు",
                    "tikka", "leaf spot", "brown spots", "yellow halo",
                    "टिक्का", "पत्ती धब्बा", "भूरे काले धब्बे", "पीला घेरा"
                ],
                "symptoms_desc_te": "ఆకులపై నల్లటి వలయాకార మచ్చలు చుట్టూ పసుపు రంగు అంచుతో కనిపిస్తాయి. ఆకులు రాలిపోతాయి.",
                "symptoms_desc_en": "Circular dark brown to black spots surrounded by yellow halos, causing premature leaf shedding.",
                "symptoms_desc_hi": "पत्तियों पर गोलाकार गहरे भूरे और काले धब्बे बनते हैं जिनके चारों ओर पीला घेरा होता है।",
                "chemical_te": "మ్యాంకోజెబ్ 2 గ్రాములు లేదా హెక్సాకోనాజోల్ 2 మి.లీ. లీటరు నీటికి కలిపి పిచికారీ చేయాలి (16 లీటర్ల పంపుకు 32 మి.లీ).",
                "chemical_en": "Mancozeb @ 2g/L or Hexaconazole 5% EC @ 2ml/L (32ml per 16L knapsack sprayer).",
                "chemical_hi": "मैंकोजेब 2 ग्राम या हेक्साकोनाज़ोल 2 मिली प्रति लीटर पानी (16 लीटर पंप में 32 मिली) मिलाकर छिड़कें।",
                "organic_te": "ట్రైకోడెర్మా విరిడేతో విత్తన శుద్ధి చేయాలి. ఆవు మూత్రం ద్రావణం పిచికారీ చేయవచ్చు.",
                "organic_en": "Seed treatment with Trichoderma viride @ 10g/kg. Spray 10% cow urine solution.",
                "organic_hi": "ट्राइकोडर्मा विरिडी से बीज उपचार करें और 10% गोमूत्र घोल का छिड़काव करें।",
                "precautions_te": "మబ్బులు పట్టి తేమ ఎక్కువగా ఉన్నప్పుడు తెగులు తీవ్రత పెరుగుతుంది.",
                "precautions_en": "Disease spreads fast in humid weather. Spray before rain starts.",
                "precautions_hi": "बादल छाए रहने और अधिक नमी में यह रोग तेजी से फैलता है।"
            }
        ]
    }
}

class AgriDoctorSession:
    """Stateful diagnostic session conducting a strict 4-question step-by-step dialog."""

    def __init__(self, session_id: str, phone: str = "+919848022338", current_lang: str = "te"):
        self.session_id = session_id
        self.phone = phone
        self.current_lang = current_lang  # "te", "hi", "en"
        
        # Step-by-step diagnostic workflow:
        # STEP 1: ASK_CROP
        # STEP 2: ASK_SYMPTOMS
        # STEP 3: ASK_DURATION
        # STEP 4: ASK_SEVERITY
        # STEP 5: DELIVER_PRESCRIPTION
        # STEP 6: COMPLETED
        self.step = "ASK_CROP"
        
        self.crop_key = None
        self.crop_name = None
        self.symptoms_text = None
        self.duration_text = None
        self.severity_text = None
        self.diagnosed_disease = None
        self.history = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "phone": self.phone,
            "current_lang": self.current_lang,
            "step": self.step,
            "crop_key": self.crop_key,
            "crop_name": self.crop_name,
            "symptoms": self.symptoms_text,
            "duration": self.duration_text,
            "severity": self.severity_text,
            "diagnosed_disease": self.diagnosed_disease.get(f"name_{self.current_lang}", self.diagnosed_disease.get("name_en")) if self.diagnosed_disease else None,
            "turns_count": len(self.history)
        }

class AgriDoctorEngine:
    """Multi-turn multilingual voice engine for farmer consultation."""

    def __init__(self):
        self.sessions: Dict[str, AgriDoctorSession] = {}

    def get_or_create_session(self, session_id: str, phone: str = "+919848022338", initial_lang: str = "te") -> AgriDoctorSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = AgriDoctorSession(session_id, phone, initial_lang)
        return self.sessions[session_id]

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def start_call(self, session_id: str, phone: str = "+919848022338", lang: str = "te") -> Dict[str, Any]:
        """Initiates call and delivers warm welcoming prompt in caller's language."""
        session = self.get_or_create_session(session_id, phone, lang)
        session.step = "ASK_CROP"

        greetings = {
            "te": "నమస్కారం రైతు బాంధవుడా! నేను మీ AI అగ్రి-డాక్టర్‌ని. మీ పంటను రక్షించడానికి నేను కొన్ని ప్రశ్నలు అడుగుతాను. మొదట చెప్పండి—మీది ఏ పంట? (ఉదాహరణకు: వరి, చెరకు, జీడిమామిడి, లేదా వేరుశనగ)",
            "hi": "नमस्ते किसान भाई! मैं आपका एआई एग्री-डॉक्टर हूँ। आपकी फसल के इलाज के लिए मैं एक-एक करके कुछ सवाल पूछूँगा। सबसे पहले बताइए—आपकी कौन सी फसल है? (जैसे: धान, गन्ना, काजू, या मूंगफली)",
            "en": "Hello respected farmer! I am your AI Agricultural Doctor. To diagnose and treat your crop, I will ask you a few simple questions one by one. First, please tell me: Which crop are you growing? (For example: Paddy, Sugarcane, Cashew, or Groundnut)"
        }

        spoken_greeting = greetings.get(lang, greetings["te"])
        session.history.append({"speaker": "agri_doctor", "text": spoken_greeting, "lang": lang})

        return {
            "session_id": session_id,
            "step": session.step,
            "detected_lang": session.current_lang,
            "spoken_response": spoken_greeting,
            "session": session.to_dict()
        }

    def process_turn(self, session_id: str, farmer_utterance: str) -> Dict[str, Any]:
        """
        Processes farmer utterance:
        1. Auto-detects spoken language (and updates session language if changed).
        2. Progresses through the step-by-step diagnostic workflow:
           Crop -> Symptoms -> Duration -> Severity -> Prescription.
        3. Generates response strictly in that language.
        """
        session = self.get_or_create_session(session_id)
        
        # Detect language of current utterance
        detected_lang = DialectProcessor.detect_language(farmer_utterance)
        if detected_lang in ["te", "hi", "en"]:
            session.current_lang = detected_lang

        session.history.append({"speaker": "farmer", "text": farmer_utterance, "lang": session.current_lang})
        lang = session.current_lang
        normalized_text = DialectProcessor.normalize_text(farmer_utterance)

        # -------------------------------------------------------------
        # STEP 1: CROP IDENTIFICATION
        # -------------------------------------------------------------
        if session.step == "ASK_CROP":
            crop_key, name_te, name_en, name_hi = DialectProcessor.extract_crop(farmer_utterance)
            if crop_key:
                session.crop_key = crop_key
                session.crop_name = name_te if lang == "te" else name_hi if lang == "hi" else name_en
                session.step = "ASK_SYMPTOMS"

                prompts = {
                    "te": f"సరేనయ్యా, మీ {session.crop_name} పంట గురించి అర్థమైంది. రెండవ ప్రశ్న: మీ పంటలో ఎలాంటి లక్షణాలు లేదా మార్పులు కనిపిస్తున్నాయి? (ఉదాహరణకు: ఆకులపై మచ్చలా, కాండం ఎండిపోతోందా, లేక పురుగులున్నాయా?)",
                    "hi": f"बहुत बढ़िया, आपकी {session.crop_name} की फसल समझ गया। दूसरा सवाल: फसल में क्या लक्षण या खराबी दिख रही है? (जैसे: पत्तियों पर धब्बे, तने में सड़न, कीड़े, या पत्तियां सूखना?)",
                    "en": f"Understood, you are growing {session.crop_name}. Question 2: What visual symptoms are you noticing on your crop? (For example: spots on leaves, stem drying, rot, or insect larvae?)"
                }
                spoken_resp = prompts.get(lang, prompts["te"])
            else:
                prompts = {
                    "te": "క్షమించండి అయ్యా, మీ పంట పేరు స్పష్టంగా వినపడలేదు. మీది వరియా, చెరకా, జీడిమామిడా లేక వేరుశనగా? దయచేసి మళ్లీ చెప్పండి.",
                    "hi": "माफ कीजिए किसान भाई, फसल का नाम स्पष्ट समझ नहीं आया। क्या आपकी फसल धान, गन्ना, काजू या मूंगफली है? कृपया दोबारा बताएं।",
                    "en": "Pardon me farmer, I couldn't clearly identify the crop name. Is it Paddy, Sugarcane, Cashew, or Groundnut? Please say it again."
                }
                spoken_resp = prompts.get(lang, prompts["te"])

        # -------------------------------------------------------------
        # STEP 2: SYMPTOMS RECORDING
        # -------------------------------------------------------------
        elif session.step == "ASK_SYMPTOMS":
            session.symptoms_text = farmer_utterance
            matched_disease = self._match_disease(session.crop_key, normalized_text)
            if matched_disease:
                session.diagnosed_disease = matched_disease

            session.step = "ASK_DURATION"
            prompts = {
                "te": "లక్షణాలు అర్థమయ్యాయి అయ్యా. మూడవ ప్రశ్న: ఈ సమస్య మీ చేనులో మొదలై ఎన్ని రోజులు లేదా వారాలు అయ్యింది? చెప్పండి.",
                "hi": "लक्षण समझ आ गए। तीसरा सवाल: यह बीमारी या समस्या आपके खेत में कितने दिनों या हफ्तों से दिख रही है?",
                "en": "Got the symptoms. Question 3: For how many days or weeks has this problem persisted in your field?"
            }
            spoken_resp = prompts.get(lang, prompts["te"])

        # -------------------------------------------------------------
        # STEP 3: DISEASE DURATION
        # -------------------------------------------------------------
        elif session.step == "ASK_DURATION":
            session.duration_text = farmer_utterance
            session.step = "ASK_SEVERITY"
            prompts = {
                "te": "సరేనయ్యా. నాల్గవ ప్రశ్న: ఈ సమస్య చేనులో తీవ్రత ఎలా ఉంది? అక్కడక్కడా కొద్దిగానే ఉందా, లేక చేను అంతా జాస్తిగా వ్యాపించిందా?",
                "hi": "ठीक है। चौथा सवाल: यह बीमारी खेत में कितनी गंभीर है? क्या यह कुछ ही पौधों पर है, या पूरे खेत में फैल चुकी है?",
                "en": "Noted. Question 4: How severe is the spread? Is it confined to a few localized clumps, or has it spread heavily across the entire field?"
            }
            spoken_resp = prompts.get(lang, prompts["te"])

        # -------------------------------------------------------------
        # STEP 4: SEVERITY -> DELIVER PRESCRIPTION
        # -------------------------------------------------------------
        elif session.step == "ASK_SEVERITY":
            session.severity_text = farmer_utterance
            session.step = "DELIVER_PRESCRIPTION"

            # Check if Gemini API can synthesize advanced advice
            gemini_advice = GeminiClient.generate_agricultural_advice(
                crop=session.crop_name or session.crop_key,
                symptoms=session.symptoms_text,
                duration=session.duration_text,
                severity=session.severity_text,
                language=lang
            )

            if gemini_advice:
                spoken_resp = gemini_advice
            else:
                # Built-in expert pathology prescription
                disease = session.diagnosed_disease or self._get_fallback_disease(session.crop_key)
                session.diagnosed_disease = disease

                dis_name = disease.get(f"name_{lang}", disease.get("name_en"))
                chem_treat = disease.get(f"chemical_{lang}", disease.get("chemical_en"))
                org_treat = disease.get(f"organic_{lang}", disease.get("organic_en"))
                precautions = disease.get(f"precautions_{lang}", disease.get("precautions_en"))

                if lang == "hi":
                    spoken_resp = (
                        f"किसान भाई! आपके {session.crop_name} में मुख्य रोग: {dis_name} है। "
                        f"दवा का उपाय: {chem_treat} "
                        f"जैविक उपाय: {org_treat} "
                        f"सावधानी: {precautions} "
                        f"क्या आप दवा का नाम या मात्रा दोबारा सुनना चाहते हैं?"
                    )
                elif lang == "en":
                    spoken_resp = (
                        f"Respected farmer! The diagnosed condition for your {session.crop_name} is: {dis_name}. "
                        f"Chemical treatment: {chem_treat} "
                        f"Organic remedy: {org_treat} "
                        f"Precaution: {precautions} "
                        f"Would you like me to repeat the medicine dosage?"
                    )
                else: # Telugu
                    spoken_resp = (
                        f"అయ్యా రైతు బాంధవుడా! మీ {session.crop_name} పంటకు వచ్చిన రోగం: {dis_name}. "
                        f"వెంటనే చేయవలసిన మందు నివారణ: {chem_treat} "
                        f"సేంద్రియ పద్ధతి: {org_treat} "
                        f"ముఖ్యమైన జాగ్రత్త: {precautions} "
                        f"మందు పేరు లేదా మోతాదు మళ్లీ చెప్పమంటారా?"
                    )

        # -------------------------------------------------------------
        # STEP 5: FOLLOWUP & WRAP UP
        # -------------------------------------------------------------
        elif session.step == "DELIVER_PRESCRIPTION":
            repeat_words = ["మళ్లీ", "మరోసారి", "repeat", "again", "दोबारा", "फिर", "मात्रा"]
            if any(w in normalized_text.lower() for w in repeat_words):
                disease = session.diagnosed_disease or self._get_fallback_disease(session.crop_key)
                chem = disease.get(f"chemical_{lang}", disease.get("chemical_en"))
                if lang == "hi":
                    spoken_resp = f"फिर से सुनिए: {chem} 16 लीटर नैपसैक पंप के हिसाब से मिलाकर सुबह छिड़काव करें।"
                elif lang == "en":
                    spoken_resp = f"Please listen again: {chem} Spray carefully using a 16-liter knapsack pump during the morning."
                else:
                    spoken_resp = f"అయ్యా మళ్ళీ వినండి: {chem} 16 లీటర్ల చేతి పంపుతో జాగ్రత్తగా కొలత ప్రకారం కలపండి."
            else:
                session.step = "COMPLETED"
                prompts = {
                    "te": "సంతోషం అయ్యా! సూచించిన మోతాదు ప్రకారం జాగ్రత్తగా పిచికారీ చేయండి. మీ పంట క్షేమంగా ఉండి మంచి దిగుబడి రావాలని కోరుకుంటున్నాం. ధన్యవాదాలు!",
                    "hi": "धन्यवाद किसान भाई! बताई गई मात्रा के अनुसार सावधानीपूर्वक छिड़काव करें। आपकी फसल सुरक्षित रहे और अच्छी पैदावार हो। धन्यवाद!",
                    "en": "Thank you farmer! Follow the recommended knapsack dosage carefully. Wishing you a healthy crop and a bumper harvest. Have a great day!"
                }
                spoken_resp = prompts.get(lang, prompts["te"])

        else:
            session.step = "ASK_CROP"
            prompts = {
                "te": "నమస్కారం! కొత్త పంట లేదా సమస్య గురించి మాట్లాడాలంటే మీ పంట పేరు చెప్పండి.",
                "hi": "नमस्ते! किसी अन्य फसल या समस्या के समाधान के लिए अपनी फसल का नाम बताएं।",
                "en": "Hello! To start a new diagnosis, please tell me your crop name."
            }
            spoken_resp = prompts.get(lang, prompts["te"])

        session.history.append({"speaker": "agri_doctor", "text": spoken_resp, "lang": session.current_lang})

        return {
            "session_id": session_id,
            "step": session.step,
            "detected_lang": session.current_lang,
            "spoken_response": spoken_resp,
            "is_call_active": session.step != "COMPLETED",
            "session": session.to_dict()
        }

    def _match_disease(self, crop_key: Optional[str], text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        if not crop_key or crop_key not in CROP_PATHOLOGY_KB:
            for c_key, c_data in CROP_PATHOLOGY_KB.items():
                for dis in c_data["diseases"]:
                    for kw in dis["keywords"]:
                        if kw.lower() in text_lower:
                            return dis
            return None

        crop_info = CROP_PATHOLOGY_KB[crop_key]
        for disease in crop_info["diseases"]:
            for keyword in disease["keywords"]:
                if keyword.lower() in text_lower:
                    return disease
        return None

    def _get_fallback_disease(self, crop_key: Optional[str]) -> Dict[str, Any]:
        if crop_key and crop_key in CROP_PATHOLOGY_KB:
            return CROP_PATHOLOGY_KB[crop_key]["diseases"][0]
        return CROP_PATHOLOGY_KB["paddy"]["diseases"][0]
