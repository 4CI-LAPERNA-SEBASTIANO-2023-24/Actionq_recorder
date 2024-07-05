import os
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk

class VideoRecorder:
    def __init__(self, root):
        self.recording = False
        self.output = None
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.frame = None
        self.loop_counter = 0
        self.remaining_time = 0
        self.pause_seconds = 5  # Secondi di pausa tra un video e l'altro

        self.root = root
        self.root.bind('<Escape>', lambda e: root.quit())
        self.root.minsize(800, 600)
        self.root.title("Option selection")

        self.init_widgets()
        self.update_frame()

    def init_widgets(self):
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

        self.label_widget = tk.Label(self.root)
        self.label_widget.pack()

        self.recording_label = tk.Label(self.root, text="Not Recording", bg="green", fg="white")
        self.recording_label.pack()

        self.timer_label = tk.Label(self.root, text="Time left: 30 seconds", bg="white", fg="black")
        self.timer_label.pack()

        button_start = tk.Button(self.root, text="Start", command=self.start_rec)
        button_start.pack()

        button_stop = tk.Button(self.root, text="Stop", command=self.stop_rec)
        button_stop.pack()

        button_exit = tk.Button(self.root, text="Exit", command=self.exit_button)
        button_exit.pack()

    def dir(self, fold) -> list:
        directory = os.path.join(os.getcwd(), fold)
        if not os.path.exists(directory):
            os.makedirs(directory)
        list_files = os.listdir(directory)
        return list_files

    def new_filename(self, n):
        filename1 = 'output' + str(n) + '.mp4'
        return filename1

    def file_search(self, filename, list_files, n):
        for file in list_files:
            if filename == file:
                n += 1
        return n

    def create_new_filename(self, fold) -> str:
        n = 0
        list_files = self.dir(fold)
        filename = self.new_filename(n)
        while filename in list_files:
            n = self.file_search(filename, list_files, n)
            filename = self.new_filename(n)
        return filename

    def update_frame(self):
        ret, self.frame = self.cap.read()
        if ret:
            self.frame = cv.flip(self.frame, 1)
            opencv_image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            photo_image = ImageTk.PhotoImage(image=captured_image)
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)

            if self.recording:
                if self.output is None:
                    self.start_new_recording()  # Start a new recording if output is None

                try:
                    self.output.write(self.frame)
                except Exception as e:
                    print(f"Error writing frame: {e}")

        self.label_widget.after(10, self.update_frame)


    def start_rec(self):
        if self.recording:
            return

        self.recording = True
        self.loop_counter = int(self.spin.get())
        duration = int(self.duration_entry.get())
        self.remaining_time = duration
        self.recording_label.config(text="Recording", bg="red")
        self.timer_label.config(text=f"Time left: {self.remaining_time} seconds")
        self.start_new_recording()

    def start_new_recording(self):
        if self.loop_counter <= 0:
            self.stop_rec()
            self.recording_label.config(text="Not Recording", bg="green")
            return

        folder = self.folder_name.get()
        if not os.path.exists(folder):
            os.makedirs(folder)

        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        nomefile = os.path.join(folder, self.create_new_filename(folder))
        try:
            self.output = cv.VideoWriter(nomefile, fourcc, 20.0, (640, 480))
            self.remaining_time = int(self.duration_entry.get())
            self.update_timer()
        except Exception as e:
            print(f"Error creating VideoWriter: {e}")

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Time left: {self.remaining_time} seconds")
            self.root.after(1000, self.update_timer)
        else:
            self.stop_rec()
            if self.loop_counter > 1:
                self.loop_counter -= 1
                self.recording_label.config(text="Paused", bg="yellow")
                self.root.after(self.pause_seconds * 1000, self.resume_recording)
            else:
                self.loop_counter = 0
                self.recording_label.config(text="Not Recording", bg="green")

    def resume_recording(self):
        self.recording_label.config(text="Recording", bg="red")
        self.start_new_recording()

    def stop_rec(self):
        self.recording = False
        if self.output:
            try:
                self.output.release()
                self.output = None
            except Exception as e:
                print(f"Error releasing VideoWriter: {e}")

    def exit_button(self):
        self.cap.release()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VideoRecorder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
