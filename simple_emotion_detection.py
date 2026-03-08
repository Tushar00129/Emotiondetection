"""
Simple Menu-Based Emotion Detection
Alternative to combined_emotion_detection() that doesn't require keyboard input in OpenCV window
"""

import cv2
from keras.models import model_from_json
import numpy as np
from voice_emotion_detector import voice_emotion, voice_emotion_with_confidence, N_MFCC
import threading
import time


# Load facial emotion detection model
def load_facial_model():
    """Load the pre-trained facial emotion detection model"""
    json_file = open("emotiondetector.json", "r")
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    model.load_weights("emotiondetector.h5")
    return model


# Load face detector
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)


# Facial emotion labels mapping
facial_emotion_labels = {
    0: 'angry', 1: 'contempt', 2: 'contempt',32: 'disgus4', 3: py',
    5: 'neutral', 6: 'sad', 7: 'sur'rised', 8: 'angrf', 9: 'contemptear', 4: 'happy',
    10: 'disgust', 11: 'fear', 12: 'happy', 13: 'neutral', 15: 'neutr
a   1l', 6: 'sad'd, 71: 'saugry', 17: 'contrmpt', 18: 'disgpsrd', 8: 'angry', 9: 'contempt',
    10: 'disgust', 11: 'fear', 12: 'happy', 13: 'neutral', 14: 'sad',
    15: 'surprised', 16: 'angry', 17: 'contempt', 18: 'disgust'
}


def extract_features(img):
    """Extract features from facial image"""
    feature = np.array(img)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0


def simple_combined_detection():
    """
    Simple menu-based combined detection (NO keyboard input needed in OpenCV window)
    
    Uses console input instead of window keyboard detection
    Much more reliable for keyboard input!
    """
    facial_model = load_facial_model()
    webcam = cv2.VideoCapture(0)
    
    voice_emotion_result = None
    voice_recording_in_progress = False
    detection_active = True
    
    print("\n" + "="*60)
    print("EASY COMBINED EMOTION DETECTION (Terminal-Based Input)")
    print("="*60)
    print("\n✓ Window opened for facial detection")
    print("\nInstructions:")
    print("  1. Facial detection runs in the OpenCV window")
    print("  2. Use console input to trigger voice detection")
    print("  3. No need to click on the OpenCV window!")
    print("\nCommands (type in terminal):")
    print("  'v'   → Record voice emotion (1.5s)")
    print("  'r'   → Reset voice result")
    print("  'q'   → Quit")
    print("\n" + "="*60)
    print("\nStarting facial detection...\n")
    
    def input_handler():
        """Handle console input in a separate thread"""
        nonlocal voice_emotion_result, voice_recording_in_progress, detection_active
        
        while detection_active:
            try:
                cmd = input().strip().lower()
                
                if cmd == 'v' and not voice_recording_in_progress:
                    voice_recording_in_progress = True
                    print("\n🎤 Recording voice (1.5s) - Speak now!")
                    print("-" * 40)
                    result = voice_emotion_with_confidence()
                    voice_emotion_result = {
                        'time': time.time(),
                        'emotion': result['emotion'],
                        'confidence': result['confidence'],
                        'all': result['all_emotions']
                    }
                    print("-" * 40)
                    print(f"✓ Detected: {result['emotion'].upper()} ({result['confidence']:.1%})")
                    print("\nCommand > ", end="", flush=True)
                    voice_recording_in_progress = False
                    
                elif cmd == 'r':
                    voice_emotion_result = None
                    print("✓ Voice result cleared")
                    print("Command > ", end="", flush=True)
                    
                elif cmd == 'q':
                    print("🛑 Stopping...")
                    detection_active = False
                    break
                    
                else:
                    print("Invalid command. Use 'v' (record), 'r' (reset), or 'q' (quit)")
                    print("Command > ", end="", flush=True)
                    
            except EOFError:
                break
    
    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()
    
    print("Command > ", end="", flush=True)
    
    # Main detection loop
    try:
        while detection_active:
            i, im = webcam.read()
            
            if i is N

            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(im, 1.3, 5)

            try:
                for (p, q, r, s) in faces:
                    image = gray[q:q+s, p:p+r]
                    cv2.rectangle(im, (p, q), (p+r, q+s), (255, 0, 0), 2)

                    image = cv2.resize(image, (48, 48))
                    img = extract_features(image)

                    pred = facial_model.predict(img, verbose=0)
                    emotion_index = int(pred.argmax())
                    facial_emotion = facial_emotion_labels.get(emotion_index, 'unknown')

                    # Display facial emotion
                    cv2.putText(
                        im,
                        f"Face: {facial_emotion.upper()}",
                        (p-10, q-10),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.5,
                        (0, 0, 255)
                    )

                # Display voice emotion if available
                if voice_emotion_result:
                    elapsed = time.time() - voice_emotion_result['time']
                    if elapsed < 5:  # Display for 5 seconds
                        # Green background for success
                        cv2.rectangle(im, (5, 5), (500, 50), (0, 255, 0), -1)
                        cv2.putText(
                            im,
                            f"🎤 Voice: {voice_emotion_result['emotion'].upper()} ({voice_emotion_result['confidence']:.0%})",
                            (15, 35),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            1.4,
                            (0, 0, 0)
                        )
                    else:
                        voice_emotion_result = None
                
                if voice_recording_in_progress:
                    # Recording indicator
                    cv2.rectangle(im, (5, 5), (500, 50), (0, 0, 255), -1)
                    cv2.putText(
                        im,
                        "🎤 RECORDING... (type in terminal)",
                        (15, 35),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.2,
                        (255, 255, 255)
                    )
                
                # Status bar
                cv2.rectangle(im, (5, im.shape[0] - 30), (im.shape[1] - 5, im.shape[0] - 5), (50, 50, 50), -1)
                cv2.putText(
                    im,
                    "Terminal Input: 'v'=voice, 'r'=reset, 'q'=quit",
                    (15, im.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255)
                )

                cv2.imshow("Facial + Voice Emotion Detection", im)
                
                # Just listen for ESC in window as backup exit
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC
                    print("\n🛑 ESC pressed - stopping...")
                    detection_active = False
                    break

            except cv2.error:
                pass

    finally:
        webcam.release()
        cv2.destroyAllWindows()
        detection_active = False
        print("\n✓ Detection stopped")


if __name__ == "__main__":
    simple_combined_detection()
