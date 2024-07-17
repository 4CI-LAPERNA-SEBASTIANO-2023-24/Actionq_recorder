import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
import time
import threading
from PIL import Image, ImageTk

class CameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Recorder")

        self.output_folder = ""
        self.recording_duration = 10.0  # Default recording duration in seconds
        self.countdown_time = 3
        self.num_videos = 1  # Default number of videos to record
        self.camera_index = 0  # Default camera index
        self.camera_preview = None
        self.cap = None
        self.recording = False
        self.file_index = 0  # Initialize file index for naming files

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

        # Initialize camera preview
        self.start_camera_preview()

    def start_camera_preview(self):
        self.camera_index = int(self.camera_selection.get())
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Failed to open camera {self.camera_index}")  #update
            return

        self.show_frame()

    def show_frame(self):
        _, frame = self.cap.read()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  # Flip horizontally to correct inversion
            frame = cv2.resize(frame, (640, 480))
            self.camera_preview = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_canvas.create_image(0, 0, anchor=tk.NW, image=self.camera_preview)
        self.camera_canvas.after(10, self.show_frame)

    def update_camera_index(self, value):
        self.camera_index = int(value) 
        if self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index)  #update

    def select_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.output_folder)

    def start_recording(self):
        # Get recording parameters
        self.output_folder = self.folder_entry.get()
        self.recording_duration = self.parse_duration(self.duration_entry.get())
        self.countdown_time = int(self.countdown_entry.get())
        self.num_videos = int(self.num_videos_entry.get())

        # Validate input values
        if not os.path.isdir(self.output_folder):
            messagebox.showerror("Error", "Please select a valid output folder.") #update
            return

        if self.recording_duration is None or self.recording_duration < 0 or self.countdown_time < 0 or self.num_videos == 0:
            messagebox.showerror("Error", "Please enter valid values for duration, countdown time, and number of videos.") #update
            return

        self.recording = True 
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start recording thread with countdown
        self.recording_thread = threading.Thread(target=self.record_video_with_countdown) #update
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
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

    def record_video_with_countdown(self):
        while self.recording:
            # Countdown before recording starts
            for i in range(self.countdown_time, 0, -1):
                self.show_countdown(i) #update
                time.sleep(1)

            # Start recording
            file_name = os.path.join(self.output_folder, f"output_{self.file_index:03d}.mp4") #update

            while os.path.exists(file_name):
                self.file_index += 1
                file_name = os.path.join(self.output_folder, f"output_{self.file_index:03d}.mp4") #update

            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            size = (frame_width, frame_height)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(file_name, fourcc, 20.0, size)

            start_time = time.time()
            while self.recording:
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    out.write(frame) 
                else:
                    break

                if self.recording_duration is not None and time.time() - start_time >= self.recording_duration:
                    break

            # Release resources
            out.release()

            # If num_videos is -1 (loop), continue recording indefinitely
            if self.num_videos == -1:
                continue
            elif self.num_videos > 0:
                self.num_videos -= 1
                if self.num_videos == 0:
                    break

    def show_countdown(self, count):
        countdown_label = tk.Label(self.root, text=f"Recording starts in {count} seconds...",
                                   font=("Helvetica", 24), bg="white")
        countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.root.update()
        time.sleep(1)
        countdown_label.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraGUI(root)
    root.mainloop()
 