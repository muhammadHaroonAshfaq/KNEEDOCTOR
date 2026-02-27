"""Enhanced RAG model — adaptive session planner, clinical citations, flare-up protocol."""

import json
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import streamlit as st
import numpy as np


class KneeArthritisRAG:
    """AI-powered knee arthritis therapy engine with adaptive session planning."""

    FLARE_PAIN_THRESHOLD = 8  # VAS score triggering flare-up protocol

    def __init__(self, data_loader, openai_api_key: str):
        self.loader = data_loader
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.exercises_text = self._prepare_exercises()
        self.education_text = self._prepare_education()
        self.qa_text = self._prepare_qa()

        # Pre-compute embeddings for semantic retrieval
        self._embed_kb()

    # ------------------------------------------------------------------
    #  Data preparation
    # ------------------------------------------------------------------
    def _prepare_exercises(self) -> List[str]:
        docs = []
        for ex in getattr(self.loader, "exercises", []):
            text = (
                f"Exercise: {ex.get('name', 'Unknown')}. "
                f"Category: {ex.get('category', 'General')}. "
                f"Target muscles: {', '.join(ex.get('target_muscles', []))}. "
                f"Difficulty: {ex.get('difficulty_level', 1)}/4. "
                f"Instructions: {' '.join(ex.get('instructions', []))}. "
                f"Primary benefit: {ex.get('primary_benefit', 'mobility improvement')}."
            )
            docs.append(text)
        return docs

    def _prepare_education(self) -> List[str]:
        return [
            f"Topic: {edu.get('title', '')}. {edu.get('content', '')}"
            for edu in getattr(self.loader, "education", [])
        ]

    def _prepare_qa(self) -> List[str]:
        return [
            f"Q: {qa.get('question', '')} A: {qa.get('answer', '')}"
            for qa in getattr(self.loader, "qa_pairs", [])
        ]

    def _embed_kb(self):
        """Embed all knowledge-base documents for cosine-similarity retrieval."""
        all_texts = self.education_text + self.qa_text
        if all_texts:
            self._kb_texts = all_texts
            self._kb_embeddings = self.embedding_model.encode(
                all_texts, show_progress_bar=False
            )
        else:
            self._kb_texts = []
            self._kb_embeddings = np.array([])

    # ------------------------------------------------------------------
    #  Semantic retrieval
    # ------------------------------------------------------------------
    def _semantic_retrieve(self, query: str, top_k: int = 4) -> List[str]:
        """Return top-k KB chunks most similar to query."""
        if not self._kb_texts:
            return []
        q_emb = self.embedding_model.encode([query])
        scores = np.dot(self._kb_embeddings, q_emb.T).flatten()
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [self._kb_texts[i] for i in top_idx]

    def _get_citation_source(self, chunk: str) -> str:
        """Map a retrieved chunk to a human-readable source label."""
        if chunk.startswith("Q:"):
            return "📚 Clinical Q&A Database"
        if chunk.startswith("Topic:"):
            title = chunk.split(".")[0].replace("Topic: ", "")
            return f"📖 {title}"
        return "📋 Therapy Knowledge Base"

    # ------------------------------------------------------------------
    #  Patient info extraction
    # ------------------------------------------------------------------
    def extract_patient_info(self, query: str) -> dict:
        prompt = f"""
Analyze this patient's message: "{query}"
Return ONLY valid JSON with:
- severity (1–4)
- age (integer)
- pain_level (0–10)
- goals (list)
- limitations (list)
"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                max_tokens=400,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1].replace("json", "").strip()
            return json.loads(txt)
        except Exception:
            return {
                "severity": 3,
                "age": 65,
                "pain_level": 5,
                "goals": ["reduce pain", "improve mobility"],
                "limitations": ["stiffness", "joint discomfort"],
            }

    # ------------------------------------------------------------------
    #  Adaptive session planning
    # ------------------------------------------------------------------
    def build_session_plan(self, profile: dict) -> List[dict]:
        """
        Build an exercise plan adapted to the patient's recovery stage and pain level.
        Stages: Acute / Sub-Acute / Chronic
        Flare-up: pain >= 8 → passive/ice protocol only
        """
        pain = profile.get("pain_level", 5)
        stage = profile.get("stage", "Sub-Acute")

        # Flare-up override
        if pain >= self.FLARE_PAIN_THRESHOLD:
            return self._flare_up_protocol()

        exercises = self.loader.get_exercises_by_stage(stage)
        if not exercises:
            exercises = self.loader.exercises[:5]

        # Climate/weather mode: reduce reps by 20% if active
        weather_mode = profile.get("weather_mode", False)

        plan = []
        for i, ex in enumerate(exercises[:6], 1):
            reps = ex.get("reps", 10)
            sets = ex.get("sets", 2)
            if weather_mode:
                reps = max(5, int(reps * 0.8))

            plan.append(
                {
                    "id": ex.get("exercise_id", f"ex_{i}"),
                    "name": ex.get("name", f"Exercise {i}"),
                    "category": ex.get("category", "Mobility"),
                    "difficulty": ex.get("difficulty_level", 2),
                    "reps": reps,
                    "sets": sets,
                    "duration": ex.get("duration_seconds", 30),
                    "instructions": ex.get("instructions", ["Perform slowly and steadily."]),
                    "primary_benefit": ex.get("primary_benefit", "Mobility improvement"),
                    "form_tips": ex.get("form_tips", ["Keep knees aligned", "Breathe evenly"]),
                    "contraindications": ex.get("contraindications", []),
                    "completed": False,
                }
            )
        return plan

    def _flare_up_protocol(self) -> List[dict]:
        """Return passive/ice protocol for flare-up days."""
        return [
            {
                "id": "flare_1",
                "name": "🧊 Ice Therapy",
                "category": "Passive",
                "difficulty": 1,
                "reps": 1,
                "sets": 3,
                "duration": 600,
                "instructions": [
                    "Apply ice pack wrapped in cloth to the affected knee.",
                    "Hold for 15–20 minutes.",
                    "Repeat 3× daily.",
                ],
                "primary_benefit": "Reduce inflammation",
                "form_tips": ["Never apply ice directly to skin."],
                "contraindications": [],
                "completed": False,
                "is_passive": True,
            },
            {
                "id": "flare_2",
                "name": "🦵 Elevation Rest",
                "category": "Passive",
                "difficulty": 1,
                "reps": 1,
                "sets": 1,
                "duration": 1200,
                "instructions": [
                    "Lie flat on your back.",
                    "Elevate the affected leg on 2–3 pillows above heart level.",
                    "Rest for 20–30 minutes.",
                ],
                "primary_benefit": "Reduce swelling",
                "form_tips": ["Do not bend the knee forcefully."],
                "contraindications": [],
                "completed": False,
                "is_passive": True,
            },
            {
                "id": "flare_3",
                "name": "🌬️ Deep Breathing & Relaxation",
                "category": "Passive",
                "difficulty": 1,
                "reps": 10,
                "sets": 2,
                "duration": 300,
                "instructions": [
                    "Sit or lie comfortably.",
                    "Inhale slowly for 4 counts, exhale for 6 counts.",
                    "Focus on relaxing your legs and knee muscles.",
                ],
                "primary_benefit": "Reduce pain perception & muscle tension",
                "form_tips": [],
                "contraindications": [],
                "completed": False,
                "is_passive": True,
            },
        ]

    # ------------------------------------------------------------------
    #  Contraindication check
    # ------------------------------------------------------------------
    def check_contraindications(self, profile: dict) -> List[str]:
        """Return list of warnings relevant to this patient's conditions."""
        conditions = [c.lower() for c in profile.get("conditions", [])]
        warnings = []
        raw_ci = self.loader.get_contraindications()
        if isinstance(raw_ci, list):
            for item in raw_ci:
                if isinstance(item, str):
                    for cond in conditions:
                        if cond in item.lower():
                            warnings.append(item)
                            break
        # Hard-coded critical flags
        critical_flags = ["post-surgery", "bone-on-bone", "total knee replacement", "tkr"]
        for flag in critical_flags:
            for cond in conditions:
                if flag in cond:
                    warnings.append(
                        f"⚠️ {flag.title()} detected — high-impact exercises are contraindicated. Always consult your surgeon before proceeding."
                    )
        return list(set(warnings))

    # ------------------------------------------------------------------
    #  Context retrieval
    # ------------------------------------------------------------------
    def retrieve_context(self, query: str, patient_info: dict) -> dict:
        """Semantic retrieval of relevant KB chunks + safety info."""
        chunks = self._semantic_retrieve(query, top_k=4)
        citations = [self._get_citation_source(c) for c in chunks]
        context_text = "\n\n".join(chunks) if chunks else "\n".join(self.education_text[:3])
        return {
            "context_text": context_text,
            "citations": citations,
            "safety": getattr(self.loader, "safety", {}),
        }

    # ------------------------------------------------------------------
    #  AI Response Generation
    # ------------------------------------------------------------------
    def generate_response(
        self,
        query: str,
        patient_info: dict,
        context: dict,
        conversation_history: List[dict],
    ) -> tuple:
        """
        Generate a clinical response and return (response_text, citations_list).
        """
        pain = patient_info.get("pain_level", 5)
        flare_note = ""
        if pain >= self.FLARE_PAIN_THRESHOLD:
            flare_note = "\n⚠️ FLARE-UP MODE ACTIVE: Prioritise ice, elevation, and rest. Avoid weight-bearing exercises."

        system_prompt = f"""
You are KneeDoc AI — an empathetic, evidence-based physiotherapy coach specialising in knee arthritis.

Rules:
- Only answer questions about knee pain, arthritis, rehabilitation, mobility, or exercise safety.
- If asked anything unrelated, say: "I'm only able to provide knee arthritis and rehabilitation guidance."
- Always explain WHY an exercise helps, not just what to do.
- Cite clinical reasoning where possible.
- Keep responses clear and accessible (suitable for 55+ users).
{flare_note}

Patient Profile:
- Name: {patient_info.get('name', 'Patient')}
- Age: {patient_info.get('age', 65)}
- Pain Level: {pain}/10
- Recovery Stage: {patient_info.get('stage', 'Sub-Acute')}
- Conditions: {', '.join(patient_info.get('conditions', [])) or 'Not specified'}
- Goals: {', '.join(patient_info.get('goals', [])) or 'General recovery'}
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append(
            {
                "role": "user",
                "content": f"{query}\n\nKnowledge Base Context:\n{context.get('context_text', '')}",
            }
        )

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                temperature=0.6,
                max_tokens=1000,
                messages=messages,
            )
            response_text = resp.choices[0].message.content.strip()
            return response_text, context.get("citations", [])
        except Exception as e:
            return f"⚠️ Error: {e}", []

    # ------------------------------------------------------------------
    #  Insight of the day
    # ------------------------------------------------------------------
    def get_daily_insight(self, profile: dict) -> str:
        """Return a short motivational/clinical insight personalised to profile."""
        pain = profile.get("pain_level", 5)
        stage = profile.get("stage", "Sub-Acute")
        name = profile.get("name", "there")

        tips = {
            "Acute": [
                f"Hey {name} — focus on gentle range-of-motion today. Small movements now prevent long-term stiffness. 🌿",
                "Icing 3× daily for 15 min can reduce inflammation by up to 40% during the acute phase. ❄️",
                "Rest is a treatment, not a weakness. Your joints are healing — honour that process. 💙",
            ],
            "Sub-Acute": [
                f"Great work, {name}! Progressive resistance training in this phase rebuilds the quad strength that protects your knee joint. 💪",
                "Hydrotherapy and cycling are gold-standard sub-acute exercises — low impact, high reward. 🚴",
                "Consistent 20-min daily sessions outperform sporadic long workouts for joint recovery. ⏱️",
            ],
            "Chronic": [
                f"{name}, daily movement is your best medicine — even a 10-min walk reduces osteoarthritis pain scores significantly. 🚶",
                "Strength training 3× weekly can reduce knee OA pain by up to 50% over 12 weeks. 🏋️",
                "Omega-3 rich foods (salmon, flaxseed) have anti-inflammatory effects that complement your therapy. 🐟",
            ],
        }

        stage_tips = tips.get(stage, tips["Sub-Acute"])
        # Deterministic selection based on day of year
        day_idx = datetime.now().timetuple().tm_yday % len(stage_tips)
        return stage_tips[day_idx]

    # ------------------------------------------------------------------
    #  Clinical summary for Doctor Panel
    # ------------------------------------------------------------------
    def generate_clinical_summary(self, profile: dict, log: List[dict]) -> str:
        """Generate a plain-text clinical progress report."""
        pain_history = [e.get("pain", 5) for e in log] if log else [profile.get("pain_level", 5)]
        avg_pain = round(sum(pain_history) / len(pain_history), 1)
        total_sessions = len([e for e in log if e.get("type") == "session"]) if log else 0

        report = f"""
KNEE REHABILITATION PROGRESS REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATIENT INFORMATION
  Name            : {profile.get('name', 'N/A')}
  Age             : {profile.get('age', 'N/A')}
  Recovery Stage  : {profile.get('stage', 'N/A')}
  Primary Condition: {', '.join(profile.get('conditions', ['Knee Arthritis'])) or 'Knee Arthritis'}

PAIN & PROGRESS SUMMARY
  Current Pain Level : {profile.get('pain_level', 'N/A')}/10 (VAS Scale)
  Average Pain (trend): {avg_pain}/10
  Total Sessions Logged: {total_sessions}
  Therapy Streak       : {profile.get('streak', 0)} days

PATIENT GOALS
  {chr(10).join(['  • ' + g for g in profile.get('goals', ['Reduce pain', 'Improve mobility'])])}

CONTRAINDICATIONS / CAUTIONS
  {chr(10).join(['  ⚠️ ' + c for c in profile.get('conditions', [])]) or '  None flagged.'}

NOTES FOR CLINICIAN
  This report was generated by KneeDoc AI — an AI-assisted rehabilitation tool.
  This is NOT a substitute for clinical assessment. Please review with patient
  and validate exercise appropriateness for their specific diagnosis.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Powered by KneeDoc AI | AI-assisted physiotherapy support tool
⚠️  Not a medical device. For clinical review purposes only.
""".strip()
        return report

    # ------------------------------------------------------------------
    #  Conversational intake (multi-step onboarding)
    # ------------------------------------------------------------------
    def conversational_intake(self, user_message: str):
        """
        Multi-step conversational patient intake.
        Flow: greet → name → age → problem → conditions → stage → pain → goals → done
        Returns (response_text, step_name)
        """
        if "intake_step" not in st.session_state:
            st.session_state.intake_step = "greet"
            st.session_state.patient_profile = {}

        step = st.session_state.intake_step
        profile = st.session_state.patient_profile

        if step == "greet":
            st.session_state.intake_step = "ask_name"
            return (
                "👋 Welcome! I'm **KneeDoc AI** — your personal knee rehabilitation coach.\n\n"
                "Let's set up your profile so I can create a personalised therapy plan. What's your name?",
                "ask_name",
            )

        elif step == "ask_name":
            profile["name"] = user_message.strip().split()[0].capitalize() if user_message.strip() else "Friend"
            st.session_state.intake_step = "ask_age"
            return f"Great to meet you, **{profile['name']}**! 😊 How old are you?", "ask_age"

        elif step == "ask_age":
            try:
                age = int("".join([c for c in user_message if c.isdigit()]))
                if 10 < age < 110:
                    profile["age"] = age
                    st.session_state.intake_step = "ask_problem"
                    return (
                        f"Got it, {profile['name']}! What kind of knee problem are you experiencing?\n\n"
                        "_e.g. pain, stiffness, swelling, post-surgery recovery, limited movement_",
                        "ask_problem",
                    )
                else:
                    return "Please enter a valid age between 10 and 110.", "ask_age"
            except Exception:
                return "Please tell me your age as a number (e.g., **45**).", "ask_age"

        elif step == "ask_problem":
            profile["problem"] = user_message.strip()
            st.session_state.intake_step = "ask_conditions"
            return (
                "Understood. Do you have any diagnosed conditions or recent surgeries I should be aware of?\n\n"
                "_e.g. osteoarthritis, bone-on-bone, total knee replacement, meniscus tear — or type 'None'_",
                "ask_conditions",
            )

        elif step == "ask_conditions":
            raw = user_message.strip().lower()
            if raw in ("none", "no", "nothing", "n/a", "na"):
                profile["conditions"] = []
            else:
                profile["conditions"] = [c.strip() for c in user_message.replace(",", " ").split() if len(c.strip()) > 2]
            st.session_state.intake_step = "ask_stage"
            return (
                "Which stage best describes your recovery right now?\n\n"
                "1️⃣ **Acute** — recent injury/flare, significant pain, limited movement\n"
                "2️⃣ **Sub-Acute** — improving, moderate symptoms, ready for gentle exercise\n"
                "3️⃣ **Chronic** — ongoing condition, manageable pain, working on long-term strength\n\n"
                "Type 1, 2, or 3.",
                "ask_stage",
            )

        elif step == "ask_stage":
            mapping = {"1": "Acute", "2": "Sub-Acute", "3": "Chronic",
                       "acute": "Acute", "sub-acute": "Sub-Acute", "chronic": "Chronic",
                       "sub acute": "Sub-Acute"}
            chosen = mapping.get(user_message.strip().lower(), "Sub-Acute")
            profile["stage"] = chosen
            st.session_state.intake_step = "ask_pain"
            return (
                f"**{chosen}** — noted! 📋\n\n"
                "On a scale of **0–10**, how would you rate your knee pain *right now*?\n_(0 = no pain, 10 = unbearable)_",
                "ask_pain",
            )

        elif step == "ask_pain":
            try:
                pain = int("".join([c for c in user_message if c.isdigit()]))
                if 0 <= pain <= 10:
                    profile["pain_level"] = pain
                    severity = 1 if pain <= 3 else 2 if pain <= 6 else 3 if pain <= 8 else 4
                    profile["severity"] = severity
                    st.session_state.intake_step = "ask_goals"
                    pain_label = {1: "mild", 2: "moderate", 3: "severe", 4: "critical"}.get(severity, "moderate")
                    return (
                        f"Pain level **{pain}/10** ({pain_label}) — logged. ✅\n\n"
                        "Finally, what are your top recovery goals?\n\n"
                        "_e.g. reduce pain, walk without limping, return to sport, manage long-term arthritis_",
                        "ask_goals",
                    )
                else:
                    return "Please give a number between 0 and 10.", "ask_pain"
            except Exception:
                return "Please give your pain level as a number, e.g. **6**.", "ask_pain"

        elif step == "ask_goals":
            profile["goals"] = [g.strip() for g in user_message.replace(",", " ").split() if len(g.strip()) > 2]
            if not profile["goals"]:
                profile["goals"] = ["reduce pain", "improve mobility"]
            profile["streak"] = 0
            profile["weather_mode"] = False
            st.session_state.intake_step = "done"
            # Build initial session plan
            plan = self.build_session_plan(profile)
            st.session_state.session_plan = plan
            name = profile.get("name", "friend")
            stage = profile.get("stage", "Sub-Acute")
            return (
                f"🎉 **Profile complete, {name}!**\n\n"
                f"I've created your **{stage}** therapy plan with {len(plan)} personalised exercises.\n\n"
                "Head to the **📊 Dashboard** to see today's plan, or use **💬 AI Chat** to ask me anything about your recovery! 💪",
                "done",
            )

        else:
            profile_name = profile.get("name", "friend")
            return (
                f"You're all set, {profile_name}! ✅ Ask me anything about your knee recovery, exercises, or pain management.",
                "done",
            )
