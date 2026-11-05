import unittest
import os
import re

class TestUIElements(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(base_dir, "templates", "index.html"), encoding="utf-8") as f:
            self.html = f.read()
        with open(os.path.join(base_dir, "static", "app.js"), encoding="utf-8") as f:
            self.js = f.read()

    def test_all_required_button_ids_in_html(self):
        required_ids = [
            'btnDoctorCall', 'btnWeatherMissedCall', 'btnEndCall', 'btnKeypadOk',
            'btnSoftLeft', 'btnSoftRight', 'btnDpadUp', 'btnDpadDown', 'btnDpadLeft', 'btnDpadRight',
            'keypad1', 'keypad2', 'keypad3', 'keypad4', 'keypad5', 'keypad6',
            'keypad7', 'keypad8', 'keypad9', 'keypad0', 'keypadStar', 'keypadHash',
            'selMicLanguage', 'selFarmerProfile', 'btnReplayAudio', 'btnWeatherReplay',
            'screenIdle', 'screenActiveCall', 'screenIncoming', 'screenStatusBadge',
            'menuItem1', 'menuItem2', 'screenNumberPreview', 'channelIndicator', 'channelStatusText'
        ]
        for elem_id in required_ids:
            self.assertIn(f'id="{elem_id}"', self.html, f"Missing id '{elem_id}' in index.html")

    def test_keypad_keys_have_data_key_attributes(self):
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        for k in keys:
            self.assertIn(f'data-key="{k}"', self.html, f"Missing data-key for '{k}' in keypad")

    def test_javascript_event_handlers_bound(self):
        # Verify event listener bindings in app.js
        bindings = [
            'btnDoctorCall.addEventListener',
            'btnWeatherMissedCall.addEventListener',
            'btnEndCall.addEventListener',
            'btnKeypadOk.addEventListener',
            'btnSoftLeft.addEventListener',
            'btnSoftRight.addEventListener',
            'btnMicTrigger.addEventListener',
            'btnReplayAudio.addEventListener',
            'btnWeatherReplay.addEventListener',
            'numKeys.forEach',
            'selFarmerProfile.addEventListener',
            'selMicLanguage.addEventListener'
        ]
        for b in bindings:
            self.assertIn(b, self.js, f"Missing listener binding '{b}' in app.js")

    def test_dynamic_statuses_handled_in_js(self):
        statuses = ['IDLE', 'CALLING', 'CONNECTED', 'LISTENING', 'PROCESSING', 'SPEAKING', 'CALL_ENDED', 'ERROR']
        for s in statuses:
            self.assertIn(f"case '{s}':", self.js, f"Status '{s}' not handled in updateSystemStatus switch")

    def test_multilingual_language_support(self):
        # Ensure Telugu, Hindi, English are mapped in speech synthesis and recognition
        self.assertIn("'te-IN'", self.js)
        self.assertIn("'hi-IN'", self.js)
        self.assertIn("'en-IN'", self.js)

if __name__ == '__main__':
    unittest.main()
