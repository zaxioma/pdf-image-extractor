import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import io

st.title("Segmentasi Gambar Otomatis dari PDF (tanpa Poppler)")

uploaded_file = st.file_uploader("Unggah PDF", type="pdf")

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        st.subheader(f"Halaman {page_num + 1}")
        st.image(img, caption="Halaman penuh")

        img_np = np.array(img.convert("L"))
        _, thresh = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        count = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 100 and h > 100:
                cropped = img.crop((x, y, x + w, y + h))
                st.image(cropped, caption=f"Segmen {count + 1} - {w}x{h}", use_column_width=True)

                buf = io.BytesIO()
                cropped.save(buf, format="PNG")
                st.download_button(f"Unduh Segmen {count + 1}", data=buf.getvalue(),
                                   file_name=f"segmen_{page_num + 1}_{count + 1}.png",
                                   mime="image/png")
                count += 1

        if count == 0:
            st.warning("Tidak ada blok gambar cukup besar pada halaman ini.")
