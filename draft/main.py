import cv2
import tkinter as tk
from tkinter import ttk
import moviepy.editor as mp
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
        self.stop_recording_flag = False

        # create GUI elements
        self.start_button = ttk.Button(self.root, text="Start", command=self.start_recording)
        self.pause_button = ttk.Button(self.root, text="Pause", command=self.pause_recording)
        self.resume_button = ttk.Button(self.root, text="Resume", command=self.resume_recording, state=tk.DISABLED)
        self.stop_button = ttk.Button(self.root, text="Stop", command=self.stop_recording)
        
        self.format_menu = ttk.OptionMenu(self.root, self.video_format, "MP4", "AVI", "MOV", command=self.refresh_format_menu)
        self.folder_entry = ttk.Entry(self.root, textvariable=self.output_folder)
        self.status_label = ttk.Label(self.root, textvariable=self.status)
        self.preview_label = ttk.Label(self.root, text="Camera Preview")

        # layout GUI elements
        self.start_button.pack()
        self.pause_button.pack()
        self.resume_button.pack()
        self.stop_button.pack()
        self.format_menu.pack()
        self.folder_entry.pack()
        self.status_label.pack()
        self.preview_label.pack()

        # create a canvas for camera preview
        self.preview_canvas = tk.Canvas(self.root, width=640, height=480)
        self.preview_canvas.pack()

        # initialize video capture
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture from default camera
        if not self.cap.isOpened():
            self.status.set("Error: Camera not found")
            self.start_button.config(state=tk.DISABLED)
            return

        # Start preview update in a separate thread
        self.preview_thread = threading.Thread(target=self.update_preview)
        self.preview_thread.daemon = True
        self.preview_thread.start()

        # Bind exit event to release resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.paused = False
            self.frames = []
            self.status.set("Recording...")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.capture_thread = threading.Thread(target=self.capture_video)
            self.capture_thread.start()

    def capture_video(self):
        while self.recording and not self.stop_recording_flag:
            ret, frame = self.cap.read()
            if ret:
                if not self.paused:
                    self.frames.append(frame)
            else:
                self.stop_recording()
                self.status.set("Error: Camera disconnected")

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
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)

    def stop_recording(self):
        if self.recording:
            self.stop_recording_flag = True
            self.recording = False
            self.status.set("Not recording")
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.save_video()
            self.stop_recording_flag = False

    def save_video(self):
        if not self.frames:
            return
        try:
            # create output folder if it doesn't exist
            if not os.path.exists(self.output_folder.get()):
                os.makedirs(self.output_folder.get())

            # convert recorded video to selected format and save to disk
            fps = 30  # specify the frames per second
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # specify the codec
            output_filename = os.path.join(self.output_folder.get(), "output." + self.video_format.get().lower())
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
        while True:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                photo = tk.PhotoImage(data=cv2.imencode(".ppm", frame)[1].tobytes())
                self.preview_canvas.config(height=photo.height(), width=photo.width())
                self.preview_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                self.preview_canvas.image = photo  # Avoid garbage collection
            else:
                # Handle case where camera is disconnected
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(320, 240, text="Camera Disconnected", anchor=tk.CENTER, font=("Helvetica", 20))
            self.root.update()
            if self.stop_recording_flag:
                break

    def on_closing(self):
        if self.recording:
            self.stop_recording()
        self.stop_recording_flag = True
        if self.preview_thread:
            self.preview_thread.join()
        if self.capture_thread:
            self.capture_thread.join()
        self.cap.release()
        self.root.destroy()
        exit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    recorder = VideoRecorder()
    recorder.run()