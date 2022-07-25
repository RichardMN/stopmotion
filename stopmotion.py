########################################################
#-------------STOPMOTION WITH RASPBERRY PI-------------#
#------------------------------------------------------#
#----------------AUTHOR: DANIEL LAVINO-----------------#
########################################################

#loading opensource libraries - some may not be native
import cv2
import numpy as np
from time import sleep
from tkinter import *
from imutils.video import WebcamVideoStream # https://github.com/jrosebr1/imutils
from datetime import datetime
import imutils
import sys
#from threading import Thread
# import RPi.GPIO as GPIO

#initializing GPIO pins
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(26,GPIO.OUT)
# GPIO.setup(6,GPIO.IN,GPIO.PUD_DOWN) #capture
# GPIO.setup(5,GPIO.IN,GPIO.PUD_DOWN) #play
# GPIO.setup(4,GPIO.IN,GPIO.PUD_DOWN) #reset
# GPIO.setup(17,GPIO.IN,GPIO.PUD_DOWN) #undo
# GPIO.output(26,GPIO.HIGH)

#initializing some variables
AnimFrameRate = 10
opacity = 0.0
key = 0
seq = []
seqIcon = []
actIcon = 0
actSeqFrame = 0
actSeqIcon = 0
font = cv2.FONT_HERSHEY_SIMPLEX

#here we use a Tkinter root just to get screen resolutions
#without initializing any screen though
#This way we can make it screen adaptive
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print("Resolution: %s x %s" %(screen_width, screen_height))

vs = WebcamVideoStream(src=0).start() #start threading

cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print("initializing camera...") #Initializing Camera
sleep(0.5)
print("adjusting expositon...") #Adjusting Exposition - Otherwise camera
#could start darker
sleep(0.5)
# GPIO.output(26,GPIO.LOW)
print("Running...")

try:
    vid_height, vid_width = vs.read().shape[:2]
except:
    print("Camera nao encontrada. Reconecte a camera e tente novamente.")
    sys.exit()

icon_width = int(vid_width*screen_height*0.1/vid_height)
icon_height = int(screen_height*0.1)
vid_width = int(vid_width*screen_height*0.9/vid_height)
vid_height = int(screen_height*0.9)
black = np.zeros((screen_height,screen_width,3), np.uint8)
overlay = np.zeros((vid_height,vid_width,3), np.uint8)

#layout drawing function

def layout():
    for i in range(0,9):
        cv2.rectangle(black,(i*icon_width,int(screen_height*0.9)),(icon_width + i*icon_width,screen_height),(255,255,255),3)
    cv2.putText(black,'Stop Motion',(int(vid_width + (screen_width - vid_width)*0.05),int((screen_width - vid_width)*0.12)), font, int((screen_width - vid_width)/210.0),(0,0,255), int(screen_width/480),cv2.LINE_AA)
    cv2.putText(black,'MACHINE',(int(vid_width + (screen_width - vid_width)*0.05),int((screen_width - vid_width)*0.28)), font, int((screen_width - vid_width)/150.0),(0,0,255), int(screen_width/720),cv2.LINE_AA)
    cv2.putText(black,'Taxa:',(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.55)), font, int((screen_width - vid_width)/210.0),(255,255,255), int(screen_width/480),cv2.LINE_AA)
    cv2.putText(black,str(AnimFrameRate),(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.7)), font, int((screen_width - vid_width)/210.0),(0,255,0), int(screen_width/480),cv2.LINE_AA)
    cv2.putText(black,'FPS',(int(vid_width + (screen_width - vid_width)*0.3),int((screen_width - vid_width)*0.7)), font, int((screen_width - vid_width)/210.0),(255,255,255), int(screen_width/480),cv2.LINE_AA)

#capture function
def cap():
    global overlay
    global opacity
    global actSeqFrame
    global actSeqIcon
    global seq
    global seqIcon
    opacity = 0.6
    seq.insert(actSeqFrame,imutils.resize(vs.read(), height=int(screen_height*0.9)))
    seqIcon.insert(actSeqIcon,imutils.resize(seq[actSeqFrame], height=int(screen_height*0.1)))
    actSeqFrame += 1
    actSeqIcon += 1
    ovlay()

def ovlay():
    global overlay
    global opacity
    global actSeqFrame
    global seq
    overlay = np.zeros((vid_height,vid_width,3), np.uint8)
    if (actSeqFrame == 0):
        opacity = 0
    if (actSeqFrame == 1):
        overlay = seq[actSeqFrame-1]
    if (actSeqFrame == 2):
        cv2.addWeighted(seq[actSeqFrame-2], 0.5, seq[actSeqFrame-1], 0.5, 0, overlay)
    if (actSeqFrame == 3):
        cv2.addWeighted(seq[actSeqFrame-3], 0.5, seq[actSeqFrame-2], 0.5, 0, overlay)
        cv2.addWeighted(overlay, 0.5, seq[actSeqFrame-1], 0.5, 0, overlay)
    if (actSeqFrame >= 4):
        cv2.addWeighted(seq[actSeqFrame-4], 0.5, seq[actSeqFrame-3], 0.5, 0, overlay)
        cv2.addWeighted(overlay, 0.5, seq[actSeqFrame-2],0.5, 0, overlay)
        cv2.addWeighted(overlay, 0.5, seq[actSeqFrame-1], 0.5, 0, overlay)


def play():
    global key
    global AnimFrameRate
    for i in range(0, actSeqFrame):
        black[0:vid_height, 0:vid_width] = seq[i]
        cv2.imshow('video', black)
        key = cv2.waitKey(int(1000/AnimFrameRate)) & 0xFF
        if (key == ord('r')):# or GPIO.input(4):
            reset()
            return
        else:
            if (key == ord('c')):# or GPIO.input(6):
                return
            else:
                fRate()

def save():
    global key
    global AnimFrameRate
    global vid_width
    global vid_height
    global overlay
    now = datetime.now()
    filename = now.strftime("output-%H%M%S.avi")
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'MJPG'),
        AnimFrameRate, (vid_width, vid_height), True)
    for i in range(0, actSeqFrame):
        overlay = np.zeros((vid_height,vid_width,3), np.uint8)
        overlay[0:vid_height, 0:vid_width] = seq[i]
        cv2.imshow('video', overlay)
        out.write(overlay)
    out.release()

def reset():
    global black
    global seq
    global seqIcon
    global actSeqFrame
    global actSeqIcon
    global actIcon
    global opacity
    black = np.zeros((screen_height,screen_width,3), np.uint8)
    layout()
    cv2.imshow('video', black)
    seq = []
    seqIcon = []
    actSeqFrame = 0
    actSeqIcon = 0
    actIcon = 0
    opacity = 0.0

def fRate():
    global key
    global AnimFrameRate
    if (key == ord('m')) & (AnimFrameRate < 30):
        cv2.putText(black,str(AnimFrameRate),(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.7)), font, (screen_width - vid_width)/210.0,(0,0,0), screen_width/480,cv2.LINE_AA)
        AnimFrameRate = AnimFrameRate + 1
        cv2.putText(black,str(AnimFrameRate),(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.7)), font, (screen_width - vid_width)/210.0,(0,255,0), screen_width/480,cv2.LINE_AA)
    else:
        if (key == ord('n')) & (AnimFrameRate > 1):
            cv2.putText(black,str(AnimFrameRate),(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.7)), font, (screen_width - vid_width)/210.0,(0,0,0), screen_width/480,cv2.LINE_AA)
            AnimFrameRate = AnimFrameRate - 1
            cv2.putText(black,str(AnimFrameRate),(int(vid_width + (screen_width - vid_width)*0.1),int((screen_width - vid_width)*0.7)), font, (screen_width - vid_width)/210.0,(0,255,0), screen_width/480,cv2.LINE_AA)

layout() #starts drawing layout

while key!= ord('q'):

    img = vs.read()
    img = imutils.resize(img, height=int(screen_height*0.9))
    cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, black[0:vid_height, 0:vid_width])
    cv2.imshow('video', black)

    key = cv2.waitKey(1) & 0xFF #keys are listened at this line

    if (key == ord('c')):# or GPIO.input(6):
        for i in range(0,9):
            cv2.rectangle(black,(i*icon_width,int(screen_height*0.9)),(icon_width + i*icon_width,screen_height),(255,255,255),3)
        cap()
        black[int(screen_height*0.9):int(screen_height*0.9 + icon_height), int(actIcon*icon_width):int(actIcon*icon_width + icon_width)] = seqIcon[actSeqIcon-1]
        cv2.rectangle(black,(actIcon*icon_width,int(screen_height*0.9)),(icon_width + actIcon*icon_width,screen_height),(0,255,0),3)
        actIcon += 1
        if actIcon == 9:
            actIcon = 0
    else:
        if (key == ord('p')):# or GPIO.input(5):
            if actSeqFrame > 0:
                play()
            else:
                print("Nao existem quadros para a sequencia!")
        else:
            if (key == ord('r')):# or GPIO.input(4):
                reset()
            else:
                if (key == ord('a')):# or GPIO.input(17):
                    if actSeqFrame > 0:
                        actSeqFrame -= 1
                    if actSeqIcon > 0:
                        actSeqIcon -= 1
                        if actIcon == 0:
                            actIcon = 8
                        else:
                            actIcon -= 1
                        if (actIcon == 0) and (actSeqIcon > 0):
                            for i in range(0,9):
                                black[int(screen_height*0.9):int(screen_height*0.9 + icon_height), (8-i)*icon_width:(8-i)*icon_width + icon_width] = seqIcon[actSeqIcon-1-i]
                            for i in range(0,9):
                                cv2.rectangle(black,(i*icon_width,int(screen_height*0.9)),(icon_width + i*icon_width,screen_height),(255,255,255),3)
                            cv2.rectangle(black,(8*icon_width,int(screen_height*0.9)),(icon_width + 8*icon_width,screen_height),(0,255,0),3)
                        else:
                            cv2.rectangle(black,(actIcon*icon_width,int(screen_height*0.9)),(icon_width + actIcon*icon_width,screen_height),(0,0,0),-1)
                            cv2.rectangle(black,(actIcon*icon_width,int(screen_height*0.9)),(icon_width + actIcon*icon_width,screen_height),(255,255,255),3)
                            cv2.rectangle(black,((actIcon-1)*icon_width,int(screen_height*0.9)),(icon_width + (actIcon-1)*icon_width,screen_height),(0,255,0),3)
                    ovlay()
                else:
                    if (key == ord('s')):# or GPIO.input(17):
                        save()
                    fRate()

cv2.destroyAllWindows()
vs.stop()
print("Programa finalizado.")