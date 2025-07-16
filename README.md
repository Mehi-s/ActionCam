# Action Cam - Control Your Games with Gestures!

Action Cam is a Python application that uses your webcam to detect your body poses and translate them into keyboard or mouse inputs. This allows you to control games or other applications using gestures, providing a unique and immersive interactive experience.

## Features

- **Gesture-based control:** Control your computer using body movements.
- **Customizable controls:** Map different poses to specific keyboard keys or mouse actions.
- **Real-time pose detection:** Uses Mediapipe for accurate and responsive pose tracking.
- **User-friendly interface:** Easy-to-use UI for starting, customizing, and learning the controls.

## How it Works

Action Cam captures video from your webcam and uses the Mediapipe library to detect your body landmarks in real-time. Based on the detected pose, it simulates keyboard presses or mouse movements, allowing you to interact with your computer hands-free.

## Getting Started

### Prerequisites

- Python 3.x
- OpenCV (`cv2`)
- Mediapipe (`mediapipe`)
- PyAutoGUI (`pyautogui`)
- PyQt5 (`PyQt5`)
- Tkinter (`tk`)
- Mouse (`mouse`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/action-cam.git
   cd action-cam
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You may need to create a `requirements.txt` file if one doesn't exist. See below.)*

### Running the Application

1. Execute the `main.py` script:
   ```bash
   python main.py
   ```
2. The application window will open. You can then:
    - Click **Start** to begin gesture control.
    - Click **Customize** to map poses to different actions.
    - Click **Tutorial** for a guide on available gestures.

## Customizing Controls

The **Customize** menu allows you to define which gestures trigger specific actions:

You can map various poses, such as raising your right hand, jumping, or sitting, to different keyboard keys or mouse clicks.

## Home Menu and Webcam View

- **Home Menu:**
  ![Home Menu](https://github.com/user-attachments/assets/137a39a4-5b1e-445e-b33a-bd9327837396)

- **Webcam View (during operation):**
  ![Webcam View](https://github.com/user-attachments/assets/d7bd168d-fc6d-4f0c-8fad-7854fb9b6f75)

## Creating a `requirements.txt` File

If a `requirements.txt` file is not included in the repository, you can create one by listing the dependencies mentioned above:

```
opencv-python
mediapipe
pyautogui
PyQt5
tk
mouse
```

Save this as `requirements.txt` in the root directory of the project.

## Contributing

Contributions are welcome! If you have ideas for improvements or new features, feel free to fork the repository and submit a pull request.

---

*This README was generated with the assistance of an AI coding assistant.*
