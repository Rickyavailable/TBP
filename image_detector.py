import cv2
import numpy as np
import time


def detect_image_in_video(image_path, video_path, progress_callback=None):
    """
    Detect if an image appears in a video and return timestamps of matches.

    Args:
        image_path (str): Path to the reference image file
        video_path (str): Path to the video file
        progress_callback (function): Callback function to report progress (0.0 to 1.0)

    Returns:
        tuple: (bool, list) - Whether image was found and list of timestamps in seconds
    """
    # Load the reference image and convert to grayscale
    reference_img = cv2.imread(image_path)
    reference_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)

    # Initialize video capture
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Compute keypoints and descriptors for reference image
    kp_reference, des_reference = sift.detectAndCompute(reference_gray, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # Create FLANN matcher
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Timestamps where image is found
    timestamps = []
    found = False

    # Set frame sampling rate (process every Nth frame for efficiency)
    # Adjust this value based on performance needs
    frame_sample_rate = 15

    # Set minimum match threshold
    min_match_count = 10

    # Process video frames
    frame_idx = 0

    # Initialize previous match status
    previous_match = False
    match_start_time = None

    # Define a cooldown between match detections (in seconds)
    match_cooldown = 1.0  # seconds
    last_match_time = -match_cooldown

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process only every Nth frame
        if frame_idx % frame_sample_rate == 0:
            # Calculate current timestamp
            current_time = frame_idx / fps

            # Update progress
            if progress_callback:
                progress = min(frame_idx / frame_count, 1.0)
                progress_callback(progress)

            # Convert frame to grayscale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect keypoints and compute descriptors
            kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)

            # If no descriptors found in this frame, skip
            if des_frame is None or len(des_frame) < 2:
                frame_idx += 1
                continue

            # Match descriptors
            matches = flann.knnMatch(des_reference, des_frame, k=2)

            # Apply ratio test to filter good matches
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

            # Check if we have enough good matches
            if len(good_matches) >= min_match_count:
                # Only add timestamp if it's been at least match_cooldown seconds since last match
                if current_time - last_match_time >= match_cooldown:
                    timestamps.append(current_time)
                    last_match_time = current_time
                    found = True

        frame_idx += 1

    # Release resources
    cap.release()

    # Final progress update
    if progress_callback:
        progress_callback(1.0)

    return found, timestamps