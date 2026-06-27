import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from flask import Flask, render_template, Response, jsonify
import cv2
import threading
from pose_detector import PoseDetector
from audio_analyzer import AudioAnalyzer
from alert_system import AlertSystem

app = Flask(__name__)

# Global state to share between video loop and web requests
system_status = {
    "status": "NORMAL",
    "pose_score": 0.0,
    "audio_vol": 0.0,
    "is_aggressive": False
}

# Initialize our modules
detector = PoseDetector()
audio_analyzer = AudioAnalyzer()
alert_system = AlertSystem()

# Start audio listener globally
audio_analyzer.start_listening()

# Camera
camera = cv2.VideoCapture(0)

def generate_frames():
    global system_status
    
    while True:
        success, img = camera.read()
        if not success:
            break
            
        # 1. Pose Detection
        img = detector.find_pose(img)
        lmList = detector.get_position(img, draw=False)
        
        pose_aggressive, p_score = detector.detect_aggression(lmList)
        
        # 2. Audio Analysis
        audio_aggressive, a_score = audio_analyzer.detect_yelling()
        
        # 3. Decision Logic
        is_aggressive = pose_aggressive or audio_aggressive
        
        # Update global state for web UI polling
        system_status['pose_score'] = float(p_score)
        system_status['audio_vol'] = float(a_score)
        system_status['is_aggressive'] = bool(is_aggressive)
        
        if is_aggressive:
            system_status['status'] = "AGGRESSIVE DETECTED!"
            # We must run the alert in a background thread so we don't stall the video feed
            threading.Thread(target=alert_system.send_alert, args=("Aggressive action (fighting or yelling) detected in camera feed!",)).start()
        else:
            system_status['status'] = "NORMAL"
            
        # We don't draw text on the img itself anymore! The web UI will handle the sleek text display!
        # Encode the frame in JPEG
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        
        # Yield the output in multipart MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify(system_status)

if __name__ == "__main__":
    # Run the web server
    app.run(host='0.0.0.0', port=5000, threaded=True)
