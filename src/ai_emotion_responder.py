"""
AI Emotion Response Module
Generates intelligent text and voice responses based on detected emotions
"""

import pyttsx3
import time
from typing import Dict, Tuple


# Emotion-specific responses
EMOTION_RESPONSES = {
    'Happy': {
        'text': "You seem happy! Keep the energy going! 😊",
        'variants': [
            "That's wonderful! Your happiness is contagious!",
            "You're radiating positivity! Love the energy!",
            "Great vibes! Keep smiling!",
            "Your happiness is inspiring! Keep it up!",
        ]
    },
    'Sad': {
        'text': "I notice you are feeling down. Want to talk? 💙",
        'variants': [
            "I'm here for you. It's okay to feel sad sometimes.",
            "Don't worry, this feeling will pass. Need support?",
            "Your feelings matter. Would you like to share?",
            "It's alright to feel down. You're not alone.",
        ]
    },
    'Angry': {
        'text': "Take a deep breath. Try to calm down. 🧘",
        'variants': [
            "Let's pause and take some time to cool off.",
            "Deep breathing can help. Inhale slowly... exhale.",
            "Anger is understandable. Let's work through this.",
            "Take a step back. You've got this.",
        ]
    },
    'Neutral': {
        'text': "Let's keep moving! How's your day going? 👋",
        'variants': [
            "Feeling neutral? That's fine. Tell me more!",
            "Steady as she goes! What's on your mind?",
            "Neutral mood detected. Anything I can help with?",
            "You seem calm. Ready for whatever comes next?",
        ]
    },
    'Fear': {
        'text': "I sense you're worried. You're safe here. What's concerning you? 🤝",
        'variants': [
            "It's okay to be afraid. Let's talk about it.",
            "Fear is natural. I'm here to listen.",
            "Take your time. What's making you anxious?",
            "You can confide in me. What's troubling you?",
        ]
    },
    'Disgust': {
        'text': "Something's bothering you. Want to vent about it? 💬",
        'variants': [
            "I sense disapproval. What happened?",
            "You seem put off. Do you want to talk?",
            "Something's not sitting right with you. What is it?",
            "I notice dissatisfaction. Care to share?",
        ]
    },
    'Surprised': {
        'text': "Oh, something caught you off guard! Tell me about it! 😲",
        'variants': [
            "Wow, that's surprising! What happened?",
            "You seem amazed! Do tell!",
            "Surprise! What just happened?",
            "I sense excitement from the surprise!",
        ]
    },
}

# Initialize text-to-speech engine
_tts_engine = None


def _initialize_tts():
    """
    Initialize the text-to-speech engine.
    Called once when first response is generated.
    """
    global _tts_engine
    
    if _tts_engine is None:
        try:
            _tts_engine = pyttsx3.init()
            
            # Configure voice properties
            _tts_engine.setProperty('rate', 150)        # Speed: 150 words per minute
            _tts_engine.setProperty('volume', 0.9)      # Volume: 90%
            
            # Try to set a good voice
            voices = _tts_engine.getProperty('voices')
            if len(voices) > 1:
                # Use second voice (usually female on Windows)
                _tts_engine.setProperty('voice', voices[1].id)
            
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize text-to-speech: {e}")
            return False
    
    return True


def get_emotion_response(emotion: str, use_variant: bool = False) -> Tuple[str, str]:
    """
    Get text response for a given emotion.
    
    Args:
        emotion (str): The detected emotion (e.g., 'Happy', 'Sad')
        use_variant (bool): If True, return a variant response
    
    Returns:
        tuple: (emotion_category, response_text)
    """
    
    # Normalize emotion name
    emotion_lower = emotion.lower()
    
    # Find matching emotion (case-insensitive)
    matched_emotion = None
    for key in EMOTION_RESPONSES.keys():
        if key.lower() == emotion_lower:
            matched_emotion = key
            break
    
    if matched_emotion is None:
        # Default response for unknown emotions
        matched_emotion = 'Neutral'
    
    # Get response
    response_data = EMOTION_RESPONSES[matched_emotion]
    
    if use_variant and len(response_data['variants']) > 0:
        response_text = response_data['variants'][0]
    else:
        response_text = response_data['text']
    
    return matched_emotion, response_text


def speak_response(text: str, verbose: bool = True) -> bool:
    """
    Speak the response aloud using text-to-speech.
    
    This function converts text to speech and plays it through the speaker.
    Uses pyttsx3 which works offline (no internet required).
    
    Args:
        text (str): The text to speak
        verbose (bool): Print status messages
    
    Returns:
        bool: True if successful, False if TTS unavailable
    """
    
    try:
        # Initialize TTS if needed
        if not _initialize_tts():
            if verbose:
                print("⚠️  Text-to-speech not available")
            return False
        
        if verbose:
            print(f"🔊 Speaking: \"{text}\"")
        
        # Queue text for speaking
        _tts_engine.say(text)
        
        # Process the speech
        _tts_engine.runAndWait()
        
        return True
    
    except Exception as e:
        if verbose:
            print(f"⚠️  Error speaking: {e}")
        return False


def ai_response(
    final_emotion: str,
    speak: bool = True,
    verbose: bool = True
) -> str:
    """
    MAIN FUNCTION: Generate and speak AI response based on emotion.
    
    This function is the core AI assistant that responds to detected emotions.
    
    Process:
    1. Normalize the emotion input
    2. Select appropriate response text
    3. Print the response
    4. Speak the response aloud (if enabled)
    5. Return the response text
    
    Args:
        final_emotion (str): The detected/fused emotion
                            (e.g., 'Happy', 'Sad', 'Angry', 'Neutral', etc.)
        speak (bool): Whether to speak the response aloud (default: True)
        verbose (bool): Print status messages (default: True)
    
    Returns:
        str: The response text
    
    Example:
        >>> emotion = 'Happy'
        >>> response = ai_response(emotion)
        >>> print(response)
        >>> # Output will be spoken aloud
    """
    
    print("\n" + "="*70)
    print("🤖 AI EMOTION RESPONSE")
    print("="*70)
    
    # Step 1: Normalize emotion and get response
    # ──────────────────────────────────────────
    # The get_emotion_response function handles:
    # - Case-insensitive emotion matching
    # - Unknown emotions (defaults to 'Neutral')
    # - Mapping to appropriate responses
    
    matched_emotion, response_text = get_emotion_response(final_emotion)
    
    print(f"\n📊 Detected Emotion: {final_emotion.upper()}")
    print(f"✨ Matched Category: {matched_emotion}")
    
    # Step 2: Print the response
    # ────────────────────────
    # Visual feedback showing what the AI will say
    print(f"\n💬 AI Response:")
    print(f"   \"{response_text}\"")
    
    # Step 3: Speak the response (optional)
    # ─────────────────────────────────────
    # Uses pyttsx3 for offline text-to-speech
    # No internet required - works locally
    
    if speak:
        print(f"\n🔊 Playing audio response...")
        speak_success = speak_response(response_text, verbose=verbose)
        
        if speak_success:
            print("✓ Audio response played")
        else:
            if verbose:
                print("ℹ️  Continuing without audio")
    
    # Step 4: Return response for logging/further use
    # ───────────────────────────────────────────────
    
    print("\n" + "="*70 + "\n")
    
    return response_text


def ai_response_silent(final_emotion: str) -> str:
    """
    Generate response without speaking (text only).
    
    Useful for logging, saving, or when you want visual feedback only.
    
    Args:
        final_emotion (str): The detected emotion
    
    Returns:
        str: The response text
    """
    return ai_response(final_emotion, speak=False, verbose=False)


def ai_response_with_options(
    final_emotion: str,
    response_style: str = 'supportive',
    speak: bool = True
) -> str:
    """
    Generate response with different styles.
    
    Args:
        final_emotion (str): The detected emotion
        response_style (str): 'supportive', 'motivational', 'casual', 'professional'
        speak (bool): Whether to speak response
    
    Returns:
        str: The response text
    """
    
    # Enhanced responses by style
    style_prefixes = {
        'supportive': "I hear you.",
        'motivational': "You've got this!",
        'casual': "So,",
        'professional': "I understand.",
    }
    
    _, base_response = get_emotion_response(final_emotion)
    
    # Customize based on style
    if response_style in style_prefixes:
        response_text = f"{style_prefixes[response_style]} {base_response}"
    else:
        response_text = base_response
    
    if speak:
        speak_response(response_text)
    
    return response_text


def get_all_responses() -> Dict[str, Dict]:
    """
    Get all available emotion responses.
    Useful for reviewing or customizing responses.
    
    Returns:
        dict: Complete emotion-response mapping
    """
    return EMOTION_RESPONSES


def update_response(emotion: str, new_text: str, update_variants: bool = False) -> bool:
    """
    Update response for a specific emotion.
    Allows customization of AI responses.
    
    Args:
        emotion (str): Emotion to update
        new_text (str): New response text
        update_variants (bool): Also update variant responses
    
    Returns:
        bool: True if successful
    """
    
    if emotion not in EMOTION_RESPONSES:
        print(f"Unknown emotion: {emotion}")
        return False
    
    # Update main response
    EMOTION_RESPONSES[emotion]['text'] = new_text
    
    # Optionally update variants
    if update_variants:
        EMOTION_RESPONSES[emotion]['variants'] = [new_text]
    
    print(f"✓ Updated response for {emotion}")
    return True


# Testing utilities
def test_all_responses():
    """Test all emotion responses"""
    print("\n" + "="*70)
    print("TESTING ALL AI EMOTION RESPONSES")
    print("="*70)
    
    emotions = list(EMOTION_RESPONSES.keys())
    
    for emotion in emotions:
        print(f"\n{'─'*70}")
        response = ai_response(emotion, speak=False, verbose=True)
        print(f"Response: {response}")
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "="*70)
    print("✅ All responses tested!")
    print("="*70 + "\n")


def test_tts():
    """Test text-to-speech functionality"""
    print("\n" + "="*70)
    print("TESTING TEXT-TO-SPEECH")
    print("="*70)
    
    test_text = "Hello! This is a test of the text-to-speech system. Happy emotion detected!"
    
    print(f"\nTest text: \"{test_text}\"")
    print("Playing audio...\n")
    
    success = speak_response(test_text)
    
    if success:
        print("\n✅ Text-to-speech works!")
    else:
        print("\n❌ Text-to-speech failed")
        print("Make sure pyttsx3 is installed: pip install pyttsx3")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║               AI EMOTION RESPONSE DEMONSTRATION                       ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test all responses
    test_all_responses()
    
    # Test text-to-speech
    test_tts()
    
    print("\nDone! Ready to use in your emotion detection system.")
