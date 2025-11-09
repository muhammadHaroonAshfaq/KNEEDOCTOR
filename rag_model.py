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

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        st.info("✅ KneeDoc AI initialized in lightweight mode (no ChromaDB).")

        self.exercises_text = self._prepare_exercises()
        self.education_text = self._prepare_education()
        self.qa_text = self._prepare_qa()

    def _prepare_exercises(self):
        docs = []
        for ex in getattr(self.loader, "exercises", []):
            text = f"Exercise: {ex.get('name', 'Unknown')}. Category: {ex.get('category', 'General')}. "
            text += f"Target muscles: {', '.join(ex.get('target_muscles', []))}. Difficulty: {ex.get('difficulty_level', 1)}/4. "
            text += f"Instructions: {' '.join(ex.get('instructions', []))}. Primary benefit: {ex.get('primary_benefit', 'mobility improvement')}."
            docs.append(text)
        return docs

    def _prepare_education(self):
        return [f"Topic: {edu.get('title', '')}. {edu.get('content', '')}" for edu in getattr(self.loader, "education", [])]

    def _prepare_qa(self):
        return [f"Q: {qa.get('question', '')} A: {qa.get('answer', '')}" for qa in getattr(self.loader, "qa_pairs", [])]

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
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                max_tokens=400,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
            )
            txt = resp.choices[0].message.content.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1].replace("json", "").strip()
            return json.loads(txt)
        except Exception:
            return {"severity": 3, "age": 65, "pain_level": 5,
                    "goals": ["reduce pain", "improve mobility"], "limitations": ["stiffness"]}

    def retrieve_context(self, query: str, patient_info: dict):
        combined = (
            "\n".join(self.exercises_text[:5])
            + "\n\n"
            + "\n".join(self.education_text[:3])
            + "\n\n"
            + "\n".join(self.qa_text[:3])
        )
        return {"context_text": combined, "safety": getattr(self.loader, "safety", {})}

    def generate_response(self, query: str, patient_info: dict, context: dict, conversation_history: List[dict]) -> str:
        system_prompt = f"""
You are KneeDoc AI, an empathetic physiotherapy coach specialized in knee arthritis.

Only answer questions related to knee pain, arthritis, rehabilitation, mobility, or exercise safety.
If user asks anything else (like coding or chess), respond:
"I'm sorry, I can only provide guidance related to knee arthritis and physical exercises."

Patient Info:
- Age: {patient_info.get('age', 65)}
- Severity: {patient_info.get('severity', 3)}
- Pain: {patient_info.get('pain_level', 5)}/10
- Goals: {', '.join(patient_info.get('goals', []))}
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": f"{query}\n\nContext:\n{context.get('context_text', '')}"})

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name, temperature=0.6, max_tokens=1000, messages=messages
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error: {e}"

    def conversational_intake(self, user_message: str):
        if "intake_step" not in st.session_state:
            st.session_state.intake_step = "ask_age"
            st.session_state.patient_profile = {}

        step = st.session_state.intake_step
        profile = st.session_state.patient_profile

        if step == "ask_age":
            try:
                age = int("".join([c for c in user_message if c.isdigit()]))
                profile["age"] = age
                st.session_state.intake_step = "ask_pain"
                return "Got it 👍 Now, on a scale of 1–10, how much pain do you usually feel?", "ask_pain"
            except:
                return "How old are you?", "ask_age"

        elif step == "ask_pain":
            try:
                pain = int("".join([c for c in user_message if c.isdigit()]))
                profile["pain_level"] = pain
                st.session_state.intake_step = "ask_problem"
                return "Thanks! Could you briefly describe your knee problem?", "ask_problem"
            except:
                return "On a scale of 1–10, how severe is your pain?", "ask_pain"

        elif step == "ask_problem":
            profile["problem"] = user_message.strip()
            st.session_state.intake_step = "ask_goal"
            return "Understood. What’s your main goal — reduce pain, improve mobility, or strengthen your knees?", "ask_goal"

        elif step == "ask_goal":
            profile["goals"] = [user_message.strip()]
            st.session_state.intake_step = "done"
            return "Perfect 💪 I have everything I need. Let’s create your personalized plan!", "done"

        else:
            return "You're all set! You can now ask for exercise plans anytime.", "done"
