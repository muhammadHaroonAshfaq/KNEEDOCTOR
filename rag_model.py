"""RAG model without ChromaDB (temporary in-memory mode)"""

import json
from typing import List, Dict
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import streamlit as st

class KneeArthritisRAG:
    """Lightweight RAG model with no ChromaDB dependency."""

    def __init__(self, data_loader, openai_api_key: str):
        self.loader = data_loader
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        st.info("✅ RAG initialized in lightweight mode (no ChromaDB).")

        # Cache preprocessed text for quick context use
        self.exercises_text = self._prepare_exercises()
        self.education_text = self._prepare_education()
        self.qa_text = self._prepare_qa()

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

    def extract_patient_info(self, query: str) -> dict:
        """Extract key details about patient condition."""
        prompt = f"""Analyze this patient query and extract key information:
"{query}"

Return ONLY a valid JSON object with:
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
                    {"role": "user", "content": prompt}
                ]
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```"):
                txt = txt.split("```")[1].replace("json", "").strip()
            return json.loads(txt)
        except Exception:
            return {"severity": 3, "age": 65, "pain_level": 5,
                    "goals": ["reduce pain", "improve mobility"],
                    "limitations": ["stiffness", "joint discomfort"]}

    def retrieve_context(self, query: str, patient_info: dict):
        """Return simulated context (no Chroma)."""
        combined = (
            "\n".join(self.exercises_text[:5]) +
            "\n\n" + "\n".join(self.education_text[:3]) +
            "\n\n" + "\n".join(self.qa_text[:3])
        )
        return {"context_text": combined, "safety": getattr(self.loader, "safety", {})}

    def generate_response(self, query: str, patient_info: dict,
                          context: dict, conversation_history: List[dict]) -> str:
        """Generate context-restricted AI response."""
        system_prompt = f"""
You are KneeDoc AI, a physiotherapy coach specialized in knee arthritis.

You must ONLY answer questions related to:
- Knee pain, arthritis, mobility, rehabilitation, joint strength, and safe exercise.

If user asks something unrelated (e.g., chess, coding, math), say:
"I'm sorry, I can only provide guidance related to knee arthritis and physical exercises."

Patient:
- Age: {patient_info.get('age', 65)}
- Severity: {patient_info.get('severity', 3)}
- Pain level: {patient_info.get('pain_level', 5)}
Goals: {', '.join(patient_info.get('goals', []))}
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append({
            "role": "user",
            "content": f"{query}\n\nContext:\n{context['context_text']}"
        })

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                temperature=0.6,
                max_tokens=1000,
                messages=messages
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error: {e}"

    def create_exercise_plan(self, patient_info: dict, context: dict):
        """Mock plan generator without embeddings."""
        plan = []
        for i, ex_text in enumerate(self.exercises_text[:5], 1):
            plan.append({
                "id": f"ex_{i}",
                "name": f"Exercise {i}",
                "difficulty": i,
                "category": "Strength",
                "reps": 10 + i,
                "sets": 2,
                "instructions": ["Perform slowly", "Maintain posture", "Breathe evenly"],
                "completed": False
            })
        return {"exercises": plan, "created_at": datetime.now().isoformat()}

    def get_exercise_guidance(self, exercise_id: str):
        """Simulate exercise guidance."""
        return f"""
### 🏋️ Exercise {exercise_id}
- Perform 2 sets of 10–15 reps.
- Keep knees slightly bent and move slowly.
- Avoid sudden pressure or twisting.
- Breathe regularly and stop if pain increases.
"""

