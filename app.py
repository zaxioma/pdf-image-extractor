import streamlit as st
import fitz  # PyMuPDF
import requests
import io
from PIL import Image

st.set_page_config(page_title="Ekstrak Gambar dari PDF", layout="wide")
st.title("📄🔍 Ekstraksi Gambar dari PDF Koran Lama")

# Contoh URL default
default_url = "https://opac.perpusnas.go.id/uploaded_files/dokumen_isi3/Terbitan%20Berkala/CHERIBONSCHE_COURANT_1925_08_19_001.pdf"
pdf_url = st.text_input("Masukkan URL PDF:", value=default_url)

if st.button("Proses PDF"):
    try:
        st.info("Mengunduh PDF dari URL...")
        response = requests.get(pdf_url)
        response.raise_for_status()

        doc = fitz.open(stream=response.content, filetype="pdf")
        st.success(f"PDF berhasil dimuat. Total halaman: {len(doc)}")

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

                # Tombol unduh
                st.download_button(
                    label="💾 Unduh gambar ini",
                    data=image_bytes,
                    file_name=f"halaman_{page_num+1}_gambar_{img_index+1}.{image_ext}",
                    mime=f"image/{image_ext}"
                )

                image_count += 1

        if image_count == 0:
            st.warning("Tidak ditemukan gambar dalam PDF ini.")
        else:
            st.success(f"Total gambar ditemukan: {image_count}")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
