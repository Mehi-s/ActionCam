import sys
from cx_Freeze import setup, Executable

setup(
    name = "Action Cam",
    version = "1.0",
    description = "hi lets start!",
    executables = [Executable("main.py", base = "Win32GUI")],
    options = {
        "build_exe": {
            "packages": ["os",'sys','PyQt5','time','cv2','mediapipe','pyautogui','tkinter','mouse','threading'],
            "include_files": ["pose_m.py",'Action Cam.ui','Tutorial.ui','Costumize.ui','Action Cam_ui.py','Costumize_ui.py']
        }
    }
)