import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
import pose_m as pm
import time
import cv2
import mediapipe as mp
import pyautogui as p
import tkinter as tk
import mouse
import threading
class MyUi(QMainWindow):  
    def __init__(self):
        super(MyUi, self).__init__()
        loadUi('Action Cam.ui', self)
        self.show()
        
        self.pushButton_3.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.tutorial)
        self.pushButton.clicked.connect(self.customize)
        self.actionClose_app.triggered.connect(self.end)
        self.state=True
    
    def tutorial(self):
        super(MyUi, self).__init__()
        loadUi('Tutorial.ui', self)
        self.show()
    def customize(self):
        super(MyUi, self).__init__()
        loadUi('Costumize.ui', self)
        self.show()
        self.keys={}


        self.comboBox_14.currentIndexChanged.connect(self.right_hand)
        self.comboBox_13.currentIndexChanged.connect(self.double_hands)
        self.comboBox_12.currentIndexChanged.connect(self.running)
        self.comboBox_11.currentIndexChanged.connect(self.left_hand_foot) 
        self.comboBox_9.currentIndexChanged.connect(self.left_hand)
        self.comboBox_8.currentIndexChanged.connect(self.sitting)
        self.comboBox_10.currentIndexChanged.connect(self.jumping)
        #'Mouse Left Click','Mouse Right Click'
        self.combo_in=['tab','escape','Space','Left Shift','Right Shift','1','2','3','4','5','6','7','8','9','0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        self.keysdown=['w','space','Left Shift']
        self.combo_out=['tab','escape','space','lshift','rshift','1','2','3','4','5','6','7','8','9','0','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    def right_hand(self, index):
        rigth_hand_move = self.comboBox_14.currentText()
        self.keys['rigth_hand_move']=rigth_hand_move
        
    def double_hands(self, index):
        double_hands_move = self.comboBox_13.currentText()
        self.keys['double_hands_move']=double_hands_move
    def running(self, index):
        running_move = self.comboBox_12.currentText()
        self.keys['running_move']=running_move
        
    def left_hand_foot(self, index):
        left_hand_foot_move = self.comboBox_11.currentText()
        self.keys['left_hand_foot_move']=left_hand_foot_move
        
    def left_hand(self, index):
        left_hand_move = self.comboBox_9.currentText()
        self.keys['left_hand_move']=left_hand_move
        
    def sitting(self, index):
        sitting_move = self.comboBox_8.currentText()
        self.keys['sitting_move']=sitting_move
        
    def jumping(self, index):
        jumping_move = self.comboBox_10.currentText()
        self.keys['jumping_move']=jumping_move
    
    
    def end(self):
        self.close()
    
    def start(self):
        root=tk.Tk()

        cap = cv2.VideoCapture(0)
        pTime = 0

        body_pos_detector = pm.poseDetector()

        def crouch(plmList,frame):
            out=False
            l_knee_a = body_pos_detector.findAngle(frame,24,26,28)
            l_hip_a = body_pos_detector.findAngle(frame,26,24,12)

            r_knee_a = body_pos_detector.findAngle(frame,27,25,23)
            r_hip_a = body_pos_detector.findAngle(frame,11,23,25)
            if 90 < l_knee_a < 150 and 90 < r_knee_a < 150:
                out=True
            return out

        def l_one_leg(frame):
            l_knee_a=body_pos_detector.findAngle(frame,24,26,28)
            l_hip_a=body_pos_detector.findAngle(frame,26,24,12)

            r_knee_a=body_pos_detector.findAngle(frame,27,25,23)
            r_hip_a=body_pos_detector.findAngle(frame,11,23,25)

            out=False
            if 170 > l_knee_a and l_hip_a < 170 and 195 > r_knee_a > 165 and 195 > r_hip_a > 165:
                out=True
            results['l_one']=out
            return out
        def r_one_leg(frame):
            r_knee_a=body_pos_detector.findAngle(frame,27,25,23)
            r_hip_a=body_pos_detector.findAngle(frame,11,23,25)

            l_knee_a=body_pos_detector.findAngle(frame,24,26,28)
            l_hip_a=body_pos_detector.findAngle(frame,26,24,12)

            out=False
            if 170 > r_knee_a and r_hip_a < 170 and 195 > l_knee_a > 165 and 195 > l_hip_a > 165:
                out=True
            return out


        def hotbar_move(frame, body_landmarks):
            out=0
            if  135 < body_pos_detector.findAngle(frame, 24, 10, 8) < 145:
                out=1
            if 235 < body_pos_detector.findAngle(frame, 23, 9, 7) < 245:
                out=-1
            results['hb']=out
            return out
        def l_click(frame, body_landmarks):
            out=None
            elbow_angle = body_pos_detector.findAngle(frame, 12, 14, 16)
            shoulder_angle = body_pos_detector.findAngle(frame, 24, 12, 14)
            if 320 < elbow_angle < 360:
                out='click'
            if 70 < shoulder_angle < 110 and 175 < elbow_angle < 195:
                out='mouse'
            return out

        def r_click(frame ,body_landmarks):
            out = None
            elbow_angle = body_pos_detector.findAngle(frame, 11, 13, 15)
            shoulder_angle = body_pos_detector.findAngle(frame, 23, 11, 13)     
            if 0 < elbow_angle < 40:
                out = 'click'
            return out
        img=None
        step = 0
        wScr, hScr = root.winfo_screenwidth(),root.winfo_screenheight()
        last_pos = 0
        p.FAILSAFE=False

        def click(frame,body_landmarks):
            l=l_click(frame,body_landmarks)
            r=r_click(frame,body_landmarks)
            results['lc']=l
            results['rc']=r
            return[l,r]
        def cr_rone(frame,body_landmarks):
            cr=crouch(body_landmarks,img)
            rone=r_one_leg(frame)
            results['cr']=cr
            results['r_one']=rone
            return [cr,rone]

        while self.state:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            img = cv2.blur(img, (5,5))

            results={}
            
            body_pos_detector.findPose(img)
            body_landmarks = body_pos_detector.findPosition(img, draw=False)

            
            #l_one,hb,[lc,rc],[cr,r_one]

            if len (body_landmarks)!=0:
                lo=threading.Thread(target=l_one_leg,args=(img,))
                hb=threading.Thread(target=hotbar_move,args=(img,body_landmarks,))
                c=threading.Thread(target=click,args=(img,body_landmarks,))
                cr=threading.Thread(target=cr_rone,args=(img,body_landmarks,))
                threads=[lo,hb,c,cr]  

                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                try:
                    mouse.wheel(results['hb'])
                except:
                    pass
                try:
                    if results['lc']== 'click' and results['rc']== 'click':

                        if self.keys['double_hands_move']=='Mouse Left Click':
                            p.leftClick()
                        elif self.keys['double_hands_move']=='Mouse Right Click':
                            p.rightClick()
                        else:
                            ind=self.combo_in.index(self.keys['double_hands_move'])
                            p.press(self.combo_out[ind])

                    elif results['lc']=='click':
                        if self.keys['left_hand_move']=='Mouse Left Click':
                            p.leftClick()
                        elif self.keys['left_hand_move']=='Mouse Right Click':
                            p.rightClick()
                        else:
                            ind=self.combo_in.index(self.keys['left_hand_move'])
                            p.press(self.combo_out[ind])

                    elif results['lc']== 'mouse':
                        right_hand_x = body_landmarks[15][1]
                        right_hand_y =body_landmarks[15][2]
                        p.moveTo(wScr-(wScr - (right_hand_x * wScr) // 640), right_hand_y * hScr  // 480)
                    elif results['rc']=='click':
                        if self.keys['rigth_hand_move']=='Mouse Left Click':
                            p.leftClick()
                        elif self.keys['rigth_hand_move']=='Mouse Right Click':
                            p.rightClick()
                        else:
                            ind=self.combo_in.index(self.keys['rigth_hand_move'])
                            p.press(self.combo_out[ind])       
                except:
                    pass  
                try:
                    if results['cr']  :    
                        if self.keys['sitting_move']=='Mouse Left Click':
                            p.leftClick()
                        elif self.keys['sitting_move']=='Mouse Right Click':
                            p.rightClick()
                        else:
                            ind=self.combo_in.index(self.keys['sitting_move'])
                            p.press(self.combo_out[ind])
                except:
                    pass
                try:
                    if step==0:
                        if results['l_one']:
                            step=1
                    elif step==1:
                        if results['r_one']:
                            step=0
                            if self.keys['running_move']=='Mouse Left Click':
                                p.leftClick()
                            elif self.keys['running_move']=='Mouse Right Click':
                                p.rightClick()
                            else:
                                ind=self.combo_in.index(self.keys['running_move'])
                                p.keyDown(self.combo_out[ind])
                        else:
                            if last_pos - body_landmarks[0][2] > 20:
                                if self.keys['jumping_move']=='Mouse Left Click':
                                    p.leftClick()
                                elif self.keys['jumping_move']=='Mouse Right Click':
                                    p.rightClick()
                                else:
                                    ind=self.combo_in.index(self.keys['jumping_move'])
                                    p.press(self.combo_out[ind])
                except:
                    pass
                last_pos = body_landmarks[0][2]
            cTime = time.time()
            fps = int(1 / (cTime - pTime))
            pTime = cTime
            p.keyUp('w')
            cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 0), 3)
            cv2.imshow("img", img)
            cv2.waitKey(1)
            if  0xFF == ord('z'):
                self.state=False
                break
        self.close()
def main():
    app = QApplication(sys.argv)
    window = MyUi()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()