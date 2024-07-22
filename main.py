
import time
import argparse
import cv2
from icecream import ic
from camera import CameraManager
import signal
import sys
from  main_gui import CameraGUI
 

def main():
    parser = argparse.ArgumentParser(
        description="Program that opens the camera and saves the video in the current working directory."
                    " If you want to exit the cam you have to press the ESCape button or 'q' to quit!!!"
    )
    parser.add_argument("-g", action="store_true", help="Run the program in GUI format", default=False)
    parser.add_argument("-o", dest="output",   type=str, nargs='?', default="./", help="URI of the output video")
    parser.add_argument("-l", dest="looping_value", type=str, nargs='?', default=1, 
        help="Number of times to capture video (the default value is 1, if you insert -1 it loops indefinitely until 'q' is pressed)"
    )
    parser.add_argument("-d", dest="duration_vid", type=float, nargs='?', default=10,
        help="Number of seconds of video to capture"
    )
    parser.add_argument("-cd",dest="countdown", type=int, nargs='?', default=0, help="Number of seconds to wait before starting the camera"
    )
    parser.add_argument("--src", dest="camera", type=int, nargs='?', default=0, help="Number of the camera to capture"
    )

    args = parser.parse_args()
    cr = CameraRecorder(args.g,args.output,int(args.looping_value),args.duration_vid,args.countdown,args.camera)
    cr.start()


   

    


class CameraRecorder():
    def __init__(self,gui,output,looping_value,duration_vid,countdown,camera):
        self.use_gui = gui
        self.output = output 
        self.looping_value = looping_value
        self.duration_vid = duration_vid
        self.countdown = countdown
        self.camera = camera
        self.camera_manager = None
        self.last_frame = None
        self.gui = None

        signal.signal(signal.SIGINT, self.on_signal)

    def start(self):

        t1 = time.time()

        self.camera_manager = CameraManager(self.output, self.looping_value, self.duration_vid, self.countdown, self.camera)

        if self.use_gui:
           self.start_gui()
        else:
            self.start_cli()
        
        t2 = time.time()
        ic(f"Executed in {t2 - t1} seconds")
        cv2.destroyAllWindows()




    def start_gui(self):
        #gino = guil.VideoRecorder()
        #gino.run()
        
        self.gui = CameraGUI(self.camera_manager)
        self.gui.show()
        

    def start_cli(self):

        self.camera_manager.on_start = self.on_camera_start
        self.camera_manager.on_stop = self.on_camera_stop
        self.camera_manager.on_error = self.on_camera_error
        self.camera_manager.on_countdown = self.on_camera_countdown
        self.camera_manager.on_frame_ready = self.on_camera_frame
        self.camera_manager.start_camera()
        while self.camera_manager.vid is None:
            time.sleep(0.1)
        self.camera_manager.start_recording()
        while not self.camera_manager.is_recording():
            time.sleep(0.1)


        while self.camera_manager.n_loop != 0:
            if self.last_frame is not None:
                cv2.imshow('Camera', self.last_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                ic('key Q')
                self.camera_manager.close_camera()
                break
            elif key == 27:
                ic('key ESC')
                self.camera_manager.restart_camera()
        self.camera_manager.close_camera()


    def on_camera_start(self):
        #self.camera_manager.start_recording()
        ic("Starting the camera up ...")

    def on_camera_stop(self):
        #cv2.destroyAllWindows()
        ic("Stopping the camera ...")

    def on_camera_countdown(self,i):
        #cv2.destroyAllWindows()
        ic('countdown',self.countdown,i)

    def on_camera_error(self,message: str):
        ic(message)
        

    def on_camera_frame(self,frame):
        #ic("Starting the camera up ...")
        self.last_frame = frame
        #cv2.imshow('Camera', frame)
    
    def on_signal(self, sig, frame):
        ic('You pressed Ctrl+C!')
        if self.camera_manager is not None:
            self.camera_manager.close_camera()

        sys.exit(0)



if __name__ == '__main__':
    main()