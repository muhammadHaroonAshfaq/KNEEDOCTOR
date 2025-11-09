"""Enhanced RAG model with safety, empathy, and contextual intelligence."""

import json
import time
from typing import List, Dict
from datetime import datetime
from functools import lru_cache

from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from rapidfuzz import fuzz
import streamlit as st


class KneeArthritisRAG:
    """Context-restricted AI assistant for knee arthritis rehabilitation."""

    VALID_KEYWORDS = [
        "knee", "arthritis", "osteoarthritis", "joint", "exercise", "rehab",
        "mobility", "therapy", "pain", "swelling", "stiffness", "physiotherapy"
    ]

    def __init__(self, data_loader, openai_api_key: str):
        self.loader = data_loader
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self._create_collections()
        self._embed_all_data()

    # ---------------- COLLECTIONS & EMBEDDINGS ---------------- #

    def _create_collections(self):
        self.exercises_collection = self.chroma_client.get_or_create_collection("exercises")
        self.education_collection = self.chroma_client.get_or_create_collection("education")
        self.qa_collection = self.chroma_client.get_or_create_collection("qa_pairs")

    @lru_cache(maxsize=64)
    def get_cached_embedding(self, text: str):
        return tuple(self.embedding_model.encode(text))

    def _embed_all_data(self):
        if self.exercises_collection.count() == 0:
            self._embed_exercises()
        if self.education_collection.count() == 0:
            self._embed_education()
        if self.qa_collection.count() == 0:
            self._embed_qa()

    def _embed_exercises(self):
        docs, metas, ids = [], [], []
        for ex in self.loader.exercises:
            text = (
                f"Exercise: {ex['name']} (difficulty {ex['difficulty_level']}/4). "
                f"Targets: {', '.join(ex['target_muscles'])}. "
                f"Instructions: {' '.join(ex['instructions'])}. "
                f"Benefits: {ex['primary_benefit']}. "
            )
            docs.append(text)
            ids.append(ex["exercise_id"])
            meta = {k: ex[k] for k in ["exercise_id", "name", "category", "difficulty_level"]}
            for sev in range(1, 5):
                meta[f"severity_{sev}"] = sev in ex.get("severity_appropriate", [])
            metas.append(meta)

        emb = [self.get_cached_embedding(d) for d in docs]
        self.exercises_collection.add(documents=docs, embeddings=emb, metadatas=metas, ids=ids)

    def _embed_education(self):
        docs, metas, ids = [], [], []
        for edu in self.loader.education:
            docs.append(f"{edu['title']} — {edu['content']}")
            ids.append(edu["topic_id"])
            metas.append({"topic_id": edu["topic_id"], "title": edu["title"]})
        emb = [self.get_cached_embedding(d) for d in docs]
        self.education_collection.add(documents=docs, embeddings=emb, metadatas=metas, ids=ids)

    def _embed_qa(self):
        docs, metas, ids = [], [], []
        for qa in self.loader.qa_pairs:
            docs.append(f"Q: {qa['question']} A: {qa['answer']}")
            ids.append(qa["question_id"])
            metas.append({"question_id": qa["question_id"], "question": qa["question"]})
        emb = [self.get_cached_embedding(d) for d in docs]
        self.qa_collection.add(documents=docs, embeddings=emb, metadatas=metas, ids=ids)

    # ---------------- QUERY GUARDRAILS ---------------- #

    def _is_relevant_query(self, text: str) -> bool:
        """Check if query is related to knee arthritis context."""
        t = text.lower()
        for kw in self.VALID_KEYWORDS:
            if fuzz.partial_ratio(kw, t) > 80:
                return True
        return False

    # ---------------- NLP UTILITIES ---------------- #

    def detect_emotion(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["tired", "hurt", "hopeless", "painful", "can't"]):
            return "low"
        if any(w in t for w in ["better", "improving", "good", "great"]):
            return "high"
        return "neutral"

    def _get_tone(self, severity: int, pain: int) -> str:
        if severity >= 4 or pain >= 8:
            return "gentle and reassuring"
        if severity <= 2 and pain <= 4:
            return "motivational and upbeat"
        return "calm and supportive"

    def get_confidence(self, result):
        try:
            scores = result.get("distances", [[0.5]])[0]
            return round(1 - sum(scores) / len(scores), 2)
        except Exception:
            return 0.7

    # ---------------- CONTEXT & RETRIEVAL ---------------- #

    def retrieve_context(self, query: str, patient_info: dict, n_exercises: int = 5):
        severity = patient_info.get("severity", 3)
        where = {f"severity_{severity}": True}

        ex_res = self.exercises_collection.query(query_texts=[query], n_results=n_exercises, where=where)
        edu_res = self.education_collection.query(query_texts=[query], n_results=2)
        qa_res = self.qa_collection.query(query_texts=[query], n_results=2)

        return {"exercises": ex_res, "education": edu_res, "qa": qa_res, "safety": self.loader.safety}

    def hybrid_search(self, query: str, n_results: int = 5):
        semantic = self.exercises_collection.query(query_texts=[query], n_results=n_results)
        keyword_hits = [
            ex for ex in self.loader.exercises if any(w in query.lower() for w in ex["name"].lower().split())
        ]
        return {"semantic": semantic, "keyword": keyword_hits[:n_results]}

    def filter_safe_exercises(self, exercises: List[dict], severity: int):
        return [ex for ex in exercises if ex["difficulty_level"] <= severity + 1]

    # ---------------- RESPONSE GENERATION ---------------- #

    def generate_response(self, query: str, patient_info: dict, context: dict, history: List[dict]) -> str:
        """LLM response with context restriction and empathy."""
        if not self._is_relevant_query(query):
            return "I'm sorry, I can only provide guidance related to knee arthritis and physical exercises."

        tone = self._get_tone(patient_info.get("severity", 3), patient_info.get("pain_level", 5))
        formatted_context = self.format_context(context)

        system_prompt = f"""
You are KneeDoc AI, an empathetic {tone} physiotherapy assistant focused ONLY
on knee arthritis, mobility, and safe exercises.
Politely decline unrelated queries.

PATIENT:
Age {patient_info.get('age', 65)}, severity {patient_info.get('severity', 3)}/4,
pain {patient_info.get('pain_level', 5)}/10.
Goals: {', '.join(patient_info.get('goals', []))}.
"""

        msgs = [{"role": "system", "content": system_prompt}]
        msgs.extend(history[-6:])
        msgs.append({"role": "user", "content": f"{query}\n\nContext:\n{formatted_context}"})

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=msgs,
                temperature=0.6,
                max_tokens=900,
            )
            text = resp.choices[0].message.content.strip()

            # fallback if off-topic sneaks through
            if not any(k in text.lower() for k in self.VALID_KEYWORDS):
                return "I'm sorry, I can only provide guidance related to knee arthritis and physical exercises."

            if self.detect_emotion(query) == "low":
                text += "\n\n🌟 Remember: even small progress matters. Let’s focus on gentle movement today."
            return text
        except Exception as e:
            return f"⚠️ Error generating response: {e}"

    # ---------------- CONTEXT FORMATTING ---------------- #

    def format_context(self, ctx: dict) -> str:
        out = ["RELEVANT EXERCISES:"]
        if ctx["exercises"]["documents"][0]:
            for i, meta in enumerate(ctx["exercises"]["metadatas"][0][:4], 1):
                ex = self.loader.get_exercise_by_id(meta["exercise_id"])
                if ex:
                    out.append(
                        f"{i}. {ex['name']} (diff {ex['difficulty_level']}/4) – "
                        f"{'; '.join(ex['instructions'][:2])}"
                    )
        if ctx.get("safety"):
            out.append("\nSAFETY TIPS:")
            for rule in ctx["safety"].get("general_safety_rules", [])[:5]:
                out.append(f"- {rule}")
        return "\n".join(out)

    # ---------------- UTILITIES ---------------- #

    def summarize_session(self, messages: List[dict]) -> str:
        convo = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        prompt = (
            "Summarize this conversation highlighting exercises, improvements, and advice "
            "for knee arthritis recovery:\n" + convo
        )
        try:
            resp = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "You summarize clearly and briefly."},
                          {"role": "user", "content": prompt}],
                temperature=0.4,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Could not summarize session: {e}"

    def find_similar_exercises(self, name: str, top_k: int = 3):
        ex = next((e for e in self.loader.exercises if e["name"].lower() == name.lower()), None)
        if not ex:
            return []
        query = f"Exercises targeting {', '.join(ex['target_muscles'])}"
        res = self.exercises_collection.query(query_texts=[query], n_results=top_k)
        return [m["name"] for m in res["metadatas"][0] if m["name"] != name]
