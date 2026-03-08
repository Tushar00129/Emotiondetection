"""
RETRAIN FACIAL EMOTION MODEL - REAL-WORLD VERSION
Uses local data with augmentation for all classes
"""

import os
import numpy as np
import pandas as pd
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D, Input, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Data directory
DATA_DIR = "images"

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
    model.add(Dense(7, activation='softmax'))  # 7 emotions

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    print("Loading local data...")
    df = create_dataframe(DATA_DIR)
    print(f"Total images: {len(df)}")
    print("Label distribution:")
    print(df['label'].value_counts())

    print("Extracting features...")
    features = extract_features(df['image'])
    features = features / 255.0

    # Map labels to 7 emotions properly
    emotion_cycle = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    label_to_emotion = {}
    for i, label in enumerate(sorted(df['label'].unique())):
        label_to_emotion[label] = emotion_cycle[i % 7]
    
    df['emotion'] = df['label'].map(label_to_emotion)
    
    # Now encode emotions
    le = LabelEncoder()
    le.fit(emotion_cycle)
    labels_encoded = le.transform(df['emotion'])
    labels_categorical = to_categorical(labels_encoded, num_classes=7)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels_categorical, test_size=0.2, random_state=42, stratify=labels_encoded
    )

    print(f"Training data shape: {X_train.shape}")
    print(f"Test data shape: {X_test.shape}")

    # Data augmentation for all classes
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )

    # Generate augmented images for all classes
    augmented_X = []
    augmented_y = []
    for i in range(len(X_train)):
        img = X_train[i]
        label = y_train[i]
        img_expanded = np.expand_dims(img, axis=0)
        aug_iter = datagen.flow(img_expanded, batch_size=1)
        for _ in range(5):  # Generate 5 augmented versions per image
            aug_img = next(aug_iter)[0]
            augmented_X.append(aug_img)
            augmented_y.append(label)

    # Add augmented data to training set
    X_train_aug = np.concatenate([X_train, np.array(augmented_X)])
    y_train_aug = np.concatenate([y_train, np.array(augmented_y)])

    print(f"Augmented training data shape: {X_train_aug.shape}")

    # Build and train model
    model = build_model()
    
    # Callbacks for better training
    early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=5, min_lr=1e-6)
    
    print("Training model...")
    history = model.fit(
        X_train_aug, y_train_aug,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {accuracy:.4f}")

    # Predictions and classification report
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

if __name__ == "__main__":
    main()