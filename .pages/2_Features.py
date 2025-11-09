import streamlit as st

st.title("⚙️ Features")
st.write("Explore the features that make KneeDoc AI your smart rehab companion:")

features = [
    {"emoji": "🤖", "title": "AI Chat Coach", "desc": "Get intelligent guidance through your recovery journey."},
    {"emoji": "📋", "title": "Custom Exercise Plans", "desc": "Personalized routines for your knee condition."},
    {"emoji": "📈", "title": "Progress Tracker", "desc": "Visualize improvements over time."},
    {"emoji": "🔒", "title": "Data Privacy", "desc": "Your medical details stay secure and private."},
]

cols = st.columns(2)
for i, feat in enumerate(features):
    with cols[i % 2]:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
        border-radius:12px;padding:1rem;margin:.5rem 0;">
        <h3>{feat['emoji']} {feat['title']}</h3>
        <p style="color:#aaa;">{feat['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
