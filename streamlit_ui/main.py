import streamlit as st
from pages.upload import show_upload_page
from pages.summarize import show_summarize_page
from pages.ask import show_ask_page
from pages.history import show_history_page
from pages.agent import show_agent_page


st.set_page_config(
    page_title="Thynkr", 
    layout="wide", 
    initial_sidebar_state="collapsed"
    )

# Hide sidebar completely
hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
"""

st.markdown(hide_sidebar_style, unsafe_allow_html=True)

pages = ["📤 Upload", "❓ Ask", "AI Explanation"]  # "📝 Summarize", "📜 History", 
tab = st.radio("", pages, index=0,  horizontal=True)

if tab == "📤 Upload":
    show_upload_page(key_prefix="upload")
elif tab == "📝 Summarize":
    show_summarize_page(key_prefix="summarize")
elif tab == "❓ Ask":
    show_ask_page(key_prefix="ask")
elif tab == "📜 History":
    show_history_page(key_prefix="history")
elif tab == "AI Explanation":
    show_agent_page(key_prefix="agent")
