import cv2
import time
from pose_detector import PoseDetector
from audio_analyzer import AudioAnalyzer
from alert_system import AlertSystem

def main():
    print("Initializing AI Surveillance System...")
    
    # Initialize our modules
    detector = PoseDetector()
    audio_analyzer = AudioAnalyzer()
    alert_system = AlertSystem()
    
    # Start capturing default camera and mic
    cap = cv2.VideoCapture(0)
    audio_analyzer.start_listening()
    
    print("System Running... Press 'q' to quit.")
    
    cv2.namedWindow("Behavioral Surveillance Feed", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Behavioral Surveillance Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to access webcam.")
                break
                
            # 1. Pose Detection
            img = detector.find_pose(img)
            lmList = detector.get_position(img, draw=False)
            
            pose_aggressive, p_score = detector.detect_aggression(lmList)
            
            # 2. Audio Analysis
            audio_aggressive, a_score = audio_analyzer.detect_yelling()
            
            # 3. Decision Logic (Combine Video + Audio)
            # For the final project, this part could be replaced by a TensorFlow model inference.
            is_aggressive = pose_aggressive or audio_aggressive
            
            # 4. Handle Alerts & Visualization
            status_text = "NORMAL"
            color = (0, 255, 0)
            
            if is_aggressive:
                status_text = "AGGRESSIVE DETECTED!"
                color = (0, 0, 255)
                # Trigger Twilio SMS
                alert_system.send_alert("Aggressive action (fighting or yelling) detected in camera feed!")
                
            # Draw real-time metrics on UI
            cv2.putText(img, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
            cv2.putText(img, f"Pose Score: {p_score:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Audio Vol: {a_score:.2f}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Behavioral Surveillance Feed", img)
            
            # Press 'q' to break the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nManually interrupted.")
    finally:
        # Cleanup properly
        audio_analyzer.stop_listening()
        cap.release()
        cv2.destroyAllWindows()
        print("System safely shut down.")

if __name__ == "__main__":
    main()
