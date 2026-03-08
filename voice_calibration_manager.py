"""
Voice Calibration Manager
Tests current voice detection accuracy and guides through personalization
"""

import os
import numpy as np
from voice_emotion_detector import voice_emotion_with_confidence, VOICE_EMOTION_LABELS
from voice_personalization import (
    check_personalized_model_exists,
    add_correction,
    CALIBRATION_RECORDS_FILE
)
import json


def test_voice_detection():
    """Test voice detection accuracy"""
    print("\n" + "="*70)
    print("🧪 VOICE DETECTION TEST")
    print("="*70)
    print("\nThis will test how well the system detects your emotions from voice.")
    print("You'll record voice samples for each emotion, and see the predictions.\n")
    
    results = []
    
    for emotion in VOICE_EMOTION_LABELS:
        print(f"\n{'='*70}")
        print(f"TEST EMOTION: {emotion.upper()}")
        print(f"{'='*70}")
        print(f"Prepare to speak with a {emotion.lower()} tone.")
        print("Examples:")
        
        if emotion == "Happy":
            print("  → Speak cheerfully and enthusiastically!")
        elif emotion == "Sad":
            print("  → Speak softly and sadly...")
        elif emotion == "Angry":
            print("  → Speak with intensity and frustration!")
        elif emotion == "Fear":
            print("  → Speak nervously and with hesitation...")
        elif emotion == "Neutral":
            print("  → Speak in a flat, emotionless tone...")
        
        input("\nPress Enter when ready to record...")
        
        # Record and predict
        result = voice_emotion_with_confidence()
        
        detected = result['emotion']
        confidence = result['confidence']
        correct = detected == emotion
        
        status = "✅ CORRECT" if correct else f"❌ WRONG (got {detected})"
        print(f"\nActual: {emotion} | Predicted: {detected} ({confidence:.1%}) | {status}")
        
        results.append({
            'actual': emotion,
            'predicted': detected,
            'confidence': confidence,
            'correct': correct
        })
    
    # Summary
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results) * 100
    
    print(f"\n{'='*70}")
    print("📊 TEST RESULTS")
    print(f"{'='*70}")
    print(f"Accuracy: {accuracy:.0f}% ({correct_count}/{len(results)} correct)")
    
    print("\nDetailed Results:")
    for i, r in enumerate(results, 1):
        status = "✅" if r['correct'] else "❌"
        print(f"  {status} {i}. {r['actual']:10} → {r['predicted']:10} ({r['confidence']:.0%})")
    
    return accuracy, results


def show_recommendations(accuracy):
    """Show recommendations based on accuracy"""
    print(f"\n{'='*70}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*70}\n")
    
    if accuracy >= 80:
        print("✅ GREAT! Your voice detection is working well!")
        print("   Keep using the system as is.")
    elif accuracy >= 60:
        print("⚠️  MODERATE: Some emotions are being confused.")
        print("   Consider running voice personalization to improve accuracy.")
    else:
        print("❌ LOW ACCURACY: The system needs personalization to your voice.")
        print("   Run voice personalization now to get better results!")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    if accuracy < 80:
        print("\n🚀 QUICK FIX (1 minute):")
        print("   Run: python voice_personalization.py quick")
        print("   This records 1 sample per emotion and trains a personalized model.")
        
        print("\n📚 FULL PERSONALIZATION (5-10 minutes):")
        print("   Run: python voice_personalization.py full")
        print("   Records 5-10 samples per emotion for better accuracy.")
        
        print("\n🔄 FEEDBACK LOOP:")
        print("   After personalization, the system will learn from corrections.")
        print("   When it misclassifies, tell it the correct emotion,")
        print("   and it will use that to improve over time.")


def show_current_status():
    """Show current system status"""
    print("\n" + "="*70)
    print("📊 VOICE SYSTEM STATUS")
    print("="*70)
    
    # Check for personalized model
    has_personalized = check_personalized_model_exists()
    print(f"\nPersonalized Model: {'✅ ACTIVE' if has_personalized else '❌ Not trained'}")
    print(f"  Location: voice_emotion_model_personalized.h5")
    
    # Check for corrections recorded
    if os.path.exists(CALIBRATION_RECORDS_FILE):
        try:
            with open(CALIBRATION_RECORDS_FILE, 'r') as f:
                records = json.load(f)
            print(f"\nFeedback Corrections: {len(records)} recorded")
            if len(records) > 0:
                print("  Recent corrections:")
                for record in records[-5:]:  # Show last 5
                    print(f"    • {record['system_prediction']} → {record['actual_emotion']}")
        except:
            pass
    else:
        print("\nFeedback Corrections: None recorded yet")
    
    # Check training data
    training_dir = 'voice_training_data'
    if os.path.exists(training_dir):
        sample_count = 0
        for emotion in VOICE_EMOTION_LABELS:
            emotion_dir = os.path.join(training_dir, emotion)
            if os.path.exists(emotion_dir):
                samples = len([f for f in os.listdir(emotion_dir) if f.endswith('.npy')])
                sample_count += samples
                if samples > 0:
                    print(f"\n{emotion}: {samples} samples recorded")
        print(f"\nTotal Training Samples: {sample_count}")
    else:
        print("\nTraining Data: No samples recorded yet")


def interactive_calibration_flow():
    """Full interactive calibration flow"""
    print("\n" + "="*70)
    print("🎤 VOICE EMOTION CALIBRATION FLOW")
    print("="*70)
    
    while True:
        print("\n" + "="*70)
        print("What would you like to do?")
        print("="*70)
        print("1. Test current voice detection accuracy")
        print("2. View voice system status")
        print("3. Run quick personalization (1 min, 1 sample per emotion)")
        print("4. Run full personalization (10 min, 5-10 samples per emotion)")
        print("5. Retrain with existing samples")
        print("6. Exit")
        
        choice = input("\nChoose (1-6) > ").strip()
        
        if choice == '1':
            accuracy, results = test_voice_detection()
            show_recommendations(accuracy)
            
        elif choice == '2':
            show_current_status()
            
        elif choice == '3':
            print("\n🚀 Starting quick personalization...")
            os.system('python voice_personalization.py quick')
            
        elif choice == '4':
            print("\n📚 Starting full personalization...")
            os.system('python voice_personalization.py full')
            
        elif choice == '5':
            print("\n🔄 Retraining with existing samples...")
            os.system('python voice_personalization.py train')
            
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            accuracy, results = test_voice_detection()
            show_recommendations(accuracy)
        elif command == 'status':
            show_current_status()
        elif command == 'flow':
            interactive_calibration_flow()
        else:
            print(f"Unknown command: {command}")
    else:
        interactive_calibration_flow()
