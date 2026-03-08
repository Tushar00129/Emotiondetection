"""
RETRAIN FACIAL EMOTION MODEL - REAL-WORLD VERSION
Uses FER2013 dataset for proper training

NOTE:
This project ships with a pre-trained model (emotiondetector.json/.h5).
This training script is intentionally DISABLED to avoid accidental long-running
downloads/training during normal usage.

If you really want to retrain, use retrain_model_new.py (or re-enable this file).
"""

raise SystemExit(
    "retrain_model.py is disabled to keep the system running smoothly. "
    "Use retrain_model_new.py for retraining."
)

import os
import numpy as np
import pandas as pd
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D, Input, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import requests
import zipfile
import io

# FER2013 dataset URL
FER2013_URL = "https://www.kaggle.com/api/v1/datasets/download/msambare/fer2013"

def download_fer2013():
    """Download and extract FER2013 dataset"""
    print("Downloading FER2013 dataset...")
    response = requests.get(FER2013_URL)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("fer2013")
    print("FER2013 downloaded and extracted.")

def load_fer2013():
    """Load FER2013 dataset"""
    csv_path = "fer2013/fer2013.csv"
    if not os.path.exists(csv_path):
        download_fer2013()
    
    df = pd.read_csv(csv_path)
    df = df[df['Usage'] == 'Training']  # Use training data
    
    # Convert pixels to images
    images = []
    labels = []
    for index, row in df.iterrows():
        pixels = np.array(row['pixels'].split(), dtype='float32')
        image = pixels.reshape(48, 48, 1) / 255.0
        images.append(image)
        labels.append(row['emotion'])
    
    return np.array(images), np.array(labels)

def build_model():
    """Build improved CNN model with batch normalization"""
    model = Sequential()
    model.add(Input(shape=(48, 48, 1)))
    
    model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(7, activation='softmax'))  # FER2013 has 7 emotions

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    print("Loading FER2013 dataset...")
    try:
        X, y = load_fer2013()
    except:
        print("Failed to download FER2013. Using local data...")
        # Fallback to local data
        df = create_dataframe("images")
        features = extract_features(df['image'])
        features = features / 255.0
        le = LabelEncoder()
        labels_encoded = le.fit_transform(df['label'])
        labels_categorical = to_categorical(labels_encoded, num_classes=7)
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels_categorical, test_size=0.2, random_state=42, stratify=labels_encoded
        )
        # Train with local data
        model = build_model()
        # Model is already 7 classes
        
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        datagen.fit(X_train)
        
        early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)
        reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=5, min_lr=1e-6)
        
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=32),
            validation_data=(X_test, y_test),
            epochs=50,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        loss, accuracy = model.evaluate(X_test, y_test)
        print(f"Test accuracy: {accuracy:.4f}")
        
        model_json = model.to_json()
        with open("emotiondetector.json", "w") as json_file:
            json_file.write(model_json)
        model.save("emotiondetector.h5")
        print("Model saved with local data!")
        return

    print(f"Dataset shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    
    # Encode labels (FER2013 has 0-6 for emotions)
    labels_categorical = to_categorical(y, num_classes=7)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels_categorical, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")

    # Data augmentation
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    datagen.fit(X_train)

    # Build and train model
    model = build_model()
    
    # Callbacks
    early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=5, min_lr=1e-6)
    
    print("Training model...")
    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=64),
        validation_data=(X_test, y_test),
        epochs=100,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {accuracy:.4f}")

    # Classification report
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
    
    emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    print("Classification Report:")
    print(classification_report(y_true_classes, y_pred_classes, target_names=emotion_labels))

    # Save model
    model_json = model.to_json()
    with open("emotiondetector.json", "w") as json_file:
        json_file.write(model_json)
    model.save("emotiondetector.h5")
    print("Model saved!")

    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='train accuracy')
    plt.plot(history.history['val_accuracy'], label='val accuracy')
    plt.title('Model Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='train loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.title('Model Loss')
    plt.legend()
    
    plt.savefig('training_history.png')
    plt.show()

def create_dataframe(dir_path):
    """Create dataframe from images in subfolders"""
    image_paths = []
    labels = []
    for label in sorted(os.listdir(dir_path)):
        label_path = os.path.join(dir_path, label)
        if os.path.isdir(label_path):
            for img_name in os.listdir(label_path):
                if img_name.endswith(('.jpg', '.png', '.jpeg')):
                    image_paths.append(os.path.join(label_path, img_name))
                    labels.append(label)
    return pd.DataFrame({'image': image_paths, 'label': labels})

def extract_features(images):
    """Extract features from images"""
    features = []
    for image in images:
        img = load_img(image, color_mode="grayscale", target_size=(48, 48))
        img_array = np.array(img)
        features.append(img_array)
    features = np.array(features)
    features = features.reshape(len(features), 48, 48, 1)
    return features

if __name__ == "__main__":
    main()
