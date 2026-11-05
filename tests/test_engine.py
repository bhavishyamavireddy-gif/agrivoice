"""
test_engine.py
Legacy test suite updated for upgraded Trilingual architecture.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dialect_processor import DialectProcessor
from agri_doctor import AgriDoctorEngine
from weather_service import WeatherService
from farmer_registry import FarmerRegistry
from app import app

class TestDialectProcessor(unittest.TestCase):
    def test_dialect_normalization(self):
        sample = "మా సేల్లో వరి అంతా మోడు వారిపోతాంది, జాస్తిగా ఉంది"
        normalized = DialectProcessor.normalize_text(sample)
        self.assertIn("చేనులో", normalized)
        self.assertIn("ఎండిపోతోంది", normalized)
        self.assertIn("ఎక్కువగా", normalized)

    def test_crop_extraction_telugu(self):
        key, te_name, en_name, hi_name = DialectProcessor.extract_crop("మా అనకాపల్లి చెరకు తోటలో పురుగు పట్టింది")
        self.assertEqual(key, "sugarcane")
        self.assertIn("చెరకు", te_name)
        self.assertIn("Sugarcane", en_name)
        self.assertIn("गन्ना", hi_name)

    def test_crop_extraction_english(self):
        key, te_name, en_name, hi_name = DialectProcessor.extract_crop("My sugarcane crop has red stems in Anakapalli")
        self.assertEqual(key, "sugarcane")
        self.assertIn("Sugarcane", en_name)

    def test_intent_detection(self):
        self.assertEqual(DialectProcessor.extract_intent("అనకాపల్లి బెల్లం రేటు ఎంత?"), "MANDI_PRICE")
        self.assertEqual(DialectProcessor.extract_intent("రేపు భారీ వర్షం పడుతుందా?"), "WEATHER_QUERY")
        self.assertEqual(DialectProcessor.extract_intent("धान की फसल में रोग लगा है"), "CROP_DIAGNOSIS")

class TestAgriDoctorEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AgriDoctorEngine()

    def test_multi_turn_paddy_blast_telugu(self):
        session_id = "test_farmer_te"
        self.engine.start_call(session_id, lang="te")
        res1 = self.engine.process_turn(session_id, "వరి పంట")
        self.assertEqual(res1["session"]["crop_key"], "paddy")
        self.assertEqual(res1["step"], "ASK_SYMPTOMS")

    def test_multi_turn_sugarcane_english(self):
        session_id = "test_farmer_en"
        self.engine.start_call(session_id, lang="en")
        res1 = self.engine.process_turn(session_id, "I grow sugarcane in Anakapalli")
        self.assertEqual(res1["session"]["crop_key"], "sugarcane")
        self.assertEqual(res1["step"], "ASK_SYMPTOMS")

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_session_lifecycle(self):
        start_res = self.client.post("/api/doctor/call/start", json={"phone": "+919848022338", "lang": "te"})
        self.assertEqual(start_res.status_code, 200)
        data = start_res.get_json()
        session_id = data["session_id"]
        self.assertIn("నమస్కారం", data["spoken_response"])

    def test_telephony_inbound_twiml(self):
        res = self.client.post("/api/telephony/doctor-inbound", data={"From": "+919848022338"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("<Response>", res.text)
        self.assertIn("Say", res.text)

if __name__ == "__main__":
    unittest.main()
