"""
FINAL INTEGRATED EMOTION DETECTION SYSTEM
Complete Facial + Voice Emotion Detection Running Continuously
Usage: python final_emotion_detection.py
No menu, no options - just run it!
"""

import cv2
from keras.models import model_from_json
import numpy as np
from src.voice_emotion_detector import voice_emotion_with_confidence, N_MFCC
from src.ai_emotion_responder import ai_response, ai_response_silent
import threading
import time
import sys

# optimization constants
# downscaling improves speed; skip frames removed for stability



class IntegratedEmotionDetector:
    """
    Main class for integrated continuous emotion detection
    Facial detection + Voice detection in real-time
    """
    
    def __init__(self):
        """Initialize the detector with all models"""
        print("\n" + "="*70)
        print("INTEGRATED EMOTION DETECTION SYSTEM - STARTING UP")
        print("="*70)
        
        print("\n📦 Loading facial emotion model...", end="", flush=True)
        self.facial_model = self._load_facial_model()
        print(" ✓")
        
        print("📦 Loading face detector...", end="", flush=True)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print(" ✓")
        
        print("📦 Initializing webcam...", end="", flush=True)
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print(" ✗\n❌ Error: Could not open webcam!")
            sys.exit(1)
        print(" ✓")
        
        # Facial emotion labels (FER2013 standard)
        self.facial_emotion_labels = {
            0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
            4: 'sad', 5: 'surprise', 6: 'neutral'
        }
        
        # State variables
        self.voice_emotion_result = None
        self.voice_result_time = None
        self.voice_recording_in_progress = False
        self.running = True
        self.frame_count = 0
        self.facial_emotion_current = 'neutral'
        # no frame skipping; detect every frame for consistent bounding box
        
        print("\n" + "="*70)
        print("✅ SYSTEM READY!")
        print("="*70)
        print("\n📌 INSTRUCTIONS:")
        print("   • Facial emotion is detected CONTINUOUSLY in real-time")
        print("   • Type 'v' in terminal + Press Enter to record VOICE (1s)")
        print("   • Type 'a' in terminal + Press Enter to get AI RESPONSE")
        print("   • Type 'r' in terminal + Press Enter to RESET voice result")
        print("   • Type 'q' in terminal + Press Enter to QUIT")
        print("   • Press ESC in window to exit (backup)")
        print("\n" + "="*70)
        
        # Start input handler thread
        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.input_thread.start()
        
        print("\n🎬 Starting continuous detection...\n")
        print("Command > ", end="", flush=True)
    
    def _load_facial_model(self):
        """Load the pre-trained facial emotion detection model"""
        try:
            json_file = open("emotiondetector.json", "r")
            model_json = json_file.read()
            json_file.close()
            model = model_from_json(model_json)
            model.load_weights("emotiondetector.h5")
            return model
        except FileNotFoundError:
            print("\n❌ Error: emotiondetector.json or emotiondetector.h5 not found!")
            sys.exit(1)
    
    def _extract_features(self, img):
        """Extract features from facial image"""
        feature = np.array(img)
        feature = feature.reshape(1, 48, 48, 1)
        return feature / 255.0
    
    def _input_handler(self):
        """Handle console input in a separate thread"""
        while self.running:
            try:
                cmd = input().strip().lower()
                
                if cmd == 'v' and not self.voice_recording_in_progress:
                    self.voice_recording_in_progress = True
                    print("\n" + "🎤 "*30)
                    print("🎤 RECORDING VOICE (1s) - SPEAK NOW! 🎤")
                    print("🎤 "*30)
                    result = voice_emotion_with_confidence()
                    self.voice_emotion_result = result
                    self.voice_result_time = time.time()
                    # concise output: emotion with confidence only
                    print(f"→ Voice: {result['emotion'].upper()} ({result['confidence']:.0%})")
                    self.voice_recording_in_progress = False
                    print("\nCommand > ", end="", flush=True)
                
                elif cmd == 'a':
                    self._ai_respond()
                    
                elif cmd == 'r':
                    self.voice_emotion_result = None
                    print("✓ Voice result cleared")
                    print("Command > ", end="", flush=True)
                    
                elif cmd == 'q':
                    print("\n👋 Shutting down...")
                    self.running = False
                    break
                    
                else:
                    if cmd != '':
                        print(f"Invalid command: '{cmd}' (use 'v', 'a', 'r', or 'q')")
                    print("Command > ", end="", flush=True)
                    
            except EOFError:
                break
            except Exception as e:
                print(f"Input error: {e}")
    
    def _detect_facial_emotion(self, frame):
        """Detect facial emotion in frame (optimized)."""
        # Detect on downscaled image (speed), classify on full-res ROI (correct crop)
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray_small, 1.3, 5)

        detected_emotions = []

        for (p, q, r, s) in faces:
            # scale coords back to original frame
            p_orig, q_orig, r_orig, s_orig = [int(v * 2) for v in (p, q, r, s)]

            # clamp to frame bounds
            h, w = gray.shape[:2]
            x1 = max(0, p_orig)
            y1 = max(0, q_orig)
            x2 = min(w, p_orig + r_orig)
            y2 = min(h, q_orig + s_orig)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            roi = gray[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            try:
                roi_resized = cv2.resize(roi, (48, 48), interpolation=cv2.INTER_AREA)
                img = self._extract_features(roi_resized)
                pred = self.facial_model.predict(img, verbose=0)

                emotion_index = int(np.argmax(pred[0]))  # already 0..6
                emotion = self.facial_emotion_labels.get(emotion_index, 'neutral')
                confidence = float(pred[0][emotion_index])

                # Debug: show top-2 probabilities near the box
                top2 = np.argsort(pred[0])[-2:][::-1]
                dbg = f"{self.facial_emotion_labels[int(top2[0])]}:{pred[0][int(top2[0])]*100:.0f}% " \
                      f"{self.facial_emotion_labels[int(top2[1])]}:{pred[0][int(top2[1])]*100:.0f}%"
                cv2.putText(
                    frame, dbg, (x1, max(15, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1
                )

                detected_emotions.append((emotion, confidence, (x1, y1, x2 - x1, y2 - y1)))
            except Exception:
                continue

        return frame, detected_emotions
    
    def _ai_respond(self):
        """
        Generate and speak AI response based on current emotion.
        Uses facial emotion if available, otherwise uses voice emotion.
        """
        emotion_to_respond = None
        
        # Prefer voice emotion if recently recorded
        if self.voice_emotion_result:
            elapsed = time.time() - self.voice_result_time
            if elapsed < 30:  # Use voice if within last 30 seconds
                emotion_to_respond = self.voice_emotion_result['emotion']
        
        # Fall back to facial emotion
        if not emotion_to_respond:
            emotion_to_respond = self.facial_emotion_current
        
        if emotion_to_respond:
            # Generate AI response with text-to-speech
            ai_response(
                emotion_to_respond,
                speak=True,        # Enable text-to-speech
                verbose=True       # Show status messages
            )
        else:
            print("\n⚠️  No emotion available to respond to!")
        
        print("Command > ", end="", flush=True)
    
    def _draw_results(self, frame, detected_emotions):
        """Draw facial and voice emotions on frame"""
        # Draw facial emotions
        for emotion, confidence, (p, q, r, s) in detected_emotions:
            color = (0, 255, 0)  # Green
            text = f"{emotion.upper()} ({confidence*100:.0f}%)"
            cv2.putText(frame, text, (p-10, q-30),
                       cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.2, color, 2)
            self.facial_emotion_current = emotion
        
        # Draw voice emotion if available
        if self.voice_emotion_result:
            elapsed = time.time() - self.voice_result_time
            if elapsed < 5:  # Display for 5 seconds
                # Green background for voice
                cv2.rectangle(frame, (10, 10), (frame.shape[1] - 10, 80), (0, 255, 0), -1)
                cv2.putText(frame, "🎤 VOICE EMOTION DETECTED", (20, 35),
                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.2, (0, 0, 0), 2)
                voice_text = f"{self.voice_emotion_result['emotion'].upper()} ({self.voice_emotion_result['confidence']:.0%})"
                cv2.putText(frame, voice_text, (20, 65),
                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (0, 0, 0), 2)
            else:
                self.voice_emotion_result = None
        
        # Recording indicator
        if self.voice_recording_in_progress:
            cv2.rectangle(frame, (10, 10), (frame.shape[1] - 10, 80), (0, 0, 255), -1)
            cv2.putText(frame, "🎤 RECORDING VOICE... (check terminal)", (20, 50),
                       cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.2, (255, 255, 255), 2)
        
        # Status bar
        cv2.rectangle(frame, (0, frame.shape[0] - 35), (frame.shape[1], frame.shape[0]), 
                     (50, 50, 50), -1)
        cv2.putText(frame, "Facial: Real-time | Voice: Type 'v' | AI: Type 'a' | Quit: Type 'q'", 
                   (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Frame counter
        cv2.putText(frame, f"Frames: {self.frame_count}", 
                   (frame.shape[1] - 200, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        """Main continuous detection loop"""
        try:
            while self.running:
                ret, frame = self.webcam.read()
                
                if not ret or frame is None:
                    print("Error: Could not read from webcam")
                    break
                
                self.frame_count += 1
                
                # Facial emotion detection every frame for stability
                frame, detected_emotions = self._detect_facial_emotion(frame)
                
                # Draw results
                frame = self._draw_results(frame, detected_emotions)
                
                # Display
                cv2.imshow("INTEGRATED EMOTION DETECTION - Facial + Voice", frame)
                
                # ESC key as backup exit
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC
                    print("\n👋 ESC pressed - shutting down...")
                    self.running = False
                    break
        
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🛑 Cleaning up...")
        self.running = False
        self.webcam.release()
        cv2.destroyAllWindows()
        print("✓ System shutdown complete")
        print("\n" + "="*70)
        print(f"📊 FINAL STATS:")
        print(f"   Total frames processed: {self.frame_count}")
        print(f"   Last facial emotion: {self.facial_emotion_current.upper()}")
        print(f"   Voice detections made: {1 if self.voice_emotion_result else 0}")
        print("="*70)


def main():
    """Main entry point"""
    try:
        detector = IntegratedEmotionDetector()
        detector.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
