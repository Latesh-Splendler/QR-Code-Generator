import streamlit as st
import qrcode
import qrcode.image.svg
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import tempfile

# Function to generate QR Code
def generate_qr_code(data, fg_color, bg_color, logo=None):
    qr = qrcode.QRCode(
        version=1, box_size=10, border=5
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill=fg_color, back_color=bg_color).convert("RGB")
    
    if logo:
        logo = Image.open(logo)
        img_w, img_h = img.size
        logo = logo.resize((img_w // 4, img_h // 4))
        
        pos = ((img_w - logo.size[0]) // 2, (img_h - logo.size[1]) // 2)
        img.paste(logo, pos, logo if logo.mode == 'RGBA' else None)
    
    return img

# Function to scan QR code from image
def scan_qr_code(uploaded_file):
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data if data else "No QR Code detected."

# Streamlit UI
st.set_page_config(page_title="QR Code Generator & Scanner", layout="wide")
st.title("📱 QR Code Generator & Scanner")

# Sidebar for input options
st.sidebar.header("Generate QR Code")
data = st.sidebar.text_input("Enter text/URL:")
fg_color = st.sidebar.color_picker("Foreground Color", "#000000")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
logo = st.sidebar.file_uploader("Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

if st.sidebar.button("Generate QR Code"):
    if data:
        qr_img = generate_qr_code(data, fg_color, bg_color, logo)
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        st.image(qr_img, caption="Generated QR Code", use_column_width=False)
        st.download_button("Download QR Code", buf.getvalue(), file_name="qr_code.png", mime="image/png")
    else:
        st.sidebar.error("Please enter text or a URL.")

# Batch QR Code Generation
st.sidebar.header("Batch QR Code Generation")
uploaded_file = st.sidebar.file_uploader("Upload CSV (Column: data)", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if "data" in df.columns:
        zip_buffer = BytesIO()
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, row in df.iterrows():
                qr_img = generate_qr_code(row["data"], fg_color, bg_color)
                qr_img.save(f"{temp_dir}/qr_{i}.png", format="PNG")
            st.sidebar.success("Batch QR Codes Generated!")
    else:
        st.sidebar.error("CSV must have a 'data' column.")

# QR Code Scanner
st.header("📸 QR Code Scanner")
qr_file = st.file_uploader("Upload an image containing a QR Code", type=["png", "jpg", "jpeg"])
if qr_file:
    scanned_data = scan_qr_code(qr_file)
    st.image(qr_file, caption="Uploaded Image", use_column_width=False)
    st.success(f"Scanned Data: {scanned_data}")
