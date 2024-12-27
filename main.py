from include import *
from encode import *
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

"""
main.py

Serves as the front end (Tkinter) for the app that communicates with the GCP Cloud Run service for the LLM service.

Entry point: main()
"""

url = decrypt_url()
cap = None  # Global variable for camera capture
window_size = 500  # Variable to control initial window size

def camCheck(devices, root, camera_label, check, check_btn, cam_btn):
    devices[:] = list_available_devices()
    camera_label.config(text="Cameras found!")
    check[0] = True
    check_btn.pack_forget()
    cam_btn.pack()
    root.update()

def list_available_devices(max_devices=10):
    """
    Returns array containing indices of webcams
    """
    available_devices = []
    for device_id in range(max_devices):
        cap = cv2.VideoCapture(device_id)
        if cap.isOpened():
            available_devices.append(device_id)
            cap.release()  # Release the device once checked
    return available_devices

def show_frame(frame_name, frames):
    """
    Switch to the specified frame and manage the camera lifecycle.
    """
    global cap

    if frame_name == "choose":
        if cap is None and check[0]:  # Simplified condition
            cap = cv2.VideoCapture(0)
            show_camera_feed(frames["choose"]["label"])
    else:
        if cap is not None:
            cap.release()
            cap = None

    frames[frame_name]["frame"].tkraise()

def capture_frame():
    """
    Captures and processes an image.
    """
    global cap
    ret, frame = cap.read()
    if ret:
        # Apply sharpening filter
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened_frame = cv2.filter2D(frame, -1, kernel)

        # Enhance contrast and brightness
        alpha = 1.25  # Contrast control (1.0-3.0)
        beta = 30    # Brightness control (0-100)
        enhanced_frame = cv2.convertScaleAbs(sharpened_frame, alpha=alpha, beta=beta)

        # Rotate the image 90 degrees clockwise
        rotated_frame = cv2.rotate(enhanced_frame, cv2.ROTATE_90_CLOCKWISE)

        # Save the processed image
        cv2.imwrite('captured_image.png', rotated_frame)
        send()

def show_camera_feed(label):
    """
    Display the camera feed in the given label.
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
        global cap, check
        WINDOW_RESOLUTION = "1280x720"
        check = [False]

        available_devices = []
        root = tk.Tk()
        root.geometry(WINDOW_RESOLUTION)

        # Define frames and their components in a dictionary
        frames = {
            "entry": {
                "frame": tk.Frame(root),
                "label": tk.Label(
                    text="ayoko na sa thesis",
                    font=("Helvetica", 64),
                ),
                "button": tk.Button(
                    text="Start",
                    font=("Helvetica", 24),
                    width=10,
                    height=2,
                    command=lambda: show_frame("camera", frames)
                )
            },
            "camera": {
                "frame": tk.Frame(root),
                "label": tk.Label(
                    text="Press 'Check' to check for cameras",
                    font=("Helvetica", 32),
                ),
                "check_button": tk.Button(
                    text="Check",
                    font=("Helvetica", 24),
                    width=10,
                    height=2,
                    command=lambda: camCheck(
                        available_devices, root,
                        frames["camera"]["label"], check,
                        frames["camera"]["check_button"], frames["camera"]["continue_button"]
                    )
                ),
                "continue_button": tk.Button(
                    text="Continue",
                    font=("Helvetica", 24),
                    width=10,
                    height=2,
                    command=lambda: show_frame("choose", frames)
                ),
                "back_button": tk.Button(
                    text="Back",
                    font=("Helvetica", 24),
                    width=10,
                    height=2,
                    command=lambda: show_frame("entry", frames)
                )
            },
            "choose": {
                "frame": tk.Frame(root),
                "label": tk.Label(),
                "capture_button": tk.Button(
                    text="Capture",
                    font=("Helvetica", 24),
                    width=10,
                    height=2,
                    command=lambda: capture_frame()
                )
            }
        }

        # Pack components in their respective frames
        frames["entry"]["label"].pack(pady=150)
        frames["entry"]["button"].pack()

        frames["camera"]["label"].pack(pady=150)
        frames["camera"]["check_button"].pack(pady=25)
        frames["camera"]["back_button"].pack()

        frames["choose"]["label"].pack(pady=150)
        frames["choose"]["capture_button"].pack()

        # Add frames to the grid
        for frame_data in frames.values():
            frame_data["frame"].grid(row=0, column=0, sticky="nsew")

        # Configure root weights
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Show initial frame
        show_frame("entry", frames)

        root.mainloop()
    else:
        print("Error: Cloud not active")

# Entry point for window
if __name__ == "__main__":
    main()
