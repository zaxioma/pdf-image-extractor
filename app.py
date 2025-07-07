import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="Segmentasi Gambar dari PDF Koran", layout="wide")
st.title("📰📸 Segmentasi Gambar Otomatis dari PDF Koran Lama")

uploaded_file = st.file_uploader("Unggah PDF hasil scan koran lama", type="pdf")

MIN_WIDTH = 100
MIN_HEIGHT = 100

if uploaded_file:
    with st.spinner("Mengonversi halaman PDF ke gambar..."):
        pages = convert_from_bytes(uploaded_file.read(), dpi=300)

    st.success(f"{len(pages)} halaman berhasil dikonversi.")

    for page_num, page_image in enumerate(pages):
        st.subheader(f"🧾 Halaman {page_num + 1}")
        st.image(page_image, caption="Gambar Halaman Penuh", use_column_width=True)

        # Convert PIL image to OpenCV format
        img_gray = np.array(page_image.convert("L"))
        _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        segmen_ke = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > MIN_WIDTH and h > MIN_HEIGHT:
                cropped = page_image.crop((x, y, x + w, y + h))
                st.image(cropped, caption=f"🧩 Segmen {segmen_ke + 1} (WxH: {w}x{h})", use_column_width=True)

                # Tombol unduh tiap segmen
                img_bytes = io.BytesIO()
                cropped.save(img_bytes, format="PNG")
                st.download_button(
                    label=f"💾 Unduh Segmen {segmen_ke + 1}",
                    data=img_bytes.getvalue(),
                    file_name=f"halaman_{page_num + 1}_segmen_{segmen_ke + 1}.png",
                    mime="image/png"
                )

                segmen_ke += 1

        if segmen_ke == 0:
            st.warning("Tidak ada blok gambar cukup besar terdeteksi pada halaman ini.")
