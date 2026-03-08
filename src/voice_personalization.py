"""
Voice Personalization Module
Collects samples of your voice for each emotion and trains a personalized model
This system learns from your voice patterns and corrects misclassifications
"""

import numpy as np
import librosa
import sounddevice as sd
import os
import json
from pathlib import Path
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Voice emotion labels
VOICE_EMOTION_LABELS = ['Angry', 'Fear', 'Happy', 'Neutral', 'Sad']
N_MFCC = 20
PERSONALIZED_MODEL_PATH = 'voice_emotion_model_personalized.h5'
TRAINING_DATA_DIR = 'voice_training_data'
CALIBRATION_RECORDS_FILE = 'voice_calibration_records.json'


def create_training_directory():
    """Create directory structure for training data"""
    if not os.path.exists(TRAINING_DATA_DIR):
        os.makedirs(TRAINING_DATA_DIR)
        for emotion in VOICE_EMOTION_LABELS:
            emotion_dir = os.path.join(TRAINING_DATA_DIR, emotion)
            os.makedirs(emotion_dir, exist_ok=True)
    print(f"✓ Training data directory ready at: {TRAINING_DATA_DIR}/")


def record_voice_sample(emotion, sample_number=1):
    """
    Record a voice sample for a specific emotion
    
    Args:
        emotion (str): Emotion to record (e.g., 'Happy', 'Sad')
        sample_number (int): Sample number for this emotion
    
    Returns:
        str: Path to saved audio file
    """
    print(f"\n🎤 Recording {emotion} - Sample {sample_number}")
    print(f"   Get ready... Speak for 2 seconds with {emotion} emotion!")
    print("   Starting in 3 seconds...")
    
    import time
    for i in range(3, 0, -1):
        print(f"   {i}...", end="", flush=True)
        time.sleep(1)
    print("\n   🔴 RECORDING NOW! Speak naturally...", flush=True)
    
    # Record 2 seconds of audio
    duration = 2.0
    sample_rate = 16000
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("   ✓ Recorded!")
    
    # Normalize audio
    audio_data = audio_data.flatten()
    audio_max = np.max(np.abs(audio_data))
    if audio_max > 0:
        audio_data = audio_data / audio_max
    
    # Save to file
    emotion_dir = os.path.join(TRAINING_DATA_DIR, emotion)
    file_path = os.path.join(emotion_dir, f'sample_{sample_number}.npy')
    np.save(file_path, audio_data)
    
    return file_path


def extract_mfcc_features_personalized(audio_data, sample_rate=16000):
    """Extract MFCC features from audio"""
    mfcc_features = librosa.feature.mfcc(
        y=audio_data,
        sr=sample_rate,
        n_mfcc=N_MFCC,
        n_fft=400,
        hop_length=160
    )
    
    # Use mean and std
    mfcc_mean = np.mean(mfcc_features, axis=1)
    mfcc_std = np.std(mfcc_features, axis=1)
    mfcc_combined = np.concatenate([mfcc_mean, mfcc_std])
    
    return mfcc_combined


def load_training_data():
    """Load all training samples from directory"""
    X_data = []
    y_data = []
    
    print("\n📂 Loading training data...")
    total_samples = 0
    
    for emotion_idx, emotion in enumerate(VOICE_EMOTION_LABELS):
        emotion_dir = os.path.join(TRAINING_DATA_DIR, emotion)
        
        if not os.path.exists(emotion_dir):
            print(f"   ⚠ No data for {emotion}")
            continue
        
        # Load all .npy files for this emotion
        npy_files = [f for f in os.listdir(emotion_dir) if f.endswith('.npy')]
        
        if len(npy_files) == 0:
            print(f"   ⚠ No samples recorded for {emotion}")
            continue
        
        print(f"   ✓ {emotion}: {len(npy_files)} samples", end="")
        
        for npy_file in npy_files:
            try:
                file_path = os.path.join(emotion_dir, npy_file)
                audio_data = np.load(file_path)
                
                # Extract MFCC features
                features = extract_mfcc_features_personalized(audio_data, sample_rate=16000)
                X_data.append(features)
                y_data.append(emotion_idx)
                
            except Exception as e:
                print(f"\n      Error loading {npy_file}: {e}")
        
        print(f" → loaded")
        total_samples += len(npy_files)
    
    print(f"\n✓ Total samples loaded: {total_samples}")
    
    if len(X_data) == 0:
        return None, None
    
    return np.array(X_data), np.array(y_data)


def build_personalized_model(input_shape=N_MFCC*2):
    """Build a personalized voice emotion model"""
    model = Sequential()
    
    # Input layer
    model.add(Dense(128, activation='relu', input_shape=(input_shape,)))
    model.add(Dropout(0.3))
    
    # Hidden layers
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    
    # Output layer
    model.add(Dense(len(VOICE_EMOTION_LABELS), activation='softmax'))
    
    # Compile
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def train_personalized_model(X_train, y_train, epochs=50, batch_size=8):
    """Train personalized model with your voice data"""
    print("\n🧠 Training personalized model...")
    print(f"   Epochs: {epochs} | Batch size: {batch_size}")
    print(f"   Data: {len(X_train)} samples across {len(set(y_train))} emotions\n")
    
    # Split data
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train,
        test_size=0.2,
        random_state=42,
        stratify=y_train
    )
    
    # Convert labels to one-hot encoding
    y_train_split = to_categorical(y_train_split, num_classes=len(VOICE_EMOTION_LABELS))
    y_val = to_categorical(y_val, num_classes=len(VOICE_EMOTION_LABELS))
    
    # Build and train model
    model = build_personalized_model(input_shape=X_train.shape[1])
    
    history = model.fit(
        X_train_split, y_train_split,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1,
        shuffle=True
    )
    
    # Save model
    model.save(PERSONALIZED_MODEL_PATH)
    print(f"\n✅ Model saved to: {PERSONALIZED_MODEL_PATH}")
    
    # Print summary
    val_accuracy = history.history['val_accuracy'][-1]
    print(f"📊 Final validation accuracy: {val_accuracy*100:.1f}%")
    
    return model


def calibrate_voice():
    """
    Interactive calibration: Record samples for each emotion
    Recommended: 5 samples per emotion for good personalizations
    """
    print("\n" + "="*70)
    print("🎤 VOICE PERSONALIZATION CALIBRATION")
    print("="*70)
    print("\nThis will record your voice saying different emotions.")
    print("More samples = better accuracy (recommended: 5-10 per emotion)")
    print("\nEmotions to calibrate:")
    for i, emotion in enumerate(VOICE_EMOTION_LABELS, 1):
        print(f"  {i}. {emotion}")
    
    create_training_directory()
    
    # Ask user how many samples per emotion
    try:
        num_samples = int(input("\nHow many samples per emotion? (recommended: 5) > "))
    except:
        num_samples = 5
    
    # Record samples for each emotion
    for emotion in VOICE_EMOTION_LABELS:
        print(f"\n{'='*70}")
        print(f"EMOTION: {emotion.upper()}")
        print(f"{'='*70}")
        
        for sample_num in range(1, num_samples + 1):
            record_voice_sample(emotion, sample_num)
            
            if sample_num < num_samples:
                input("\n   Press Enter to record next sample...")
    
    print("\n" + "="*70)
    print("✅ All samples recorded!")
    print("="*70)
    
    # Train model
    X_train, y_train = load_training_data()
    
    if X_train is not None:
        train_personalized_model(X_train, y_train, epochs=100, batch_size=8)
        print("\n✅ Personalized model created and saved!")
        print(f"   Location: {PERSONALIZED_MODEL_PATH}")
    else:
        print("\n❌ No training data found!")


def quick_calibration():
    """Quick 10-second calibration (1 sample per emotion)"""
    print("\n" + "="*70)
    print("⚡ QUICK VOICE CALIBRATION (1 sample per emotion)")
    print("="*70)
    
    create_training_directory()
    
    for emotion in VOICE_EMOTION_LABELS:
        print(f"\n{'='*70}")
        print(f"EMOTION: {emotion.upper()}")
        print(f"{'='*70}")
        record_voice_sample(emotion, 1)
    
    print("\n" + "="*70)
    print("✅ Quick calibration samples recorded!")
    print("="*70)
    
    # Train model
    X_train, y_train = load_training_data()
    
    if X_train is not None:
        train_personalized_model(X_train, y_train, epochs=30, batch_size=4)
        print("\n✅ Quick personalized model created!")
    else:
        print("\n❌ No training data found!")


def add_correction(system_prediction, correct_emotion, audio_path=None):
    """
    Record a correction when system misclassifies
    
    Args:
        system_prediction (str): What the system predicted
        correct_emotion (str): What the actual emotion is
        audio_path (str): Optional path to audio file to save
    """
    # This will be used to retrain the model over time
    record = {
        'system_prediction': system_prediction,
        'actual_emotion': correct_emotion,
        'timestamp': str(np.datetime64('now'))
    }
    
    # Load existing records
    records = []
    if os.path.exists(CALIBRATION_RECORDS_FILE):
        try:
            with open(CALIBRATION_RECORDS_FILE, 'r') as f:
                records = json.load(f)
        except:
            records = []
    
    # Add new record
    records.append(record)
    
    # Save updated records
    with open(CALIBRATION_RECORDS_FILE, 'w') as f:
        json.dump(records, f, indent=2)
    
    print(f"✅ Correction recorded: {system_prediction} → {correct_emotion}")


def check_personalized_model_exists():
    """Check if personalized model exists"""
    return os.path.exists(PERSONALIZED_MODEL_PATH)


def load_personalized_model():
    """Load the personalized model if it exists"""
    if check_personalized_model_exists():
        try:
            model = load_model(PERSONALIZED_MODEL_PATH)
            return model
        except Exception as e:
            print(f"❌ Error loading personalized model: {e}")
            return None
    return None


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("VOICE PERSONALIZATION TOOL")
    print("="*70)
    print("\nUsage:")
    print("  python voice_personalization.py full     - Full calibration (5+ samples)")
    print("  python voice_personalization.py quick    - Quick calibration (1 sample)")
    print("  python voice_personalization.py train    - Retrain with existing samples")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'full':
            calibrate_voice()
        elif command == 'quick':
            quick_calibration()
        elif command == 'train':
            print("\n🧠 Retraining with existing samples...")
            X_train, y_train = load_training_data()
            if X_train is not None:
                train_personalized_model(X_train, y_train, epochs=100)
            else:
                print("❌ No training data found! Run calibration first.")
        else:
            print(f"\n❌ Unknown command: {command}")
    else:
        print("\n⚠ Please specify a command (full, quick, or train)")
