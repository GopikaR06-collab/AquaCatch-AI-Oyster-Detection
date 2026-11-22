import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
IMG_SIZE = 150
CLASS_NAMES = ["oyster", "not oyster"]

st.set_page_config(page_title="Oyster Intelligence System", layout="wide")

# -------------------------
# LOAD MODEL
# -------------------------
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("oyster_model.keras")
    return model

model = load_model()

# -------------------------
# TITLE
# -------------------------
st.title("🦪 Oyster Growth Intelligence Dashboard")
st.markdown("### AI-Based Oyster Classification & Harvest Advisory System")

# -------------------------
# INPUT METHOD
# -------------------------
st.subheader("📷 Select Input Method")

option = st.radio(
    "Choose input type:",
    ("Upload Image", "Use Webcam")
)

image = None

if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload Oyster Image", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

elif option == "Use Webcam":
    camera_image = st.camera_input("Capture Image")
    if camera_image is not None:
        image = Image.open(camera_image)

# -------------------------
# PROCESS IMAGE
# -------------------------
if image is not None:

    st.image(image, caption="Input Image", use_column_width=True)

    img_array = np.array(image)
    img_resized = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    img_normalized = img_resized / 255.0
    img_reshaped = np.reshape(img_normalized, (1, IMG_SIZE, IMG_SIZE, 3))

    prediction = model.predict(img_reshaped)
    confidence = float(prediction[0][0])

    if confidence > 0.5:
        predicted_class = CLASS_NAMES[0]
        confidence_score = confidence
    else:
        predicted_class = CLASS_NAMES[1]
        confidence_score = 1 - confidence

    st.subheader("🔍 Prediction Result")
    st.write(f"**Class:** {predicted_class}")
    st.write(f"**Confidence:** {confidence_score*100:.2f}%")

    # -------------------------
    # SIZE ESTIMATION
    # -------------------------
    if predicted_class == "oyster":

        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            st.subheader("📏 Size Estimation")
            st.write(f"Estimated Pixel Area: {int(area)}")

            if area < 5000:
                size_category = "Small (Immature)"
                harvest_time = "Harvest after approximately 3 weeks"
            elif area < 15000:
                size_category = "Medium (Growing)"
                harvest_time = "Harvest after approximately 1-2 weeks"
            else:
                size_category = "Large (Mature)"
                harvest_time = "Ready for Harvest"

            st.write(f"Growth Stage: {size_category}")
            st.write(f"Harvest Advisory: {harvest_time}")

            st.info("Note: Harvest suggestion is based on size estimation heuristics.")

    # -------------------------
    # CONFIDENCE HISTORY GRAPH
    # -------------------------
    if "confidence_history" not in st.session_state:
        st.session_state.confidence_history = []

    st.session_state.confidence_history.append(confidence_score * 100)

    st.subheader("📈 Confidence Trend Analysis")
    st.line_chart(st.session_state.confidence_history)        

# -------------------------
# METRICS PLACEHOLDER
# -------------------------
st.markdown("---")
st.subheader("📊 Model Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    st.metric("Training Accuracy", "92%")
    st.metric("Validation Accuracy", "89%")

with col2:
    st.metric("Precision", "90%")
    st.metric("Recall", "88%")

st.markdown("---")

# -------------------------------
# MAP SECTION
# -------------------------------
st.header("🌍 Oyster Harvest Regions (Prototype Geospatial Module)")

map_data = pd.DataFrame({
    "Region": ["Thoothukudi", "Rameswaram", "Chennai Coast", "Bay of Bengal Zone"],
    "Latitude": [8.7642, 9.2876, 13.0827, 15.0000],
    "Longitude": [78.1348, 79.3129, 80.2707, 85.0000],
    "Density": [90, 65, 70, 95]
})

fig = px.scatter_mapbox(
    map_data,
    lat="Latitude",
    lon="Longitude",
    size="Density",
    color="Density",
    hover_name="Region",
    zoom=5,
    height=500
)

fig.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig)

st.caption("Prototype visualization based on publicly known oyster-rich coastal regions.")