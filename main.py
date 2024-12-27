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
window_size = 500# Variable to control initial window size

"""
1. main screen
2. webcam check
3. camera choose
4. operations
5. output
"""

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

    if frame == frame_choose:
        if cap is None and check[0]:  # Simplified condition
            cap = cv2.VideoCapture(0)
            show_camera_feed(camera_label)
    else:  # This else block was incorrectly indented
        if cap is not None:
            cap.release()
            cap = None

    frame.tkraise()  # This should always execute to raise the frame

def capture_frame(BACK_button):
    """
    Captures an image, resizes it to 1920x1080, extracts the center region, sharpens it, 
    enhances contrast and brightness, rotates it 90 degrees clockwise, and saves it as 'captured_image.png'.
    """
    BACK_button.config(text="Done", command=lambda: endCapture())

    global cap
    ret, frame = cap.read()
    if ret:
        # Resize the frame to 1920x1080
        target_width, target_height = 1920, 1080
        frame = cv2.resize(frame, (target_width, target_height))

        # Get dimensions of the resized frame
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        crop_width, crop_height = width // 4, height // 4  # 50% of frame size

        # Extract the center region
        """
        center_frame = frame[
            center_y - crop_height : center_y + crop_height,
            center_x - crop_width : center_x + crop_width
        ]
        """
        # Apply sharpening filter
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened_frame = cv2.filter2D(frame, -1, kernel)

        # Enhance contrast and brightness
        alpha = 1.3  # Contrast control (1.0-3.0)
        beta = 0     # Brightness control (0-100)
        enhanced_frame = cv2.convertScaleAbs(sharpened_frame, alpha=alpha, beta=beta)

        # Rotate the image 90 degrees clockwise
        rotated_frame = cv2.rotate(enhanced_frame, cv2.ROTATE_90_CLOCKWISE)

        # Save the processed image
        cv2.imwrite('captured_image.png', rotated_frame)
        print("Image captured and saved!")
        send(questionBuffer)
        root.update()


def show_camera_feed(label):
    """
    Display the camera feed in the given label, highlighting the center region for focus.
    """
    global cap, window_size

    if cap is not None:
        ret, frame = cap.read()

        if ret:
            # Correct color format from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape

            # Draw a rectangle to indicate the center focus area
            center_x, center_y = width // 2, height // 2
            rect_width, rect_height = width // 4, height // 4  # 50% of frame size
            cv2.rectangle(
                frame,
                (center_x - rect_width, center_y - rect_height),
                (center_x + rect_width, center_y + rect_height),
                (255, 0, 0), 2  # Blue rectangle
            )

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

def endCapture():
    file_name = "out.txt"

    with open(file_name, "w") as file:
        file.write("\n".join(questionBuffer))
    
    root.quit()
    root.destroy()
    print("success, sana grumaduate ka na")


def main():
    if connectivity_test(url):  # Entry point
        global frame_choose, camera_label, check, questionBuffer
        WINDOW_RESOLUTION="1024x600"
        check = [False]
        questionBuffer = []
        available_devices = []
        # Main canvas
        global root
        root = tk.Tk()
        root.geometry(WINDOW_RESOLUTION)

        # Define the frames here
        frame_entry = tk.Frame(root)  # Main entry screen
        frame_camera = tk.Frame(root)  # Camera check screen
        frame_choose = tk.Frame(root)  # Camera feed screen
        frame_qr = tk.Frame(root)

        # Modify this if changing the display frame
        camera_label = tk.Label(frame_choose)
        camera_label.pack(pady=25)

        # Main frame elements
        ENTRY_label = tk.Label(
            frame_entry,
            text="ayoko na sa thesis",
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

        CAMERA_label = tk.Label(frame_camera,
                                text="Press 'Check' to check for cameras",
                                font=("Helvetica", 32),
                                )
        CAMERA_label.pack(pady=150)

        CHECK_button = tk.Button(
            frame_camera,
            text="Check",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: camCheck(available_devices, root, CAMERA_label, check, CHECK_button, CAMERA_continue)
        )

        CAMERA_continue = tk.Button(frame_camera, 
                                    text="Continue",
                                    font=("Helvetica", 24), 
                                    width=10,
                                    height=2,
                                    command=lambda: show_frame(frame_choose))

        CHECK_button.pack(pady=25)

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
            frame_choose,
            text="Capture",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: capture_frame(CAMERA_BACK_button),
        )

        CAPTURE_button.pack()

        CAMERA_BACK_button = tk.Button(
            frame_choose,
            text="Home",
            font=("Helvetica", 24),
            width=10,
            height=2,
            command=lambda: show_frame(frame_entry),
        )

        CAMERA_BACK_button.pack()

        # Stack the elements from the grid
        for frame in (frame_entry, frame_camera, frame_choose):
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
