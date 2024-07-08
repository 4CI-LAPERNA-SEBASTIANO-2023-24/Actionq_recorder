import tkinter as tk
import time
import argparse
import threading
import os
import cv2
from icecream import ic
from main import VideoRecorder


class CameraLooper:
    def __init__(self, path="./", n_loop=1, vid_dur=10, countdown=0, cam=0):
        self.path = path
        self.ext = "mp4"
        self.n_loop = n_loop
        self.duration = vid_dur
        self.countdown = countdown
        self.cam = cam


    def looping_cam(self) -> None:
        """
        Method that loops the camera opening.

        :return: None
        """
        if self.n_loop != -1:
            for i in range(self.n_loop):
                self.open_cam(self.duration)
        else:
            while True:
                exir_code = self.open_cam(self.duration)
                if exir_code:
                    break


    def count_down(self, countdown_event: threading.Event) -> None:
        """
        Method that prints a countdown before starting the camera.

        :param threading.Event countdown_event: Event to signal countdown completion
        :return: None
        """
        if self.countdown > 0:
            self.print_count(self.countdown)
            time.sleep(self.countdown)
        countdown_event.set()


    def print_count(self, seconds: int) -> None:
        """
        Recursive method that prints the countdown.

        :param int seconds: The remaining seconds
        :return: None
        """
        if seconds > 0:
            ic(seconds)
            threading.Timer(1.0, self.print_count, [seconds - 1]).start()


    def open_cam(self, duration: int) -> bool:
        """
        Method that opens the camera and displays the feed until the escape button is pressed.
        This method also saves the video streamed into a file with the specified extension.

        :return: bool: True if 'q' key was pressed, otherwise False
        """
        countdown_event = threading.Event()
        countdown_thread = threading.Thread(target=self.count_down, args=(countdown_event,))
        countdown_thread.start()
        countdown_event.wait()

        vid = cv2.VideoCapture(self.cam, cv2.CAP_DSHOW)
        vid.set(cv2.CAP_PROP_FPS, 16.0)

        if not vid.isOpened():
            ic("Error: Could not open video device.")
            return False

        frame_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (frame_width, frame_height)

        result = cv2.VideoWriter(
            f"{self.path}/{self.file_name()}",
            cv2.VideoWriter_fourcc(*'mp4v'),
            16.0, size
        )

        start_time = time.time()
        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                ic("Error: Failed to capture image")
                break

            frame = cv2.flip(frame, 1)
            result.write(frame)
            cv2.imshow('Camera', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                vid.release()
                result.release()
                cv2.destroyAllWindows()
                return True

            if time.time() - start_time >= duration:
                break

        vid.release()
        result.release()
        cv2.destroyAllWindows()
        return False



    def file_name(self) -> str:
        """
        Method that create the name of the output file adding an incremental index for organization purpose

        :return str filename: the filename of the output file
        """
        n = 0
        file_lists = self.map_dir()
        filename = self.name_file(n)
        while filename in file_lists:
            for file in file_lists:
                if filename == file:
                    n += 1
            filename = self.name_file(n)
        return filename


    def name_file(self, n: int) -> str:
        """
        Method that gets the file name updated with the index n

        :param int n: incremental index
        :return str filename: the file name with the index
        """
        return f'output{n}.{self.ext}'


    def map_dir(self) -> list:
        """
        Method that gets the file of the cwd and return it like a list

        :return list file_lists: a list of file of the cwd
        """
        return os.listdir(self.path)


if __name__ == '__main__':
    t1 = time.time()

    parser = argparse.ArgumentParser(
        description="Program that opens the camera and saves the video in the current working directory."
                    " If you want to exit the cam you have to press the ESCape button !!!"
    )
    parser.add_argument("-g", action="store_true", help="Run the program in GUI format")
    parser.add_argument("output", type=str, nargs='?', default="./", help="URI of the output video")
    parser.add_argument(
        "looping_value", type=int, nargs='?', default=1, 
        help="Number of times to capture video (the default value is 1, if you insert -1 it loops indefinitely until 'q' is pressed)"
    )
    parser.add_argument(
        "duration_vid", type=int, nargs='?', default=10,
        help="Number of seconds of video to capture"
    )
    parser.add_argument(
        "countdown", type=int, nargs='?', default=0, help="Number of seconds to wait before starting the camera"
    )
    parser.add_argument(
        "camera", type=int, nargs='?', default=0, help="Number of the camera to capture"
    )

    args = parser.parse_args()
    if args.g:
        root = tk.Tk()
        app = VideoRecorder(root)
        root.mainloop()
    else:
        camera_looper = CameraLooper(args.output, args.looping_value, args.duration_vid, args.countdown, args.camera)
        camera_looper.looping_cam()

    t2 = time.time()
    ic(f"Executed in {t2 - t1} seconds")
