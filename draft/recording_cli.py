import time
import argparse
from graphic.gui import VideoRecorder
import threading
import os
import cv2
from icecream import ic


def looping_cam(path="./", ext="avi", n_loop=1, countdown=0) -> None:
    """
    Function that loops the camera opening.

    :param str path: The path to the video file in output
    :param str ext: The extension of the output video file
    :param int n_loop: The number of times to loop the open_cam call
    :param int countdown: The countdown timer in seconds before opening the camera
    :return: None
    """
    if n_loop != -1:
        for i in range(n_loop):
            countdown_event = threading.Event()
            countdown_thread = threading.Thread(target=count_down, args=(countdown, countdown_event))
            countdown_thread.start()
            countdown_event.wait()
            if open_cam(path, ext) == 'q':
                break
    else:
        while True:
            countdown_event = threading.Event()
            countdown_thread = threading.Thread(target=count_down, args=(countdown, countdown_event))
            countdown_thread.start()
            countdown_event.wait()
            if open_cam(path, ext) == 'q':
                break


def count_down(seconds: int, countdown_event: threading.Event) -> None:
    """
    Function that prints a countdown before starting the camera.

    :param int seconds: The countdown timer in seconds
    :param threading.Event countdown_event: Event to signal countdown completion
    :return: None
    """
    if seconds > 0:
        print_count(seconds)
        time.sleep(seconds)
    countdown_event.set()

def print_count(seconds: int) -> None:
    """
    Recursive function that prints the countdown.

    :param int seconds: The remaining seconds
    :return: None
    """
    if seconds > 0:
        ic(seconds)
        threading.Timer(1.0, print_count, [seconds - 1]).start()


def open_cam(path="./", ext="avi") -> str:
    """
    Function that opens the camera and displays the feed until the escape button is pressed.
    This function also saves the video streamed into a file with the specified extension.

    :param str path: The path to the video file in output
    :param str ext: The extension of the output video file
    :return: str: 'q' if the 'q' key was pressed, otherwise an empty string
    """
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    vid.set(cv2.CAP_PROP_FPS, 24.0)

    if not vid.isOpened():
        ic("Error: Could not open video device.")
        return

    frame_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (frame_width, frame_height)

    if ext.lower() == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    elif ext.lower() == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        ic(f"Unsupported file extension: {ext}")
        return

    result = cv2.VideoWriter(
        f"{path}/{file_name(path, ext)}",
        fourcc,
        24.0, size
    )

    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            ic("Error: Failed to capture image")
            break

        frame = cv2.flip(frame, 1)
        result.write(frame)
        cv2.imshow('Camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('q'):
            vid.release()
            result.release()
            cv2.destroyAllWindows()
            return 'q'

    vid.release()
    result.release()
    cv2.destroyAllWindows()
    return ''


def file_name(path, ext) -> str:
    """
    Function that create the name of the output file adding an incremental index for organization purpose
    
    :param str path: path of the directory to map
    :param str ext: extension
    :return str filename: the filename of the output file
    """
    n = 0
    file_lists = map_dir(path)
    filename = name_file(n, ext)
    while filename in file_lists:
        for file in file_lists:
            if filename == file:
                n = n + 1
        filename = name_file(n, ext)
    return filename


def name_file(n, ext) -> str:
    """
    Function that gets the file name updated with the index n
    
    :param int n: incremental index
    :param str ext: extension
    :return str filename: the file name with the index
    """
    filename = 'output' + str(n) + f".{ext}"
    return filename


def map_dir(path) -> list:
    """
    Function that gets the file of the cwd and return it like a list
    
    :param str path: path of the directory to map
    :return list file_lists: a list of file of the cwd
    """
    lista_files = os.listdir(path)
    return lista_files


if __name__ == '__main__':
    t1 = time.time()

    parser = argparse.ArgumentParser(
        description="Program that opens the camera and saves the video in the current working directory." 
        + " If you want to exit the cam you have to press the ESCape button !!!"
    )
    parser.add_argument("-g", action="store_true", help="Run the program in GUI format")
    parser.add_argument("output", type=str, default="./", nargs='?', help="URI of the output video")
    parser.add_argument(
        "extension", type=str, default="avi",
        nargs='?', help="Extension of the output video. Supported extensions are avi and mp4"
    )
    parser.add_argument(
        "looping_value", type=int, default=1, nargs='?', help="Number of times to capture video (the " +
        "default value is 1, if you insert -1 it loops indefinitely until 'q' is pressed)"
        )
    parser.add_argument(
        "countdown", type=int, default=0, nargs='?', help="Number of seconds to wait before starting the camera"
        )

    args = parser.parse_args()
    if args.g:
        recorder = VideoRecorder()
        recorder.run()
    else:
        looping_cam(args.output, args.extension, args.looping_value, args.countdown)

    t2 = time.time()
    ic(f"Executed in {t2 - t1} seconds")
