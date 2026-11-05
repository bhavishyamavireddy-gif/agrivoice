/**
 * app.js
 * AgriVoice - Inclusive Voice-First AI Platform for Rural Feature-Phone Farmers.
 *
 * Fully dynamic and interactive rural farmer service:
 * 1. Keypad Phone Interface (0-9, *, #, OK, Back, Navigation, DTMF synth tones)
 * 2. Feature 1: Multi-Turn AI Agricultural Doctor Voice Calling (Telugu, Hindi, English)
 * 3. Feature 2: Automatic Missed-Call Weather Voice Service (Open-Meteo & Coastal Model)
 * 4. Dynamic Menu Navigation & Number Dialing / Deletion
 * 5. Strict Language Continuity (Telugu, Hindi, English)
 * 6. Real-Time Dynamic Statuses (Idle, Calling, Connected, Listening, Processing, Speaking, Call Ended, Error)
 * 7. Audio Replay Controls & Web Speech API Integration
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // 1. STATE MANAGEMENT
    // -------------------------------------------------------------
    let currentSessionId = null;
    let isCallActive = false;
    let isDialing = false;
    let activeService = null; // "DOCTOR_CALL" or "WEATHER_MISSED_CALL"
    let callTimerInterval = null;
    let callSeconds = 0;
    let recognition = null;
    let isListening = false;
    let audioOutputEnabled = true;
    let activeLanguage = "te"; // "te", "hi", "en"
    let dialedBuffer = "";
    let selectedMenuIndex = 1; // 1 = AI Doctor Call, 2 = Weather Alert
    let lastSpokenText = "";
    let lastSpokenLang = "te";
    let systemStatus = "IDLE"; // "IDLE", "CALLING", "CONNECTED", "LISTENING", "PROCESSING", "SPEAKING", "CALL_ENDED", "ERROR"

    // Registered Farmer Database (Caller ID Lookup)
    const FARMERS = {
        "+919848022338": { name: "Apparao", village: "Kasimkota, Anakapalli", crop: "Sugarcane", lang: "te", langName: "Telugu (తెలుగు)" },
        "+919440112233": { name: "Rajesh Verma", village: "Pendurthi, Vizag", crop: "Paddy", lang: "hi", langName: "Hindi (हिन्दी)" },
        "+919866554433": { name: "K. Satyam", village: "Palasa, Srikakulam", crop: "Cashew", lang: "te", langName: "Telugu (తెలుగు)" },
        "+919123456789": { name: "John Peter", village: "Tagarapuvalasa, Bheemili", crop: "Groundnut", lang: "en", langName: "English" }
    };

    // -------------------------------------------------------------
    // 2. DOM ELEMENTS SELECTION
    // -------------------------------------------------------------
    // Farmer Profile Bar
    const selFarmerProfile = document.getElementById('selFarmerProfile');
    const pillVillage = document.getElementById('pillVillage');
    const pillCrop = document.getElementById('pillCrop');
    const pillLang = document.getElementById('pillLang');

    // Mode Switcher
    const tabSimulatorMode = document.getElementById('tabSimulatorMode');
    const tabTelephonyMode = document.getElementById('tabTelephonyMode');
    const simulatorViewContainer = document.getElementById('simulatorViewContainer');
    const telephonyViewContainer = document.getElementById('telephonyViewContainer');

    // Phone Screen
    const screenIdle = document.getElementById('screenIdle');
    const screenActiveCall = document.getElementById('screenActiveCall');
    const screenIncoming = document.getElementById('screenIncoming');
    const screenClock = document.getElementById('screenClock');
    const screenStatusBadge = document.getElementById('screenStatusBadge');
    const menuItem1 = document.getElementById('menuItem1');
    const menuItem2 = document.getElementById('menuItem2');
    const screenNumberPreview = document.getElementById('screenNumberPreview');
    const screenCallerTitle = document.getElementById('screenCallerTitle');
    const callServiceHeader = document.getElementById('callServiceHeader');
    const callStatusSub = document.getElementById('callStatusSub');
    const callDtmfFeedback = document.getElementById('callDtmfFeedback');
    const lblCallDuration = document.getElementById('lblCallDuration');
    const liveSubtitleBox = document.getElementById('liveSubtitleBox');
    const voiceWave = document.getElementById('voiceWave');
    const incomingSubText = document.getElementById('incomingSubText');
    const screenFooterLeft = document.getElementById('screenFooterLeft');
    const screenFooterRight = document.getElementById('screenFooterRight');

    // Action Buttons
    const btnDoctorCall = document.getElementById('btnDoctorCall');
    const btnWeatherMissedCall = document.getElementById('btnWeatherMissedCall');
    const btnEndCall = document.getElementById('btnEndCall');

    // Navigation & D-Pad
    const btnSoftLeft = document.getElementById('btnSoftLeft');
    const btnSoftRight = document.getElementById('btnSoftRight');
    const btnKeypadOk = document.getElementById('btnKeypadOk');
    const btnDpadUp = document.getElementById('btnDpadUp');
    const btnDpadDown = document.getElementById('btnDpadDown');
    const btnDpadLeft = document.getElementById('btnDpadLeft');
    const btnDpadRight = document.getElementById('btnDpadRight');
    const numKeys = document.querySelectorAll('.num-key');

    // Voice Input & Replay Controls
    const btnMicTrigger = document.getElementById('btnMicTrigger');
    const btnSendUtterance = document.getElementById('btnSendUtterance');
    const btnReplayAudio = document.getElementById('btnReplayAudio');
    const btnWeatherReplay = document.getElementById('btnWeatherReplay');
    const customUtteranceInput = document.getElementById('customUtteranceInput');
    const selMicLanguage = document.getElementById('selMicLanguage');
    const voiceStatusMsg = document.getElementById('voiceStatusMsg');
    const chkAudioOutput = document.getElementById('chkAudioOutput');
    const btnClearLog = document.getElementById('btnClearLog');

    // Monitor Header Statuses
    const channelIndicator = document.getElementById('channelIndicator');
    const channelStatusText = document.getElementById('channelStatusText');
    const langDetectedBadge = document.getElementById('langDetectedBadge');
    const audioEngineStatus = document.getElementById('audioEngineStatus');

    // Step Pipeline (Feature 1)
    const currentStepBadge = document.getElementById('currentStepBadge');
    const stepNode1 = document.getElementById('stepNode1');
    const stepNode2 = document.getElementById('stepNode2');
    const stepNode3 = document.getElementById('stepNode3');
    const stepNode4 = document.getElementById('stepNode4');
    const stepNode5 = document.getElementById('stepNode5');
    const stepLine1 = document.getElementById('stepLine1');
    const stepLine2 = document.getElementById('stepLine2');
    const stepLine3 = document.getElementById('stepLine3');
    const stepLine4 = document.getElementById('stepLine4');
    const diagCrop = document.getElementById('diagCrop');
    const diagDisease = document.getElementById('diagDisease');
    const diagSymptoms = document.getElementById('diagSymptoms');
    const diagDurationSeverity = document.getElementById('diagDurationSeverity');
    const prescriptionBody = document.getElementById('prescriptionBody');

    // Weather Metrics (Feature 2)
    const weatherSourceBadge = document.getElementById('weatherSourceBadge');
    const metricTemp = document.getElementById('metricTemp');
    const metricRain = document.getElementById('metricRain');
    const metricWind = document.getElementById('metricWind');
    const metricSpray = document.getElementById('metricSpray');
    const weatherSpokenPreview = document.getElementById('weatherSpokenPreview');
    const transcriptScroll = document.getElementById('transcriptScroll');

    // -------------------------------------------------------------
    // 3. RETRO KEYPAD DTMF AUDIO SYNTHESIZER (Web Audio API)
    // -------------------------------------------------------------
    function playKeypadTone(key) {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            if (!window._agriAudioCtx) {
                window._agriAudioCtx = new AudioContext();
            }
            if (window._agriAudioCtx.state === 'suspended') {
                window._agriAudioCtx.resume();
            }
            const dtmfFrequencies = {
                '1': [697, 1209], '2': [697, 1336], '3': [697, 1477],
                '4': [770, 1209], '5': [770, 1336], '6': [770, 1477],
                '7': [852, 1209], '8': [852, 1336], '9': [852, 1477],
                '*': [941, 1209], '0': [941, 1336], '#': [941, 1477]
            };
            const freqs = dtmfFrequencies[key] || [750, 1200];
            const now = window._agriAudioCtx.currentTime;
            freqs.forEach(f => {
                const osc = window._agriAudioCtx.createOscillator();
                const gain = window._agriAudioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, now);
                gain.gain.setValueAtTime(0.06, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);
                osc.connect(gain);
                gain.connect(window._agriAudioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.12);
            });
        } catch (e) {
            // Ignore audio context autoplay restriction gracefully
        }
    }

    // -------------------------------------------------------------
    // 4. CENTRAL REAL-TIME STATUS CONTROLLER (Requirement 6)
    // -------------------------------------------------------------
    function updateSystemStatus(status, customSub = null) {
        systemStatus = status;
        console.log(`[AgriVoice Status] -> ${status}${customSub ? ` (${customSub})` : ''}`);

        // Reset channel indicator status classes
        channelIndicator.className = 'channel-indicator';

        switch (status) {
            case 'IDLE':
                channelIndicator.classList.add('status-idle');
                channelStatusText.textContent = "IDLE (Awaiting Call)";
                if (screenStatusBadge) screenStatusBadge.textContent = "IDLE • స్టాండ్‌బై";
                audioEngineStatus.textContent = "Idle ⏸️";
                voiceWave.style.opacity = '0.3';

                btnDoctorCall.disabled = false;
                btnWeatherMissedCall.disabled = false;
                btnEndCall.disabled = true;

                if (screenFooterLeft) screenFooterLeft.textContent = "Select [OK]";
                if (screenFooterRight) screenFooterRight.textContent = "⌫ Clear";
                break;

            case 'CALLING':
                channelIndicator.classList.add('status-calling');
                channelStatusText.textContent = "CALLING (Connecting Channel...)";
                if (screenStatusBadge) screenStatusBadge.textContent = "CALLING • కాలింగ్...";
                callStatusSub.textContent = customSub || "Connecting voice channel...";
                audioEngineStatus.textContent = "Connecting 📞";
                voiceWave.style.opacity = '0.5';

                btnDoctorCall.disabled = true;
                btnWeatherMissedCall.disabled = true;
                btnEndCall.disabled = false;

                if (screenFooterLeft) screenFooterLeft.textContent = "Options";
                if (screenFooterRight) screenFooterRight.textContent = "Hang Up";
                break;

            case 'CONNECTED':
                channelIndicator.classList.add('status-connected');
                channelStatusText.textContent = activeService === 'DOCTOR_CALL' ? "CONNECTED (AI Doctor Live)" : "CONNECTED (Weather Broadcast)";
                callStatusSub.textContent = customSub || "Channel live. Listening...";
                audioEngineStatus.textContent = "Connected 🟢";
                voiceWave.style.opacity = '0.7';

                btnDoctorCall.disabled = true;
                btnWeatherMissedCall.disabled = true;
                btnEndCall.disabled = false;

                if (screenFooterLeft) screenFooterLeft.textContent = "Replay [OK]";
                if (screenFooterRight) screenFooterRight.textContent = "Hang Up";
                break;

            case 'LISTENING':
                channelIndicator.classList.add('status-listening');
                channelStatusText.textContent = "LISTENING (Awaiting Farmer Speech)";
                callStatusSub.textContent = customSub || `Listening in ${getLangLabel(activeLanguage)}... Speak now`;
                audioEngineStatus.textContent = "Listening 🎙️";
                voiceWave.style.opacity = '1';

                btnDoctorCall.disabled = true;
                btnWeatherMissedCall.disabled = true;
                btnEndCall.disabled = false;
                break;

            case 'PROCESSING':
                channelIndicator.classList.add('status-processing');
                channelStatusText.textContent = "PROCESSING (AI Doctor Thinking...)";
                callStatusSub.textContent = customSub || "AI Doctor diagnosing symptoms...";
                audioEngineStatus.textContent = "Thinking ⚙️";
                voiceWave.style.opacity = '0.4';

                btnDoctorCall.disabled = true;
                btnWeatherMissedCall.disabled = true;
                btnEndCall.disabled = false;
                break;

            case 'SPEAKING':
                channelIndicator.classList.add('status-speaking');
                channelStatusText.textContent = "SPEAKING (Spoken Voice Broadcast)";
                callStatusSub.textContent = customSub || (activeService === 'DOCTOR_CALL' ? "AI Doctor Speaking..." : "Weather Broadcast Speaking...");
                audioEngineStatus.textContent = "Speaking 🔊";
                voiceWave.style.opacity = '1';

                btnDoctorCall.disabled = true;
                btnWeatherMissedCall.disabled = true;
                btnEndCall.disabled = false;
                break;

            case 'CALL_ENDED':
                channelIndicator.classList.add('status-ended');
                channelStatusText.textContent = "CALL ENDED (Channel Released)";
                if (screenStatusBadge) screenStatusBadge.textContent = "CALL ENDED • కాల్ ముగిసింది";
                callStatusSub.textContent = "Call ended. Returning to Idle...";
                audioEngineStatus.textContent = "Idle ⏸️";
                voiceWave.style.opacity = '0.2';

                btnDoctorCall.disabled = false;
                btnWeatherMissedCall.disabled = false;
                btnEndCall.disabled = true;
                break;

            case 'ERROR':
                channelIndicator.classList.add('status-error');
                channelStatusText.textContent = "ERROR (Check Connection / Mic)";
                if (screenStatusBadge) screenStatusBadge.textContent = "ERROR • లోపం";
                callStatusSub.textContent = customSub || "Error encountered.";
                audioEngineStatus.textContent = "Error ⚠️";
                voiceWave.style.opacity = '0.2';

                btnDoctorCall.disabled = false;
                btnWeatherMissedCall.disabled = false;
                break;
        }
    }

    function getLangLabel(lang) {
        if (lang === 'hi') return 'Hindi (हिन्दी)';
        if (lang === 'en') return 'English';
        return 'Telugu (తెలుగు)';
    }

    function showVoiceMessage(msg, type = 'info') {
        if (!voiceStatusMsg) return;
        voiceStatusMsg.textContent = msg;
        if (type === 'error') voiceStatusMsg.style.color = '#f87171';
        else if (type === 'listening' || type === 'success') voiceStatusMsg.style.color = '#34d399';
        else if (type === 'warning') voiceStatusMsg.style.color = '#fbbf24';
        else voiceStatusMsg.style.color = '#38bdf8';
    }

    // -------------------------------------------------------------
    // 5. CLOCK & MODE TOGGLES
    // -------------------------------------------------------------
    function updateClock() {
        const now = new Date();
        if (screenClock) {
            screenClock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    tabSimulatorMode.addEventListener('click', () => {
        tabSimulatorMode.classList.add('active');
        tabTelephonyMode.classList.remove('active');
        simulatorViewContainer.classList.remove('hidden');
        telephonyViewContainer.classList.add('hidden');
    });

    tabTelephonyMode.addEventListener('click', () => {
        tabTelephonyMode.classList.add('active');
        tabSimulatorMode.classList.remove('active');
        telephonyViewContainer.classList.remove('hidden');
        simulatorViewContainer.classList.add('hidden');
    });

    // -------------------------------------------------------------
    // 6. FARMER SELECTION & LANGUAGE CONTROLS (Requirement 5)
    // -------------------------------------------------------------
    selFarmerProfile.addEventListener('change', (e) => {
        const phone = e.target.value;
        const profile = FARMERS[phone] || FARMERS["+919848022338"];
        pillVillage.textContent = `📍 ${profile.village}`;
        pillCrop.textContent = `🌱 Crop: ${profile.crop}`;
        pillLang.textContent = `🌐 Registered Lang: ${profile.langName}`;
        activeLanguage = profile.lang;
        updateLangBadge(activeLanguage);

        if (selMicLanguage) {
            if (profile.lang === 'hi') selMicLanguage.value = 'hi-IN';
            else if (profile.lang === 'en') selMicLanguage.value = 'en-IN';
            else selMicLanguage.value = 'te-IN';
        }
        showVoiceMessage(`Farmer profile updated to ${profile.name} (${profile.village}). Preferred language: ${profile.langName}.`, 'info');
    });

    if (selMicLanguage) {
        selMicLanguage.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val === 'hi-IN') activeLanguage = 'hi';
            else if (val === 'en-IN') activeLanguage = 'en';
            else activeLanguage = 'te';
            updateLangBadge(activeLanguage);
            showVoiceMessage(`Language selector set to ${getLangLabel(activeLanguage)}.`, 'info');
        });
    }

    function updateLangBadge(lang) {
        if (lang === 'hi') {
            langDetectedBadge.innerHTML = '🇮🇳 Hindi / हिन्दी (Active)';
            langDetectedBadge.style.color = '#f59e0b';
            langDetectedBadge.style.borderColor = 'rgba(245, 158, 11, 0.4)';
        } else if (lang === 'en') {
            langDetectedBadge.innerHTML = '🇬🇧 English (Active)';
            langDetectedBadge.style.color = '#38bdf8';
            langDetectedBadge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
        } else {
            langDetectedBadge.innerHTML = '🇮🇳 Telugu / తెలుగు (Active)';
            langDetectedBadge.style.color = '#10b981';
            langDetectedBadge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        }
    }

    function cycleLanguage() {
        if (activeLanguage === 'te') {
            activeLanguage = 'hi';
            if (selMicLanguage) selMicLanguage.value = 'hi-IN';
        } else if (activeLanguage === 'hi') {
            activeLanguage = 'en';
            if (selMicLanguage) selMicLanguage.value = 'en-IN';
        } else {
            activeLanguage = 'te';
            if (selMicLanguage) selMicLanguage.value = 'te-IN';
        }
        updateLangBadge(activeLanguage);
        playKeypadTone('#');
        showVoiceMessage(`Language switched to: ${getLangLabel(activeLanguage)}.`, 'info');

        if (isCallActive) {
            callDtmfFeedback.textContent = `Language: ${getLangLabel(activeLanguage)}`;
        } else {
            screenNumberPreview.textContent = `LANG: ${activeLanguage.toUpperCase()}`;
            setTimeout(() => {
                screenNumberPreview.textContent = dialedBuffer || "1800-AGRI-VOICE";
            }, 1200);
        }
    }

    // -------------------------------------------------------------
    // 7. DYNAMIC KEYPAD & NAVIGATION (Requirements 1 & 4)
    // -------------------------------------------------------------
    function updateMenuHighlight() {
        if (selectedMenuIndex === 1) {
            menuItem1.classList.add('active-menu');
            menuItem2.classList.remove('active-menu');
        } else {
            menuItem2.classList.add('active-menu');
            menuItem1.classList.remove('active-menu');
        }
    }

    // Handle number key presses (0-9, *, #)
    numKeys.forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-key');
            handleKeyInput(key, btn);
        });
    });

    function handleKeyInput(key, btnElement = null) {
        console.log(`[AgriVoice Keypad] Key pressed: ${key}`);
        playKeypadTone(key);

        if (btnElement) {
            btnElement.classList.add('pressed');
            setTimeout(() => btnElement.classList.remove('pressed'), 140);
        }

        // If call is active: process DTMF input or Replay
        if (isCallActive) {
            callDtmfFeedback.textContent = `DTMF Key [${key}] sent over GSM channel`;
            if (key === '0') {
                // Key 0 during call triggers Replay
                replayLastAudio();
            } else if (key === '#') {
                cycleLanguage();
            }
            return;
        }

        // If Idle: Menu Selection and Number Dialing / Buffer
        if (key === '#') {
            cycleLanguage();
            return;
        }

        if (key === '1') {
            selectedMenuIndex = 1;
            updateMenuHighlight();
            if (dialedBuffer.length === 0) {
                dialedBuffer = "1";
            } else if (dialedBuffer.length < 16) {
                dialedBuffer += "1";
            }
            screenNumberPreview.textContent = dialedBuffer;
            return;
        }

        if (key === '2') {
            selectedMenuIndex = 2;
            updateMenuHighlight();
            if (dialedBuffer.length === 0) {
                dialedBuffer = "2";
            } else if (dialedBuffer.length < 16) {
                dialedBuffer += "2";
            }
            screenNumberPreview.textContent = dialedBuffer;
            return;
        }

        // Other digits (0, 3-9, *)
        if (dialedBuffer.length < 16) {
            dialedBuffer += key;
            screenNumberPreview.textContent = dialedBuffer;
        }
    }

    // D-Pad Up / Down Navigation
    btnDpadUp.addEventListener('click', () => {
        playKeypadTone('2');
        selectedMenuIndex = 1;
        updateMenuHighlight();
    });

    btnDpadDown.addEventListener('click', () => {
        playKeypadTone('8');
        selectedMenuIndex = 2;
        updateMenuHighlight();
    });

    btnDpadLeft.addEventListener('click', () => {
        playKeypadTone('4');
    });

    btnDpadRight.addEventListener('click', () => {
        playKeypadTone('6');
    });

    // OK Button: Confirms selection, dials number, or triggers audio replay
    btnKeypadOk.addEventListener('click', () => {
        playKeypadTone('5');
        console.log("[AgriVoice Keypad] 'OK' button clicked.");

        if (isCallActive) {
            // Replay audio if call is already connected
            replayLastAudio();
            return;
        }

        // If in idle: execute selected service
        executeSelectedService();
    });

    // Left Soft Key ("Select / Call")
    btnSoftLeft.addEventListener('click', () => {
        playKeypadTone('1');
        console.log("[AgriVoice Keypad] 'Select' soft key clicked.");
        if (isCallActive) {
            replayLastAudio();
            return;
        }
        executeSelectedService();
    });

    // Right Soft Key ("Back ⌫ / Clear")
    btnSoftRight.addEventListener('click', () => {
        playKeypadTone('3');
        console.log("[AgriVoice Keypad] 'Back' soft key clicked.");

        if (isCallActive) {
            endCall();
            return;
        }

        // Number deletion
        if (dialedBuffer.length > 0) {
            dialedBuffer = dialedBuffer.slice(0, -1);
            if (dialedBuffer.length === 0) {
                screenNumberPreview.textContent = "1800-AGRI-VOICE";
                selectedMenuIndex = 1;
                updateMenuHighlight();
            } else {
                screenNumberPreview.textContent = dialedBuffer;
                if (dialedBuffer === "1") {
                    selectedMenuIndex = 1;
                    updateMenuHighlight();
                } else if (dialedBuffer === "2") {
                    selectedMenuIndex = 2;
                    updateMenuHighlight();
                }
            }
        } else {
            screenNumberPreview.textContent = "1800-AGRI-VOICE";
        }
    });

    function executeSelectedService() {
        if (isCallActive || isDialing) return; // Prevent duplicate calls

        // If dialed buffer matches 2 or menu index is 2: Weather callback
        if (dialedBuffer === "2" || (dialedBuffer === "" && selectedMenuIndex === 2)) {
            triggerWeatherMissedCall();
        } else {
            // Otherwise start Feature 1: AI Doctor Call
            startDoctorCall();
        }
    }

    // -------------------------------------------------------------
    // 8. TEXT-TO-SPEECH SYNTHESIS & REPLAY (Requirement 2, 3, 8)
    // -------------------------------------------------------------
    function speakSpokenText(text, lang) {
        if (!text) return;
        lastSpokenText = text;
        lastSpokenLang = lang;

        // Enable replay buttons
        if (btnReplayAudio) btnReplayAudio.disabled = false;
        if (btnWeatherReplay) btnWeatherReplay.disabled = false;

        if (!audioOutputEnabled || !('speechSynthesis' in window)) {
            console.log("[AgriVoice Audio] Speech synthesis disabled or unsupported.");
            return;
        }

        try {
            window.speechSynthesis.cancel(); // Stop any pending speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.92;

            if (lang === 'hi') {
                utterance.lang = 'hi-IN';
            } else if (lang === 'en') {
                utterance.lang = 'en-IN';
            } else {
                utterance.lang = 'te-IN';
            }

            const voices = window.speechSynthesis.getVoices();
            const matchedVoice = voices.find(v => v.lang.startsWith(utterance.lang.substring(0, 2)));
            if (matchedVoice) utterance.voice = matchedVoice;

            utterance.onstart = () => {
                updateSystemStatus('SPEAKING');
            };

            utterance.onend = () => {
                if (isCallActive) {
                    updateSystemStatus('LISTENING');
                } else {
                    updateSystemStatus('IDLE');
                }
            };

            utterance.onerror = (e) => {
                console.warn("[AgriVoice Audio] Speech synthesis event:", e);
                if (isCallActive) updateSystemStatus('LISTENING');
            };

            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.error("[AgriVoice Audio] Speech error:", e);
        }
    }

    function replayLastAudio() {
        if (!lastSpokenText) {
            showVoiceMessage("No audio response available to replay yet.", "warning");
            return;
        }
        console.log(`[AgriVoice Audio] Replaying audio response in ${getLangLabel(lastSpokenLang)}...`);
        showVoiceMessage(`🔊 Replaying audio in ${getLangLabel(lastSpokenLang)}...`, 'info');
        speakSpokenText(lastSpokenText, lastSpokenLang);
    }

    if (btnReplayAudio) {
        btnReplayAudio.addEventListener('click', replayLastAudio);
    }
    if (btnWeatherReplay) {
        btnWeatherReplay.addEventListener('click', replayLastAudio);
    }

    // -------------------------------------------------------------
    // 9. WEB SPEECH API: DYNAMIC SPEECH RECOGNITION (Feature 1)
    // -------------------------------------------------------------
    let finalTranscribedText = "";

    async function handleMicButtonClick() {
        console.log("[AgriVoice] 'Speak' button clicked.");

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("[AgriVoice] Speech Recognition API not supported.");
            alert("Speech Recognition API is not supported in this browser. Please use Google Chrome on desktop.");
            showVoiceMessage("❌ Speech Recognition not supported in this browser. Use Google Chrome.", "error");
            return;
        }

        if (isListening) {
            stopSpeechRecognition();
            return;
        }

        // Never insert predefined demo text
        customUtteranceInput.value = "";
        finalTranscribedText = "";

        showVoiceMessage("⏳ Requesting microphone access...", "info");
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop());
                console.log("[AgriVoice] Microphone hardware access confirmed.");
            }
        } catch (err) {
            console.error("[AgriVoice] Microphone error:", err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                alert("Microphone permission was denied. Please allow microphone permissions in Chrome's address bar to speak.");
                showVoiceMessage("❌ Microphone permission denied. Please allow microphone access.", "error");
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                alert("No microphone found on your device. Please connect a working microphone.");
                showVoiceMessage("❌ No microphone found.", "error");
            } else {
                alert("Microphone error: " + err.message);
                showVoiceMessage("❌ Microphone error: " + err.message, "error");
            }
            return;
        }

        startSpeechRecognition();
    }

    function startSpeechRecognition() {
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return;

            if (recognition) {
                try { recognition.abort(); } catch(e) {}
            }

            recognition = new SpeechRecognition();

            const targetLang = selMicLanguage ? selMicLanguage.value : (
                activeLanguage === 'hi' ? 'hi-IN' : activeLanguage === 'en' ? 'en-IN' : 'te-IN'
            );
            recognition.lang = targetLang;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;
            recognition.continuous = false;

            recognition.onstart = () => {
                isListening = true;
                finalTranscribedText = "";
                btnMicTrigger.classList.add('mic-recording');
                document.getElementById('micIcon').textContent = '🔴';
                document.getElementById('micLabel').textContent = 'Listening... (Click to Stop)';

                updateSystemStatus('LISTENING', `Listening in ${getLangLabel(activeLanguage)}...`);
                showVoiceMessage(`🎙️ Listening in ${getLangLabel(activeLanguage)}... Speak your crop name or symptoms now!`, 'listening');
            };

            recognition.onresult = (event) => {
                let currentTranscript = "";
                if (event.results && event.results.length > 0) {
                    currentTranscript = event.results[0][0].transcript;
                }
                customUtteranceInput.value = currentTranscript;
                finalTranscribedText = currentTranscript;

                liveSubtitleBox.textContent = `Farmer: "${currentTranscript}"`;
                showVoiceMessage(`Hearing: "${currentTranscript}"`, 'listening');
            };

            recognition.onerror = (event) => {
                console.error("[AgriVoice] SpeechRecognition error:", event.error);
                isListening = false;
                resetMicUI();

                if (event.error === 'not-allowed') {
                    alert("Microphone permission was denied. Please allow microphone access in Chrome settings.");
                    showVoiceMessage("❌ Microphone permission denied.", "error");
                    updateSystemStatus('ERROR', 'Mic permission denied');
                } else if (event.error === 'no-speech') {
                    showVoiceMessage("⚠️ No speech detected. Please speak closer to microphone.", "warning");
                    if (isCallActive) updateSystemStatus('LISTENING');
                } else if (event.error === 'network') {
                    alert("Network error: Chrome requires internet connection to Google's speech recognition service.");
                    showVoiceMessage("⚠️ Network error during speech recognition.", "warning");
                    updateSystemStatus('ERROR', 'Speech network error');
                } else if (event.error !== 'aborted') {
                    showVoiceMessage(`⚠️ Speech recognition error: ${event.error}`, "warning");
                }
            };

            recognition.onend = () => {
                isListening = false;
                resetMicUI();

                const textToSend = finalTranscribedText.trim() || customUtteranceInput.value.trim();
                if (textToSend) {
                    console.log("[AgriVoice] Speech recognition finished:", textToSend);
                    showVoiceMessage(`✓ Final Transcript: "${textToSend}". Contacting AI Doctor...`, "success");
                    appendBubble('farmer', textToSend, activeLanguage);
                    customUtteranceInput.value = textToSend;
                    sendTranscribedTextToDoctor(textToSend);
                } else {
                    showVoiceMessage("Speech ended. No words detected. Click Speak to try again.", "info");
                    if (isCallActive) updateSystemStatus('LISTENING');
                }
            };

            recognition.start();

        } catch (err) {
            console.error("[AgriVoice] Failed to start SpeechRecognition:", err);
            showVoiceMessage(`❌ Error starting voice input: ${err.message}`, "error");
            resetMicUI();
        }
    }

    function stopSpeechRecognition() {
        if (recognition) {
            try { recognition.stop(); } catch (e) {
                try { recognition.abort(); } catch(e2) {}
            }
        }
        isListening = false;
        resetMicUI();
        showVoiceMessage("Speech listening stopped.", "info");
    }

    function resetMicUI() {
        btnMicTrigger.classList.remove('mic-recording');
        document.getElementById('micIcon').textContent = '🎙️';
        document.getElementById('micLabel').textContent = 'Speak (మైక్ / माइक)';
        voiceWave.style.opacity = '0.3';
    }

    // -------------------------------------------------------------
    // 10. FEATURE 1: MULTILINGUAL AI AGRI-DOCTOR CALL
    // -------------------------------------------------------------
    async function startDoctorCall() {
        if (isCallActive || isDialing) return; // Prevent duplicate calls

        isDialing = true;
        const phone = selFarmerProfile.value;
        const profile = FARMERS[phone] || FARMERS["+919848022338"];

        activeService = "DOCTOR_CALL";
        currentSessionId = "doc_" + Math.random().toString(36).substring(2, 8);

        // Update phone screen views
        screenIdle.classList.add('hidden');
        screenIncoming.classList.add('hidden');
        screenActiveCall.classList.remove('hidden');

        callServiceHeader.textContent = "AI AGRI-DOCTOR CALL (1800-AGRI)";
        screenCallerTitle.textContent = "AI Crop Doctor";
        callDtmfFeedback.textContent = "";

        updateSystemStatus('CALLING', 'Dialing 1800-AGRI-VOICE Toll-Free...');
        appendBubble('system', `📞 Farmer (${profile.name}, ${profile.village}) calling toll-free 1800-AGRI-VOICE for crop diagnosis.`);

        // Reset step pipeline
        updateStepPipeline("ASK_CROP");

        // Start call timer
        callSeconds = 0;
        lblCallDuration.textContent = "00:00";
        if (callTimerInterval) clearInterval(callTimerInterval);
        callTimerInterval = setInterval(() => {
            callSeconds++;
            const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
            const secs = String(callSeconds % 60).padStart(2, '0');
            lblCallDuration.textContent = `${mins}:${secs}`;
        }, 1000);

        try {
            const res = await fetch('/api/doctor/call/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    phone: phone,
                    lang: activeLanguage
                })
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            isDialing = false;
            isCallActive = true;

            activeLanguage = data.detected_lang;
            updateLangBadge(activeLanguage);

            updateSystemStatus('CONNECTED');
            liveSubtitleBox.textContent = `Doctor: "${data.spoken_response}"`;
            appendBubble('doctor', data.spoken_response, activeLanguage);

            speakSpokenText(data.spoken_response, activeLanguage);
            showVoiceMessage(`Connected to AI Doctor in ${getLangLabel(activeLanguage)}. Click 'Speak' to answer.`, 'success');

        } catch (err) {
            console.error('Failed to start doctor call:', err);
            isDialing = false;
            updateSystemStatus('ERROR', err.message);
            showVoiceMessage(`❌ Error starting call: ${err.message}`, 'error');
            setTimeout(endCall, 3000);
        }
    }

    async function sendTranscribedTextToDoctor(text) {
        if (!text) return;

        if (!isCallActive) {
            console.log("[AgriVoice] Starting AI Doctor call session first...");
            await startDoctorCall();
            setTimeout(() => {
                dispatchDoctorTurn(text);
            }, 1200);
        } else {
            dispatchDoctorTurn(text);
        }
    }

    async function dispatchDoctorTurn(text) {
        if (!text || !currentSessionId) return;

        updateSystemStatus('PROCESSING');
        showVoiceMessage(`AI Doctor processing your query: "${text}"...`, 'info');

        try {
            const res = await fetch('/api/doctor/call/turn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    utterance: text
                })
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();

            // Language strictly maintained or dynamically updated
            activeLanguage = data.detected_lang;
            updateLangBadge(activeLanguage);
            updateStepPipeline(data.step, data.session);

            liveSubtitleBox.textContent = `Doctor: "${data.spoken_response}"`;
            appendBubble('doctor', data.spoken_response, activeLanguage);
            showVoiceMessage(`AI Doctor answered in ${getLangLabel(activeLanguage)}.`, 'success');

            speakSpokenText(data.spoken_response, activeLanguage);

            if (!data.is_call_active) {
                setTimeout(endCall, 8000);
            }
        } catch (err) {
            console.error('Failed processing turn:', err);
            updateSystemStatus('ERROR', err.message);
            showVoiceMessage(`❌ Error connecting to AI Doctor: ${err.message}`, 'error');
        }
    }

    function updateStepPipeline(step, session = null) {
        currentStepBadge.textContent = step;

        [stepNode1, stepNode2, stepNode3, stepNode4, stepNode5].forEach(n => {
            n.classList.remove('active', 'completed');
        });
        [stepLine1, stepLine2, stepLine3, stepLine4].forEach(l => l.classList.remove('active-line'));

        if (step === 'ASK_CROP') {
            stepNode1.classList.add('active');
        } else if (step === 'ASK_SYMPTOMS') {
            stepNode1.classList.add('completed');
            stepLine1.classList.add('active-line');
            stepNode2.classList.add('active');
        } else if (step === 'ASK_DURATION') {
            stepNode1.classList.add('completed');
            stepLine1.classList.add('active-line');
            stepNode2.classList.add('completed');
            stepLine2.classList.add('active-line');
            stepNode3.classList.add('active');
        } else if (step === 'ASK_SEVERITY') {
            stepNode1.classList.add('completed');
            stepLine1.classList.add('active-line');
            stepNode2.classList.add('completed');
            stepLine2.classList.add('active-line');
            stepNode3.classList.add('completed');
            stepLine3.classList.add('active-line');
            stepNode4.classList.add('active');
        } else if (step === 'DELIVER_PRESCRIPTION' || step === 'COMPLETED') {
            [stepNode1, stepNode2, stepNode3, stepNode4].forEach(n => n.classList.add('completed'));
            [stepLine1, stepLine2, stepLine3, stepLine4].forEach(l => l.classList.add('active-line'));
            stepNode5.classList.add('active');
        }

        if (session) {
            diagCrop.textContent = session.crop_name || '-';
            diagDisease.textContent = session.diagnosed_disease || '-';
            diagSymptoms.textContent = session.symptoms || '-';
            diagDurationSeverity.textContent = `${session.duration || '-'} | ${session.severity || '-'}`;

            if (session.diagnosed_disease) {
                prescriptionBody.innerHTML = `
                    <strong>Diagnosed:</strong> ${session.diagnosed_disease}<br>
                    <strong>Dosage:</strong> Follow the exact knapsack pump dosage prescribed in the voice audio above.<br>
                    <span style="color:#6ee7b7">✓ Precautions: Avoid excess nitrogen; spray in early morning under dry weather.</span>
                `;
            }
        }
    }

    // -------------------------------------------------------------
    // 11. FEATURE 2: MISSED CALL WEATHER SERVICE (Requirement 3)
    // -------------------------------------------------------------
    async function triggerWeatherMissedCall() {
        if (isCallActive || isDialing || activeService) return; // Prevent duplicate calls

        isDialing = true;
        const phone = selFarmerProfile.value;
        const profile = FARMERS[phone] || FARMERS["+919848022338"];

        activeService = "WEATHER_MISSED_CALL";
        updateSystemStatus('CALLING', 'Missed call registered. Disconnecting after 2 rings...');

        appendBubble('system', `📞 Farmer (${profile.name}, ${profile.village}) dialed 1800-AGRI-VOICE. Disconnected after 2 rings (Zero cost for farmer).`);

        screenIdle.classList.add('hidden');
        screenActiveCall.classList.add('hidden');
        screenIncoming.classList.remove('hidden');

        try {
            const res = await fetch('/api/weather/missed-call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: phone,
                    lang: activeLanguage
                })
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            const bulletin = data.weather_bulletin;
            const metrics = bulletin.weather_metrics;

            // Update weather metrics cards
            metricTemp.textContent = `${metrics.temperature_c}°C`;
            metricRain.textContent = `${metrics.rain_probability}%`;
            metricWind.textContent = `${metrics.wind_speed_kmh} km/h (${metrics.wind_direction})`;
            metricSpray.textContent = metrics.safe_to_spray ? "✓ SAFE TO SPRAY" : "⚠️ DO NOT SPRAY";
            metricSpray.style.color = metrics.safe_to_spray ? "#34d399" : "#f87171";
            weatherSourceBadge.textContent = metrics.source.substring(0, 24);

            weatherSpokenPreview.innerHTML = `<strong>Spoken Script (${bulletin.language.toUpperCase()}):</strong><br>${bulletin.spoken_report}`;

            let countdown = 3;
            incomingSubText.textContent = `Zero Balance Call • Auto-Callback in ${countdown}s...`;

            const callbackTimer = setInterval(() => {
                countdown--;
                if (countdown > 0) {
                    incomingSubText.textContent = `Zero Balance Call • Auto-Callback in ${countdown}s...`;
                } else {
                    clearInterval(callbackTimer);
                    isDialing = false;
                    isCallActive = true;

                    screenIncoming.classList.add('hidden');
                    screenActiveCall.classList.remove('hidden');

                    callServiceHeader.textContent = "MISSED-CALL WEATHER BROADCAST";
                    screenCallerTitle.textContent = "Agri-Weather Outbound";
                    callDtmfFeedback.textContent = "";

                    updateSystemStatus('CONNECTED');
                    activeLanguage = bulletin.language;
                    updateLangBadge(activeLanguage);

                    liveSubtitleBox.textContent = `"${bulletin.spoken_report.substring(0, 90)}..."`;
                    appendBubble('weather', bulletin.spoken_report, activeLanguage);
                    speakSpokenText(bulletin.spoken_report, activeLanguage);

                    appendBubble('system', `📩 Feature Phone Received SMS Bulletin:\n${bulletin.sms_text}`);

                    setTimeout(() => {
                        endCall();
                    }, 16000);
                }
            }, 1000);

        } catch (err) {
            console.error('Failed to trigger missed call:', err);
            isDialing = false;
            updateSystemStatus('ERROR', err.message);
            showVoiceMessage(`❌ Error retrieving weather: ${err.message}`, 'error');
            setTimeout(endCall, 2500);
        }
    }

    // -------------------------------------------------------------
    // 12. HANG UP / END CALL
    // -------------------------------------------------------------
    function endCall() {
        console.log("[AgriVoice] Ending active call / resetting phone state.");
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (callTimerInterval) clearInterval(callTimerInterval);
        if (isListening) stopSpeechRecognition();

        isCallActive = false;
        isDialing = false;
        activeService = null;
        dialedBuffer = "";
        selectedMenuIndex = 1;
        updateMenuHighlight();

        updateSystemStatus('CALL_ENDED');
        appendBubble('system', '📴 Call Ended (కాల్ ముగిసింది • कॉल समाप्त हुआ). Channel released.');
        showVoiceMessage('Call ended. Phone returned to standby.', 'info');

        setTimeout(() => {
            screenActiveCall.classList.add('hidden');
            screenIncoming.classList.add('hidden');
            screenIdle.classList.remove('hidden');
            screenNumberPreview.textContent = "1800-AGRI-VOICE";
            updateSystemStatus('IDLE');
        }, 1200);
    }

    // -------------------------------------------------------------
    // 13. CONVERSATION TRANSCRIPT BUBBLES
    // -------------------------------------------------------------
    function appendBubble(role, text, lang = "te") {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble bubble-${role}`;

        let prefix = '';
        if (role === 'farmer') prefix = `👨‍🌾 Farmer (${lang.toUpperCase()}): `;
        if (role === 'doctor') prefix = `🩺 AI Agri-Doctor (${lang.toUpperCase()}): `;
        if (role === 'weather') prefix = `🌧️ Weather Broadcast (${lang.toUpperCase()}): `;
        if (role === 'system') prefix = `ℹ️ `;

        const formatted = text.replace(/\n/g, '<br>');
        bubble.innerHTML = `<strong>${prefix}</strong>${formatted}`;
        transcriptScroll.appendChild(bubble);
        transcriptScroll.scrollTop = transcriptScroll.scrollHeight;
    }

    // -------------------------------------------------------------
    // 14. EVENT LISTENERS
    // -------------------------------------------------------------
    btnDoctorCall.addEventListener('click', startDoctorCall);
    btnWeatherMissedCall.addEventListener('click', triggerWeatherMissedCall);
    btnEndCall.addEventListener('click', endCall);

    btnMicTrigger.addEventListener('click', handleMicButtonClick);

    btnSendUtterance.addEventListener('click', () => {
        const val = customUtteranceInput.value.trim();
        if (val) {
            appendBubble('farmer', val, activeLanguage);
            sendTranscribedTextToDoctor(val);
            customUtteranceInput.value = '';
        }
    });

    customUtteranceInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const val = customUtteranceInput.value.trim();
            if (val) {
                appendBubble('farmer', val, activeLanguage);
                sendTranscribedTextToDoctor(val);
                customUtteranceInput.value = '';
            }
        }
    });

    chkAudioOutput.addEventListener('change', (e) => {
        audioOutputEnabled = e.target.checked;
        if (!audioOutputEnabled && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    });

    // One-Click Demonstration Scenarios
    document.querySelectorAll('.scenario-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const utterance = pill.getAttribute('data-utterance');
            console.log("[AgriVoice] Demo scenario chip clicked:", utterance);
            customUtteranceInput.value = utterance;
            appendBubble('farmer', utterance, activeLanguage);
            sendTranscribedTextToDoctor(utterance);
        });
    });

    // Clear Transcript
    btnClearLog.addEventListener('click', () => {
        transcriptScroll.innerHTML = '<div class="system-welcome-bubble">💡 Transcript cleared. Ready for new demonstration.</div>';
    });

    // Initial setup
    updateSystemStatus('IDLE');
    updateMenuHighlight();
    showVoiceMessage('AgriVoice 2G keypad phone ready. Dial 1 for Doctor, 2 for Weather, or click buttons below.', 'info');
});
