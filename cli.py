import tkinter as tk
import time
import argparse
import os
import cv2
from icecream import ic
import guis
import guil

class CameraLooper:
    def __init__(self, path="./", n_loop=1, vid_dur=10, countdown=0, cam=0):
        self.path = path
        self.ext = "mp4"
        self.n_loop = n_loop
        self.duration = vid_dur
        self.countdown = countdown
        self.cam = cam
        self.index = 0  # Initialize index for unique filenames

    def looping_cam(self) -> None:
        """
        Method that loops the camera opening.

        :return: None
        """
        if self.n_loop != -1:
            for i in range(self.n_loop):
                self.count_down()
                exit_code = self.open_cam(self.duration)
                if exit_code == 1:
                    break
        else:
            while True:
                self.count_down()
                exit_code = self.open_cam(self.duration)
                if exit_code == 1:
                    break

    def open_cam(self, duration: int) -> int:
        """
        Method that opens the camera and displays the feed until the escape button is pressed.
        This method also saves the video streamed into a file with the specified extension.

        :return: int: 1 if 'q' key was pressed, 2 if 'ESC' key was pressed, otherwise 0
        """

        vid = cv2.VideoCapture(self.cam, cv2.CAP_DSHOW)
        vid.set(cv2.CAP_PROP_FPS, 16.0)

        if not vid.isOpened():
            ic("Error: Could not open video device.")
            return 0

        frame_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (frame_width, frame_height)

        result = cv2.VideoWriter(
            self.get_next_filename(),
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
            if key == ord('q'):
                vid.release()
                result.release()
                cv2.destroyAllWindows()
                return 1
            elif key == 27:
                vid.release()
                result.release()
                cv2.destroyAllWindows()
                return 2

            if time.time() - start_time >= duration:
                break

        vid.release()
        result.release()
        cv2.destroyAllWindows()
        return 0

    def count_down(self) -> None:
        """
        Method that prints a countdown before starting the camera.

        :return: None
        """
        for i in range(self.countdown, 0, -1):
            ic(i)
            time.sleep(1)
        ic("Starting the camera up ...")

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


if __name__ == '__main__':
    t1 = time.time()

    parser = argparse.ArgumentParser(
        description="Program that opens the camera and saves the video in the current working directory."
                    " If you want to exit the cam you have to press the ESCape button or 'q' to quit!!!"
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
        #gino = guil.VideoRecorder()
        #gino.run()

        root = tk.Tk()
        app = guis.CameraGUI(root)
        root.mainloop()


    else:
        camera_looper = CameraLooper(args.output, args.looping_value, args.duration_vid, args.countdown, args.camera)
        camera_looper.looping_cam()

    t2 = time.time()
    ic(f"Executed in {t2 - t1} seconds")
