# AI Emotion Responder - Quick Reference Card

## 🚀 Quick Start (60 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run the system
python triple_emotion_detection.py

# 3. In terminal, type these commands in order:
v      # Record your voice (1.5s)
f      # Fuse emotions
a      # Get AI RESPONSE with AUDIO! 🔊
```

---

## 📌 Commands Cheat Sheet

### Triple Emotion Detection
```
v = Voice (record 1.5s)
t = Text  (type sentiment)
f = Fuse  (combine all three)
a = AI    (response + audio) ⭐
r = Reset
q = Quit
```

### Final Emotion Detection
```
v = Voice (record 1.5s)
a = AI    (response + audio) ⭐
r = Reset
q = Quit
```

---

## 🎯 Use Cases

| Use Case | Command Sequence |
|----------|------------------|
| **Voice → AI Response** | `v` → Wait → `a` → 🔊 |
| **Face + Voice + Text + AI** | `v` → `t` → `f` → `a` → 🔊 |
| **Just Test AI** | `a` (uses facial emotion) |

---

## 💬 7 Emotion Responses

```
😊 Happy        → "Keep the energy going!"
😢 Sad          → "Want to talk?"
😠 Angry        → "Take a deep breath."
😐 Neutral      → "How's your day?"
😨 Fear         → "You're safe here."
🤢 Disgust      → "Want to vent?"
😲 Surprised    → "Tell me about it!"
```

---

## 🔧 Customization

### Change a Response
```python
from ai_emotion_responder import update_response

update_response('Happy', 'Your custom message here!')
```

### Test Responses
```bash
python ai_emotion_responder.py
```

### Silent Mode (no audio)
```python
from ai_emotion_responder import ai_response

response = ai_response('Happy', speak=False)
```

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| **ai_emotion_responder.py** | Core AI module |
| **triple_emotion_detection.py** | Face + Voice + Text + AI |
| **final_emotion_detection.py** | Face + Voice + AI |
| **AI_RESPONDER_GUIDE.md** | Full documentation |
| **QUICKSTART_AI.md** | Quick start guide |

---

## ✅ Verify Installation

```bash
python -c "from ai_emotion_responder import ai_response; ai_response('Happy', speak=False)"
```

Should output a response starting with:
```
════════════════════════════════════════════════════════════════════════
🤖 AI EMOTION RESPONSE
```

---

## 🎤 Run Complete System

### System 1: ALL Features (Recommended)
```bash
python triple_emotion_detection.py
```
Features: Facial, Voice, Text, Fusion, **AI Response** 🔊

### System 2: Simple Version
```bash
python final_emotion_detection.py
```
Features: Facial, Voice, **AI Response** 🔊

---

## 🔊 Audio Issues?

```bash
# Test text-to-speech
python -c "from ai_emotion_responder import test_tts; test_tts()"

# Check volume
# Disable 'speak' parameter:
# ai_response('Happy', speak=False)  # Text only
```

---

## 📊 Performance

| Action | Time |
|--------|------|
| Module load | <100ms |
| Response gen | <50ms |
| TTS init | ~2s (first) |
| Audio play | 3-6s |
| **Total** | **3-8s** |

---

## 🎓 Example Workflows

### Workflow 1: Voice & AI Response
```
1. Press 'v' → Speak for 1.5 seconds
2. Press 'a' → System responds with audio 🔊
```

### Workflow 2: Everything (Face+Voice+Text+AI)
```
1. Face detection starts automatically
2. Press 'v' → Record voice
3. Press 't' → Type text
4. Press 'f' → Combine emotions
5. Press 'a' → AI responds with audio 🔊
```

### Workflow 3: Just Test AI
```
1. System starts (detects facial emotion)
2. Press 'a' → AI responds immediately 🔊
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No audio | Check system volume, run test_tts() |
| Command 'a' not found | Reinstall: `pip install -r requirements.txt` |
| Module not found | Run: `pip install pyttsx3` |
| Webcam error | Check camera is connected & working |
| Model not found | Verify emotiondetector.json/h5 files exist |

---

## 💡 Pro Tips

- **Speak clearly** for better voice detection (quiet room)
- **Good lighting** for better facial detection
- **Natural text** for better sentiment analysis
- **Combine inputs** for best accuracy
- **Test responses** with `python ai_emotion_responder.py`

---

## 📚 Documentation Map

```
For quick start:      → QUICKSTART_AI.md
For complete guide:   → AI_RESPONDER_GUIDE.md
For setup/verify:     → INSTALLATION_VERIFICATION.md
For implementation:   → AI_RESPONDER_IMPLEMENTATION.md
For source code:      → ai_emotion_responder.py
```

---

## 🎯 Core Functions

```python
# Main function (speaks result)
from ai_emotion_responder import ai_response
ai_response('Happy')

# Text only (no audio)
from ai_emotion_responder import ai_response_silent
text = ai_response_silent('Sad')

# Custom styles
from ai_emotion_responder import ai_response_with_options
ai_response_with_options('Angry', response_style='supportive')

# Test everything
python ai_emotion_responder.py
```

---

## 🚀 One-Liner Commands

```bash
# Test module
python -c "from ai_emotion_responder import ai_response; ai_response('Happy')"

# Test TTS
python -c "from ai_emotion_responder import test_tts; test_tts()"

# Run system
python triple_emotion_detection.py

# Show all responses
python -c "from ai_emotion_responder import get_all_responses; import json; print(json.dumps(get_all_responses(), indent=2))"
```

---

## 📋 Setup Checklist

- [ ] Model files present (emotiondetector.json/h5)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] pyttsx3 installed (`pip install pyttsx3`)
- [ ] AI module loads (`python -c "from ai_emotion_responder import ai_response"`)
- [ ] TTS works (`python ai_emotion_responder.py`)
- [ ] Main system runs (`python triple_emotion_detection.py`)
- [ ] 'a' command works (press 'a' after detecting emotion)

---

## 🔗 Integration Summary

| File | Added |
|------|-------|
| **triple_emotion_detection.py** | `ai_response(emotion)` + command 'a' |
| **final_emotion_detection.py** | `ai_response(emotion)` + command 'a' |
| **requirements.txt** | pyttsx3 |

---

## Ready? 

```bash
python triple_emotion_detection.py
# Then press: v, t, f, a
# Listen to the AI response! 🔊
```

---

**Quick Reference v1.0** | Last Updated: 2026-03-08
