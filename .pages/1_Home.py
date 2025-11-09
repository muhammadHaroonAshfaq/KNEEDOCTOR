import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Home - KneeDoc AI", page_icon="🏠", layout="wide")

# --- Styling ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #000000 0%, #001a33 100%) !important;
    color: white !important;
}
h1, h2, h3, h4, h5, h6 { color: white !important; }
p, div, span, label { color: #cccccc !important; }
.card {
    background: rgba(0, 51, 102, 0.4);
    border: 1px solid rgba(0,153,255,0.3);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 10px rgba(0,153,255,0.2);
}
.highlight {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stButton > button {
    background: linear-gradient(135deg, #0077ff, #33ccff);
    color: white; border: none; border-radius: 10px;
    padding: 0.8rem 2rem; font-weight: 600; font-size: 1rem;
    transition: all 0.3s ease; width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(0,153,255,0.8);
}
</style>
""", unsafe_allow_html=True)

# --- Content ---
st.markdown("<h1 class='highlight' style='text-align:center;'>Welcome to KneeDoc AI 🦵</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa;'>Your intelligent physiotherapy assistant for knee arthritis relief and mobility improvement.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.markdown("<div class='card'><h3>Personalized Care</h3><p>AI-generated exercise routines tailored to your knee condition and goals.</p></div>", unsafe_allow_html=True)
with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1865/1865269.png", width=100)
    st.markdown("<div class='card'><h3>Safe & Effective</h3><p>Every exercise is reviewed for safety and designed for gradual improvement.</p></div>", unsafe_allow_html=True)
with col3:
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920243.png", width=100)
    st.markdown("<div class='card'><h3>Track Your Progress</h3><p>Monitor your progress and improvement over time with simple analytics.</p></div>", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

colA, colB = st.columns([2, 1])
with colA:
    st.subheader("💬 Quick Start")
    st.write("You can jump right in by heading to the **AI Coach** page and describing your symptoms. The AI will build a safe, personalized plan.")
    if st.button("Go to AI Coach 🚀", use_container_width=True):
        st.switch_page("pages/4_Coach.py")

with colB:
    st.subheader("📅 Session Info")
    st.write(f"🕐 Started: {datetime.now().strftime('%I:%M %p')}")
    st.write(f"💬 Messages in this session: {len(st.session_state.get('messages', []))}")

st.markdown("<hr>", unsafe_allow_html=True)
st.info("⚠️ Always consult your healthcare provider before beginning new exercises.")
