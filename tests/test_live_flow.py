import unittest
import json
from app import app

class TestLiveFlow(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_feature1_doctor_call_telugu(self):
        # Start call in Telugu
        res = self.client.post("/api/doctor/call/start", json={
            "phone": "+919848022338",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["detected_lang"], "te")
        self.assertEqual(data["step"], "ASK_CROP")
        session_id = data["session_id"]

        # Turn 1: Farmer mentions crop (చెరకు)
        res1 = self.client.post("/api/doctor/call/turn", json={
            "session_id": session_id,
            "utterance": "మాది అనకాపల్లి, చెరకు పంట వేసాను బాబూ"
        })
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertEqual(data1["detected_lang"], "te")
        self.assertEqual(data1["step"], "ASK_SYMPTOMS")

        # Turn 2: Farmer describes symptoms (ఎర్ర కుళ్లు)
        res2 = self.client.post("/api/doctor/call/turn", json={
            "session_id": session_id,
            "utterance": "ఆకులు ఎండిపోయాయి, గడ లోపల ఎర్రగా ఉంది, పిప్పి వాసన వస్తోంది"
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2["detected_lang"], "te")
        self.assertEqual(data2["step"], "ASK_DURATION")

        # Turn 3: Duration
        res3 = self.client.post("/api/doctor/call/turn", json={
            "session_id": session_id,
            "utterance": "వారం రోజులు అయ్యింది"
        })
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertEqual(data3["detected_lang"], "te")
        self.assertEqual(data3["step"], "ASK_SEVERITY")

        # Turn 4: Severity -> Delivers prescription
        res4 = self.client.post("/api/doctor/call/turn", json={
            "session_id": session_id,
            "utterance": "చేను అంతా వ్యాపించింది"
        })
        self.assertEqual(res4.status_code, 200)
        data4 = res4.get_json()
        self.assertEqual(data4["detected_lang"], "te")
        self.assertIn("DELIVER_PRESCRIPTION", [data4["step"], "COMPLETED"])
        self.assertIn("కార్బండజిమ్", data4["spoken_response"])

    def test_feature1_doctor_call_hindi(self):
        res = self.client.post("/api/doctor/call/start", json={
            "phone": "+919440112233",
            "lang": "hi"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["detected_lang"], "hi")
        self.assertIn("नमस्ते", data["spoken_response"])

    def test_feature1_doctor_call_english(self):
        res = self.client.post("/api/doctor/call/start", json={
            "phone": "+919123456789",
            "lang": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["detected_lang"], "en")
        self.assertIn("Hello", data["spoken_response"])

    def test_feature2_missed_call_weather(self):
        res = self.client.post("/api/weather/missed-call", json={
            "phone": "+919848022338",
            "lang": "te"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        bulletin = data["weather_bulletin"]
        self.assertEqual(bulletin["language"], "te")
        metrics = bulletin["weather_metrics"]
        self.assertIn("temperature_c", metrics)
        self.assertIn("rain_probability", metrics)
        self.assertIn("wind_speed_kmh", metrics)
        self.assertIn("safe_to_spray", metrics)
        self.assertTrue(len(bulletin["spoken_report"]) > 20)

if __name__ == '__main__':
    unittest.main()
