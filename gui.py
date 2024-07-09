import tkinter as tk
import os
import cv2 as cv
from cli import CameraLooper  # Assuming cli.py has the CameraLooper class
from threading import Thread
from PIL import Image, ImageTk

class GUI:
    def __init__(self, root):
        self.camera = None
        self.root = root
        self.root.bind('<Escape>', lambda e: root.quit())
        self.root.minsize(800, 600)
        self.root.title("Option selection")
    
        Label_Format_File = tk.Label(self.root, text="File format : mp4")
        Label_Format_File.pack()

        folder = tk.Label(self.root, text="Folder:")
        folder.pack()
        self.folder_name = tk.Entry(self.root, width=50)
        self.folder_name.pack()
        self.folder_name.insert(0, os.getcwd())

        loop = tk.Label(self.root, text="Registration loop recording:")
        loop.pack()
        self.spin = tk.Spinbox(self.root, from_=1, to=9999999)
        self.spin.pack()

        duration_label = tk.Label(self.root, text="Duration of each recording (seconds):")
        duration_label.pack()
        self.duration_entry = tk.Entry(self.root)
        self.duration_entry.pack()
        self.duration_entry.insert(0, "30")

        self.wait_label = tk.Label(self.root, text="Insert the time between every registration (seconds):")
        self.wait_label.pack()
        self.wait_entry = tk.Entry(self.root)
        self.wait_entry.pack()
        self.wait_entry.insert(0, "5")

        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack()

        self.label = tk.Label(root, font=('Helvetica', 48), fg='red')
        self.label.pack()

        self.preview_label = tk.Label(self.root)
        self.preview_label.pack()

        self.preview_thread = Thread(target=self.update_preview, daemon=True)
        self.preview_thread.start()

    def update_preview(self):
        cap = cv.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv.flip(frame, 1)
                cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.preview_label.imgtk = imgtk
                self.preview_label.configure(image=imgtk)
            cv.waitKey(30)
        cap.release()

    def start_recording(self):
        thread = Thread(target=self._start_recording_thread)
        thread.start()

    def _start_recording_thread(self):
        duration = int(self.duration_entry.get())
        folder_name = str(self.folder_name.get())
        loop_count = int(self.spin.get())
        wait_time = int(self.wait_entry.get())
        self.camera = CameraLooper(folder_name, loop_count, duration, wait_time)
        self.camera.open_cam(duration)

