from include import *
from encode import *
import tkinter as tk
from PIL import Image, ImageTk
import cv2

"""
main.py

Serves as the front end (Tkinter) for the app that communicates with the GCP Cloud Run service for the LLM service.

Entry point: main()
"""

url = decrypt_url()
cap = None  # Global variable for camera capture
window_size = 300# Variable to control initial window size

"""
1. main screen
2. webcam check
3. camera choose
4. operations
5. output
"""



def list_available_devices(max_devices=10):
    """
    Returns array containing indices of webcams

    Arguments: none
    Returns: array: integers
    """
    available_devices = []
    for device_id in range(max_devices):
        cap = cv2.VideoCapture(device_id)
        if cap.isOpened():
            available_devices.append(device_id)
            cap.release()  # Release the device once checked
    return available_devices

def show_frame(frame):
    """
    Switch to the specified frame and manage the camera lifecycle.
    """
    global cap

    if frame == frame_operation:
        if cap is None:
            cap = cv2.VideoCapture(2)
        show_camera_feed(camera_label)
    else:
        if cap is not None:
            cap.release()
            cap = None

    frame.tkraise()

def capture_frame():
    """
    Writes the image as 'captured_image.png' as being detected by the given camera

    Arguments: none
    Returns: none
    """

    global cap
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('captured_image.png', frame)
        send()

def show_camera_feed(label):
    """
    Display the camera feed in the given label.

    Arguments: label (webcam index)
    Returns: none
    """

    global cap, window_size

    if cap is not None:
        ret, frame = cap.read()

        if ret:
            # Correct color format from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape

            # Resize image based on window size while maintaining aspect ratio
            scale = window_size / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Convert OpenCV image to PIL format
            img = Image.fromarray(resized_frame)
            imgtk = ImageTk.PhotoImage(image=img)

            label.imgtk = imgtk
            label.config(image=imgtk)

        label.after(10, lambda: show_camera_feed(label))

def main():
    if connectivity_test(url):  # Entry point
        #global stuff
        WINDOW_RESOLUTION="1280x720"
        # Main canvas
        root = tk.Tk()
        root.geometry(WINDOW_RESOLUTION)

        # Define the frames here
        global frame_operation, camera_label
        frame_entry = tk.Frame(root) #1
        frame_camera = tk.Frame(root) #2
        frame_operation = tk.Frame(root) #3
        frame_output = tk.Frame(root) #4

        # Main frame elements
        ENTRY_label = tk.Label(
            frame_entry,
            text="Automatic Question Generation",
            font=("Helvetica", 64),
        )
        ENTRY_label.pack(pady=150)

        ENTRY_button = tk.Button(
            frame_entry,
            text="Start",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: show_frame(frame_camera),
        )
        ENTRY_button.pack()

        # Elements for camera frame
        camera_label = tk.Label(frame_operation)
        camera_label.pack(pady=100)

        CAMERA_label = tk.Label(frame_camera,
                                text="Please wait as the cameras are checked",
                                font=("Helvetica", 32),
                                )
        CAMERA_label.pack(pady=150)

        BACK_button = tk.Button(
            frame_camera,
            text="Back",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: show_frame(frame_entry),
        )
        BACK_button.pack()

        CHECK_button = tk.Button(
            frame_camera,
            text="Check",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: show_frame(frame_entry),
        )
        CHECK_button.pack()


        ###frame_operation elements
        CAPTURE_button = tk.Button(
            frame_operation,
            text="Capture",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: capture_frame(),
        )

        CAPTURE_button.pack()

        # Stack the elements from the grid
        for frame in (frame_entry, frame_camera):
            frame.grid(row=0, column=0, sticky="nsew")

        # Unrestrict the main canvas for resizing using weights
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        show_frame(frame_entry)

        root.mainloop()
    else:
        print("Error: cloud not active")

# Entry point for window
if __name__ == "__main__":
    main()
