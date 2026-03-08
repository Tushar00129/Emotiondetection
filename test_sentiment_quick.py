#!/usr/bin/env python
"""Quick test of text sentiment analyzer"""

try:
    from text_sentiment_analyzer import analyze_text_sentiment, convert_sentiment_to_emotion
    print("✓ Module imported")
    result = analyze_text_sentiment("I am very happy!", verbose=False)
    print(f"✓ Result: {result}")
    emotion = convert_sentiment_to_emotion(result['sentiment'])
    print(f"✓ Emotion: {emotion}")
except Exception as e:
    import traceback
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
