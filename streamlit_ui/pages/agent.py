import streamlit as st
# from streamlit_card import card
from api_client import call_agent

def show_agent_page(key_prefix="agent"):
    st.title("🤖 Please ask your query to AI")
    st.write("Run the autonomous research agent on your ingested content.")

    # Query input with unique key
    query = st.text_area(
        "🔎 Enter your query",
        placeholder="e.g., Summarize uploaded content",
        key=f"{key_prefix}_query"
    )

    if st.button("🚀 Submit", key=f"{key_prefix}_button", use_container_width=True):
        if not query.strip():
            st.error("Please enter a query first.")
        else:
            with st.spinner("Work in progress..."):
                try:
                    response = call_agent(query)
                    if response.status_code == 200:
                        data = response.json()
                        st.write(data)

                        # if "steps" in data:
                        #     st.subheader("🪜 Agent Steps")
                        #     for idx, step in enumerate(data["steps"], start=1):
                        #         st.markdown(f"**Step {idx}:** {step}")

                        # Final Result card
                        # if "result" in data:
                        #     st.subheader("📌 Final Result")
                        #     card(
                        #         title="Agent Output",
                        #         text=data["result"],
                        #         key=f"{key_prefix}_result_card"
                        #     )

                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"❌ Something went wrong: {e}")
