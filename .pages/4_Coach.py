import streamlit as st
from datetime import datetime
import time

st.title("🤖 AI Coach")

if "rag" not in st.session_state or not st.session_state.rag_initialized:
    st.warning("Please go back to the login page and enter your API key.")
else:
    rag = st.session_state.rag

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Hi! I'm your KneeDoc AI Coach. Tell me a bit about your knee condition to begin."}]

    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f"🤖 **KneeDoc AI:** {m['content']}")
        else:
            st.markdown(f"👤 **You:** {m['content']}")

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("KneeDoc AI is thinking..."):
            time.sleep(1)
            try:
                profile = rag.extract_patient_info(user_input)
                context = rag.retrieve_context(user_input, profile)
                response = rag.generate_response(user_input, profile, context, st.session_state.messages)
            except Exception as e:
                response = f"⚠️ Error generating response: {e}"

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.experimental_rerun()
