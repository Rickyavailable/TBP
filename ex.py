import streamlit as st

# Add custom CSS for font (Poppins applied to the title)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

    /* Apply Poppins font to the body */
    body {
        font-family: 'Poppins', sans-serif;
    }

    /* Specifically apply a different font to the title */
    h1 {
        font-family: 'Poppins', sans-serif;
        font-size: 48px;
        font-weight: bold;
        color: #fff; /* White color for the title */
    }

    /* Style for other text (like instructions and buttons) */
    h2, h3, h4, h5, h6, p {
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True
)

# Streamlit App content
st.title("Face Recog")

st.markdown("""
### Welcome!
This application helps you detect if an image appears in a video. Upload your image and video, and we'll locate all instances where the image appears.

### How it works:
1. Click the Start button below
2. Upload your reference image and video file
3. Our system will process the video and look for your image
4. View the results showing when and where your image appears
""")

st.button("Start", use_container_width=True)

# Footer (at the bottom)
st.markdown("---")
st.markdown("Built By Srinesh Vasy Vizznuu")
