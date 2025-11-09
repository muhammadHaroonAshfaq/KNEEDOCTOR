# streamlit_app.py
"""
KneeDoc AI — Multi-Section Web App Layout (Navbar, Hero, Feature Cards, KPIs, Exercise Plan, Coach Chat, FAQ)
Single-file build that preserves your existing RAG + DataLoader logic.

Requirements:
- data_loader.py must define KneeArthritisDataLoader with .load_all(), .exercises, .faqs
- rag_model.py must define KneeArthritisRAG with:
    - extract_patient_info(text) -> dict
    - retrieve_context(query, profile) -> dict
    - create_exercise_plan(profile, ctx) -> dict
    - generate_response(user_text, profile, ctx, history) -> str
"""

import streamlit as st
from datetime import datetime
import time

# Keep your current functionality
from data_loader import KneeArthritisDataLoader
from rag_model import KneeArthritisRAG

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="KneeDoc AI",
    page_icon="🦵",
    layout="wide"
)

# ---------------------------------------------------------
# CSS (Tailwind-like design tokens + components)
# ---------------------------------------------------------
st.markdown("""
<style>
/* Design Tokens */
:root {
  --bg: #f5f7fb;         /* page bg */
  --panel: #ffffff;      /* card/panel */
  --text: #121826;       /* primary text */
  --muted: #667085;      /* secondary text */
  --border: #e5e7eb;     /* lines */
  --brand1: #667eea;     /* gradient start */
  --brand2: #764ba2;     /* gradient end */
  --success: #16a34a;
  --warning: #f59e0b;
  --info: #0ea5e9;
}

/* Reset streamlit chrome */
#MainMenu, header, footer { visibility: hidden; }

/* Page */
.stApp { background: var(--bg); }

/* Navbar */
.navbar {
  position: sticky; top: 0; z-index: 999;
  width: 100%;
  background: linear-gradient(135deg, var(--brand1), var(--brand2));
  color: #fff;
  box-shadow: 0 4px 14px rgba(0,0,0,.15);
}
.nav-wrap {
  display: flex; align-items: center; justify-content: space-between;
  padding: .75rem 1.25rem; max-width: 1200px; margin: 0 auto;
}
.brand { font-weight: 800; letter-spacing: .2px; display: flex; gap: .5rem; align-items: center; }
.nav-links a {
  color: #fff; opacity: .95; text-decoration: none; font-weight: 600; margin-left: 1rem;
}
.nav-links a:hover { opacity: 1; text-decoration: underline; }
.nav-actions { display: flex; gap: .5rem; }
.btn-ghost {
  background: rgba(255,255,255,.15); color: #fff; border: 1px solid rgba(255,255,255,.25);
  padding: .45rem .7rem; border-radius: 10px; font-weight: 600; cursor: pointer;
}
.btn-ghost:hover { background: rgba(255,255,255,.22); }

/* Hero */
.hero {
  max-width: 1200px; margin: 2.5rem auto 1.5rem; padding: 0 1.25rem;
  display: grid; grid-template-columns: 1.15fr .85fr; gap: 2rem; align-items: center;
}
.hero-left {
  background: var(--panel); border: 1px solid var(--border); border-radius: 16px;
  padding: 2rem; box-shadow: 0 8px 24px rgba(2,6,23,.06);
}
.kicker { color: var(--brand1); font-weight: 800; letter-spacing: .1em; font-size: .8rem; text-transform: uppercase; }
.h1 {
  font-size: 2.2rem; font-weight: 900; line-height: 1.15; margin: .4rem 0 1rem;
  background: linear-gradient(135deg, var(--brand1), var(--brand2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { color: var(--muted); font-size: 1.05rem; }
.hero-cta { display: flex; gap: .6rem; margin-top: 1.25rem; }
.btn-primary {
  background: linear-gradient(135deg, var(--brand1), var(--brand2)); color: #fff; border: none;
  padding: .8rem 1rem; border-radius: 12px; font-weight: 700; cursor: pointer;
  box-shadow: 0 8px 20px rgba(102,126,234,.28);
}
.btn-primary:hover { transform: translateY(-1px); }
.btn-outline {
  background: #fff; border: 1px solid var(--border); color: var(--text);
  padding: .8rem 1rem; border-radius: 12px; font-weight: 700; cursor: pointer;
}

/* Tiles / cards */
.section { max-width: 1200px; margin: 1rem auto; padding: 0 1.25rem; }
.section-title { font-size: 1.4rem; font-weight: 800; margin: .3rem 0 1rem; color: var(--text); }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.card {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem;
  box-shadow: 0 6px 20px rgba(2,6,23,.05);
}
.card h4 { margin: 0 0 .35rem; font-weight: 800; color: var(--text); }
.card p { margin: 0; color: var(--muted); }

/* KPI */
.kpi {
  display: flex; gap: .75rem; align-items: center;
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem; box-shadow: 0 4px 14px rgba(2,6,23,.05);
}
.kpi .badge { font-size: .8rem; color: #fff; padding: .15rem .5rem; border-radius: 999px; }
.badge-success { background: var(--success); } .badge-warning { background: var(--warning); } .badge-info { background: var(--info); }
.kpi .value { font-size: 1.6rem; font-weight: 900; color: var(--text); }
.kpi .label { color: var(--muted); font-size: .95rem; }

/* Plan cards */
.plan-item { border: 1px dashed var(--border); border-radius: 12px; padding: .9rem; }
.meta { color: var(--muted); font-size: .9rem; }

/* Coach chat mini-panel */
.chat-panel {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem; box-shadow: 0 8px 24px rgba(2,6,23,.06);
}
.msg { display: flex; gap: .6rem; margin: .8rem 0; }
.bubble {
  background: #f7f8fa; border: 1px solid var(--border); color: var(--text);
  padding: .65rem .8rem; border-radius: 12px; max-width: 80%;
}
.bubble.me { background: linear-gradient(135deg, var(--brand1), var(--brand2)); color: #fff; border: none; }
.time { font-size: .72rem; color: var(--muted); margin-left: auto; }

/* Typing dots */
.typing { display:flex; gap:4px; align-items:center; padding: .4rem 0; }
.dot { width:8px; height:8px; border-radius:50%; background:#bbb; animation: blink 1.2s infinite; }
.dot:nth-child(2){animation-delay:.2s;} .dot:nth-child(3){animation-delay:.4s;}
@keyframes blink { 0%,80%,100%{opacity:0;} 40%{opacity:1;} }

/* FAQ */
.details { border: 1px solid var(--border); border-radius: 12px; padding: .8rem 1rem; background: var(--panel); }
.details summary { cursor: pointer; font-weight: 800; color: var(--text); }

/* Footer */
.footer {
  margin: 2rem 0 0; padding: 1.2rem;
  background: #0f172a; color: #e5e7eb;
}
.footer .inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------
defaults = {
    "rag_initialized": False,
    "messages": [],
    "patient_profile": None,
    "current_plan": None,
    "settings_open": False
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------------------------------------------------
# Cached loaders (underscore trick for hashing)
# ---------------------------------------------------------
@st.cache_resource
def load_data():
    loader = KneeArthritisDataLoader(data_dir="data")
    loader.load_all()
    return loader

@st.cache_resource
def init_rag(_loader, api_key):
    return KneeArthritisRAG(_loader, api_key)

# ---------------------------------------------------------
# Navbar
# ---------------------------------------------------------
st.markdown("""
<div class="navbar">
  <div class="nav-wrap">
    <div class="brand">🦵 KneeDoc AI</div>
    <div class="nav-links">
      <a href="#home">Home</a>
      <a href="#features">Features</a>
      <a href="#plan">Exercise Plan</a>
      <a href="#coach">Coach</a>
      <a href="#faq">FAQ</a>
    </div>
    <div class="nav-actions">
      <button class="btn-ghost" onclick="window.parent.postMessage({type:'toggle_settings'}, '*')">⚙️ Settings</button>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Settings Drawer toggle JS (uses query param to persist)
st.markdown("""
<script>
window.addEventListener('message', (ev) => {
  try {
    if (!ev.data || !ev.data.type) return;
    if (ev.data.type === 'toggle_settings') {
      const qp = new URLSearchParams(window.location.search);
      const s = qp.get('settings') === '1' ? '0' : '1';
      qp.set('settings', s);
      window.location.search = qp.toString();
    }
  } catch(e) {}
});
</script>
""", unsafe_allow_html=True)

# Sync settings drawer state via query param
qp = st.experimental_get_query_params()
st.session_state.settings_open = qp.get("settings", ["0"])[0] == "1"

# ---------------------------------------------------------
# Settings Drawer (overlay card)
# ---------------------------------------------------------
if st.session_state.settings_open:
    with st.container():
        st.markdown(
            """
            <div style="
              position: fixed; top: 70px; right: 16px; z-index: 1001;
              width: 360px; background: var(--panel); border: 1px solid var(--border);
              border-radius: 16px; box-shadow: 0 20px 60px rgba(2,6,23,.18); padding: 1rem;">
              <div style="display:flex; align-items:center; justify-content:space-between;">
                <h4 style="margin:0;">Settings</h4>
                <span style="color:var(--muted); font-size:.9rem;">Close from navbar</span>
              </div>
            """,
            unsafe_allow_html=True
        )

        api_key = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")
        if api_key:
            if not st.session_state.rag_initialized:
                with st.spinner("Loading exercise database & initializing RAG..."):
                    try:
                        loader = load_data()
                        st.session_state.rag = init_rag(loader, api_key)
                        st.session_state.rag_initialized = True
                        st.success(f"✅ {len(loader.exercises)} exercises loaded")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.info("RAG is already initialized.")
        else:
            st.info("Enter your OpenAI API key to enable GPT-backed answers. (Your local RAG fallback may still respond.)")

        if st.session_state.patient_profile:
            prof = st.session_state.patient_profile
            st.caption(f"Profile: Age {prof.get('age','N/A')} • Severity {prof.get('severity','N/A')}/4 • Pain {prof.get('pain_level','N/A')}/10")

        colA, colB = st.columns(2)
        with colA:
            if st.button("🔄 New Session", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k not in ["rag", "rag_initialized"]:
                        del st.session_state[k]
                st.rerun()
        with colB:
            st.write("")  # spacer

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
st.markdown('<a id="home"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    <div class="hero">
      <div class="hero-left">
        <div class="kicker">Personalized Rehab</div>
        <div class="h1">Build safer, smarter knee routines with AI guidance.</div>
        <div class="hero-sub">Evidence-based exercises, tailored progress, and real-time coaching—designed for knee arthritis relief and long-term mobility.</div>
        <div class="hero-cta">
          <button class="btn-primary" onclick="window.location.hash='#coach'">Start Assessment</button>
          <button class="btn-outline" onclick="window.location.hash='#features'">Explore Features</button>
        </div>
      </div>
      <div style="background: var(--panel); border:1px solid var(--border); border-radius:16px; padding:1rem; box-shadow: 0 8px 24px rgba(2,6,23,.06);">
        <img src="https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=1600&auto=format&fit=crop" style="width:100%; border-radius:12px;" />
        <div style="margin-top:.6rem; color:var(--muted); font-size:.9rem;">Daily mobility boosters • Low-impact strength • Step-by-step guidance</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------
st.markdown('<a id="features"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="section-title">Features</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        <div class="card">
          <h4>Personalized Plans</h4>
          <p>We adapt exercises to your profile—age, severity, pain tolerance, and goals.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="card">
          <h4>Progress Tracking</h4>
          <p>Simple KPIs let you see improvements in comfort, strength, and range of motion.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="card">
          <h4>Coach Chat</h4>
          <p>Ask questions and get step-by-step guidance—with safety tips built in.</p>
        </div>
        """, unsafe_allow_html=True)

# KPIs
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="kpi"><span class="badge badge-success">Live</span><div><div class="value">3–5</div><div class="label">Sessions per week</div></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi"><span class="badge badge-info">Avg</span><div><div class="value">12</div><div class="label">Reps per set</div></div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi"><span class="badge badge-warning">Safe</span><div><div class="value">2</div><div class="label">Pain scale max</div></div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# EXERCISE PLAN (uses loader + RAG when available)
# ---------------------------------------------------------
st.markdown('<a id="plan"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="section-title">Your Exercise Plan</div>', unsafe_allow_html=True)

    if not st.session_state.get("rag_initialized"):
        st.info("Initialize in Settings to see a personalized plan. Showing sample exercises:")
        # fallback to sample loader just for display
        try:
            tmp_loader = load_data()
            sample_exs = tmp_loader.exercises[:3]
        except Exception:
            sample_exs = []
    else:
        # If plan not built yet, suggest building via Coach
        if not st.session_state.get("current_plan"):
            st.warning("No plan generated yet. Go to the Coach section to start your assessment.")
            try:
                sample_exs = load_data().exercises[:3]
            except Exception:
                sample_exs = []
        else:
            sample_exs = st.session_state["current_plan"].get("exercises", [])[:6]

    if sample_exs:
        grid = st.columns(3)
        for i, ex in enumerate(sample_exs):
            with grid[i % 3]:
                name = ex.get("name", "Exercise")
                reps = ex.get("reps", "—")
                diff = ex.get("difficulty", "—")
                desc = ex.get("desc", "")
                st.markdown(f"""
                <div class="card plan-item">
                  <h4>{name}</h4>
                  <div class="meta">Reps: {reps} • Difficulty: {diff}/4</div>
                  <p style="margin-top:.45rem;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# COACH (compact chat with streaming)
# ---------------------------------------------------------
st.markdown('<a id="coach"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="section-title">KneeDoc Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)

    # Seed message when RAG is ready and chat empty
    if st.session_state.rag_initialized and not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 I’m your AI coach. Tell me your age and describe your knee discomfort. I’ll suggest a safe starting plan.",
            "time": datetime.now().strftime("%I:%M %p")
        })

    # Render history
    for m in st.session_state.messages:
        role = m["role"]
        bubble_class = "bubble me" if role == "user" else "bubble"
        avatar = "🧑" if role == "user" else "🤖"
        st.markdown(
            f'<div class="msg"><div>{avatar}</div><div class="{bubble_class}">{m["content"]}</div>'
            f'<div class="time">{m["time"]}</div></div>',
            unsafe_allow_html=True
        )

    # Input
    user_text = st.text_input("Ask the coach a question or describe your condition:", key="coach_input")
    send_col1, send_col2 = st.columns([0.12, 0.88])
    with send_col1:
        send = st.button("Send", use_container_width=True)
    with send_col2:
        st.caption("Tip: e.g., “I’m 64 with moderate pain when climbing stairs.”")

    if send and user_text.strip():
        st.session_state.messages.append({
            "role": "user",
            "content": user_text.strip(),
            "time": datetime.now().strftime("%I:%M %p")
        })

        # Typing indicator
        ph = st.empty()
        with ph.container():
            st.markdown('<div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>', unsafe_allow_html=True)
        time.sleep(0.8)

        try:
            if not st.session_state.get("rag_initialized"):
                # Not initialized: graceful note
                ph.empty()
                reply = "Please open ⚙️ Settings and add your OpenAI key to enable personalized guidance."
            else:
                rag = st.session_state.rag
                if not st.session_state.get("patient_profile"):
                    profile = rag.extract_patient_info(user_text)
                    st.session_state.patient_profile = profile
                    ctx = rag.retrieve_context(user_text, profile)
                    st.session_state.current_plan = rag.create_exercise_plan(profile, ctx)
                    reply = rag.generate_response(user_text, profile, ctx, st.session_state.messages)
                else:
                    ctx = rag.retrieve_context(user_text, st.session_state.patient_profile)
                    reply = rag.generate_response(user_text, st.session_state.patient_profile, ctx, st.session_state.messages)

            # streaming the reply
            ph.empty()
            live = st.empty()
            showed = ""
            for tk in reply.split():
                showed += tk + " "
                live.markdown(f'<div class="msg"><div>🤖</div><div class="bubble">{showed.strip()}</div><div class="time">{datetime.now().strftime("%I:%M %p")}</div></div>', unsafe_allow_html=True)
                time.sleep(0.02)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "time": datetime.now().strftime("%I:%M %p")
            })

            # Clear input after sending
            st.session_state.coach_input = ""

        except Exception as e:
            ph.empty()
            st.error(f"⚠️ {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# FAQ
# ---------------------------------------------------------
st.markdown('<a id="faq"></a>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="section-title">Frequently Asked Questions</div>', unsafe_allow_html=True)

    # Try to use loader FAQs
    faqs = []
    try:
        faqs = load_data().faqs
    except Exception:
        pass

    if faqs:
        for item in faqs[:6]:
            q = item.get("q", "Question")
            a = item.get("a", "Answer")
            st.markdown(f'<div class="details"><summary>{q}</summary><div style="margin-top:.6rem; color:var(--muted);">{a}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="details"><summary>How often should I do the exercises?</summary><div style="margin-top:.6rem; color:var(--muted);">Most people do well with 3–5 sessions per week. Adjust based on soreness and your provider’s advice.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="details"><summary>What if I feel knee pain?</summary><div style="margin-top:.6rem; color:var(--muted);">Mild muscle soreness is okay; sharp joint pain or swelling means rest, reduce intensity, and consider icing for 10–15 minutes.</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div class="footer">
  <div class="inner">
    <div>© 2025 KneeDoc AI</div>
    <div style="opacity:.85;">Educational only — consult your clinician for personalized medical advice.</div>
  </div>
</div>
""", unsafe_allow_html=True)
