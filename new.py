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
cap=cv2.VideoCapture('base.jpg')
success, img = cap.read()
img = cv2.flip(img, 1)
img = cv2.blur(img, (5,5))
body_pos_detector = pm.poseDetector()
body_pos_detector.findPose(img)
base_landmarks = body_pos_detector.findPosition(img, draw=False)
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
        self.l_knee=MyUi.dis(self,base_landmarks,24,28)
        self.r_knee=MyUi.dis(self,base_landmarks,27,23)
        self.l_elbow=MyUi.dis(self,base_landmarks,12,16)
        self.r_elbow=MyUi.dis(self,base_landmarks,11,15)
        self.l_shoulder=MyUi.dis(self,base_landmarks,24,14)
        self.r_shoulder=MyUi.dis(self,base_landmarks,23,13)
        self.results={}
    def dis(self,plmList,p1,p2):
            x1, y1 = plmList[p1][1:]
            x2, y2 = plmList[p2][1:]
            return (abs(x1-x2)**2+abs(y1-y2))**0.5
    def crouch(self,plmList):
            out=False
            l_knee_a = MyUi.dis(self,plmList,24,28)
            r_knee_a = MyUi.dis(self,plmList,27,23)
            if self.l_knee**0.7>l_knee_a and self.r_knee**0.7>r_knee_a :
                out=True
            return out

    def l_one_leg(self,plmList):
            l_knee_a = MyUi.dis(self,plmList,24,28)
            r_knee_a = MyUi.dis(self,plmList,27,23)

            out=False
            if self.l_knee**0.7>l_knee_a  and -self.r_knee/7<self.r_knee**0.7-r_knee_a<self.r_knee/7 :
                out=True
            self.results['l_one']=out
            return out
    def r_one_leg(self,plmList):
            l_knee_a = MyUi.dis(self,plmList,24,28)
            r_knee_a = MyUi.dis(self,plmList,27,23)

            out=False
            if self.r_knee**0.7>r_knee_a  and -self.r_knee/7<self.l_knee**0.7-l_knee_a<self.l_knee/7 :
                out=True
            return out


    def hotbar_move(self,frame):
            out=0
            if  135 < body_pos_detector.findAngle(frame, 24, 10, 8) < 145:
                out=1
            if 235 < body_pos_detector.findAngle(frame, 23, 9, 7) < 245:
                out=-1
            self.results['hb']=out
            return out
    def l_click(self, body_landmarks):
            out=None
            elbow_angle = MyUi.dis(self,body_landmarks,12,16)
            shoulder_angle =MyUi.dis(self,body_landmarks,24,14)
            if self.l_elbow**0.3>elbow_angle:
                out='click'
            if self.r_shoulder**0.6>shoulder_angle>self.r_shoulder**0.4 and self.r_elbow**1.1>elbow_angle>self.r_elbow**0.9:
                out='mouse'
            return out

    def r_click(self,body_landmarks):
            out = None
            elbow_angle =MyUi.dis(self,body_landmarks,11,15)
            if self.r_elbow**0.3>elbow_angle:
                out = 'click'
            return out
    def click(self,body_landmarks):
            l=MyUi.l_click(self,body_landmarks)
            r=MyUi.r_click(self,body_landmarks)
            self.results['lc']=l
            self.results['rc']=r
            return[l,r]
    def cr_rone(self,body_landmarks):
            cr=MyUi.crouch(self,body_landmarks)
            rone=MyUi.r_one_leg(self,body_landmarks)
            self.results['cr']=cr
            self.results['r_one']=rone
            return [cr,rone]
    
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

       
        img=None
        step = 0
        wScr, hScr = root.winfo_screenwidth(),root.winfo_screenheight()
        last_pos = 0
        p.FAILSAFE=False
        while self.state:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            img = cv2.blur(img, (5,5))

            self.results={}
            
            body_pos_detector.findPose(img)
            body_landmarks = body_pos_detector.findPosition(img, draw=False)

            
            #l_one,hb,[lc,rc],[cr,r_one]

            if len (body_landmarks)!=0:
                lo=threading.Thread(target=MyUi.l_one_leg,args=(self,body_landmarks))
                hb=threading.Thread(target=MyUi.hotbar_move,args=(self,img))
                c=threading.Thread(target=MyUi.click,args=(self,body_landmarks,))
                cr=threading.Thread(target=MyUi.cr_rone,args=(self,body_landmarks,))
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