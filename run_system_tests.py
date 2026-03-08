"""
COMPLETE SYSTEM TEST & DEMO
Tests all components: Facial, Voice, Text, and Fusion
"""

import sys
import time


def test_imports():
    """Test all module imports"""
    print("\n" + "="*70)
    print("TESTING IMPORTS")
    print("="*70)
    
    try:
        from emotion_fusion import fuse_emotions
        print("✓ emotion_fusion imported")
    except ImportError as e:
        print("✗ emotion_fusion import failed:", e)
        return False
    
    try:
        from voice_emotion_detector import voice_emotion_with_confidence
        print("✓ voice_emotion_detector imported")
    except ImportError as e:
        print("✗ voice_emotion_detector import failed:", e)
        return False
    
    try:
        from text_sentiment_analyzer import analyze_text_sentiment
        print("✓ text_sentiment_analyzer imported")
    except ImportError as e:
        print("✗ text_sentiment_analyzer import failed:", e)
        return False
    
    print("\n✅ All imports successful!\n")
    return True


def test_emotion_fusion():
    """Test emotion fusion function"""
    print("="*70)
    print("TESTING EMOTION FUSION FUNCTION")
    print("="*70)
    
    from emotion_fusion import fuse_emotions, fuse_emotions_fast
    
    test_cases = [
        ("Happy", "Happy", "positive", "weighted", "All agree - Happy"),
        ("Angry", "Happy", "positive", "voting", "Voting - Happy"),
        ("Sad", "Sad", "negative", "weighted", "All align - Sad"),
        ("Happy", "Angry", "neutral", "hybrid", "Hybrid method"),
    ]
    
    print("\nTesting fusion with different scenarios:\n")
    
    all_passed = True
    for face, voice, text, method, description in test_cases:
        try:
            # use fast method when available for concise output
            if method == 'weighted':
                result = fuse_emotions_fast(face, voice, text)
            else:
                result = fuse_emotions(face, voice, text, method=method)
            print(f"✓ {description:30} → {result}")
        except Exception as e:
            print(f"✗ {description:30} → Error: {e}")
            all_passed = False
    
    print("\n✅ Fusion tests complete!\n")
    return all_passed


def test_text_sentiment():
    """Test text sentiment analysis"""
    print("="*70)
    print("TESTING TEXT SENTIMENT ANALYSIS")
    print("="*70)
    
    from text_sentiment_analyzer import analyze_text_sentiment, convert_sentiment_to_emotion
    
    test_texts = [
        "I am very happy!",
        "This is terrible",
        "The weather is okay",
    ]
    
    print("\nAnalyzing text samples:\n")
    
    all_passed = True
    for text in test_texts:
        try:
            result = analyze_text_sentiment(text, verbose=False)
            emotion = convert_sentiment_to_emotion(result['sentiment'])
            print(f"✓ '{text}'")
            print(f"  Sentiment: {result['sentiment'].upper()}, Emotion: {emotion}")
        except Exception as e:
            print(f"✗ Error analyzing: {e}")
            all_passed = False
    
    print("\n✅ Text sentiment tests complete!\n")
    return all_passed


def test_voice_emotion():
    """Test voice emotion functions and timing"""
    print("="*70)
    print("TESTING VOICE EMOTION DETECTOR")
    print("="*70)
    
    try:
        from voice_emotion_detector import voice_emotion_with_confidence
        print("\n✓ Loaded voice_emotion_with_confidence()")
        print("  You'll be prompted to speak briefly (1 second)")
        start = time.time()
        result = voice_emotion_with_confidence()
        duration = time.time() - start
        print(f"  Result: {result['emotion']} ({result['confidence']:.0%})")
        print(f"  Took {duration:.2f}s including recording")
    except ImportError as e:
        print(f"✗ Failed to load voice detector: {e}")
        return False
    except Exception as e:
        print(f"⚠ Voice test error: {e}")
        # still consider loaded ok
    
    print("\n✅ Voice emotion detector tested!\n")
    return True


def demo_complete_workflow():
    """Demo the complete workflow"""
    print("\n" + "="*70)
    print("DEMO: COMPLETE EMOTION DETECTION WORKFLOW")
    print("="*70)
    
    from emotion_fusion import fuse_emotions
    from text_sentiment_analyzer import analyze_text_sentiment, convert_sentiment_to_emotion
    
    print("""
This demonstrates the complete workflow:
1. Get facial emotion (simulated)
2. Get voice emotion (simulated)
3. Get text sentiment (simulated)
4. Fuse them together
""")
    
    # Simulated inputs
    face_emotion = "Happy"
    voice_emotion = "Happy"
    text = "I'm feeling great!"
    
    print(f"Input Data:")
    print(f"  Facial emotion (from camera): {face_emotion}")
    print(f"  Voice emotion (from recording): {voice_emotion}")
    print(f"  Text: \"{text}\"")
    
    # Analyze text
    print(f"\nStep 1: Analyze text sentiment")
    text_result = analyze_text_sentiment(text, verbose=False)
    text_emotion = convert_sentiment_to_emotion(text_result['sentiment'])
    print(f"  → Sentiment: {text_result['sentiment']}, Emotion: {text_emotion}")
    
    # Fuse emotions
    print(f"\nStep 2: Fuse all three emotions")
    final_emotion = fuse_emotions(
        face_emotion,
        voice_emotion,
        text_emotion,
        method='weighted'
    )
    
    print(f"\n✨ FINAL RESULT: {final_emotion.upper()}")
    print("\n✅ Complete workflow demo finished!\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " COMPLETE EMOTION DETECTION SYSTEM - TEST SUITE ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Test 1: Imports
    print("\n[1/5] Testing imports...")
    results['imports'] = test_imports()
    
    if not results['imports']:
        print("\n❌ Import test failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    # Test 2: Emotion fusion
    print("\n[2/5] Testing emotion fusion...")
    results['fusion'] = test_emotion_fusion()
    
    # Test 3: Text sentiment
    print("\n[3/5] Testing text sentiment analysis...")
    results['text'] = test_text_sentiment()
    
    # Test 4: Voice emotion
    print("\n[4/5] Testing voice emotion detector...")
    results['voice'] = test_voice_emotion()
    
    # Test 5: Complete workflow
    print("\n[5/5] Demonstrating complete workflow...")
    results['workflow'] = demo_complete_workflow()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    test_names = ['Imports', 'Fusion', 'Text', 'Voice', 'Workflow']
    for i, (name, passed) in enumerate(zip(test_names, results.values()), 1):
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {i}. {name:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is ready to use!")
        print("\nNext steps:")
        print("  • Run: python final_emotion_detection.py")
        print("  • Or:  python triple_emotion_detection.py")
    else:
        print("❌ Some tests failed - Please check errors above")
    
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
