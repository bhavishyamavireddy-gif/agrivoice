"""
app.py
AgriVoice Backend Server.
FEATURE 1: Multilingual AI Agricultural Doctor Voice Calling (Telugu, Hindi, English).
FEATURE 2: Missed Call Automatic Weather Voice Service (Live Weather + Spoken Advisory).
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import uuid
from dialect_processor import DialectProcessor
from agri_doctor import AgriDoctorEngine
from weather_service import WeatherService
from farmer_registry import FarmerRegistry
from google_speech_client import GoogleSpeechClient

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

doctor_engine = AgriDoctorEngine()

@app.route("/")
def index():
    """Serves the interactive Feature Phone Simulator and Hackathon Dashboard."""
    return render_template("index.html")

# -------------------------------------------------------------
# GOOGLE CLOUD SPEECH-TO-TEXT ENDPOINT
# Safely transcribes recorded farmer audio on the server
# -------------------------------------------------------------
@app.route("/api/voice/transcribe", methods=["POST"])
def voice_transcribe():
    """
    Receives recorded microphone audio (WebM/WAV) from frontend MediaRecorder.
    Calls Google Cloud Speech-to-Text v1 API server-side.
    API keys remain safely on the server and are never exposed to browser.
    """
    language_code = request.form.get("language", "te-IN")
    audio_file = request.files.get("audio")

    if not audio_file:
        data = request.json or {}
        language_code = data.get("language", language_code)
        audio_b64 = data.get("audio_base64", "")
        if audio_b64:
            import base64
            audio_bytes = base64.b64decode(audio_b64)
            mime_type = data.get("mime_type", "audio/webm")
        else:
            return jsonify({"status": "error", "message": "No audio file uploaded"}), 400
    else:
        audio_bytes = audio_file.read()
        mime_type = audio_file.content_type or "audio/webm"

    result = GoogleSpeechClient.transcribe_audio(
        audio_bytes=audio_bytes,
        language_code=language_code,
        mime_type=mime_type
    )

    return jsonify(result)

# -------------------------------------------------------------
# FEATURE 1: MULTILINGUAL AI AGRI-DOCTOR VOICE CALLING
# -------------------------------------------------------------
@app.route("/api/doctor/call/start", methods=["POST"])
def doctor_call_start():
    """
    Farmer calls the AI Agri Doctor.
    Answers call and delivers greeting in caller's preferred or detected language.
    """
    data = request.json or {}
    session_id = data.get("session_id", str(uuid.uuid4())[:8])
    phone = data.get("phone", "+919848022338")
    initial_lang = data.get("lang", "te")

    doctor_engine.reset_session(session_id)
    result = doctor_engine.start_call(session_id=session_id, phone=phone, lang=initial_lang)

    return jsonify({
        "status": "success",
        "service": "AI_AGRI_DOCTOR",
        **result
    })

@app.route("/api/doctor/call/turn", methods=["POST"])
def doctor_call_turn():
    """
    Processes farmer's spoken turn:
    - Automatically detects language (Telugu, Hindi, English).
    - Maintains language continuity or adapts dynamically if farmer switches.
    - Asks questions one by one: Crop -> Symptoms -> Duration -> Severity -> Prescription.
    - Delivers diagnosis and knapsack sprayer treatment via spoken audio.
    """
    data = request.json or {}
    session_id = data.get("session_id")
    utterance = data.get("utterance", "").strip()

    if not session_id or not utterance:
        return jsonify({"status": "error", "message": "Missing session_id or utterance"}), 400

    result = doctor_engine.process_turn(session_id, utterance)
    return jsonify({
        "status": "success",
        "service": "AI_AGRI_DOCTOR",
        **result
    })

@app.route("/api/doctor/call/reset", methods=["POST"])
def doctor_call_reset():
    """Terminates or resets active Agri-Doctor session."""
    data = request.json or {}
    session_id = data.get("session_id")
    if session_id:
        doctor_engine.reset_session(session_id)
    return jsonify({"status": "success", "message": "Session reset"})

# -------------------------------------------------------------
# FEATURE 2: MISSED CALL AUTOMATIC WEATHER VOICE SERVICE
# -------------------------------------------------------------
@app.route("/api/weather/missed-call", methods=["POST"])
def weather_missed_call():
    """
    Farmer gives a missed call at zero cost.
    1. Identifies caller ID / phone number.
    2. Identifies registered village and GPS coordinates.
    3. Fetches latest dynamic live weather forecast (not static).
    4. Generates spoken weather report in farmer's preferred language (Telugu/Hindi/English).
    5. Includes temperature, rain probability, wind conditions, and spray advisories.
    6. Schedules immediate audio callback.
    """
    data = request.json or {}
    phone = data.get("phone", "+919848022338")
    override_lang = data.get("lang")

    # 1. Lookup farmer profile
    farmer_profile = FarmerRegistry.get_farmer_profile(phone)
    target_lang = override_lang if override_lang else farmer_profile.get("preferred_language", "te")

    # 2. Generate live weather report and spoken audio script
    report = WeatherService.generate_weather_report(farmer_profile, language=target_lang)

    return jsonify({
        "status": "success",
        "service": "MISSED_CALL_WEATHER_SERVICE",
        "message": "Missed call registered. Zero-balance outbound callback scheduled.",
        "callback_delay_sec": 3,
        "caller_phone": phone,
        "detected_farmer": farmer_profile,
        "weather_bulletin": report
    })

@app.route("/api/farmers", methods=["GET"])
def list_farmers():
    """Returns demo registered farmers for easy hackathon demonstration."""
    return jsonify({
        "status": "success",
        "farmers": FarmerRegistry.list_all_farmers()
    })

# -------------------------------------------------------------
# REAL CLOUD TELEPHONY WEBHOOKS (Exotel / Twilio VoiceXML / TwiML)
# Clearly separated from simulator browser endpoints
# -------------------------------------------------------------
@app.route("/api/telephony/doctor-inbound", methods=["GET", "POST"])
def telephony_doctor_inbound():
    """Telephony gateway entry point for inbound farmer call to 1800-AGRI-VOICE."""
    caller_phone = request.values.get("From", "+919848022338")
    session_id = f"tele_{uuid.uuid4().hex[:6]}"
    
    # Auto identify caller language preference
    farmer = FarmerRegistry.get_farmer_profile(caller_phone)
    lang = farmer.get("preferred_language", "te")
    start_data = doctor_engine.start_call(session_id, phone=caller_phone, lang=lang)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="{ 'hi-IN' if lang == 'hi' else 'en-IN' if lang == 'en' else 'te-IN' }">
        {start_data['spoken_response']}
    </Say>
    <Gather input="speech" timeout="6" speechTimeout="auto" action="/api/telephony/doctor-turn?sessionId={session_id}" language="te-IN,hi-IN,en-IN"/>
</Response>"""
    return Response(twiml, mimetype="application/xml")

@app.route("/api/telephony/doctor-turn", methods=["POST"])
def telephony_doctor_turn():
    """Telephony webhook handling caller speech from PSTN feature phone."""
    session_id = request.args.get("sessionId", "call_default")
    speech_result = request.values.get("SpeechResult", "")

    result = doctor_engine.process_turn(session_id, speech_result)
    spoken_text = result["spoken_response"]
    lang = result["detected_lang"]
    is_active = result["is_call_active"]

    voice_code = 'hi-IN' if lang == 'hi' else 'en-IN' if lang == 'en' else 'te-IN'

    if is_active:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="{voice_code}">{spoken_text}</Say>
    <Gather input="speech" timeout="6" speechTimeout="auto" action="/api/telephony/doctor-turn?sessionId={session_id}" language="te-IN,hi-IN,en-IN"/>
</Response>"""
    else:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="{voice_code}">{spoken_text}</Say>
    <Hangup/>
</Response>"""

    return Response(twiml, mimetype="application/xml")

@app.route("/api/telephony/weather-missed-call", methods=["GET", "POST"])
def telephony_weather_missed_call():
    """Webhook invoked by telecom provider when a farmer dials the missed-call number."""
    caller_phone = request.values.get("From", "+919848022338")
    farmer = FarmerRegistry.get_farmer_profile(caller_phone)
    report = WeatherService.generate_weather_report(farmer, language=farmer.get("preferred_language", "te"))

    # Return VoiceXML that immediately drops the call after 1 ring, then triggers OBD callback
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Reject reason="busy"/>
    <!-- Cloud Telephony Outbound Dialer triggers callback using report['spoken_report'] -->
</Response>"""
    return Response(twiml, mimetype="application/xml")

# -------------------------------------------------------------
# BACKWARDS COMPATIBILITY ROUTES (Legacy Aliases)
# -------------------------------------------------------------
@app.route("/api/session/start", methods=["POST"])
def legacy_session_start():
    return doctor_call_start()

@app.route("/api/session/turn", methods=["POST"])
def legacy_session_turn():
    return doctor_call_turn()

@app.route("/api/missed-call", methods=["POST"])
def legacy_missed_call():
    return weather_missed_call()

@app.route("/api/telephony/inbound", methods=["GET", "POST"])
def legacy_telephony_inbound():
    return telephony_doctor_inbound()

if __name__ == "__main__":
    print("Starting AgriVoice Multilingual Voice Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
