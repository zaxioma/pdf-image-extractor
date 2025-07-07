import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

st.set_page_config(page_title="Ekstrak Gambar dari PDF", layout="wide")
st.title("📄🔍 Ekstraksi Gambar dari PDF Koran Lama")

uploaded_file = st.file_uploader("Unggah file PDF koran lama", type="pdf")

if uploaded_file is not None:
    try:
        st.success("PDF berhasil diunggah.")
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        image_count = 0

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            images = page.get_images(full=True)

            if images:
                st.subheader(f"Halaman {page_num + 1}")
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption=f"Gambar {image_count + 1} (halaman {page_num + 1})", use_column_width=True)

                st.download_button(
                    label="💾 Unduh gambar ini",
                    data=image_bytes,
                    file_name=f"halaman_{page_num+1}_gambar_{img_index+1}.{image_ext}",
                    mime=f"image/{image_ext}"
                )

                image_count += 1

        if image_count == 0:
            st.warning("Tidak ditemukan gambar dalam PDF.")
        else:
            st.success(f"Total gambar ditemukan: {image_count}")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
