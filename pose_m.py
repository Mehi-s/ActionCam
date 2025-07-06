import cv2
import mediapipe as mp
import math
import time # Not strictly used in this class, but often kept for related timing tasks
from typing import List, Tuple, Optional # For type hinting
import numpy as np # For type hinting image arrays

class PoseDetector:
    """
    A class to detect human poses and landmarks from an image using Mediapipe.
    """
    def __init__(self,
                 static_image_mode: bool = False,
                 model_complexity: int = 1,
                 smooth_landmarks: bool = True,
                 enable_segmentation: bool = False,
                 smooth_segmentation: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initializes the PoseDetector.

        Args:
            static_image_mode: Whether to treat the input images as a batch of static
                               and possibly unrelated images, or a video stream.
            model_complexity: Complexity of the pose landmark model: 0, 1 or 2.
                              Landmark accuracy as well as inference latency generally go up with model complexity.
            smooth_landmarks: If True, filter landmarks across different input images to reduce jitter.
            enable_segmentation: If True, in addition to the pose landmarks, also predict segmentation mask.
            smooth_segmentation: If True, filter segmentation masks across different input images to reduce jitter.
            min_detection_confidence: Minimum confidence value ([0.0, 1.0]) for the person detection to be considered successful.
            min_tracking_confidence: Minimum confidence value ([0.0, 1.0]) for the landmark tracking to be considered successful.
        """
        self.static_image_mode = static_image_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mp_pose = mp.solutions.pose
        # Renamed self.pose to self.pose_processor for clarity
        self.pose_processor = self.mp_pose.Pose(static_image_mode=self.static_image_mode,
                                                model_complexity=self.model_complexity,
                                                smooth_landmarks=self.smooth_landmarks,
                                                enable_segmentation=self.enable_segmentation,
                                                smooth_segmentation=self.smooth_segmentation,
                                                min_detection_confidence=self.min_detection_confidence,
                                                min_tracking_confidence=self.min_tracking_confidence)
        # Renamed self.mpDraw to self.mp_drawing
        self.mp_drawing = mp.solutions.drawing_utils
        self.landmark_list: List[List[int]] = [] # Stores [id, x, y] for each landmark
        self.pose_results = None # Stores the latest results from pose processing

    def findPose(self, image: np.ndarray, draw_skeleton: bool = True) -> np.ndarray:
        """
        Detects pose landmarks in an image and stores the results in self.pose_results.

        Args:
            image: The input image (OpenCV BGR format).
            draw_skeleton: If True, draws the pose skeleton on the image.

        Returns:
            The image, potentially with the pose skeleton drawn.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.pose_results = self.pose_processor.process(image_rgb)

        if self.pose_results and self.pose_results.pose_landmarks:
            if draw_skeleton:
                self.mp_drawing.draw_landmarks(image, self.pose_results.pose_landmarks,
                                               self.mp_pose.POSE_CONNECTIONS)
        return image

    def findPosition(self, image: np.ndarray, draw_landmark_circles: bool = True) -> List[List[int]]:
        """
        Extracts the screen coordinates of each detected pose landmark from self.pose_results.
        Populates self.landmark_list. Call findPose() first.

        Args:
            image: The input image (OpenCV BGR format, used for dimensions and optionally drawing).
            draw_landmark_circles: If True, draws circles on detected landmark positions on the image.

        Returns:
            A list of landmarks, where each landmark is [id, x, y].
            Returns an empty list if no landmarks are detected or findPose() wasn't successful.
        """
        self.landmark_list = [] # Reset landmark list for current frame
        if self.pose_results and self.pose_results.pose_landmarks:
            img_h, img_w, _ = image.shape # Get image dimensions for coordinate conversion
            for landmark_id, landmark in enumerate(self.pose_results.pose_landmarks.landmark):
                # Convert normalized (0.0-1.0) coordinates to pixel coordinates
                cx, cy = int(landmark.x * img_w), int(landmark.y * img_h)
                self.landmark_list.append([landmark_id, cx, cy])
                if draw_landmark_circles:
                    cv2.circle(image, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.landmark_list

    def findAngle(self, image: np.ndarray,
                  point1_idx: int, point2_idx: int, point3_idx: int,
                  draw_angle_visualization: bool = True) -> Optional[float]:
        """
        Calculates the angle formed by three landmarks (point2_idx is the vertex).
        Uses self.landmark_list, so call findPosition() first.

        Args:
            image: The input image (OpenCV BGR format, used for drawing).
            point1_idx: Index of the first landmark in self.landmark_list.
            point2_idx: Index of the second landmark (the vertex) in self.landmark_list.
            point3_idx: Index of the third landmark in self.landmark_list.
            draw_angle_visualization: If True, draws the angle lines and text on the image.

        Returns:
            The calculated angle in degrees (0-360). Returns None if landmarks are not found or indices are invalid.
        """
        if not self.landmark_list:
            # print("Warning: Landmark list is empty. Call findPosition() before findAngle().")
            return None

        # Check if all points are within the bounds of the landmark list
        required_indices = [point1_idx, point2_idx, point3_idx]
        if not all(0 <= idx < len(self.landmark_list) for idx in required_indices):
            # print(f"Warning: One or more landmark indices are out of bounds. List size: {len(self.landmark_list)}, Indices: {required_indices}")
            return None

        try:
            # Coordinates are stored as [id, x, y]
            _, x1, y1 = self.landmark_list[point1_idx]
            _, x2, y2 = self.landmark_list[point2_idx] # Vertex
            _, x3, y3 = self.landmark_list[point3_idx]
        except IndexError:
            # This should be caught by the check above, but as a final safeguard.
            # print("Error: Unexpected IndexError while accessing landmark coordinates.")
            return None

        # Calculate angle using atan2
        angle_rad = math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
        angle_deg = math.degrees(angle_rad)

        # Normalize angle to be positive (0-360 degrees)
        if angle_deg < 0:
            angle_deg += 360

        if draw_angle_visualization:
            # Draw lines connecting the points
            cv2.line(image, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(image, (x3, y3), (x2, y2), (255, 255, 255), 3)
            # Draw circles at the landmark points
            for px, py in [(x1,y1), (x2,y2), (x3,y3)]:
                cv2.circle(image, (px, py), 10, (0, 0, 255), cv2.FILLED)
                cv2.circle(image, (px, py), 15, (0, 0, 255), 2) # Outer circle
            # Display the angle value on the image near the vertex
            cv2.putText(image, f"{int(angle_deg)}", (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return angle_deg

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    # Initialize video capture
    cap = cv2.VideoCapture(0) # Use 0 for default webcam
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        exit()

    # Create a PoseDetector instance
    detector = PoseDetector(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    p_time = 0 # Previous time, for FPS calculation

    while True:
        # Read a frame from the camera
        success, img = cap.read()
        if not success:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        # Process the frame to find pose
        img_with_pose = detector.findPose(img, draw_skeleton=True)

        # Get landmark positions
        landmark_positions = detector.findPosition(img_with_pose, draw_landmark_circles=False) # Circles can be drawn by findAngle

        if landmark_positions:
            # Example: Calculate and draw the angle of the right elbow
            # Right shoulder (11), Right elbow (13), Right wrist (15)
            # Check if enough landmarks are detected (e.g., max index needed is 15)
            if len(landmark_positions) > 15:
                 right_elbow_angle = detector.findAngle(img_with_pose, 11, 13, 15, draw_angle_visualization=True)
                 if right_elbow_angle is not None:
                     # print(f"Right Elbow Angle: {right_elbow_angle:.2f} degrees")
                     pass # Angle is drawn on img_with_pose

            # Example: Calculate and draw the angle of the left knee
            # Left hip (23), Left knee (25), Left ankle (27)
            if len(landmark_positions) > 27:
                left_knee_angle = detector.findAngle(img_with_pose, 23, 25, 27, draw_angle_visualization=True)
                if left_knee_angle is not None:
                    # print(f"Left Knee Angle: {left_knee_angle:.2f} degrees")
                    pass


        # Calculate and display FPS
        c_time = time.time()
        fps = 0
        if (c_time - p_time) > 0: # Avoid division by zero if c_time == p_time
            fps = 1 / (c_time - p_time)
        p_time = c_time
        cv2.putText(img_with_pose, f'FPS: {int(fps)}', (20, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 100), 3)

        # Display the resulting frame
        cv2.imshow('Action Cam - Pose Detection Test', img_with_pose)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
