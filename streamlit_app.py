"""KneeDoc AI — Main application router (production-ready 42-screen build)."""
import streamlit as st
from datetime import datetime

# ── Page config — must be first Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="KneeDoc AI — Knee Therapy Coach",
    page_icon="🦵",
    layout="wide",
    initial_sidebar_state="expanded",  # always expanded; hidden via CSS on auth pages
)


# ── Design system ─────────────────────────────────────────────────────────────
from design import inject_css, go, PRIMARY, MUTED, TEXT, BORDER
inject_css()

# ── Session state defaults ────────────────────────────────────────────────────
_defaults = {
    "api_key":              None,
    "user_name":            "",
    "user_email":           "",
    "rag":                  None,
    "rag_initialized":      False,
    "current_page":         "splash",
    "therapy_page":         "plan",
    "progress_page":        "dashboard",
    "patient_profile":      {},
    "session_plan":         [],
    "pain_log":             [],
    "rom_log":              [],
    "flare_log":            [],
    "completed_sessions":   0,
    "chat_messages":        [],
    "saved_answers":        [],
    "ob_step":              1,
    "active_ex_idx":        0,
    "checkin_done":         False,
    "clinical_report":      "",
    "preview_ex":           {},
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# ── Hide sidebar on auth/onboarding pages, show on main app ──────────────────
_NO_SIDEBAR_PAGES = ("splash", "welcome", "signup", "login", "onboarding")
if st.session_state.get("current_page", "splash") in _NO_SIDEBAR_PAGES:
    st.html("""<style>
    section[data-testid="stSidebar"],
    button[data-testid="collapsedControl"] { display:none !important; }
    </style>""")


# ── Sidebar navigation (main app only) ───────────────────────────────────────
def _sidebar():
    profile = st.session_state.patient_profile
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:1rem 0 0.5rem;text-align:center;'>
          <div style='font-size:2rem;'>🦵</div>
          <div style='font-weight:800;font-size:1.1rem;color:{PRIMARY};'>KneeDoc AI</div>
          <div style='font-size:0.78rem;color:{MUTED};'>Recovery Coach</div>
        </div>
        <hr style='border-color:{BORDER};margin:0.5rem 0;'>
        """, unsafe_allow_html=True)

        # User summary
        pain  = profile.get("pain_level", "—")
        stage = profile.get("stage","—")
        streak= profile.get("streak", 0)
        st.markdown(f"""
        <div style='background:#F7FAFC;border-radius:12px;padding:0.8rem;margin-bottom:0.8rem;font-size:0.85rem;'>
          <strong>{profile.get("name","User")}</strong><br>
          <span style='color:{MUTED};'>{stage} · Pain {pain}/10 · 🔥{streak}</span>
        </div>""", unsafe_allow_html=True)

        pages = [
            ("🏠", "Home",     "home"),
            ("🦵", "Therapy",  "therapy"),
            ("📊", "Progress", "progress"),
            ("🤖", "AI Coach", "coach"),
            ("👤", "Profile",  "profile"),
        ]
        cur = st.session_state.current_page
        for icon, label, key in pages:
            active = cur == key
            bg = f"background:#EBF8FF;color:{PRIMARY};font-weight:700;" if active else ""
            col = st.columns([1,4])[0]
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("<hr style='border-color:#E2E8F0;margin:1rem 0 0.5rem;'>", unsafe_allow_html=True)

        # Weather/flare toggle
        weather = st.toggle("🌧️ Flare / Weather Mode",
                            value=profile.get("weather_mode", False),
                            help="Reduces session intensity on difficult days")
        profile["weather_mode"] = weather
        st.session_state.patient_profile = profile

        st.markdown(f"<p style='font-size:0.7rem;color:{MUTED};text-align:center;margin-top:1rem;'>⚠️ Not a medical device.<br>Consult your physician.</p>",
                    unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.current_page

# Auth pages (no sidebar)
if page == "splash":
    from screens.auth import screen_splash
    screen_splash()

elif page == "welcome":
    from screens.auth import screen_welcome
    screen_welcome()

elif page == "signup":
    from screens.auth import screen_signup
    screen_signup()

elif page == "login":
    from screens.auth import screen_login
    screen_login()

# Onboarding (no sidebar)
elif page == "onboarding":
    from screens.onboarding import screen_onboarding
    screen_onboarding()

# Main app pages (with sidebar — naturally shown since initial_sidebar_state="expanded")
elif page in ("home","therapy","progress","coach","profile"):
    if not st.session_state.api_key:
        go("welcome")
    else:
        _sidebar()

        if page == "home":
            from screens.home import screen_home
            screen_home()
        elif page == "therapy":
            from screens.therapy import screen_therapy
            screen_therapy()
        elif page == "progress":
            from screens.progress import screen_progress
            screen_progress()
        elif page == "coach":
            from screens.coach import screen_coach
            screen_coach()
        elif page == "profile":
            from screens.profile import screen_profile
            screen_profile()

else:
    # Fallback
    go("splash")
