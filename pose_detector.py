import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_landmarks = None

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
        return img

    def get_position(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList

    def detect_aggression(self, lmList):
        """
        A basic heuristic for aggression using Pose Landmarks.
        We can track sudden rapid movements or hands raised above the nose.
        A real TensorFlow model can also use these coordinates. 
        """
        aggression_score = 0.0
        is_aggressive = False

        if len(lmList) > 0:
            # Simple heuristic 1: Hands raised aggressively (wrists above nose)
            nose_y = lmList[0][2]
            left_wrist_y = lmList[15][2]
            right_wrist_y = lmList[16][2]
            
            if left_wrist_y < nose_y or right_wrist_y < nose_y:
                aggression_score += 0.5
            
            # Simple heuristic 2: Rapid movement detection (comparing to previous frames)
            # For a more advanced architecture, this list of landmarks is sent to TensorFlow.
            
            if aggression_score >= 0.5:
                is_aggressive = True
                
        return is_aggressive, aggression_score
