import streamlit as st

st.markdown("""
<h1 style='text-align:center;'>Welcome to KneeDoc AI 🦵</h1>
<p style='text-align:center;color:#aaa;'>Your personal AI-powered companion for managing knee arthritis through science-backed exercises.</p>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920243.png", width=220)
with col2:
    st.subheader("🌟 Why KneeDoc AI?")
    st.write("""
    - Personalized exercise plans powered by AI  
    - Monitors your pain, progress, and flexibility  
    - Developed with physiotherapy expertise  
    - Easy to use anywhere, anytime  
    """)

st.markdown("---")
st.success("✅ Get started by navigating to the 'AI Coach' section to build your first plan!")
