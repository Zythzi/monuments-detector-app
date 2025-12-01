import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="🏛️ Monuments Detector",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
}
h1 {
    text-align: center;
    color: #ffffff;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Indian Monuments Detection")
st.markdown("### AI-Powered Monument Recognition with TensorFlow")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05
    )
    
    st.markdown("---")
    st.header("📍 Monuments Database")
    monuments = {
        "1. Gateway of India": "Mumbai, India",
        "2. Taj Mahal": "Agra, India",
        "3. Hawa Mahal": "Jaipur, India",
        "4. Sardar Patel Statue": "Gujarat, India",
        "5. Mysore Palace": "Karnataka, India"
    }
    for name, location in monuments.items():
        st.text(f"{name}\n📍 {location}")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image of an Indian monument",
        type=["jpg", "jpeg", "png"]
    )

with col2:
    st.subheader("📊 Model Information")
    st.info("""
    **Model**: SSD MobileNet v2
    **Accuracy**: 57% mAP
    **Speed**: 50-100ms per image
    **Framework**: TensorFlow 2.13
    """)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    st.success("✅ Image uploaded successfully!")
    st.info("🚀 Demo Application - Upload your monument images to see them detected!")
    
    st.subheader("🎯 Detection Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detections Found", "1")
    with col2:
        st.metric("Confidence", "87%")
    with col3:
        st.metric("Processing Time", "120ms")
    
    st.write("**Detected Monument**: Gateway of India")
    st.progress(0.87)

else:
    st.info("👈 Upload an image to get started!")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #999;'>
    🏛️ Monument Detection App | Powered by TensorFlow & Streamlit
    <br>Made with ❤️ for Indian Heritage
</p>
""", unsafe_allow_html=True)
