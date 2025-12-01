import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime
# Page configuration
st.set_page_config(
    page_title="🏛️ Monuments Detector",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Monument database with enhanced characteristics
MONUMENTS_DB = {
    'Gateway of India': {
        'location': 'Mumbai',
        'description': 'Iconic gateway monument in Mumbai',
        'colors': {'primary': 'brown', 'secondary': 'stone'},
        'features': ['arches', 'structured', 'monument']
    },
    'Taj Mahal': {
        'location': 'Agra',
        'description': 'White marble mausoleum in Agra',
        'colors': {'primary': 'white', 'secondary': 'cream'},
        'features': ['dome', 'symmetrical', 'bright']
    },
    'Hawa Mahal': {
        'location': 'Jaipur',
        'description': 'Pink sandstone palace in Jaipur',
        'colors': {'primary': 'pink', 'secondary': 'red'},
        'features': ['intricate', 'windows', 'pattern']
    },
    'Sardar Patel Statue': {
        'location': 'Gujarat',
        'description': 'World\'s tallest statue in Gujarat',
        'colors': {'primary': 'dark', 'secondary': 'bronze'},
        'features': ['tall', 'dark', 'vertical']
    },
    'Mysore Palace': {
        'location': 'Karnataka',
        'description': 'Indo-Saracenic palace in Karnataka',
        'colors': {'primary': 'golden', 'secondary': 'brown'},
        'features': ['ornate', 'palace', 'grand']
    }
}

def extract_advanced_features(image):
    """Extract advanced features from image using PIL and NumPy"""
    img_array = np.array(image)
    
    # Handle different image formats
    if len(img_array.shape) == 3:
        if img_array.shape[2] == 4:  # RGBA
            rgb = img_array[:, :, :3]
        else:  # RGB
            rgb = img_array[:, :, :3]
    else:
        rgb = np.stack([img_array] * 3, axis=-1)
    
    # 1. Color Analysis
    avg_color = np.mean(rgb, axis=(0, 1))
    color_std = np.std(rgb, axis=(0, 1))
    
    # RGB channel dominance
    r_channel = rgb[:, :, 0]
    g_channel = rgb[:, :, 1]
    b_channel = rgb[:, :, 2]
    
    # 2. Brightness and Contrast
    gray = np.dot(rgb, [0.299, 0.587, 0.114])
    brightness = np.mean(gray)
    contrast = np.std(gray)
    
    # 3. Edge Detection (Sobel-like)
    edges_x = np.abs(np.diff(gray, axis=1))
    edges_y = np.abs(np.diff(gray, axis=0))
    edge_density = (np.mean(edges_x) + np.mean(edges_y)) / 2
    
    # 4. Texture Analysis
    texture_variance = np.var(gray)
    
    # 5. Spatial features
    height, width = gray.shape
    aspect_ratio = height / width if width > 0 else 1
    
    # 6. Color ratios
    r_dominance = np.mean(r_channel) / (np.mean([r_channel, g_channel, b_channel]) + 0.001)
    g_dominance = np.mean(g_channel) / (np.mean([r_channel, g_channel, b_channel]) + 0.001)
    b_dominance = np.mean(b_channel) / (np.mean([r_channel, g_channel, b_channel]) + 0.001)
    
    return {
        'avg_color': avg_color,
        'color_std': color_std,
        'brightness': brightness,
        'contrast': contrast,
        'edge_density': edge_density,
        'texture_variance': texture_variance,
        'aspect_ratio': aspect_ratio,
        'r_dominance': r_dominance,
        'g_dominance': g_dominance,
        'b_dominance': b_dominance,
        'r_channel': r_channel,
        'g_channel': g_channel,
        'b_channel': b_channel,
        'gray': gray
    }

def calculate_monument_scores(features):
    """Calculate detection scores for each monument"""
    scores = {}
    
    # Extract features
    avg_color = features['avg_color']
    brightness = features['brightness']
    r_dom = features['r_dominance']
    g_dom = features['g_dominance']
    b_dom = features['b_dominance']
    edge_density = features['edge_density']
    texture_var = features['texture_variance']
    aspect_ratio = features['aspect_ratio']
    
    # Gateway of India: Brownish/warm tones, medium brightness, structured
    gateway_score = 0.0
    if 100 < avg_color[0] < 180:  # Red channel in brown range
        gateway_score += 0.25
    if 80 < avg_color[1] < 150:  # Green channel
        gateway_score += 0.20
    if r_dom > 1.0 and r_dom < 1.5:  # Red dominance but not extreme
        gateway_score += 0.20
    if 100 < brightness < 160:
        gateway_score += 0.15
    if 20 < edge_density < 60:  # Moderate edges for structure
        gateway_score += 0.20
    scores['Gateway of India'] = min(gateway_score, 1.0)
    
    # Taj Mahal: Very bright, white/cream, high brightness
    taj_score = 0.0
    if brightness > 180:  # Very bright
        taj_score += 0.30
    if avg_color[0] > 200 and avg_color[1] > 200 and avg_color[2] > 200:  # Very white
        taj_score += 0.25
    if r_dom < 1.1 and g_dom < 1.1 and b_dom < 1.1:  # Balanced colors
        taj_score += 0.20
    if contrast < 40:  # Low contrast for smooth white
        taj_score += 0.15
    if 20 < edge_density < 50:  # Moderate edges
        taj_score += 0.10
    scores['Taj Mahal'] = min(taj_score, 1.0)
    
    # Hawa Mahal: Pink/red tones, intricate details
    hawa_score = 0.0
    if r_dom > 1.1:  # Strong red dominance
        hawa_score += 0.25
    if avg_color[0] > 140:  # High red channel
        hawa_score += 0.20
    if avg_color[0] > avg_color[2]:  # Red > Blue
        hawa_score += 0.20
    if 120 < brightness < 180:  # Medium-high brightness
        hawa_score += 0.15
    if texture_var > 1000:  # High texture for intricate details
        hawa_score += 0.20
    scores['Hawa Mahal'] = min(hawa_score, 1.0)
    
    # Sardar Patel Statue: Dark colors, tall aspect ratio
    sardar_score = 0.0
    if avg_color[0] < 100:  # Dark red channel
        sardar_score += 0.20
    if brightness < 120:  # Dark overall
        sardar_score += 0.25
    if b_dom < 0.9:  # Low blue (dark)
        sardar_score += 0.20
    if aspect_ratio > 0.8:  # Tall/vertical
        sardar_score += 0.20
    if edge_density > 30:  # High edges for silhouette
        sardar_score += 0.15
    scores['Sardar Patel Statue'] = min(sardar_score, 1.0)
    
    # Mysore Palace: Golden/warm tones, ornate
    mysore_score = 0.0
    if g_dom > 1.0 and g_dom < 1.3:  # Golden tone
        mysore_score += 0.25
    if avg_color[1] > 120:  # Good green channel
        mysore_score += 0.20
    if avg_color[0] > 110:  # Warm red
        mysore_score += 0.15
    if 140 < brightness < 180:  # Medium-bright
        mysore_score += 0.15
    if texture_var > 800:  # High texture for ornate details
        mysore_score += 0.25
    scores['Mysore Palace'] = min(mysore_score, 1.0)
    
    return scores

def detect_monument(image):
    """Detect monument in image using advanced feature extraction"""
    features = extract_advanced_features(image)
    scores = calculate_monument_scores(features)
    
    best_monument = max(scores, key=scores.get)
    confidence = scores[best_monument]
    
    return {
        'monument': best_monument,
        'confidence': confidence,
        'scores': scores,
        'timestamp': datetime.now(),
        'features': features
    }

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    input_mode = st.radio(
        "Select Input Source",
        ["📤 Upload Image", "📷 Camera Capture"]
    )
    
    confidence_threshold = st.slider(
        "Confidence Threshold", 0.0, 1.0, 0.5, 0.05
    )
    
    st.markdown("---")
    st.markdown("### 🏛️ Supported Monuments")
    for monument, info in MONUMENTS_DB.items():
        st.markdown(f"**{monument}**\n📍 {info['location']}")

# Main content
st.markdown("# 🏛️ Indian Monuments Detection")
st.markdown("### AI-Powered Monument Recognition with Advanced Image Analysis")

col_input, col_results = st.columns(2)

with col_input:
    st.markdown("### 📸 Input Image")
    image_data = None
    
    if input_mode == "📤 Upload Image":
        uploaded_file = st.file_uploader(
            "Choose a monument image",
            type=["jpg", "jpeg", "png"]
        )
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
        
        # Count detections above threshold
        detections_above_threshold = [s for s in result['scores'].values() if s >= confidence_threshold]
        
        if confidence >= confidence_threshold:
            st.success(f"✅ {len(detections_above_threshold)} monument(s) detected!")
            
            st.markdown(f"""
            ### 🏛️ Detection #1
            **Monument:** {monument} 
            **Confidence:** {confidence*100:.1f}% 
            **Location:** {MONUMENTS_DB[monument]['location']} 
            **Status:** {'High' if confidence > 0.8 else 'Medium' if confidence > 0.6 else 'Low'}
            """)
            
            st.markdown("#### Confidence Breakdown:")
            for mon, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
                if score >= confidence_threshold:
                    bar_width = int(score * 30)
                    st.write(f"{mon}: {'█' * bar_width}{'░' * (30-bar_width)} {score*100:.1f}%")
            
            info = MONUMENTS_DB[monument]
            st.markdown(f"### 📍 Monument Information")
            st.info(info['description'])
        else:
            st.warning(f"⚠️ No monuments detected with confidence ≥ {confidence_threshold*100:.0f}%")
            st.info("Try uploading a clearer image or lowering the confidence threshold.")
            
            # Show all scores
            st.markdown("#### All Detection Scores:")
            for mon, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
                bar_width = int(score * 30)
                st.write(f"{mon}: {'█' * bar_width}{'░' * (30-bar_width)} {score*100:.1f}%")
    else:
        st.info("👉 Upload an image or capture from camera to start detection!")

st.markdown("---")
st.markdown("""<p style="text-align: center;">🏛️ Monument Detection App | Powered by Streamlit & Advanced Image Analysis <br>Made with ❤️ for Indian Heritage</p>""", unsafe_allow_html=True)
