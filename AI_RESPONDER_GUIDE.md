# AI Emotion Responder Guide

## Overview

The AI Emotion Responder (`ai_emotion_responder.py`) is a module that generates intelligent text and voice responses based on detected emotions. It uses **pyttsx3** for offline text-to-speech synthesis, making responses both visible and audible.

## Features

✅ **7 Emotion Categories**: Happy, Sad, Angry, Neutral, Fear, Disgust, Surprised
✅ **Text Responses**: Warm, supportive messages for each emotion
✅ **Text-to-Speech**: Speaks responses aloud using pyttsx3
✅ **Offline**: No internet required - everything runs locally
✅ **Customizable**: Easy to modify responses for your use case
✅ **Case-Insensitive**: Works with emotion names in any case
✅ **Integrated**: Works with the complete emotion detection systems

---

## Core Function

### `ai_response(final_emotion, speak=True, verbose=True)`

**Main entry point** - Generates and (optionally) speaks an AI response.

**Parameters:**
- `final_emotion` (str): The detected emotion (e.g., 'Happy', 'Sad', 'Angry')
- `speak` (bool): Whether to speak the response aloud (default: True)
- `verbose` (bool): Print status messages (default: True)

**Returns:**
- str: The response text

**Example:**
```python
from ai_emotion_responder import ai_response

# Generate response and speak it
response = ai_response('Happy')
# Output:
# ════════════════════════════════════════════════════════════════════════
# 🤖 AI EMOTION RESPONSE
# ════════════════════════════════════════════════════════════════════════
# 
# 📊 Detected Emotion: HAPPY
# ✨ Matched Category: Happy
# 
# 💬 AI Response:
#    "You seem happy! Keep the energy going! 😊"
# 
# 🔊 Playing audio response...
# ✓ Audio response played
# 
# ════════════════════════════════════════════════════════════════════════
```

---

## Emotion Responses

| Emotion | Primary Response |
|---------|-----------------|
| **Happy** | "You seem happy! Keep the energy going! 😊" |
| **Sad** | "I notice you are feeling down. Want to talk? 💙" |
| **Angry** | "Take a deep breath. Try to calm down. 🧘" |
| **Neutral** | "Let's keep moving! How's your day going? 👋" |
| **Fear** | "I sense you're worried. You're safe here. What's concerning you? 🤝" |
| **Disgust** | "Something's bothering you. Want to vent about it? 💬" |
| **Surprised** | "Oh, something caught you off guard! Tell me about it! 😲" |

Each emotion has multiple variant responses for variety.

---

## Integration with Main Systems

### 1. Triple Emotion Detection (Face + Voice + Text)

**Usage in `triple_emotion_detection.py`:**

```bash
python triple_emotion_detection.py
```

**Commands:**
- `v` = Record voice emotion
- `t` = Type text for sentiment
- `f` = Fuse all emotions
- **`a` = Get AI response** ← NEW!
- `r` = Reset results
- `q` = Quit

**Workflow:**
```
Step 1: System detects facial emotion continuously
Step 2: Press 'v' to record voice (1.5s)
Step 3: Press 't' to type text for sentiment
Step 4: Press 'f' to fuse all three emotions
Step 5: Press 'a' to get AI response based on fused emotion
```

### 2. Final Emotion Detection (Face + Voice)

**Usage in `final_emotion_detection.py`:**

```bash
python final_emotion_detection.py
```

**Commands:**
- `v` = Record voice emotion
- **`a` = Get AI response** ← NEW!
- `r` = Reset voice result
- `q` = Quit

**Workflow:**
```
Step 1: System detects facial emotion continuously
Step 2: Press 'v' to record voice emotion
Step 3: Press 'a' to get AI response (uses latest available emotion)
```

---

## Advanced Usage

### Silent Response (No Speaking)

```python
from ai_emotion_responder import ai_response_silent

# Get response text without speaking
response = ai_response_silent('Happy')
print(response)
# Output: "You seem happy! Keep the energy going! 😊"
```

### Get Response Without Output

```python
from ai_emotion_responder import ai_response

# Generate response but just get the text
response = ai_response('Sad', speak=False, verbose=False)
# Can now use `response` for logging, saving, or further processing
```

### Different Response Styles

```python
from ai_emotion_responder import ai_response_with_options

# Supportive style
response = ai_response_with_options('Happy', response_style='supportive')

# Motivational style
response = ai_response_with_options('Sad', response_style='motivational')

# Casual style
response = ai_response_with_options('Angry', response_style='casual')

# Professional style
response = ai_response_with_options('Neutral', response_style='professional')
```

### Get All Available Responses

```python
from ai_emotion_responder import get_all_responses
import json

all_responses = get_all_responses()
print(json.dumps(all_responses, indent=2))
```

### Customize Responses

```python
from ai_emotion_responder import update_response

# Change response for Happy emotion
update_response('Happy', "You're doing amazing! Keep up the great work!")

# Now when you call ai_response('Happy'), it will use your custom text
```

---

## Text-to-Speech Features

### TTS Configuration

The text-to-speech engine is automatically configured with:
- **Speed:** 150 words per minute (readable but engaging)
- **Volume:** 90% (clear but not too loud)
- **Voice:** Second available voice (usually female on Windows)

### Test TTS

```python
from ai_emotion_responder import test_tts

# Test if text-to-speech works on your system
test_tts()
```

### Speaking Low-Level

```python
from ai_emotion_responder import speak_response

# Speak any text directly
speak_response("Hello! This is a test message.")
```

---

## Testing

### Run All Tests

```bash
python ai_emotion_responder.py
```

This runs:
1. **All Responses Test** - Tests each emotion with audio
2. **TTS Test** - Verifies text-to-speech functionality

### Test in Your Code

```python
from ai_emotion_responder import test_all_responses, test_tts

# Test all responses
test_all_responses()

# Test TTS only
test_tts()
```

---

## Troubleshooting

### "pyttsx3 not installed"

```bash
pip install pyttsx3
```

### "Warning: Could not initialize text-to-speech"

The system will continue to work with text output only. To fix:

**Windows:**
- Ensure Windows TTS drivers are installed
- Go to Settings → Time & Language → Speech
- Ensure a voice is installed

**Linux:**
```bash
sudo apt install espeak
```

**macOS:**
```bash
brew install espeak
```

### Audio plays but is too slow/fast

Modify the engine speed:

1. Open `ai_emotion_responder.py`
2. Find `_initialize_tts()` function
3. Change: `_tts_engine.setProperty('rate', 150)` to desired speed
   - Lower numbers = slower (e.g., 100)
   - Higher numbers = faster (e.g., 200)

### Can't hear audio

1. Check system volume
2. Check if speakers are working
3. Try: `test_tts()` to verify TTS works
4. Try different voice:
   ```python
   voices = _tts_engine.getProperty('voices')
   _tts_engine.setProperty('voice', voices[0].id)  # Try first voice
   ```

---

## Function Reference

### Main Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `ai_response()` | Generate response with TTS | str |
| `ai_response_silent()` | Generate response text only | str |
| `ai_response_with_options()` | Custom style response | str |
| `speak_response()` | Speak any text | bool |
| `get_emotion_response()` | Get response for emotion | tuple |

### Utility Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_all_responses()` | Get all emotion responses | dict |
| `update_response()` | Change emotion response | bool |
| `test_all_responses()` | Test each emotion | None |
| `test_tts()` | Test TTS system | None |

---

## Use Cases

### 1. Mental Health Support
Provide empathetic responses to users showing signs of distress:
```python
if emotion in ['sad', 'angry', 'fear']:
    ai_response(emotion)  # Get supportive message
```

### 2. Smart Assistant Integration
Combine with other systems:
```python
final_emotion = fuse_emotions(face, voice, text)
ai_response(final_emotion)  # Smart response
```

### 3. Gaming/Interactive Apps
Real-time character responses to player emotion:
```python
player_emotion = detect_face_emotion()
ai_response(player_emotion, speak=True)
```

### 4. Educational Tools
Encourage students based on emotional state:
```python
student_emotion = voice_emotion_detector.voice_emotion()
ai_response(student_emotion, speak=True)
```

### 5. Customer Service Bots
Personalized interactions:
```python
response = ai_response_with_options(
    customer_emotion,
    response_style='professional'
)
```

---

## Files Modified

✅ `ai_emotion_responder.py` - NEW (600+ lines)
✅ `triple_emotion_detection.py` - Added AI response command
✅ `final_emotion_detection.py` - Added AI response command
✅ `requirements.txt` - Added pyttsx3

---

## Example Workflow

### Complete Example: Face + Voice + Text + AI Response

```python
from triple_emotion_detection import TripleEmotionDetector

# Start the system
detector = TripleEmotionDetector()

# In the system's terminal, you would:
# 1. Press 'v' → Records 1.5s voice
# 2. Press 't' → Types text
# 3. Press 'f' → Fuses emotions
# 4. Press 'a' → Gets AI response and hears it spoken aloud!
```

---

## Performance Notes

- **TTS Initialization:** ~1-2 seconds first time (cached after)
- **Response Generation:** <100ms per response
- **Audio Playback:** Varies by text length (3-6 seconds typical)
- **Overall:** AI response completes in 3-8 seconds total

---

## Future Enhancements

Potential improvements for future versions:

- [ ] Multi-language support (multiple voice languages)
- [ ] Emotion intensity levels (very sad vs slightly sad)
- [ ] Context-aware responses (remember previous emotions)
- [ ] Custom voice parameters (male/female, accent)
- [ ] Response logging and analytics
- [ ] Emotion-music pairing
- [ ] Emoji generation with responses
- [ ] Confidence scoring for responses

---

## License & Attribution

This module uses:
- **pyttsx3** - Text-to-speech conversion (Apache 2.0)
- **TensorFlow/Keras** - Emotion models
- **OpenCV** - Computer vision

All designed to integrate seamlessly with your emotion detection system.

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Run `test_tts()` to verify functionality
3. Check `requirements.txt` to ensure all packages installed
4. See emotion response examples in code comments

---

**Version: 1.0**  
**Last Updated: 2026-03-08**  
**Status: Production Ready ✅**
