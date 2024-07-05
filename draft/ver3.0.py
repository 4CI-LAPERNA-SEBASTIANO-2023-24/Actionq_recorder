import os
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
# hi
spin = None
duration_entry = None

recording = False
output = None
cap = None
frame = None
loop_counter = 0
remaining_time = 0
pause_seconds = 5  # Secondi di pausa tra un video e l'altro

def dir(fold) -> list:
    """
    Function that creates the list of files
    starting from the folder of the .py program it will
    go inside the folder <fold> name and scan for all the file
    inside that

    :return str fold: insert the string name
    of the folder where will be created the new file
    """
    initial_directory = os.getcwd()
    directory = os.path.join(initial_directory, fold)
    if not os.path.exists(directory):
        os.makedirs(directory)
    list_files = os.listdir(directory)
    return list_files

def new_filename(n):
    """create a string filename"""
    filename1 = 'output' + str(n) + '.mp4'
    return filename1

def file_search(filename, list_files, n):
    """_file_search_

    Args:
        filename (str): filename string that we will search
        inside of the folder
        list_files (list): list of files
        n (int): starting number for the filename modify

    Returns:
        n: new number for filename
    """
    for file in list_files:
        if filename == file:
            n = n + 1
    return n

def create_new_filename(fold) -> str:
    """
    Function that creates the new filename ,
    using the other function:
    dir(fold);new_filename(n),
    file_search(filename,list_files,n)

    :return str fold: insert the string name
    of the folder where will be created the new file
    """
    n = 0
    list_files = dir(fold)
    filename = new_filename(n)
    while filename in list_files:
        n = file_search(filename, list_files, n)
        filename = new_filename(n)
    return filename

def update_frame():
    global frame, recording, label_widget, output
    ret, frame = cap.read()
    if ret:
        frame = cv.flip(frame, 1)
        
        # Convert image from one color space to other
        opencv_image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        
        # Capture the latest frame and transform to image
        captured_image = Image.fromarray(opencv_image)
        
        # Convert captured image to photoimage
        photo_image = ImageTk.PhotoImage(image=captured_image)
        
        # Displaying photoimage in the label
        label_widget.photo_image = photo_image
        
        # Configure image in the label
        label_widget.configure(image=photo_image)
        
        if recording and output is not None:
            output.write(frame)
        
    # Repeat the same process after every 10 milliseconds
    label_widget.after(10, update_frame)

def start_rec():
    global recording, output, loop_counter, timer_label, remaining_time, spin
    
    # Se si sta già registrando, non fare nulla
    if recording:
        return
    
    recording = True
    loop_counter = int(spin.get())  # Ora spin è accessibile globalmente
    duration = int(duration_entry.get())  # Durata della registrazione in secondi
    remaining_time = duration
    recording_label.config(text="Recording", bg="red")
    timer_label.config(text=f"Time left: {remaining_time} seconds")
    folder = folder_name.get()
    start_new_recording()

def start_new_recording():
    global recording, output, loop_counter, remaining_time
    
    # Se non ci sono più registrazioni da fare, interrompi tutto
    if loop_counter <= 0:
        stop_rec()
        recording_label.config(text="Not Recording", bg="green")
        return
    
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    folder = folder_name.get()
    nomefile = os.path.join(folder, create_new_filename(folder))
    output = cv.VideoWriter(nomefile, fourcc, 20.0, (640, 480))
    remaining_time = int(duration_entry.get())  # Durata della registrazione in secondi
    update_timer()

def update_timer():
    global remaining_time, loop_counter
    
    if remaining_time > 0:
        remaining_time -= 1
        timer_label.config(text=f"Time left: {remaining_time} seconds")
        root.after(1000, update_timer)
    else:
        stop_rec()
        if loop_counter > 1:
            loop_counter -= 1
            recording_label.config(text="Paused", bg="yellow")
            root.after(pause_seconds * 1000, resume_recording)
        else:
            loop_counter = 0
            recording_label.config(text="Not Recording", bg="green")

def resume_recording():
    global recording
    recording_label.config(text="Recording", bg="red")
    start_new_recording()

def stop_rec():#fatto
    global recording, output
    recording = False
    if output:
        output.release()

def exit_button():#fatto
    global cap
    cap.release()
    root.destroy()

def main(): #done
    global folder_name, root, cap, label_widget, recording, output, recording_label, timer_label, spin, duration_entry
    
    recording = False
    output = None
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    
    root = tk.Tk()
    root.bind('<Escape>', lambda e: root.quit())
    
    root.minsize(800, 600)
    root.title("Option selection")
    
    Label_Format_File = tk.Label(root, text="File format : mp4")
    Label_Format_File.pack()
    
    folder = tk.Label(root, text="Folder:")
    folder.pack()
    folder_name = tk.Entry(root, width=50)
    folder_name.pack()
    folder_name.insert(0, os.getcwd())
    
    loop = tk.Label(root, text="Registration loop recording:")
    loop.pack()
    spin = tk.Spinbox(root, from_=1, to=9999999)
    spin.pack()
    
    duration_label = tk.Label(root, text="Duration of each recording (seconds):")
    duration_label.pack()
    duration_entry = tk.Entry(root)
    duration_entry.pack()
    duration_entry.insert(0, "30")
    
    label_widget = tk.Label(root)
    label_widget.pack()
    
    recording_label = tk.Label(root, text="Not Recording", bg="green", fg="white")
    recording_label.pack()
    
    timer_label = tk.Label(root, text="Time left: 30 seconds", bg="white", fg="black")
    timer_label.pack()
    
    button_start = tk.Button(root, text="Start", command=start_rec)
    button_start.pack()
    
    button_stop = tk.Button(root, text="Stop", command=stop_rec)
    button_stop.pack()
    
    button_exit = tk.Button(root, text="Exit", command=exit_button)
    button_exit.pack()
    
    update_frame()
    root.mainloop()

if __name__ == "__main__":
    main()
