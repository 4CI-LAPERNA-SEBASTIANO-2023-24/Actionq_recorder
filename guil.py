import cv2
import tkinter as tk
from tkinter import ttk
import os
import threading

class VideoRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Recorder")
        self.video_format = tk.StringVar()
        self.video_format.set("MP4")  # default format
        self.output_folder = tk.StringVar()
        self.output_folder.set("videos")  # default output folder
        self.status = tk.StringVar()
        self.status.set("Not recording")
        self.recording = False
        self.paused = False
        self.frames = []
        self.preview_thread = None
        self.capture_thread = None
        self.stop_recording_flag = threading.Event()
        self.pause_resume_event = threading.Event()  # Event for pausing/resuming capture

        # Timer related variables
        self.timer_value = tk.StringVar()
        self.timer_value.set("5")  # default timer value in seconds

        # Duration related variables
        self.duration_value = tk.StringVar()
        self.duration_value.set("10")  # default duration value in seconds

        # Filename variable
        self.filename = tk.StringVar()
        self.filename.set("output")  # default filename

        # Camera index variable
        self.camera_index = tk.StringVar()
        self.camera_index.set("0")  # default camera index

        # create GUI elements
        self.start_button = ttk.Button(self.root, text="Start", command=self.start_recording)
        self.pause_button = ttk.Button(self.root, text="Pause", command=self.pause_recording, state=tk.DISABLED)
        self.resume_button = ttk.Button(self.root, text="Resume", command=self.resume_recording, state=tk.DISABLED)
        self.stop_button = ttk.Button(self.root, text="Stop", command=self.stop_recording)

        self.format_menu = ttk.OptionMenu(self.root, self.video_format, "MP4", "AVI", "MOV", command=self.refresh_format_menu)
        self.folder_entry = ttk.Entry(self.root, textvariable=self.output_folder)
        self.timer_entry = ttk.Entry(self.root, textvariable=self.timer_value)
        self.duration_entry = ttk.Entry(self.root, textvariable=self.duration_value)
        self.filename_entry = ttk.Entry(self.root, textvariable=self.filename)
        self.camera_index_entry = ttk.Entry(self.root, textvariable=self.camera_index)
        self.status_label = ttk.Label(self.root, textvariable=self.status)
        self.preview_label = ttk.Label(self.root, text="Camera Preview")

        # layout GUI elements
        self.start_button.pack()
        self.pause_button.pack()
        self.resume_button.pack()
        self.stop_button.pack()
        self.format_menu.pack()
        self.folder_entry.pack()
        self.timer_entry.pack()
        self.duration_entry.pack()
        self.filename_entry.pack()
        self.camera_index_entry.pack()
        self.status_label.pack()
        self.preview_label.pack()

        # create a canvas for camera preview
        self.preview_canvas = tk.Canvas(self.root, width=640, height=480)
        self.preview_canvas.pack()

        # initialize video capture
        self.cap = None  # will be initialized in start_recording method

        # Start preview update in a separate thread
        self.preview_thread = threading.Thread(target=self.update_preview)
        self.preview_thread.daemon = True
        self.preview_thread.start()

        # Bind exit event to release resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        if not self.recording:
            try:
                self.timer_seconds = int(self.timer_value.get())
                self.duration_seconds = int(self.duration_value.get())
                self.camera_index_value = int(self.camera_index.get())
            except ValueError:
                self.status.set("Invalid timer, duration, or camera index value")
                return

            self.cap = cv2.VideoCapture(self.camera_index_value, cv2.CAP_DSHOW)  # capture from specified camera index
            if not self.cap.isOpened():
                self.status.set("Error: Camera not found")
                return

            self.recording = True
            self.paused = False
            self.frames = []
            self.status.set("Starting in {} seconds...".format(self.timer_seconds))
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)

            self.root.after(1000, self.countdown_timer)

    def countdown_timer(self):
        if self.timer_seconds > 0:
            self.status.set("Starting in {} seconds...".format(self.timer_seconds))
            self.timer_seconds -= 1
            self.root.after(1000, self.countdown_timer)
        else:
            self.status.set("Recording...")
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.capture_thread = threading.Thread(target=self.capture_video)
            self.capture_thread.start()

    def capture_video(self):
        start_time = cv2.getTickCount() / cv2.getTickFrequency()
        try:
            while self.recording and not self.stop_recording_flag.is_set():
                ret, frame = self.cap.read()
                if ret:
                    if not self.paused:
                        self.frames.append(frame)
                        elapsed_time = (cv2.getTickCount() / cv2.getTickFrequency()) - start_time
                        if elapsed_time >= self.duration_seconds:
                            self.stop_recording_flag.set()
                            self.root.after(0, self.stop_recording)  # Trigger stop recording when duration is reached
                            break
                    else:
                        self.pause_resume_event.wait()  # Pause capture until resumed
                else:
                    self.stop_recording_flag.set()
                    self.status.set("Error: Camera disconnected")
                    break
        except Exception as e:
            self.status.set(f"Error capturing video: {e}")
            self.stop_recording()

    def pause_recording(self):
        if self.recording and not self.paused:
            self.paused = True
            self.status.set("Paused")
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)

    def resume_recording(self):
        if self.recording and self.paused:
            self.paused = False
            self.status.set("Recording...")
            self.pause_resume_event.set()  # Signal to resume capture
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stop_recording_flag.set()
            self.pause_resume_event.set()  # Ensure capture thread resumes to stop cleanly
            self.status.set("Not recording")
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            if self.capture_thread:
                self.capture_thread.join()  # Wait for capture thread to finish
            self.save_video()  # Save video when stopped
            self.frames = []  # Clear frames for next recording
            self.stop_recording_flag.clear()
            self.recording = False  # Ensure recording flag is set correctly for next session
            if self.cap:
                self.cap.release()

    def save_video(self):
        if not self.frames:
            return
        try:
            # create output folder if it doesn't exist
            if not os.path.exists(self.output_folder.get()):
                os.makedirs(self.output_folder.get())

            # choose the correct codec based on format
            format_codecs = {
                'MP4': 'mp4v',
                'AVI': 'XVID',
                'MOV': 'mp4v'
            }
            codec = format_codecs.get(self.video_format.get().upper(), 'mp4v')

            # determine the filename
            base_filename = self.filename.get()
            extension = self.video_format.get().lower()
            count = 0
            output_filename = os.path.join(self.output_folder.get(), f"{base_filename}_{count:03d}.{extension}")
            while os.path.exists(output_filename):
                output_filename = os.path.join(self.output_folder.get(), f"{base_filename}_{count:03d}.{extension}")
                count += 1

            # convert recorded video to selected format and save to disk
            fps = 30  # specify the frames per second
            fourcc = cv2.VideoWriter_fourcc(*codec)  # specify the codec
            out = cv2.VideoWriter(output_filename, fourcc, fps, (640, 480))  # specify the resolution

            for frame in self.frames:
                out.write(frame)

            out.release()
            self.status.set("Video saved successfully!")
        except Exception as e:
            self.status.set(f"Error saving video: {e}")

    def refresh_format_menu(self, value):
        menu = self.format_menu["menu"]
        menu.delete(0, "end")
        formats = ["MP4", "AVI", "MOV"]
        for format in formats:
            menu.add_command(label=format, command=lambda format=format: self.video_format.set(format))
        self.format_menu["menu"] = menu

    def update_preview(self):
        while not self.stop_recording_flag.is_set():
            if self.recording:  # Check if still recording
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)  # Flip frame if needed
                    photo = tk.PhotoImage(data=cv2.imencode(".ppm", frame)[1].tobytes())
                    self.root.after(0, self.update_canvas, photo)
                else:
                    self.root.after(0, self.show_camera_disconnected)
            self.root.update()

    def update_canvas(self, photo):
        self.preview_canvas.config(height=photo.height(), width=photo.width())
        self.preview_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.preview_canvas.image = photo  # Avoid garbage collection

    def show_camera_disconnected(self):
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(320, 240, text="Camera Disconnected", anchor=tk.CENTER, font=("Helvetica", 20))

    def on_closing(self):
        self.stop_recording_flag.set()
        if self.recording:
            self.stop_recording()
        if self.preview_thread:
            self.preview_thread.join()
        if self.capture_thread:
            self.capture_thread.join()
        if self.cap:
            self.cap.release()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    recorder = VideoRecorder()
    recorder.run()
