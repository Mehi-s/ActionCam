import cv2
import mediapipe as mp
import time
import concurrent.futures

# Initialize MediaPipe Pose
pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define the number of threads to use
NUM_THREADS = 2

# Function to process a frame and draw landmarks
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

# Open webcam
cap = cv2.VideoCapture(0)

# Initialize FPS calculation variables
prev_time = 0

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Break the loop if no frame is captured
    if not ret:
        break

    # Divide the frame into equal parts for parallel processing
    frame_height, frame_width = frame.shape[:2]
    part_height = frame_height // NUM_THREADS
    parts = [(frame[y:y+part_height, :], y) for y in range(0, frame_height, part_height)]

    # Process frames in parallel using multi-threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        processed_frames = executor.map(process_frame, [part[0] for part in parts])

    # Merge processed frames
    processed_frame = cv2.vconcat(list(processed_frames))

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
