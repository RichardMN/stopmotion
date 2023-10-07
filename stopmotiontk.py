#!/usr/local/bin/python3

import tkinter as tk
from PIL import Image, ImageTk
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
import imutils
import cv2
import datetime

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()

        self.window.title("Stop Motion Capture")
        # label = tk.Label(
        #     text="hello, Tkinter",
        #     foreground="white",
        #     background="black"
        # )

        self.window.rowconfigure(0, minsize=480, weight=1)
        self.window.columnconfigure(0, minsize=640, weight=1)

        self.window.rowconfigure(1,minsize=48, weight=1)

        # button = tk.Button(
        #     text = "Click me!",
        #     width=25,
        #     height=5,
        #     background="green",
        #     foreground="yellow",
        # )

        # entry = tk.Entry(fg="yellow", bg="blue", width = 50)
        # label.pack()
        # button.pack()
        #entry.pack()

        # frame1 = tk.Frame(master=window, height=50, bg="red")
        # frame1.pack(fill=tk.X)

        # frame2 = tk.Frame(master=window, height=50, bg="yellow")
        # frame2.pack(fill=tk.X)

        # frame3 = tk.Frame(master=window, height=25, bg="blue")
        # frame3.pack(fill=tk.X)

        self.mainFrame = tk.Label(master=self.window, height=480, bg="grey")
        self.mainFrame.grid(row=0, column=0, sticky="nw", padx=5)


        self.miniFrameStrip = tk.Frame(master = self.window, height=48, bg="black" )
        self.miniFrameStrip.columnconfigure(0, minsize=64)
        self.frameImages = list()
        self.miniFrames = list()

        for i in range(0,9):
            self.miniFrames.append(tk.Label(master = self.miniFrameStrip,height=46,width=64, bg="blue"))
            self.miniFrames[i].grid(row=0, column=i, sticky="nw", padx=4)

        self.miniFrameStrip.grid(row=1,column=0, sticky="sw", padx=4)

        self.stream = VideoStream(0)
        self.stream.start()
        self.stop = False

        self.window.after(100, self.video_loop)

        self.window.wm_protocol("WM_DELETE-WINDOW", self.on_close)
        self.frameCount = 0
        self.window.bind('<ButtonPress-1>', self.capture_frame)
        self.window.mainloop()

    def capture_frame(self, event):
        print("button press")
        self.frameCount = self.frameCount + 1 
        smallerFrame = self.photo
        self.miniFrames[self.frameCount % 10].configure( image=smallerFrame )
        self.frameImages.append(self.photo)
    
    def video_loop(self):
        frame = self.stream.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(image)
        self.photo = ImageTk.PhotoImage(self.image)
        self.mainFrame.configure(image=self.photo)
        if not self.stop:
            self.window.after(500, self.video_loop)
    
    def on_close(self):
        self.stop = True
        self.stream.stop()
        self.window.destroy()

    def handle_keypress(event):
        """Print the character associated to the key pressed"""
        print(event.char)

    # window.bind("<Key>", handle_keypress)

if __name__ == '__main__':
    MainWindow()