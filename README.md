# AgriVoice (అగ్రివాయిస్)
> **Voice-First AI Platform for Feature-Phone Farmers in Rural North Andhra**  
> *Targeted for Smallholders across Visakhapatnam, Anakapalli, and Srikakulam.*

---

## 🌾 The Problem
Over **60% of rural farmers in North Andhra** (Srikakulam, Vizianagaram, Visakhapatnam, Anakapalli) rely on basic keypad phones without internet, mobile apps, or digital literacy. Existing AgriTech tools demand smartphones and apps, while traditional IVR helplines use confusing "Press 1, Press 2" menus and standard coastal Telugu that fail to understand local **Srikakulam and Vizag yaasa (accents)**. This creates severe market exploitation and preventable crop losses due to a lack of accessible real-time advisories.

## 🚀 The Solution: Core Innovations
1. **Zero-Touch Conversational Navigation & 2G Keypad Simulation**:
   - Farmers dial a toll-free number (e.g. `1800-AGRI-VOICE`) and speak naturally or navigate using interactive keypad shortcuts.
   - Eliminates confusing menus through dynamic speech-recognition intent detection and retro phone simulator.
2. **Multi-Turn "Agri-Doctor" Diagnosis (Telugu • Hindi • English)**:
   - Acts like a virtual crop doctor through guided multi-turn dialog: `Crop Type` → `Symptom Verification` → `Timeline & Spread` → `Prescription`.
   - Delivers non-technical, spoken prescriptions with exact dosages per 16-liter knapsack sprayer tank.
3. **Dialect-Aware Localized Support**:
   - Tuned for regional North Andhra *yaasa* (e.g., *యెట్నున్నావ్*, *ఎట్టాగ ఉంది*, *యాడ*, *జాస్తిగా*, *మోడు వారిపోతాంది*, *కాటు పడింది*).
   - Generates warm, local-voice audio responses.
4. **Missed-Call Weather & Mandi Voice Service**:
   - Farmers give a missed call at zero cost.
   - The platform immediately triggers an automated voice callback and SMS with **Anakapalli APMC Mandi prices** and **Live Meteorological Advisory** (Open-Meteo & Coastal atmospheric model).

---

## 📂 Project Structure

```text
agrivoice/
├── app.py                   # Flask server, Telephony VoiceXML/TwiML webhooks & REST API
├── agri_doctor.py           # Multi-turn diagnostic state machine & Crop Pathology KB
├── dialect_processor.py     # Srikakulam / Vizag dialect normalizer & entity extractor
├── farmer_registry.py       # Caller-ID lookup & rural farmer profiles
├── gemini_client.py         # Google Gemini generative AI reasoning
├── google_speech_client.py  # Server-side Google Speech-to-Text v1 interface
├── weather_service.py       # Live Open-Meteo & dynamic coastal meteorological model
├── mandi_weather.py         # Anakapalli/Palasa Mandi prices & Rain alert service
├── templates/
│   └── index.html           # Interactive 2G Keypad Phone Simulator UI
├── static/
│   ├── style.css            # Retro feature phone + modern AI diagnostics styling
│   └── app.js               # Web Speech API, DTMF audio synthesis & call loop
├── tests/                   # 28 unit and live-flow test cases
└── README.md
```

---

## ⚡ Quickstart: Running the Interactive Simulator

```bash
# 1. Install dependencies
pip install -r requirements.txt   # flask flask-cors

# 2. Run the application
python app.py

# 3. Open in browser
http://127.0.0.1:5000
```

---

## 🧪 Running Unit Tests
```bash
python -m unittest discover -s tests
```

---

## 📞 Production Telephony Integration (Exotel / Twilio)
Point your cloud telephony incoming voice webhook to:
- **Inbound Toll-Free Webhook**: `POST /api/telephony/doctor-inbound`
- **Speech Processing Webhook**: `POST /api/telephony/doctor-turn`
- **Missed Call Dispatcher**: `POST /api/telephony/weather-missed-call`
