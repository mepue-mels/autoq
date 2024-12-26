import base64
import requests
import mimetypes

def encode_image_to_base64(image_path):
    """
    Encodes an image file to a Base64 string with a MIME type prefix.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64-encoded string of the image with MIME type, or None if an error occurs.
    """
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            print("Could not determine the MIME type of the image.")
            return None

        with open(image_path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{base64_string}"
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def send_image_to_flask(image_base64, url):
    """
    Sends a Base64-encoded image to a Flask app via a POST request.

    Args:
        image_base64 (str): Base64-encoded string of the image with MIME type.
        url (str): The endpoint URL of the Flask app.

    Returns:
        dict: JSON response from the Flask app, or None if an error occurs.
    """
    headers = {'Content-Type': 'application/json'}
    data = {'image': image_base64}
    try:
        # Set a reasonable timeout, for example, 30 seconds
        response = requests.post(url, json=data, headers=headers, timeout=None)
        response.raise_for_status()  # Raise an error for bad HTTP status
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to Flask app: {e}")
        return None


# Main execution
def send():
    # Path to the image
    image_path = "./captured_image.png"  # Replace with the correct path to your image
    # Flask app endpoint URL (adjusted for Cloud Run)
    flask_url = "https://aqg-183264939006.asia-east1.run.app/predict"  # Update to Cloud Run URL

    # Encode the image
    encoded_image = encode_image_to_base64(image_path)
    if not encoded_image:
        print("Failed to encode the image. Exiting.")
    else:
        # Send to Flask app
        print("Sending the encoded image to the Flask app...")
        response = send_image_to_flask(encoded_image, flask_url)
        if response:
            print("Response from Flask app:")
            print(response)
        else:
            print("Failed to get a valid response from the Flask app.")
