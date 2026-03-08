"""
Test Script - Verify Keyboard Input Methods
Helps diagnose which input method works best on your system
"""

import cv2
import numpy as np
import threading
import time


def test_window_keyboard():
    """Test keyboard input from OpenCV window"""
    print("\n" + "="*60)
    print("TEST 1: OpenCV Window Keyboard Input")
    print("="*60)
    print("Instructions:")
    print("  1. A window will appear")
    print("  2. CLICK on the window to focus it")
    print("  3. Try pressing: v, V, ESC")
    print("  4. Check if input is detected below")
    print("\nStarting...\n")
    
    time.sleep(2)
    
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    keys_pressed = []
    
    cv2.imshow("Keyboard Test - Click window, then press 'v', 'V', or 'ESC'", img)
    
    for i in range(100):  # Try for ~3 seconds
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Draw instructions
        cv2.putText(img, "Keyboard Test - Press 'v', 'V', or 'ESC'", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Attempts remaining: {100-i}", (50, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if keys_pressed:
            cv2.putText(img, f"Keys detected: {keys_pressed}", (50, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(img, "Waiting for key press...", (50, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
        
        cv2.imshow("Keyboard Test - Click window, then press 'v', 'V', or 'ESC'", img)
        
        key = cv2.waitKey(30) & 0xFF
        
        if key != 255:  # 255 means no key was pressed
            key_char = chr(key) if 32 <= key < 127 else f"code_{key}"
            keys_pressed.append(key_char)
            print(f"✓ Key detected: {key_char} (code: {key})")
            
            if key == 27:  # ESC
                print("✓ ESC key works!")
                break
    
    cv2.destroyAllWindows()
    
    print("\nResult:")
    if 'v' in keys_pressed or 'V' in keys_pressed:
        print("✅ Window keyboard input WORKS - You can use Option 2 or 3")
    else:
        print("❌ Window keyboard input had issues - Use Option 3 (SIMPLE MODE) instead")
    
    return len(keys_pressed) > 0


def test_terminal_input():
    """Test terminal input"""
    print("\n" + "="*60)
    print("TEST 2: Terminal Keyboard Input")
    print("="*60)
    print("Instructions:")
    print("  1. Type 'v' or 'V' in the TERMINAL below")
    print("  2. Press Enter")
    print("\nTesting terminal input...\n")
    
    try:
        response = input("Type 'v' and press Enter: ").strip().lower()
        
        if response == 'v':
            print("✅ Terminal input WORKS - You can definitely use Option 3")
            return True
        else:
            print(f"Got: {response}")
            return False
    except:
        print("❌ Terminal input could not be tested")
        return False


def test_voice_recording():
    """Test if voice recording works"""
    print("\n" + "="*60)
    print("TEST 3: Voice Recording Test")
    print("="*60)
    print("Testing if voice recording module works...\n")
    
    try:
        from voice_emotion_detector import voice_emotion
        
        print("Press Enter when ready to test recording (will record 1.5 seconds)")
        input()
        
        emotion = voice_emotion()
        print(f"✅ Voice recording WORKS - Detected: {emotion}")
        return True
        
    except Exception as e:
        print(f"❌ Voice recording error: {e}")
        return False


def run_all_tests():
    """Run all diagnostic tests"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " EMOTION DETECTION - KEYBOARD INPUT DIAGNOSTICS ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Test 1: Window keyboard
    try:
        results['window_keyboard'] = test_window_keyboard()
    except Exception as e:
        print(f"Error in window test: {e}")
        results['window_keyboard'] = False
    
    # Test 2: Terminal input
    try:
        results['terminal_input'] = test_terminal_input()
    except Exception as e:
        print(f"Error in terminal test: {e}")
        results['terminal_input'] = False
    
    # Test 3: Voice recording
    try:
        results['voice_recording'] = test_voice_recording()
    except Exception as e:
        print(f"Error in voice test: {e}")
        results['voice_recording'] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Window Keyboard Input: {'✅ WORKS' if results['window_keyboard'] else '❌ FAILED'}")
    print(f"Terminal Input:        {'✅ WORKS' if results['terminal_input'] else '❌ FAILED'}")
    print(f"Voice Recording:       {'✅ WORKS' if results['voice_recording'] else '❌ FAILED'}")
    print("="*60)
    
    # Recommendation
    print("\n📋 RECOMMENDATIONS:\n")
    
    if results['terminal_input'] and results['voice_recording']:
        print("✨ Use OPTION 3: SIMPLE COMBINED MODE (Terminal Input)")
        print("   Command: python emotion_detection_integrated.py → Select 3")
        print("   Why: Most reliable, no window focus issues")
    
    if results['window_keyboard'] and results['voice_recording']:
        print("\n✨ Alternative: Use OPTION 2: Combined Mode (Window Keyboard)")
        print("   Command: python emotion_detection_integrated.py → Select 2")
        print("   Remember: Click on window first!")
    
    if results['voice_recording']:
        print("\n✨ Voice Only: Test voice detection separately")
        print("   Command: python emotion_detection_integrated.py → Select 4")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    run_all_tests()
    
    print("\n👋 Diagnostic complete!")
    print("\nNext step: Run the appropriate emotion detection mode")
