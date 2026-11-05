"""
test_features.py
Comprehensive test suite for AgriVoice Feature 1 and Feature 2.
"""

import unittest
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dialect_processor import DialectProcessor
from agri_doctor import AgriDoctorEngine
from weather_service import WeatherService
from farmer_registry import FarmerRegistry
from app import app

class TestFeature1AgriDoctor(unittest.TestCase):
    """Tests Feature 1: Multilingual AI Agricultural Doctor Voice Calling."""

    def setUp(self):
        self.engine = AgriDoctorEngine()

    def test_language_detection(self):
        # Telugu
        self.assertEqual(DialectProcessor.detect_language("వరి చేనులో ఆకులు ఎండిపోయాయి"), "te")
        self.assertEqual(DialectProcessor.detect_language("చెరకు తోట"), "te")

        # Hindi
        self.assertEqual(DialectProcessor.detect_language("मेरी धान की फसल में कीड़े लगे हैं"), "hi")
        self.assertEqual(DialectProcessor.detect_language("गन्ने में लाल सड़न रोग है"), "hi")
        self.assertEqual(DialectProcessor.detect_language("namaste kisan bhai"), "hi")

        # English
        self.assertEqual(DialectProcessor.detect_language("My sugarcane leaves are drying up"), "en")
        self.assertEqual(DialectProcessor.detect_language("There is blast disease on paddy"), "en")

    def test_step_by_step_telugu_diagnostic_workflow(self):
        session_id = "test_doc_te"
        # 1. Start Call
        start = self.engine.start_call(session_id, phone="+919848022338", lang="te")
        self.assertEqual(start["step"], "ASK_CROP")
        self.assertIn("నమస్కారం", start["spoken_response"])

        # 2. Step 1: Crop Name
        t1 = self.engine.process_turn(session_id, "మాది అనకాపల్లి, చెరకు పంట వేసాను")
        self.assertEqual(t1["step"], "ASK_SYMPTOMS")
        self.assertEqual(t1["detected_lang"], "te")
        self.assertIn("లక్షణాలు", t1["spoken_response"])

        # 3. Step 2: Symptoms
        t2 = self.engine.process_turn(session_id, "ఆకులు ఎర్రబడి పిప్పి వాసన వస్తోంది")
        self.assertEqual(t2["step"], "ASK_DURATION")
        self.assertIn("ఎన్ని రోజులు", t2["spoken_response"])

        # 4. Step 3: Duration
        t3 = self.engine.process_turn(session_id, "నాలుగు రోజుల నుంచి ఉంది")
        self.assertEqual(t3["step"], "ASK_SEVERITY")
        self.assertIn("తీవ్రత", t3["spoken_response"])

        # 5. Step 4: Severity -> Prescription
        t4 = self.engine.process_turn(session_id, "చేను అంతా జాస్తిగా వ్యాపించింది")
        self.assertEqual(t4["step"], "DELIVER_PRESCRIPTION")
        self.assertIn("ఎర్ర కుళ్లు తెగులు", t4["spoken_response"])
        self.assertIn("కార్బండజిమ్", t4["spoken_response"])

    def test_hindi_diagnostic_workflow_and_dynamic_switch(self):
        session_id = "test_doc_hi"
        # Start in Hindi
        start = self.engine.start_call(session_id, phone="+919440112233", lang="hi")
        self.assertEqual(start["detected_lang"], "hi")
        self.assertIn("नमस्ते किसान भाई", start["spoken_response"])

        # Step 1: Crop in Hindi
        t1 = self.engine.process_turn(session_id, "मेरी धान की फसल है")
        self.assertEqual(t1["detected_lang"], "hi")
        self.assertEqual(t1["step"], "ASK_SYMPTOMS")

        # Step 2: Symptoms in Hindi
        t2 = self.engine.process_turn(session_id, "पत्तियों पर भूरे धब्बे पड़ गए हैं और फसल झुलस रही है")
        self.assertEqual(t2["step"], "ASK_DURATION")
        self.assertIn("कितने दिनों", t2["spoken_response"])

        # Dynamic switch: Farmer speaks in English!
        t3 = self.engine.process_turn(session_id, "It has been there for one week")
        self.assertEqual(t3["detected_lang"], "en") # Seamlessly switched to English!
        self.assertEqual(t3["step"], "ASK_SEVERITY")
        self.assertIn("How severe", t3["spoken_response"])

class TestFeature2WeatherService(unittest.TestCase):
    """Tests Feature 2: Missed Call Automatic Weather Voice Service."""

    def test_farmer_registry_lookup(self):
        f = FarmerRegistry.get_farmer_profile("+919848022338")
        self.assertEqual(f["name_en"], "Apparao")
        self.assertIn("Kasimkota", f["village"])
        self.assertEqual(f["preferred_language"], "te")

    def test_dynamic_weather_computation(self):
        # Coordinates for Kasimkota, Anakapalli
        w = WeatherService.fetch_live_weather(17.6534, 82.9856)
        self.assertIn("temperature_c", w)
        self.assertIn("rain_probability", w)
        self.assertIn("wind_speed_kmh", w)
        self.assertGreater(w["temperature_c"], 15.0)
        self.assertLess(w["temperature_c"], 48.0)

    def test_weather_spoken_bulletin_telugu(self):
        farmer = FarmerRegistry.get_farmer_profile("+919848022338")
        report = WeatherService.generate_weather_report(farmer, language="te")
        self.assertEqual(report["language"], "te")
        self.assertIn("అగ్రివాయిస్ ఆటోమేటిక్ వాతావరణ అలర్ట్", report["spoken_report"])
        self.assertIn("Kasimkota", report["spoken_report"])
        self.assertIn("డిగ్రీల సెల్సియస్", report["spoken_report"])

    def test_weather_spoken_bulletin_hindi(self):
        farmer = FarmerRegistry.get_farmer_profile("+919440112233")
        report = WeatherService.generate_weather_report(farmer, language="hi")
        self.assertEqual(report["language"], "hi")
        self.assertIn("मौसम सेवा", report["spoken_report"])
        self.assertIn("डिग्री सेल्सियस", report["spoken_report"])

    def test_weather_spoken_bulletin_english(self):
        farmer = FarmerRegistry.get_farmer_profile("+919123456789")
        report = WeatherService.generate_weather_report(farmer, language="en")
        self.assertEqual(report["language"], "en")
        self.assertIn("AgriVoice Automatic Weather Alert", report["spoken_report"])
        self.assertIn("degrees Celsius", report["spoken_report"])

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_doctor_call_api_flow(self):
        # 1. Start Doctor Call
        res = self.client.post("/api/doctor/call/start", json={"phone": "+919848022338", "lang": "te"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        session_id = data["session_id"]

        # 2. Step 1: Crop
        res2 = self.client.post("/api/doctor/call/turn", json={"session_id": session_id, "utterance": "చెరకు తోట"})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()["step"], "ASK_SYMPTOMS")

    def test_weather_missed_call_api(self):
        res = self.client.post("/api/weather/missed-call", json={"phone": "+919848022338"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["service"], "MISSED_CALL_WEATHER_SERVICE")
        self.assertIn("weather_bulletin", data)

    def test_google_speech_transcribe_api(self):
        # Test Telugu transcription
        res_te = self.client.post("/api/voice/transcribe", json={
            "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            "language": "te-IN"
        })
        self.assertEqual(res_te.status_code, 200)
        data_te = res_te.get_json()
        self.assertIn("transcript", data_te)
        self.assertEqual(data_te["language"], "te-IN")

        # Test Hindi transcription
        res_hi = self.client.post("/api/voice/transcribe", json={
            "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            "language": "hi-IN"
        })
        self.assertEqual(res_hi.status_code, 200)
        self.assertEqual(res_hi.get_json()["language"], "hi-IN")

        # Test English transcription
        res_en = self.client.post("/api/voice/transcribe", json={
            "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            "language": "en-IN"
        })
        self.assertEqual(res_en.status_code, 200)
        self.assertEqual(res_en.get_json()["language"], "en-IN")

if __name__ == "__main__":
    unittest.main()
