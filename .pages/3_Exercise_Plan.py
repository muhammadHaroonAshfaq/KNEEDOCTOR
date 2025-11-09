import streamlit as st

st.title("💪 Exercise Plan")

if "rag" not in st.session_state or not st.session_state.rag_initialized:
    st.warning("Please log in again from the home page to initialize the model.")
else:
    st.subheader("Your Personalized Knee Exercise Plan")
    plan = st.session_state.rag.create_exercise_plan(
        st.session_state.rag.loader.patient_profile if hasattr(st.session_state.rag, "loader") else {},
        {}
    )
    st.json(plan)
