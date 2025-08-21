import streamlit as st
from api_client import ask_question

def show_ask_page(key_prefix="ask"):
    st.title("❓ Ask a Question")
    ask_content_id = st.text_input(
        "Enter Content ID", key=f"{key_prefix}_content_id"
    )
    query = st.text_area(
        "Enter your question", key=f"{key_prefix}_query"
    )

    if st.button("Ask", key=f"{key_prefix}_button"):
        if not ask_content_id or not query:
            st.warning("⚠️ Please provide both content ID and query")
            return

        with st.spinner("Thinking..."):
            res = ask_question(ask_content_id, query)

        if res.ok:
            answer = res.json().get("answer", "No answer returned")
            st.success("✅ Answer found")
            st.write(answer)
        else:
            st.error(f"❌ Question failed: {res.text}")
