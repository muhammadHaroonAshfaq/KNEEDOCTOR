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
        Returns (response_text, next_step)
        """
        if "intake_step" not in st.session_state:
            st.session_state.intake_step = "ask_age"
            st.session_state.patient_profile = {}

        step = st.session_state.intake_step
        profile = st.session_state.patient_profile

        if step == "ask_age":
            try:
                age = int("".join([c for c in user_message if c.isdigit()]))
                if 10 < age < 110:
                    profile["age"] = age
                    st.session_state.intake_step = "ask_pain"
                    return (
                        "Got it 👍 Now, on a scale of 1–10, how much pain do you usually feel in your knees?",
                        "ask_pain",
                    )
                else:
                    return "Please enter a valid age between 10 and 110.", "ask_age"
            except:
                return "How old are you?", "ask_age"

        elif step == "ask_pain":
            try:
                pain = int("".join([c for c in user_message if c.isdigit()]))
                if 0 <= pain <= 10:
                    profile["pain_level"] = pain
                    st.session_state.intake_step = "ask_problem"
                    return (
                        "Thanks! Could you briefly describe your knee problem or symptoms?",
                        "ask_problem",
                    )
                else:
                    return "Please enter a number between 0 and 10.", "ask_pain"
            except:
                return "On a scale of 1–10, how severe is your pain?", "ask_pain"

        elif step == "ask_problem":
            profile["problem"] = user_message.strip()
            st.session_state.intake_step = "ask_goal"
            return (
                "Understood. What’s your main goal — reduce pain, improve mobility, or strengthen your knees?",
                "ask_goal",
            )

        elif step == "ask_goal":
            profile["goals"] = [user_message.strip()]
            st.session_state.intake_step = "done"
            return (
                "Perfect 💪 I have everything I need. Let’s create your personalized exercise plan!",
                "done",
            )

        else:
            return (
                "I already have your details! You can now ask for your exercise plan or guidance anytime.",
                "done",
            )
