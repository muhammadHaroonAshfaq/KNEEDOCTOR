"""KneeDoc AI — CSS design system, shared helpers & constants."""
import streamlit as st


# ── Blueprint colour tokens ──────────────────────────────────────────────────
PRIMARY   = "#2B6CB0"
GREEN     = "#38A169"
RED       = "#E53E3E"
AMBER     = "#D69E2E"
BG        = "#F7FAFC"
CARD_BG   = "#FFFFFF"
TEXT      = "#1A202C"
MUTED     = "#718096"
BORDER    = "#E2E8F0"
LIGHT_BG  = "#EBF8FF"


def inject_css():
    st.html(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp {{
    font-family: 'Inter', sans-serif;
    background: {BG} !important;
    color: {TEXT} !important;
}}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background: transparent !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: #FFFFFF !important;
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

/* ── Typography ── */
h1,h2,h3,h4 {{ color:{TEXT} !important; font-weight:700 !important; letter-spacing:-0.01em; }}
p, label, span, div {{ color:{TEXT};font-size:1rem; }}

/* ── Cards ── */
.kd-card {{
    background:{CARD_BG};
    border:1px solid {BORDER};
    border-radius:16px;
    padding:1.3rem 1.5rem;
    margin-bottom:0.9rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s ease;
}}
.kd-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.1); }}
.kd-card-title {{ font-size:0.82rem; font-weight:600; color:{MUTED} !important; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.3rem; }}
.kd-card-value {{ font-size:2rem; font-weight:800; color:{TEXT} !important; line-height:1.1; }}
.kd-card-sub   {{ font-size:0.8rem; color:{MUTED} !important; margin-top:0.15rem; }}

/* ── Badges ── */
.badge {{ display:inline-block; padding:0.2rem 0.65rem; border-radius:20px; font-size:0.75rem; font-weight:600; margin-right:0.3rem; }}
.badge-blue  {{ background:#EBF8FF; color:{PRIMARY} !important; border:1px solid #BEE3F8; }}
.badge-green {{ background:#F0FFF4; color:{GREEN} !important;   border:1px solid #9AE6B4; }}
.badge-red   {{ background:#FFF5F5; color:{RED} !important;     border:1px solid #FEB2B2; }}
.badge-amber {{ background:#FFFFF0; color:{AMBER} !important;   border:1px solid #FAF089; }}
.badge-grey  {{ background:#F7FAFC; color:{MUTED} !important;   border:1px solid {BORDER}; }}

/* ── Pain scale bar ── */
.pain-bar {{ height:6px; border-radius:3px; background:linear-gradient(90deg,{GREEN},{AMBER},{RED}); margin:0.4rem 0; }}

/* ── Chat bubbles ── */
.chat-bubble {{ padding:0.85rem 1.1rem; border-radius:16px; max-width:78%; line-height:1.55; font-size:0.95rem; word-break:break-word; margin-bottom:0.5rem; }}
.user-bubble {{ background:{PRIMARY}; color:#fff !important; margin-left:auto; border-bottom-right-radius:4px; }}
.ai-bubble   {{ background:#fff; color:{TEXT} !important; border:1px solid {BORDER}; border-bottom-left-radius:4px; }}
.citation-badge {{ background:{LIGHT_BG}; border:1px solid #BEE3F8; border-radius:8px; padding:0.2rem 0.55rem; font-size:0.72rem; color:{PRIMARY} !important; margin-top:0.4rem; display:inline-block; margin-right:0.3rem; }}

/* ── Buttons ── */
.stButton > button {{
    background:{PRIMARY} !important; color:#fff !important; border:none !important;
    border-radius:12px !important; font-size:1rem !important; font-weight:600 !important;
    padding:0.6rem 1.5rem !important; transition:all 0.2s ease !important; min-height:44px !important;
}}
.stButton > button:hover {{
    background:#2C5282 !important;
    box-shadow:0 4px 14px rgba(43,108,176,0.35) !important;
    transform:translateY(-1px) !important;
}}
/* Secondary button override via class */
.btn-secondary > button {{
    background:#fff !important; color:{PRIMARY} !important;
    border:2px solid {PRIMARY} !important;
}}
.btn-secondary > button:hover {{
    background:{LIGHT_BG} !important;
}}
.btn-danger > button {{
    background:{RED} !important;
}}
.btn-green > button {{
    background:{GREEN} !important;
}}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {{
    background:#fff !important; border:1px solid {BORDER} !important;
    border-radius:10px !important; color:{TEXT} !important; font-size:1rem !important;
    min-height:44px !important;
}}
.stSlider > div {{ color:{TEXT} !important; }}

/* ── Progress bar (onboarding) ── */
.ob-progress-wrap {{ background:{BORDER}; border-radius:4px; height:6px; margin-bottom:1.5rem; }}
.ob-progress-fill {{ background:{PRIMARY}; border-radius:4px; height:6px; transition:width 0.4s ease; }}

/* ── Onboarding step chip ── */
.chip {{ display:inline-block; padding:0.4rem 1rem; border-radius:100px; border:2px solid {BORDER};
         font-size:0.9rem; cursor:pointer; margin:0.25rem; background:#fff; color:{TEXT} !important; }}
.chip-selected {{ background:{LIGHT_BG}; border-color:{PRIMARY}; color:{PRIMARY} !important; font-weight:600; }}

/* ── Exercise card ── */
.ex-card {{ background:#fff; border:1px solid {BORDER}; border-radius:14px; padding:1.1rem 1.3rem; margin-bottom:0.7rem; transition:all 0.2s ease; }}
.ex-card.done {{ border-color:{GREEN}; background:#F0FFF4; }}
.ex-card-name {{ font-size:1rem; font-weight:600; color:{TEXT} !important; }}
.ex-benefit   {{ font-size:0.82rem; color:{GREEN} !important; margin-top:0.1rem; }}
.ex-meta      {{ font-size:0.8rem; color:{MUTED} !important; margin-top:0.3rem; }}

/* ── Stat chip row ── */
.stat-chip {{ background:#fff; border:1px solid {BORDER}; border-radius:12px; padding:0.8rem 1rem;
              text-align:center; box-shadow:0 1px 4px rgba(0,0,0,0.05); }}
.stat-chip-val {{ font-size:1.6rem; font-weight:800; color:{PRIMARY} !important; }}
.stat-chip-lbl {{ font-size:0.72rem; color:{MUTED} !important; font-weight:500; text-transform:uppercase; letter-spacing:0.04em; }}

/* ── Weekly strip ── */
.week-day {{ text-align:center; padding:0.5rem 0.3rem; border-radius:10px; font-size:0.78rem; cursor:pointer; }}
.week-done {{ background:{GREEN}; color:#fff !important; }}
.week-sched {{ background:{LIGHT_BG}; color:{PRIMARY} !important; }}
.week-miss  {{ background:#F7FAFC; color:{MUTED} !important; }}
.week-rest  {{ background:#fff; color:{MUTED} !important; border:1px dashed {BORDER}; }}

/* ── Flare-up banner ── */
.flare-banner {{ background:#FFF5F5; border:1px solid #FEB2B2; border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem; }}

/* ── Report box ── */
.report-box {{ background:#fff; border:1px solid {BORDER}; border-radius:12px; padding:1.4rem;
               font-family:'Courier New',monospace; font-size:0.8rem; white-space:pre-wrap;
               color:{TEXT} !important; line-height:1.7; }}

/* ── Milestone ── */
.milestone {{ display:inline-block; background:#fff; border:1px solid {BORDER}; border-radius:14px;
              padding:0.8rem 1rem; margin:0.3rem; text-align:center; min-width:110px; font-size:0.82rem; }}
.milestone-locked {{ opacity:0.4; filter:grayscale(1); }}

/* ── Session counter (big number) ── */
.big-counter {{ font-size:5rem; font-weight:800; color:{TEXT} !important; text-align:center; line-height:1; }}
.big-counter-lbl {{ font-size:1rem; color:{MUTED} !important; text-align:center; margin-top:0.3rem; }}

/* ── Welcome hero ── */
.hero {{ text-align:center; padding:3rem 1rem 2rem; }}
.hero-icon {{ font-size:4rem; }}
.hero-title {{ font-size:2.2rem; font-weight:800; color:{TEXT} !important; margin:0.5rem 0; }}
.hero-sub   {{ font-size:1.05rem; color:{MUTED} !important; max-width:420px; margin:0 auto; }}

/* ── Insight card ── */
.insight-card {{ background:linear-gradient(135deg,{LIGHT_BG},{CARD_BG}); border:1px solid #BEE3F8;
                 border-radius:14px; padding:1.1rem 1.4rem; font-size:0.95rem; color:{TEXT} !important; line-height:1.6; }}

/* ── Expander override ── */
.stExpander {{ border:1px solid {BORDER} !important; border-radius:12px !important; }}

/* ── Sidebar nav item ── */
.nav-item {{ padding:0.65rem 1rem; border-radius:10px; margin-bottom:0.2rem;
             font-size:0.95rem; font-weight:500; cursor:pointer; }}
.nav-active {{ background:{LIGHT_BG}; color:{PRIMARY} !important; font-weight:600; }}

/* Plotly transparent bg override */
.js-plotly-plot .plotly {{ background:transparent !important; }}
</style>
""")


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"<h2 style='margin:0;color:{TEXT};'>{title}</h2>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color:{MUTED};font-size:0.9rem;margin-top:0.2rem;margin-bottom:1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)


def card(content_html: str, extra_style: str = ""):
    st.markdown(f"<div class='kd-card' style='{extra_style}'>{content_html}</div>", unsafe_allow_html=True)


def badge(text: str, colour: str = "blue") -> str:
    return f"<span class='badge badge-{colour}'>{text}</span>"


def go(page: str, sub: str = ""):
    st.session_state.current_page = page
    if sub:
        st.session_state.sub_page = sub
    st.rerun()
