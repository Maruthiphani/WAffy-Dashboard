import streamlit as st
from app.agents.llm_agent import llm_agent

st.set_page_config(layout="wide")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Layout ===
col1, col2 = st.columns([1, 1])

# === LEFT PANEL: Chat input and history ===
with col1:
    st.markdown("### 💬 Customer Message")

    with st.form("chat_form"):
        user_input = st.text_input("Type a message", key="input")
        submit = st.form_submit_button("Send")

        if submit and user_input:
            st.session_state.chat_history.append(user_input)

    st.markdown("---")
    st.markdown("#### Chat History")
    for msg in st.session_state.chat_history:
        st.markdown(f"- {msg}")

# === RIGHT PANEL: LLM Response ===
with col2:
    st.markdown("### 📦 Extracted Information")

    result = None
    if submit and user_input:
        result = llm_agent.analyze(user_input, st.session_state.chat_history[:-1])

    if result:
        st.markdown(f"**Category:** `{result.get('category', 'N/A')}`")
        st.markdown(f"**Priority:** `{result.get('priority', 'N/A')}`")
        st.markdown(f"**Conversation Status:** `{result.get('conversation_status', 'N/A')}`")

        extracted = result.get("extracted_info", {})
        if extracted:
            st.markdown("**Extracted Info:**")

            products = extracted.get("products", [])
            if products:
                st.markdown("**Products:**")
                for p in products:
                    item = p.get("item", "❓").title()
                    qty = p.get("quantity", "?")
                    details = p.get("details")
                    notes = p.get("notes")
                    msg = f"- **{item}** — `{qty}`"
                    if details:
                        msg += f" _(Details: {details})_"
                    if notes:
                        msg += f" _(Note: {notes})_"
                    st.markdown(msg)

            # Display any other fields
            for key, value in extracted.items():
                if key != "products":
                    key_label = key.replace("_", " ").title()
                    st.markdown(f"- **{key_label}:** `{value}`")
        else:
            st.info("No structured info extracted.")
