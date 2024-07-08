import time
import argparse
import cv2
from icecream import ic
import os

def frame_analyzer(inp: str, out: str, wait : float) -> None:
    """
    Function that analyzes all the frames from a given video path and saves them as images.

    :param str inp: The path to the input video.
    :param str out: The directory to save the output frames.
    """
    cap = cv2.VideoCapture(inp)
    count = 0

    if not cap.isOpened():
        print(f"Error: Cannot open video {inp}")
        return

    if not os.path.exists(out):
        os.makedirs(out)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Frame Analyzer', frame)
        frame_filename = f"{out}/frame{count}.jpg"
        cv2.imwrite(frame_filename, frame)
        count += 1

        if cv2.waitKey(10) & 0xFF == 27:
            break

        time.sleep(wait)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    t1 = time.time()

    parser = argparse.ArgumentParser(
        description="Program that analyzes video frames and saves them as images."
                    " Press the ESC key to exit the video window."
    )
    parser.add_argument("input", type=str, nargs='?', default="../videos/output0.mp4", help="URI of the input video")
    parser.add_argument("output", type=str, nargs='?', default="./frames", help="URI of the output frames")
    parser.add_argument("wait", type=float, nargs='?', default=0.05, help="Directory to save the output frames")

    args = parser.parse_args()

    frame_analyzer(args.input, args.output, args.wait)

    t2 = time.time()
    ic(f"Executed in {t2 - t1} seconds")
