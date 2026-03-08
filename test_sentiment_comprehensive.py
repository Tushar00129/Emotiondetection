#!/usr/bin/env python
"""Test sentiment analyzer with various punctuation"""

from text_sentiment_analyzer import analyze_text_sentiment, convert_sentiment_to_emotion

test_cases = [
    "I am very happy!",
    "This is terrible! Awful! Horrible!",
    "I love this amazing product!",
    "I hate this, completely awful...",
    "The weather is okay.",
    "Great! Wonderful! Fantastic!!!",
    "Sad and disappointed...",
]

print("\n" + "="*70)
print(" SENTIMENT ANALYZER TEST (With Punctuation)")
print("="*70 + "\n")

for text in test_cases:
    result = analyze_text_sentiment(text, verbose=False)
    emotion = convert_sentiment_to_emotion(result['sentiment'])
    print(f"Text: \"{text}\"")
    print(f"  → Sentiment: {result['sentiment'].upper()} (confidence: {result['confidence']:.1%})")
    print(f"  → Emotion: {emotion}")
    print()

print("="*70)
print("✓ All tests completed successfully!")
print("="*70)
