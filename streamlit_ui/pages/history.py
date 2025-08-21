import streamlit as st
from api_client import fetch_history

def show_history_page(key_prefix="history"):
    st.title("📜 History")

    with st.spinner("Fetching history..."):
        res = fetch_history()
    if res.ok:
        history = res.json()
        if history:
            st.success("✅ History fetched")
            for item in history:
                st.markdown(f"**ID:** {item['id']}  \n📄 {item['content'][:200]}...")
        else:
            st.info("ℹ️ No history available yet")
    else:
        st.error(f"❌ Could not fetch history: {res.text}")
