import streamlit as st
from api_client import summarize_content

def show_summarize_page(key_prefix="summarize"):
    st.title("📝 Summarize Content")

    # Add key_prefix to make keys unique
    summarize_content_id = st.text_input(
        "Enter Content ID which you want to summarize", key=f"{key_prefix}_content_id"
    )

    if st.button("Summarize", key=f"{key_prefix}_button"):
        if not summarize_content_id:
            st.warning("⚠️ Please provide a content ID")
            return

        with st.spinner("Generating summary..."):
            res = summarize_content(summarize_content_id)

        if res.ok:
            summary = res.json().get("summary", "No summary returned")
            st.success("✅ Summary generated")
            st.write(summary)
        else:
            st.error(f"❌ Summarization failed: {res.text}")
