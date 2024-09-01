import cv2
import mediapipe as mp
import time
import concurrent.futures

# Initialize MediaPipe Pose
pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open webcam
cap = cv2.VideoCapture(0)

# Initialize FPS calculation variables
prev_time = 0

def process_frame(frame):
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = pose.process(frame_rgb)

    # Draw landmarks on the frame
    if results.pose_landmarks:
        for landmark in results.pose_landmarks.landmark:
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    return frame

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Use concurrent.futures for multi-threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the frame processing task
        future = executor.submit(process_frame, frame)

        # Retrieve the processed frame
        processed_frame = future.result()

    # Calculate and display FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(processed_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the output frame
    cv2.imshow('Webcam', processed_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
