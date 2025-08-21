import streamlit as st
from api_client import upload_file

def show_upload_page(key_prefix="upload"):
    st.title("📤 Upload Content")

    # File uploader with unique key
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        key=f"{key_prefix}_file_uploader"
    )

    if uploaded_file is not None:
        if st.button("Upload", key=f"{key_prefix}_upload_button"):
            with st.spinner("Uploading..."):
                res = upload_file(uploaded_file)

            if res.ok:
                st.success("✅ File uploaded successfully!")
                st.json(res.json())
            else:
                st.error(f"❌ Upload failed: {res.text}")
