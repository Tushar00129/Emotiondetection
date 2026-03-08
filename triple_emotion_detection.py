"""
Complete Integrated Emotion Detection Demo
Combines Facial + Voice + Text emotion detection with fusion
"""

import cv2
from keras.models import model_from_json
import numpy as np
from voice_emotion_detector import voice_emotion_with_confidence
from text_sentiment_analyzer import analyze_text_sentiment, convert_sentiment_to_emotion
from emotion_fusion import fuse_emotions, fuse_emotions_fast
from ai_emotion_responder import ai_response, ai_response_silent
import threading
import time
import sys


class TripleEmotionDetector:
    """
    Complete system: Facial + Voice + Text emotion detection with fusion
    """
    
    def __init__(self):
        """Initialize all three emotion detectors"""
        print("\n" + "="*70)
        print("TRIPLE EMOTION DETECTION SYSTEM (Face + Voice + Text)")
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
            print(" ✗")
            print("❌ Error: Could not open webcam!")
            sys.exit(1)
        print(" ✓")
        
        # Facial emotion labels (FER2013 standard)
        self.facial_emotion_labels = {
            0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
            4: 'sad', 5: 'surprise', 6: 'neutral'
        }
        
        # State variables
        self.facial_emotion_current = 'neutral'
        self.voice_emotion_current = None
        self.voice_confidence = None
        self.text_sentiment_current = None
        self.text_confidence = None
        self.fused_emotion = None
        
        self.running = True
        self.frame_count = 0
        # no frame skipping; detect every frame for stable bounding box
        
        print("\n" + "="*70)
        print("✅ SYSTEM READY!")
        print("="*70)
        print("\n📌 COMMANDS (in terminal):")
        print("   v = Record voice emotion (1.5s)")
        print("   t = Type text for sentiment analysis")
        print("   f = Show fusion results")
        print("   a = Get AI response (requires fused emotion)")
        print("   r = Reset results")
        print("   q = Quit")
        print("\n" + "="*70)
        
        # Start input handler
        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.input_thread.start()
        
        print("\n🎬 Starting triple emotion detection...\n")
        print("Command > ", end="", flush=True)
    
    def _load_facial_model(self):
        """Load facial emotion model"""
        try:
            json_file = open("emotiondetector.json", "r")
            model_json = json_file.read()
            json_file.close()
            model = model_from_json(model_json)
            model.load_weights("emotiondetector.h5")
            return model
        except FileNotFoundError:
            print("\n❌ Error: Model files not found!")
            sys.exit(1)
    
    def _extract_features(self, img):
        """Extract facial features"""
        feature = np.array(img)
        feature = feature.reshape(1, 48, 48, 1)
        return feature / 255.0
    
    def _input_handler(self):
        """Handle terminal commands"""
        while self.running:
            try:
                cmd = input().strip().lower()
                
                if cmd == 'v':
                    print("\n🎤 Recording voice (1s)...")
                    result = voice_emotion_with_confidence()
                    self.voice_emotion_current = result['emotion']
                    self.voice_confidence = result['confidence']
                    print(f"→ Voice: {self.voice_emotion_current} ({self.voice_confidence:.0%})")
                    print("Command > ", end="", flush=True)
                
                elif cmd == 't':
                    text = input("Text> ").strip()
                    if text:
                        result = analyze_text_sentiment(text)
                        self.text_sentiment_current = convert_sentiment_to_emotion(result['sentiment'])
                        self.text_confidence = result['confidence']
                        print(f"→ Text: {self.text_sentiment_current} ({self.text_confidence:.0%})")
                        print("Command > ", end="", flush=True)
                
                elif cmd == 'f':
                    self._show_fusion()
                
                elif cmd == 'a':
                    self._ai_respond()
                
                elif cmd == 'r':
                    self.voice_emotion_current = None
                    self.text_sentiment_current = None
                    self.fused_emotion = None
                    print("→ Results cleared")
                    print("Command > ", end="", flush=True)
                
                elif cmd == 'q':
                    print("\n👋 Shutting down...")
                    self.running = False
                    break
                
                elif cmd != '':
                    print(f"Invalid command '{cmd}'")
                    print("Command > ", end="", flush=True)
                
            except EOFError:
                break
    
    def _show_fusion(self):
        """Show the fusion results"""
        if not self.facial_emotion_current:
            print("No facial emotion detected yet")
        elif not self.voice_emotion_current:
            print("No voice emotion recorded yet")
        elif not self.text_sentiment_current:
            print("No text sentiment analyzed yet")
        else:
            # perform fast fusion using confidences to weight each modality
            self.fused_emotion = fuse_emotions_fast(
                self.facial_emotion_current,
                self.voice_emotion_current,
                self.text_sentiment_current,
                weights={'face':0.5,'voice':0.3,'text':0.2},
                confidences={'face':0.85,'voice':self.voice_confidence or 1.0,'text':self.text_confidence or 1.0}
            )
            print(f"\n✨ FUSED FINAL EMOTION: {self.fused_emotion.upper()}")
        
        print("Command > ", end="", flush=True)
    
    def _ai_respond(self):
        """
        Generate and speak AI response based on fused emotion.
        Requires that fusion has been performed (press 'f' first).
        """
        if not self.fused_emotion:
            print("\n⚠️  No fused emotion available yet!")
            print("   Please perform fusion first (press 'f')")
        else:
            # Generate AI response with text-to-speech
            ai_response(
                self.fused_emotion,
                speak=True,        # Enable text-to-speech
                verbose=True       # Show status messages
            )
        
        print("Command > ", end="", flush=True)
    
    def _detect_facial_emotion(self, frame):
        """Detect facial emotion on every frame using a downscaled image.
        """
        # downscale for speed
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_small, 1.3, 5)

        if len(faces) > 0:
            (p, q, r, s) = faces[0]
            # scale coords back to original frame size
            p_orig, q_orig, r_orig, s_orig = [int(v * 2) for v in (p, q, r, s)]
            roi = gray_small[q:(q+s), p:(p+r)]
            cv2.rectangle(frame, (p_orig, q_orig), (p_orig+r_orig, q_orig+s_orig), (0, 255, 0), 2)

            try:
                roi_resized = cv2.resize(roi, (48, 48))
                img = self._extract_features(roi_resized)
                pred = self.facial_model.predict(img, verbose=0)
                emotion_index = int(pred.argmax()) % 7  # Map to 7 emotions
                emotion = self.facial_emotion_labels.get(emotion_index, 'neutral')
                confidence = float(pred[0][emotion_index])
                self.facial_emotion_current = emotion

                color = (0, 255, 0)
                text = f"{emotion.upper()} ({confidence*100:.0f}%)"
                cv2.putText(frame, text, (p_orig-10, q_orig-30),
                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.2, color, 2)
            except Exception:
                pass

        self.frame_count += 1
        return frame
    
    def _draw_info(self, frame):
        """Draw emotion information on frame"""
        y_offset = 20
        
        # Facial emotion
        cv2.putText(frame, f"Face: {self.facial_emotion_current.upper()}", 
                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        y_offset += 35
        
        # Voice emotion
        if self.voice_emotion_current:
            cv2.putText(
                frame, f"Voice: {self.voice_emotion_current.upper()} ({self.voice_confidence:.0%})",
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2
            )
        else:
            cv2.putText(frame, "Voice: [waiting]", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        y_offset += 35
        
        # Text sentiment
        if self.text_sentiment_current:
            cv2.putText(
                frame, f"Text: {self.text_sentiment_current.upper()}",
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2
            )
        else:
            cv2.putText(frame, "Text: [waiting]", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        y_offset += 35
        
        # Fused emotion
        if self.fused_emotion:
            cv2.rectangle(frame, (15, y_offset-35), (400, y_offset+10), (0, 255, 255), -1)
            cv2.putText(
                frame, f"FUSED: {self.fused_emotion.upper()}",
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2
            )
        else:
            cv2.putText(frame, "FUSED: [press 'f' after all inputs]", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        
        # Commands bar
        cv2.rectangle(frame, (0, frame.shape[0]-30), (frame.shape[1], frame.shape[0]),
                     (50, 50, 50), -1)
        cv2.putText(
            frame, "v=Voice | t=Text | f=Fuse | a=AI | r=Reset | q=Quit",
            (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
        )
        
        return frame
    
    def run(self):
        """Main loop"""
        try:
            while self.running:
                ret, frame = self.webcam.read()
                
                if not ret or frame is None:
                    break
                
                self.frame_count += 1
                
                # Detect facial emotion
                frame = self._detect_facial_emotion(frame)
                
                # Draw all info
                frame = self._draw_info(frame)
                
                cv2.imshow("Triple Emotion Detection (Face + Voice + Text)", frame)
                
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC
                    self.running = False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup"""
        self.running = False
        self.webcam.release()
        cv2.destroyAllWindows()
        print("\n✓ System stopped")


if __name__ == "__main__":
    try:
        detector = TripleEmotionDetector()
        detector.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
