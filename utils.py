import io
from PIL import Image
import cv2
import numpy as np
import tempfile
import os


def validate_image(image_file):
    """
    Validate if the uploaded file is a valid image.

    Args:
        image_file: Streamlit file uploader object

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Read the image using PIL
        img = Image.open(image_file)
        img.verify()  # Verify it's an image

        # Reset the file pointer
        image_file.seek(0)

        # Check if it's a supported format
        if img.format.lower() not in ['jpeg', 'jpg', 'png']:
            return False

        # Check if the image has reasonable dimensions
        img = Image.open(image_file)
        width, height = img.size

        # Images should be between 50x50 and 4000x4000 pixels
        if width < 50 or height < 50 or width > 4000 or height > 4000:
            return False

        # Reset file pointer again
        image_file.seek(0)

        return True
    except Exception as e:
        return False


def validate_video(video_file):
    """
    Validate if the uploaded file is a valid video.

    Args:
        video_file: Streamlit file uploader object

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as tmp:
            tmp.write(video_file.getvalue())
            temp_filename = tmp.name

        # Try to open the video with OpenCV
        cap = cv2.VideoCapture(temp_filename)
        is_valid = cap.isOpened()

        # Check video duration (not more than 10 minutes for performance)
        if is_valid:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if fps <= 0 or frame_count <= 0:
                is_valid = False
            else:
                duration = frame_count / fps
                # Limit to 10 minutes for processing performance
                if duration > 600:  # 10 minutes in seconds
                    is_valid = False

        # Release the video capture
        cap.release()

        # Delete the temporary file
        os.unlink(temp_filename)

        # Reset the file pointer
        video_file.seek(0)

        return is_valid
    except Exception as e:
        # If an exception occurred, cleanup
        if 'temp_filename' in locals():
            try:
                os.unlink(temp_filename)
            except:
                pass
        return False