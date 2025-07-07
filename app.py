import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="Segmentasi Gambar dari PDF", layout="wide")
st.title("📰📸 Segmentasi Gambar Otomatis dari PDF Scan Koran")

uploaded_file = st.file_uploader("Unggah PDF", type="pdf")

MIN_WIDTH, MIN_HEIGHT = 100, 100

def segment_image(pil_image):
    gray = np.array(pil_image.convert("L"))

    # Naikkan kontras dengan adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 15
    )

    # Morphological closing untuk mengisi celah di dalam area
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Temukan kontur
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_num in range(len(doc)):
        st.subheader(f"📄 Halaman {page_num + 1}")
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(image, caption="Gambar Halaman Utuh", use_column_width=True)

        contours = segment_image(image)
        found = 0

        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > MIN_WIDTH and h > MIN_HEIGHT and w < pix.width * 0.9 and h < pix.height * 0.9:
                cropped = image.crop((x, y, x + w, y + h))
                st.image(cropped, caption=f"🧩 Segmen {i + 1} (WxH: {w}x{h})", use_column_width=True)

                buf = io.BytesIO()
                cropped.save(buf, format="PNG")
                st.download_button(
                    f"💾 Unduh Segmen {i + 1}",
                    data=buf.getvalue(),
                    file_name=f"halaman_{page_num + 1}_segmen_{i + 1}.png",
                    mime="image/png"
                )
                found += 1

        if found == 0:
            st.warning("Tidak ada segmen gambar terdeteksi.")
