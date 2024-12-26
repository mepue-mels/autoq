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

def show_frame(frame):
    """Switch to the specified frame and manage the camera lifecycle."""
    global cap

    if frame == frame_camera:
        if cap is None:
            cap = cv2.VideoCapture(1)
        show_camera_feed(camera_label)
    else:
        if cap is not None:
            cap.release()
            cap = None

    frame.tkraise()

def capture_frame():
	global cap

	ret, frame = cap.read()

	if ret:
		cv2.imwrite('captured_image.png', frame)
		send()

def show_camera_feed(label):
    """Display the camera feed in the given label."""
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

        # Main canvas
        root = tk.Tk()
        root.geometry("1280x720")

        # Define the frames here
        global frame_camera, camera_label
        frame_entry = tk.Frame(root)
        frame_camera = tk.Frame(root)

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
        camera_label = tk.Label(frame_camera)
        camera_label.pack(pady=100)

        BACK_button = tk.Button(
            frame_camera,
            text="Back",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: show_frame(frame_entry),
        )
        BACK_button.pack()

        CAPTURE_button = tk.Button(
            frame_camera,
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
