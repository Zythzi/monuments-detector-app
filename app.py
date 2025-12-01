import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="🏛️ Monuments Detector",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

MONUMENTS_DB = {
    'Gateway of India': {'location': 'Mumbai', 'description': 'Iconic gateway monument in Mumbai'},
    'Taj Mahal': {'location': 'Agra', 'description': 'White marble mausoleum in Agra'},
    'Hawa Mahal': {'location': 'Jaipur', 'description': 'Pink sandstone palace in Jaipur'},
    'Sardar Patel Statue': {'location': 'Gujarat', 'description': 'World\'s tallest statue in Gujarat'},
    'Mysore Palace': {'location': 'Karnataka', 'description': 'Indo-Saracenic palace in Karnataka'}
}

def analyze_image(image):
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        rgb = img_array[:,:,:3]
    else:
        rgb = np.stack([img_array]*3, axis=-1)
    
    avg_r = np.mean(rgb[:,:,0])
    avg_g = np.mean(rgb[:,:,1])
    avg_b = np.mean(rgb[:,:,2])
    
    gray = np.dot(rgb, [0.299, 0.587, 0.114])
    brightness = np.mean(gray)
    contrast = np.std(gray)
    
    height, width = gray.shape
    aspect_ratio = height / width if width > 0 else 1
    
    return {
        'avg_r': avg_r,
        'avg_g': avg_g,
        'avg_b': avg_b,
        'brightness': brightness,
        'contrast': contrast,
        'aspect_ratio': aspect_ratio,
        'gray': gray
    }

def detect_monument(image):
    feats = analyze_image(image)
    scores = {}
    
    taj_score = 0.0
    if feats['brightness'] > 190:
        taj_score += 0.5
    if feats['avg_r'] > 200 and feats['avg_g'] > 200 and feats['avg_b'] > 200:
        taj_score += 0.5
    scores['Taj Mahal'] = min(taj_score, 1.0)
    
    gateway_score = 0.0
    if 130 < feats['avg_r'] < 180 and 100 < feats['avg_g'] < 150 and 80 < feats['avg_b'] < 130:
        gateway_score += 0.6
    if 100 < feats['brightness'] < 150:
        gateway_score += 0.4
    scores['Gateway of India'] = min(gateway_score, 1.0)
    
    hawa_score = 0.0
    if feats['avg_r'] > 160 and feats['avg_g'] < 140 and feats['avg_b'] < 140:
        hawa_score += 0.6
    if 130 < feats['brightness'] < 180:
        hawa_score += 0.4
    scores['Hawa Mahal'] = min(hawa_score, 1.0)
    
    sardar_score = 0.0
    if feats['brightness'] < 110:
        sardar_score += 0.6
    if feats['aspect_ratio'] > 0.8:
        sardar_score += 0.4
    scores['Sardar Patel Statue'] = min(sardar_score, 1.0)
    
    mysore_score = 0.0
    if feats['avg_g'] > 130 and feats['avg_r'] > 120 and feats['avg_b'] < 120:
        mysore_score += 0.6
    if 140 < feats['brightness'] < 180:
        mysore_score += 0.4
    scores['Mysore Palace'] = min(mysore_score, 1.0)
    
    best = max(scores, key=scores.get)
    return {'monument': best, 'confidence': scores[best], 'scores': scores}

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    input_mode = st.radio("Select Input Source", ["📤 Upload Image", "📷 Camera Capture"])
    confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    st.markdown("---")
    st.markdown("### 🏛️ Supported Monuments")
    for monument, info in MONUMENTS_DB.items():
        st.markdown(f"**{monument}**\n📍 {info['location']}")

st.markdown("# 🏛️ Indian Monuments Detection")
st.markdown("### AI-Powered Monument Recognition with Advanced Image Analysis")

col_input, col_results = st.columns(2)

with col_input:
    st.markdown("### 📸 Input Image")
    image_data = None
    if input_mode == "📤 Upload Image":
        uploaded_file = st.file_uploader("Choose a monument image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image_data = Image.open(uploaded_file)
    else:
        camera_image = st.camera_input("Take a picture of a monument")
        if camera_image:
            image_data = Image.open(camera_image)
    if image_data:
        st.image(image_data, use_column_width=True, caption="Input Image")

with col_results:
    st.markdown("### 🎯 Detection Results")
    if image_data:
        result = detect_monument(image_data)
        monument = result['monument']
        confidence = result['confidence']
        
        if confidence >= confidence_threshold:
            st.success(f"✅ Monument detected!")
            st.markdown(f"**Monument:** {monument}\n**Confidence:** {confidence*100:.1f}%\n**Location:** {MONUMENTS_DB[monument]['location']}\n**Status:** {'High' if confidence > 0.8 else 'Medium' if confidence > 0.6 else 'Low'}")
            
            st.markdown("#### Confidence Breakdown:")
            for mon, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
                if score >= confidence_threshold:
                    bar_width = int(score * 30)
                    st.write(f"{mon}: {'█' * bar_width}{'░' * (30-bar_width)} {score*100:.1f}%")
            
            st.info(MONUMENTS_DB[monument]['description'])
        else:
            st.warning(f"⚠️ Low confidence detected")
            st.markdown("#### All Scores:")
            for mon, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
                bar_width = int(score * 30)
                st.write(f"{mon}: {'█' * bar_width}{'░' * (30-bar_width)} {score*100:.1f}%")
    else:
        st.info("👉 Upload an image to start detection!")

st.markdown("---")
st.markdown("<p style='text-align: center;'>🏛️ Monument Detection App | Powered by Streamlit<br>Made with ❤️ for Indian Heritage</p>", unsafe_allow_html=True)
