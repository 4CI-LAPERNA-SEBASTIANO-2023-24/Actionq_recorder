import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
import time
import threading
from PIL import Image, ImageTk
from camera import CameraManager
from icecream import ic

class CameraGUI:
    def __init__(self, camera_manager: CameraManager, debug=False):
        self.debug = debug
        self.root = tk.Tk()
        self.root.title("Camera Recorder")

        self.camera_manager = camera_manager

        self.camera_manager.on_start = self.on_camera_start
        self.camera_manager.on_stop = self.on_camera_stop
        self.camera_manager.on_error = self.on_camera_error
        self.camera_manager.on_countdown = self.on_camera_countdown
        self.camera_manager.on_frame_ready = self.on_camera_frame

        #self.output_folder = path
        #self.recording_duration = vid_dur  # Default recording duration in seconds
        #self.countdown_time = countdown
        #self.num_videos = n_loop  # Default number of videos to record
        #self.camera_index = cam  # Default camera index
        
        
        self.camera_preview = None
        self.cap = None
        self.recording = False
        self.file_index = 0  # Initialize file index for naming files
        self.last_frame = None

        # GUI elements
        self.setup_ui()

    def setup_ui(self):
        # Output folder selection
        folder_label = tk.Label(self.root, text="Output Folder:")
        folder_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.folder_entry = tk.Entry(self.root, width=40)
        self.folder_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        self.folder_entry.insert(0, os.getcwd())

        folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        folder_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)

        # Recording duration entry
        duration_label = tk.Label(self.root, text="Recording Duration (seconds):")
        duration_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.duration_entry = tk.Entry(self.root, width=10)
        self.duration_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.duration_entry.insert(0, "10.0")

        # Countdown time entry
        countdown_label = tk.Label(self.root, text="Countdown Time (seconds):")
        countdown_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.countdown_entry = tk.Entry(self.root, width=10)
        self.countdown_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.countdown_entry.insert(0, "3")

        # Number of videos entry
        num_videos_label = tk.Label(self.root, text="Number of Videos (-1 for loop):")
        num_videos_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.num_videos_entry = tk.Entry(self.root, width=10)
        self.num_videos_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        self.num_videos_entry.insert(0, "1")

        # Camera selection dropdown
        camera_label = tk.Label(self.root, text="Select Camera:")
        camera_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.camera_selection = tk.StringVar(self.root)
        self.camera_selection.set("0")  # Default to camera 0

        self.camera_dropdown = tk.OptionMenu(self.root, self.camera_selection, "0", "1", "2", "3", command=self.update_camera_index)
        self.camera_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        # Camera preview canvas
        self.camera_canvas = tk.Canvas(self.root, width=640, height=480)
        self.camera_canvas.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # Start/Stop buttons
        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=6, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.grid(row=6, column=1, padx=10, pady=10)

        

    def show(self):
        self.start_camera_preview()
        self.root.mainloop()
        # Initialize camera preview
        


    def on_camera_start(self):
        ic("Starting the camera up ...")

    def on_camera_stop(self):
        #cv2.destroyAllWindows()
        ic("Stopping the camera ...")

    def on_camera_countdown(self,i):
        #cv2.destroyAllWindows()
        ic('countdown',self.camera_manager.countdown,i)
        self.show_countdown(i)

    def on_camera_error(self,message: str):
        ic(message)
        

    def on_camera_frame(self,frame):
        #ic("Starting the camera up ...")
        self.last_frame = frame
        #cv2.imshow('Camera', frame)

    def start_camera_preview(self):
        self.camera_manager.camera = int(self.camera_selection.get())
        self.camera_manager.start_camera()

        self.show_frame()

    def show_frame(self):
        if self.last_frame is not None:
            frame = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            self.camera_preview = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_canvas.create_image(0, 0, anchor=tk.NW, image=self.camera_preview)
        self.camera_canvas.after(10, self.show_frame)

    def update_camera_index(self, value):
        self.camera_manager.camera = int(value)
        self.camera_manager.start_camera()
        #if self.cap.isOpened():
        #    self.cap.release()
        #self.cap = cv2.VideoCapture(self.camera_manager.camera)  #update

    def select_folder(self):
        self.camera_manager.path = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.camera_manager.path)

    def start_recording(self):
        # Get recording parameters
        self.camera_manager.path = self.folder_entry.get()
        self.camera_manager.duration = self.parse_duration(self.duration_entry.get())
        self.camera_manager.countdown = int(self.countdown_entry.get())
        self.camera_manager.n_loop = int(self.num_videos_entry.get())

        # Validate input values
        if not os.path.isdir(self.camera_manager.path):
            messagebox.showerror("Error", "Please select a valid output folder.") #update
            return

        if self.camera_manager.duration is None or self.camera_manager.duration < 0 or self.camera_manager.countdown < 0 or self.camera_manager.n_loop == 0:
            messagebox.showerror("Error", "Please enter valid values for duration, countdown time, and number of videos.") #update
            return

        #self.recording = True 
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start recording thread with countdown
        self.camera_manager.start_recording()
        #self.recording_thread = threading.Thread(target=self.record_video_with_countdown) #update
        #self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
        self.camera_manager.stop_recording()
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def parse_duration(self, duration_str):
        try:
            duration = float(duration_str)
            if duration < 0:
                return None
            else:
                return duration
        except ValueError:
            return None

    #def record_video_with_countdown(self):
    #    while self.recording:
    #        self.camera_manager.open_camera()
            
    def show_countdown(self, count):
        countdown_label = tk.Label(self.root, text=f"Recording starts in {count} seconds...",
                                   font=("Helvetica", 24), bg="white")
        countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()
        time.sleep(1)
        countdown_label.destroy()

    


if __name__ == "__main__":
    app = CameraGUI()
    app.show()
 