"""
Voice Emotion Training Module (Optional)
Train your own model for better accuracy with real emotion data
"""

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras.utils import to_categorical
import librosa
import os
from voice_emotion_detector import N_MFCC, VOICE_EMOTION_LABELS, extract_mfcc_features


def load_training_data(data_directory):
    """
    Load training audio files from a directory structure.
    
    Expected directory structure:
    data_directory/
        ├── Angry/
        ├── Fear/
        ├── Happy/
        ├── Neutral/
        └── Sad/
    
    Each subdirectory should contain .wav audio files.
    
    Args:
        data_directory (str): Path to training data directory
    
    Returns:
        tuple: (X_train, y_train) - features and labels
    """
    X_data = []
    y_data = []
    
    for label_idx, emotion in enumerate(VOICE_EMOTION_LABELS):
        emotion_dir = os.path.join(data_directory, emotion)
        
        if not os.path.exists(emotion_dir):
            print(f"Warning: Directory not found: {emotion_dir}")
            continue
        
        audio_files = [f for f in os.listdir(emotion_dir) if f.endswith('.wav')]
        print(f"Loading {emotion}: {len(audio_files)} files...")
        
        for audio_file in audio_files:
            file_path = os.path.join(emotion_dir, audio_file)
            
            try:
                # Load audio
                audio_data, sr = librosa.load(file_path, sr=16000)
                
                # Extract MFCC features (same as in prediction)
                mfcc_combined = extract_mfcc_features(audio_data, sample_rate=sr)
                
                X_data.append(mfcc_combined)
                y_data.append(label_idx)
                
            except Exception as e:
                print(f"  Error loading {audio_file}: {e}")
    
    return np.array(X_data), np.array(y_data)


def train_voice_emotion_model(X_train, y_train, model_save_path='voice_emotion_model.h5'):
    """
    Train the voice emotion model with your data.
    
    Args:
        X_train (np.ndarray): Training features (samples, features)
        y_train (np.ndarray): Training labels (samples,)
        model_save_path (str): Path to save trained model
    
    Returns:
        keras.models.Sequential: Trained model
    """
    from sklearn.model_selection import train_test_split
    
    print(f"\nTraining Data: {len(X_train)} samples")
    
    # Split into train and validation sets
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train,
        test_size=0.2,
        random_state=42,
        stratify=y_train
    )
    
    # Convert labels to one-hot encoding
    y_train_categorical = to_categorical(y_train_split, num_classes=len(VOICE_EMOTION_LABELS))
    y_val_categorical = to_categorical(y_val, num_classes=len(VOICE_EMOTION_LABELS))
    
    # Build model using shared helper from voice_emotion_detector
    from voice_emotion_detector import build_voice_emotion_model
    # input_shape now includes delta and delta-delta stats (6×N_MFCC)
    model = build_voice_emotion_model(input_shape=N_MFCC * 6)

    # compile is already done by builder, but ensure optimizer settings
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"Training Set: {len(X_train_split)} samples")
    print(f"Validation Set: {len(X_val)} samples")
    print("\nTraining model...")
    
    # Train model
    history = model.fit(
        X_train_split, y_train_categorical,
        validation_data=(X_val, y_val_categorical),
        epochs=50,
        batch_size=32,
        verbose=1
    )
    
    # Evaluate
    val_loss, val_accuracy = model.evaluate(X_val, y_val_categorical, verbose=0)
    print(f"\nValidation Accuracy: {val_accuracy:.2%}")
    
    # Save model
    model.save(model_save_path)
    print(f"Model saved: {model_save_path}")
    
    return model


def quick_train(data_directory='emotion_data'):
    """
    Quick training script for users with emotion data.
    
    Usage:
        Place audio files in emotion_data/Angry/, emotion_data/Happy/, etc.
        Then run: python -c "from voice_emotion_training import quick_train; quick_train()"
    """
    print("="*60)
    print("Voice Emotion Model Training")
    print("="*60)
    
    # Load data
    X_train, y_train = load_training_data(data_directory)
    
    if len(X_train) == 0:
        print(f"No training data found in {data_directory}")
        print("\nExpected structure:")
        print(f"  {data_directory}/Angry/*.wav")
        print(f"  {data_directory}/Fear/*.wav")
        print(f"  {data_directory}/Happy/*.wav")
        print(f"  {data_directory}/Neutral/*.wav")
        print(f"  {data_directory}/Sad/*.wav")
        return
    
    # Train model
    model = train_voice_emotion_model(X_train, y_train)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print("\nYour trained model is ready to use!")
    print("The voice_emotion() function will automatically use it.")


if __name__ == "__main__":
    quick_train()
