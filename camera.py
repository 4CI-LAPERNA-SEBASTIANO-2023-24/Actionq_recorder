import tkinter as tk
import time
import argparse
import os
import cv2
from icecream import ic
import guis
import guil
import threading

class CameraManager:
    def __init__(self, path="./", n_loop=1, vid_dur=10, countdown=0, cam=0, debug=False):
        self.debug = debug
        self.path = path
        self.ext = "mp4"
        self.n_loop = n_loop
        self.duration = vid_dur
        self.countdown = countdown
        self.cam = cam
        self.index = 0 
        self.on_start = None
        self.on_stop = None
        self.on_error = None
        self.on_frame_ready = None

        self.vid = None
        self.writer = None

        self.camera_thread = None

        self.camera_control = 0

        self.finished = False

    def looping_cam(self) -> None:
        """
        Method that loops the camera opening.

        :return: None
        """
        
        if self.n_loop != -1:
            for i in range(self.n_loop):
                self.count_down()
                self.open_cam(self.duration)
                ic('looping_cam:loop_n','self.camera_control',self.camera_control)
                if self.camera_control == -1: break
                if self.camera_control == 0: self.camera_control = 1
        else:
            while True:
                self.count_down()
                self.open_cam(self.duration)
                ic('looping_cam:forever','self.camera_control',self.camera_control)
                if self.camera_control == 0: self.camera_control = 1
        self.did_stop()

    def start_camera(self):
        self.finished = False
        self.camera_control = 1
        self.camera_thread = threading.Thread(target=self.looping_cam)
        self.camera_thread.start()

    def open_cam(self, duration: int) -> int:
        """
        Method that opens the camera and displays the feed until the escape button is pressed.
        This method also saves the video streamed into a file with the specified extension.

        :return: int: 1 if 'q' key was pressed, 2 if 'ESC' key was pressed, otherwise 0
        """

        self.vid = cv2.VideoCapture(self.cam, cv2.CAP_DSHOW)
        self.vid.set(cv2.CAP_PROP_FPS, 16.0)

        if not self.vid.isOpened():
            self.did_error("Error: Could not open video device.")
            return 0

        frame_width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (frame_width, frame_height)

        self.writer = cv2.VideoWriter(
            self.get_next_filename(),
            cv2.VideoWriter_fourcc(*'mp4v'),
            16.0, size
        )

        start_time = time.time()
        while self.vid.isOpened():
            #ic('open_cam','self.camera_control',self.camera_control)
            ret, frame = self.vid.read()
            if not ret:
                self.did_error("Error: Failed to capture image")
                return
            
            if self.camera_control != 1: return 
            if time.time() - start_time >= duration: return
            
            frame = cv2.flip(frame, 1)
            self.writer.write(frame)
            self.did_frame_ready(frame)

    def is_running(self):
        return not self.finished

    
    def restart_camera(self):
        if self.camera_thread is None: return
        if not self.camera_thread.is_alive: return
        self.camera_control = 0
           
    def close_camera(self):
        if self.camera_thread is None: return
        if not self.camera_thread.is_alive: return
        self.camera_control = -1
        self.camera_thread.join()

    def count_down(self) -> None:
        """
        Method that prints a countdown before starting the camera.

        :return: None
        """
        ic('countdown',self.countdown)
        for i in range(self.countdown, 0, -1):
            ic('countdown',self.countdown,i)
            time.sleep(1)
        self.did_start()

    def get_next_filename(self) -> str:
        """
        Method that generates the next available filename in the format output_000.mp4, output_001.mp4, etc.

        :return: str: the next available filename
        """
        while True:
            filename = f"output_{self.index:03d}.{self.ext}"
            file_path = os.path.join(self.path, filename)
            if not os.path.exists(file_path):
                self.index += 1
                return file_path
            self.index += 1

    def map_dir(self) -> list:
        """
        Method that gets the list of files in the current working directory.

        :return: list: a list of filenames in the current directory
        """
        return os.listdir(self.path)
    

    def did_error(self, message: str):
        if self.debug:
             ic('ERROR:',message)
        if self.on_error is None: return
        
        self.on_error(message)

    def did_start(self):
        if self.debug:
            ic("Starting the camera up ...")
        if self.on_start is None: return
        
        self.on_start()
    
    def did_stop(self):
        self.vid.release()
        self.writer.release()
        self.finished = True

        if self.debug:
            ic("Stopping the camera ...")
        if self.on_stop is None: return
        
        self.on_stop()
        

    def did_frame_ready(self, frame):
        if self.debug:
            ic("Starting the camera up ...")
            #cv2.imshow('Camera', frame)
        if self.on_frame_ready is None: return 
        
        self.on_frame_ready(frame)
        