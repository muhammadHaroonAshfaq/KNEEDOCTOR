"""Auth screens: Splash, Welcome, Sign Up, Login."""
import streamlit as st
import time
from design import card, badge, go, PRIMARY, MUTED, TEXT, BORDER, GREEN


def screen_splash():
    st.html("""
    <style>
    .splash-wrap { display:flex; flex-direction:column; align-items:center;
                   justify-content:center; min-height:70vh; text-align:center; }
    @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }
    .splash-icon { font-size:5rem; animation:pulse 1.5s ease-in-out infinite; margin-bottom:1rem; }
    .splash-title { font-size:2.4rem; font-weight:800; color:#2B6CB0; margin:0; }
    .splash-sub   { font-size:1rem; color:#718096; margin-top:0.4rem; }
    @keyframes bar { from{width:0} to{width:100%} }
    .splash-bar-wrap { width:200px; height:4px; background:#E2E8F0; border-radius:2px; margin-top:2rem; overflow:hidden; }
    .splash-bar { height:4px; background:#2B6CB0; border-radius:2px; animation:bar 2s linear forwards; }
    </style>
    <div class='splash-wrap'>
      <div class='splash-icon'>🦵</div>
      <div class='splash-title'>KneeDoc AI</div>
      <div class='splash-sub'>Your personal knee rehabilitation coach</div>
      <div class='splash-bar-wrap'><div class='splash-bar'></div></div>
    </div>
    """)
    time.sleep(2)
    profile = st.session_state.get("patient_profile", {})
    go("welcome" if not profile.get("onboarding_done") else "home")


def screen_welcome():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("""
        <div style='text-align:center;padding:3rem 0 2rem;'>
          <div style='font-size:4rem;'>🦵</div>
          <h1 style='font-size:2.2rem;font-weight:800;margin:0.5rem 0;'>KneeDoc AI</h1>
          <p style='color:#718096;font-size:1.05rem;'>Personalised AI therapy for knee arthritis recovery</p>
        </div>
        """, unsafe_allow_html=True)

        card("""
        <div style='line-height:2;font-size:0.93rem;'>
          ✅ &nbsp;Clinical-grade exercise plans<br>
          🧠 &nbsp;RAG AI coach powered by medical KB<br>
          📈 &nbsp;Pain &amp; ROM progress tracking<br>
          🩺 &nbsp;Doctor-ready progress reports<br>
          🚨 &nbsp;Flare-up emergency protocol
        </div>
        """)

        if st.button("🚀  Get Started", use_container_width=True):
            go("signup")

        st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
        if st.button("I Already Have an Account", use_container_width=True):
            go("login")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align:center;color:{MUTED};font-size:0.75rem;margin-top:1rem;'>⚠️ Not a medical device. Always consult your physician.</p>", unsafe_allow_html=True)


def screen_signup():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("<div style='padding-top:1.5rem;'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>Create Your Account</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:{MUTED};margin-bottom:1.2rem;'>Set up your profile to begin your recovery journey</p>", unsafe_allow_html=True)

        with st.form("signup_form"):
            name     = st.text_input("Full Name", placeholder="Sarah Johnson")
            email    = st.text_input("Email", placeholder="sarah@email.com")
            api_key  = st.text_input("OpenAI API Key", type="password", placeholder="sk-proj-...",
                                     help="Required to power the AI coach. Never stored on servers.")
            password = st.text_input("Password", type="password", placeholder="Min. 8 characters")
            st.markdown("""<div style='font-size:0.82rem;color:#718096;margin:0.3rem 0;'>
            By continuing, you agree to our Terms &amp; Privacy Policy.</div>""", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if not name or not email or not api_key.startswith("sk-") or len(password) < 6:
                st.error("Please fill in all fields. API key must start with 'sk-'.")
            else:
                st.session_state.user_name    = name
                st.session_state.user_email   = email
                st.session_state.api_key      = api_key
                st.session_state.patient_profile = {"name": name.split()[0]}
                with st.spinner("Setting up your account…"):
                    _init_rag(api_key)
                go("onboarding")

        st.markdown("<div style='text-align:center;margin-top:0.8rem;'>", unsafe_allow_html=True)
        if st.button("Already have an account? Login", use_container_width=False):
            go("login")
        st.markdown("</div>", unsafe_allow_html=True)


def screen_login():
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("<div style='padding-top:1.5rem;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>Welcome Back</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:{MUTED};margin-bottom:1.2rem;'>Log in to continue your recovery</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            email   = st.text_input("Email", placeholder="sarah@email.com")
            api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-proj-...")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not api_key.startswith("sk-"):
                st.error("Please enter your email and a valid API key (sk-…).")
            else:
                st.session_state.user_email = email
                st.session_state.api_key    = api_key
                name = st.session_state.get("user_name", email.split("@")[0].capitalize())
                st.session_state.patient_profile = st.session_state.get("patient_profile", {"name": name})
                with st.spinner("Logging in…"):
                    _init_rag(api_key)
                go("home")

        st.markdown("<div style='text-align:center;margin-top:0.8rem;'>", unsafe_allow_html=True)
        if st.button("← Back to Welcome"):
            go("welcome")
        st.markdown("</div>", unsafe_allow_html=True)


def _init_rag(api_key: str):
    if not st.session_state.get("rag_initialized"):
        try:
            from data_loader import KneeArthritisDataLoader
            from rag_model import KneeArthritisRAG
            loader = KneeArthritisDataLoader(data_dir="data")
            loader.load_all()
            st.session_state.rag = KneeArthritisRAG(loader, api_key)
            st.session_state.rag_initialized = True
        except Exception as e:
            st.warning(f"AI coach initialisation issue: {e}")
