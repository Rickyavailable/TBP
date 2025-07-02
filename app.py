import streamlit as st
import tempfile
import os
from PIL import Image
import time
from utils import validate_image, validate_video
from image_detector import detect_image_in_video

# Set page configuration
st.set_page_config(
    page_title="Face ReCoG",
    page_icon="🔍",
    layout="wide"
)

# Add custom CSS for font (Poppins applied globally) and gradient background
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

    body {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(45deg, #1f4037, #99f2c8); /* Background Gradient */
        color: white;  /* Make text visible on gradient */
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    h1, h2, h3, h4, h5, h6, p {
        font-family: 'Poppins', sans-serif;
    }

    /* Ensure all buttons and text are readable */
    .css-1d391kg, .css-18e3th9, .css-1q8dd3e, .css-12ttjfx {
        color: white;
    }

    /* Optional: styling the button for better visibility */
    .stButton button {
        background-color: #2563eb;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }

    /* Styling progress bar */
    .stProgressBar {
        background-color: #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True
)

# Initialize session state variables if they don't exist
if 'stage' not in st.session_state:
    st.session_state.stage = 'home'  # Stages: home, upload, processing, results
if 'results' not in st.session_state:
    st.session_state.results = None
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = []
if 'image_file' not in st.session_state:
    st.session_state.image_file = None
if 'video_file' not in st.session_state:
    st.session_state.video_file = None


def reset_app():
    st.session_state.stage = 'home'
    st.session_state.results = None
    st.session_state.image_file = None
    st.session_state.video_file = None


def start_app():
    st.session_state.stage = 'upload'


def process_files():
    if st.session_state.image_file and st.session_state.video_file:
        st.session_state.stage = 'processing'
        st.rerun()


# Home page
if st.session_state.stage == 'home':
    st.title("Face RecoG")

    st.markdown("""

    ### Welcome!
    This application helps you detect if an image appears in a video.
    Upload your image and video, and we'll locate all instances where the image appears.

    ### How it works:
    1. Click the Start button below
    2. Upload your reference image and video file
    3. Our system will process the video and look for your image
    4. View the results showing when and where your image appears
    """)

    st.button("Start", on_click=start_app, use_container_width=True)

# Upload page
elif st.session_state.stage == 'upload':
    st.title("Upload Files")

    # Upload image
    st.subheader("Upload Reference Image")
    image_file = st.file_uploader("Choose an image (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

    if image_file is not None:
        try:
            if validate_image(image_file):
                st.session_state.image_file = image_file
                st.success("Image uploaded successfully!")
                st.image(image_file, caption="Reference Image", width=300)
            else:
                st.error("Invalid image file. Please upload a valid JPG or PNG file.")
                st.session_state.image_file = None
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            st.session_state.image_file = None

    # Upload video
    st.subheader("Upload Video")
    video_file = st.file_uploader("Choose a video (MP4, AVI)", type=['mp4', 'avi'])

    if video_file is not None:
        try:
            if validate_video(video_file):
                st.session_state.video_file = video_file
                st.success("Video uploaded successfully!")

                # Display video details
                video_details = f"Filename: {video_file.name}"
                st.info(video_details)

                # Display small video preview
                st.video(video_file)
            else:
                st.error("Invalid video file. Please upload a valid MP4 or AVI file.")
                st.session_state.video_file = None
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            st.session_state.video_file = None

    # Process button - only enabled when both files are uploaded
    if st.session_state.image_file and st.session_state.video_file:
        st.button("Process Files", on_click=process_files, use_container_width=True)
    else:
        st.button("Process Files", disabled=True, help="Please upload both image and video files",
                  use_container_width=True)

    # Back button
    st.button("Back", on_click=reset_app)

# Processing page
elif st.session_state.stage == 'processing':
    st.title("Processing...")

    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=f".{st.session_state.image_file.name.split('.')[-1]}") as tmp_img:
            tmp_img.write(st.session_state.image_file.getvalue())
            img_path = tmp_img.name

        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=f".{st.session_state.video_file.name.split('.')[-1]}") as tmp_vid:
            tmp_vid.write(st.session_state.video_file.getvalue())
            vid_path = tmp_vid.name


        # Process the files with our detection function
        # The callback function updates our progress bar
        def progress_callback(progress):
            progress_bar.progress(progress)
            status_text.text(f"Processing: {int(progress * 100)}% complete")


        has_match, timestamps = detect_image_in_video(img_path, vid_path, progress_callback)

        # Clean up temporary files
        os.unlink(img_path)
        os.unlink(vid_path)

        # Update session state with results
        st.session_state.results = has_match
        st.session_state.timestamps = timestamps
        st.session_state.stage = 'results'

        # Force a rerun to show results page
        st.rerun()

    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        # Clean up if needed
        if 'img_path' in locals():
            os.unlink(img_path)
        if 'vid_path' in locals():
            os.unlink(vid_path)

        reset_app()
        st.button("Back to Home", on_click=reset_app)

# Results page
elif st.session_state.stage == 'results':
    st.title("Detection Results")

    # Display the reference image
    if st.session_state.image_file:
        st.subheader("Reference Image")
        st.image(st.session_state.image_file, width=200)

    # Display the results
    if st.session_state.results:
        st.success("✅ The image was found in the video!")

        if st.session_state.timestamps:
            st.subheader(f"Found {len(st.session_state.timestamps)} matches at:")

            # Display timestamps in a more visual way
            cols = st.columns(3)
            for i, timestamp in enumerate(st.session_state.timestamps):
                with cols[i % 3]:
                    mins, secs = divmod(int(timestamp), 60)
                    time_str = f"{mins:02d}:{secs:02d}"
                    st.metric(f"Match #{i + 1}", time_str)

            # Create a timeline visualization
            st.subheader("Timeline Visualization")

            # Get video duration (approximate from last timestamp or use a default)
            video_duration = max(st.session_state.timestamps[-1] + 5, 60) if st.session_state.timestamps else 60

            # Create a crude timeline
            timeline = st.empty()
            timeline_html = f"""
            <div style="width:100%; height:50px; background-color:#f0f0f0; position:relative; border-radius:5px; margin-top:10px;">
            """

            for ts in st.session_state.timestamps:
                position = (ts / video_duration) * 100
                timeline_html += f"""
                <div style="position:absolute; left:{position}%; top:0; height:50px; width:4px; background-color:red;"></div>
                """

            timeline_html += "</div>"
            timeline.markdown(timeline_html, unsafe_allow_html=True)

            # Display the video with the first timestamp
            if st.session_state.video_file:
                st.subheader("Video Preview")
                st.video(st.session_state.video_file)
        else:
            st.info("The image was found, but no specific timestamps were recorded.")
    else:
        st.error("❌ The image was not found in the video.")

    # Option to try again or start over
    col1, col2 = st.columns(2)
    with col1:
        st.button("Try Different Files", on_click=lambda: setattr(st.session_state, 'stage', 'upload'))
    with col2:
        st.button("Start Over", on_click=reset_app)

# Add footer
st.markdown("---")
st.markdown("Built By "
            "Srinesh "
            "Vasy "
            "Vizznuu")
