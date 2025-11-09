"""RAG model with conversational intake and lightweight mode (no ChromaDB)."""

import json
from typing import List, Dict
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import streamlit as st


class KneeArthritisRAG:
    """Lightweight RAG model for knee arthritis guidance."""

    def __init__(self, data_loader, openai_api_key: str):
        self.loader = data_loader
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"

        # Embedding model (optional but useful for contextual matching)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        st.info("✅ KneeDoc AI initialized in lightweight mode (no ChromaDB).")

        # Cache text data for in-memory retrieval
        self.exercises_text = self._prepare_exercises()
        self.education_text = self._prepare_education()
        self.qa_text = self._prepare_qa()

    # ---------------------------------------------------------------------
    #  Data preparation
    # ---------------------------------------------------------------------
    def _prepare_exercises(self):
        docs = []
        for ex in getattr(self.loader, "exercises", []):
            text = f"Exercise: {ex.get('name', 'Unknown')}. "
            text += f"Category: {ex.get('category', 'General')}. "
            text += f"Target muscles: {', '.join(ex.get('target_muscles', []))}. "
            text += f"Difficulty: {ex.get('difficulty_level', 1)}/4. "
            text += f"Instructions: {' '.join(ex.get('instructions', []))}. "
            text += f"Primary benefit: {ex.get('primary_benefit', 'mobility improvement')}."
            docs.append(text)
        return docs

    def _prepare_education(self):
        return [
            f"Topic: {edu.get('title', '')}. {edu.get('content', '')}"
            for edu in getattr(self.loader, "education", [])
        ]

    def _prepare_qa(self):
        return [
            f"Q: {qa.get('question', '')} A: {qa.get('answer', '')}"
            for qa in getattr(self.loader, "qa_pairs", [])
        ]

    # ---------------------------------------------------------------------
    #  Information extraction
    # ---------------------------------------------------------------------
    def extract_patient_info(self, query: str) -> dict:
        """Extract patient info from a free-text query."""
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

    # ---------------------------------------------------------------------
    #  Context retrieval (in-memory)
    # ---------------------------------------------------------------------
    def retrieve_context(self, query: str, patient_info: dict):
        """Return simulated context for in-memory mode."""
        combined = (
            "\n".join(self.exercises_text[:5])
            + "\n\n"
            + "\n".join(self.education_text[:3])
            + "\n\n"
            + "\n".join(self.qa_text[:3])
        )
        return {"context_text": combined, "safety": getattr(self.loader, "safety", {})}

    # ---------------------------------------------------------------------
    #  AI Response Generation
    # ---------------------------------------------------------------------
    def generate_response(
        self,
        query: str,
        patient_info: dict,
        context: dict,
        conversation_history: List[dict],
    ) -> str:
        """Generate context-restricted AI response."""
        system_prompt = f"""
You are KneeDoc AI, an empathetic physiotherapy coach specialized in knee arthritis.

You MUST only answer questions related to:
- Knee pain, arthritis, rehabilitation, mobility, or exercise safety.
If the user asks about anything else (like coding, math, or chess),
respond: "I'm sorry, I can only provide guidance related to knee arthritis and physical exercises."

Patient Info:
- Age: {patient_info.get('age', 65)}
- Severity: {patient_info.get('severity', 3)}
- Pain level: {patient_info.get('pain_level', 5)}
Goals: {', '.join(patient_info.get('goals', [])) if patient_info.get('goals') else 'N/A'}
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append(
            {
                "role": "user",
                "content": f"{query}\n\nContext:\n{context.get('context_text', '')}",
            }
        )

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                temperature=0.6,
                max_tokens=1000,
                messages=messages,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error: {e}"

    # ---------------------------------------------------------------------
    #  Exercise Plan Creation
    # ---------------------------------------------------------------------
    def create_exercise_plan(self, patient_info: dict, context: dict):
        """Generate mock exercise plan."""
        plan = []
        for i, ex_text in enumerate(self.exercises_text[:5], 1):
            plan.append(
                {
                    "id": f"ex_{i}",
                    "name": f"Exercise {i}",
                    "difficulty": i,
                    "category": "Strength",
                    "reps": 10 + i,
                    "sets": 2,
                    "instructions": [
                        "Perform slowly",
                        "Maintain posture",
                        "Breathe evenly",
                    ],
                    "completed": False,
                }
            )
        return {"exercises": plan, "created_at": datetime.now().isoformat()}

    # ---------------------------------------------------------------------
    #  Exercise Guidance
    # ---------------------------------------------------------------------
    def get_exercise_guidance(self, exercise_id: str):
        """Return guidance for a specific exercise."""
        return f"""
### 🏋️ Exercise {exercise_id}
- Perform 2 sets of 10–15 reps.
- Keep knees slightly bent and move slowly.
- Avoid sudden pressure or twisting.
- Breathe regularly and stop if pain increases.
"""

    # ---------------------------------------------------------------------
    #  Conversational intake (interactive data gathering)
    # ---------------------------------------------------------------------
    def conversational_intake(self, user_message: str):
        """
        Step-by-step conversational patient intake.
        Flow: greet → name → age → problem → pain → plan recommendation
        Returns (response_text, next_step)
        """
        if "intake_step" not in st.session_state:
            st.session_state.intake_step = "greet"
            st.session_state.patient_profile = {}

        step = st.session_state.intake_step
        profile = st.session_state.patient_profile

        if step == "greet":
            st.session_state.intake_step = "ask_name"
            return "👋 Hi! I'm your KneeDoc AI Coach. What’s your name?", "ask_name"

        elif step == "ask_name":
            profile["name"] = user_message.strip().split(" ")[0].capitalize()
            st.session_state.intake_step = "ask_age"
            return f"Nice to meet you, {profile['name']}! 😊 How old are you?", "ask_age"

        elif step == "ask_age":
            try:
                age = int("".join([c for c in user_message if c.isdigit()]))
                if 10 < age < 110:
                    profile["age"] = age
                    st.session_state.intake_step = "ask_problem"
                    return (
                        f"Got it, {profile['name']}! What kind of knee problem are you facing — pain, stiffness, or limited movement?",
                        "ask_problem",
                    )
                else:
                    return "Please enter a valid age between 10 and 110.", "ask_age"
            except:
                return "Please tell me your age in numbers (e.g., 45).", "ask_age"

        elif step == "ask_problem":
            profile["problem"] = user_message.strip()
            st.session_state.intake_step = "ask_pain"
            return (
                "Understood. On a scale of 1–10, how severe is your knee pain right now?",
                "ask_pain",
            )

        elif step == "ask_pain":
            try:
                pain = int("".join([c for c in user_message if c.isdigit()]))
                if 0 <= pain <= 10:
                    profile["pain_level"] = pain
                    severity = 1 if pain <= 3 else 2 if pain <= 6 else 3 if pain <= 8 else 4
                    profile["severity"] = severity

                    exercises = [
                        ex for ex in getattr(self.loader, "exercises", [])
                        if ex.get("difficulty_level") == severity
                    ]
                    if not exercises:
                        exercises = self.loader.exercises[:3]

                    recs = "\n".join(
                        [f"- {ex['name']}: {ex['primary_benefit']}" for ex in exercises]
                    )
                    st.session_state.intake_step = "recommend"

                    return (
                        f"""Based on your pain level ({pain}/10), your severity is level {severity}.
Here are some recommended exercises for you:
{recs}

Would you like me to guide you step-by-step through these? 💪""",
                        "recommend",
                    )
                else:
                    return "Please give a number between 0 and 10.", "ask_pain"
            except:
                return "Please give your pain level as a number (1–10).", "ask_pain"

        elif step == "recommend":
            st.session_state.intake_step = "done"
            return (
                "Awesome! Let's begin your guided exercise session. 🏋️ You can ask me for instructions anytime.",
                "done",
            )

        else:
            return (
                f"You're all set, {profile.get('name', 'friend')}! You can now ask for daily routines, safety tips, or progress tracking. ✅",
                "done",
            )
