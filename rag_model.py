# rag_model.py
"""RAG model with embedded vector database"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import streamlit as st

class KneeArthritisRAG:
    """RAG model with conversation memory and exercise guidance"""
    
    def __init__(self, data_loader, openai_api_key: str):
        self.loader = data_loader
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_name = "gpt-4o-mini"
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB (in-memory, no persistent folder needed)
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=False  # In-memory only
        ))
        
        # Create collections
        self._create_collections()
        
        # Embed data
        self._embed_all_data()
    
    def _create_collections(self):
        """Create ChromaDB collections"""
        try:
            self.exercises_collection = self.chroma_client.get_or_create_collection(
                name="exercises"
            )
            self.education_collection = self.chroma_client.get_or_create_collection(
                name="education"
            )
            self.qa_collection = self.chroma_client.get_or_create_collection(
                name="qa_pairs"
            )
        except Exception as e:
            st.error(f"Error creating collections: {e}")
    
    def _embed_all_data(self):
        """Embed all data into vector database"""
        # Only embed if collections are empty
        if self.exercises_collection.count() == 0:
            self._embed_exercises()
        if self.education_collection.count() == 0:
            self._embed_education()
        if self.qa_collection.count() == 0:
            self._embed_qa()
    
    def _embed_exercises(self):
        """Embed exercises"""
        if not self.loader.exercises:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for ex in self.loader.exercises:
            text = f"Exercise: {ex['name']}. "
            text += f"Category: {ex['category']}. "
            text += f"Difficulty: {ex['difficulty_level']}/4. "
            text += f"Target: {', '.join(ex['target_muscles'])}. "
            text += f"Instructions: {' '.join(ex['instructions'])} "
            text += f"Benefit: {ex['primary_benefit']}. "
            text += f"Sensations: {ex['expected_sensations']}"
            
            documents.append(text)
            ids.append(ex['exercise_id'])
            
            metadata = {
                'exercise_id': ex['exercise_id'],
                'name': ex['name'],
                'category': ex['category'],
                'difficulty_level': ex['difficulty_level']
            }
            
            # Add severity flags
            for sev in [1, 2, 3, 4]:
                metadata[f'severity_{sev}'] = sev in ex.get('severity_appropriate', [])
            
            metadatas.append(metadata)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.exercises_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def _embed_education(self):
        """Embed educational content"""
        if not self.loader.education:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for edu in self.loader.education:
            text = f"Topic: {edu['title']}. {edu['content']}"
            documents.append(text)
            ids.append(edu['topic_id'])
            metadatas.append({
                'topic_id': edu['topic_id'],
                'title': edu['title'],
                'category': edu['category']
            })
        
        embeddings = self.embedding_model.encode(documents).tolist()
        
        self.education_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def _embed_qa(self):
        """Embed Q&A pairs"""
        if not self.loader.qa_pairs:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for qa in self.loader.qa_pairs:
            text = f"Question: {qa['question']} Answer: {qa['answer']}"
            documents.append(text)
            ids.append(qa['question_id'])
            metadatas.append({
                'question_id': qa['question_id'],
                'question': qa['question'],
                'category': qa['category']
            })
        
        embeddings = self.embedding_model.encode(documents).tolist()
        
        self.qa_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def extract_patient_info(self, query: str) -> dict:
        """Extract patient information from query"""
        prompt = f"""Analyze this patient query and extract key information: "{query}"

Extract and return ONLY a JSON object with these fields:
- severity: integer 1-4 (1=mild, 4=severe). If not mentioned, use 3.
- age: integer. If not mentioned, use 65.
- pain_level: integer 0-10. If not mentioned, use 5.
- goals: list of strings. Patient's goals.
- limitations: list of strings. Current limitations.

Return ONLY valid JSON, no other text."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                max_tokens=400,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": "Extract structured information and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.choices[0].message.content.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            return json.loads(response_text)
        except Exception as e:
            return {
                "severity": 3,
                "age": 65,
                "pain_level": 5,
                "goals": ["reduce pain", "improve mobility"],
                "limitations": ["knee pain"]
            }
    
    def retrieve_context(self, query: str, patient_info: dict, n_exercises: int = 5):
        """Retrieve relevant context from vector database"""
        severity = patient_info.get('severity', 3)
        where_filter = {f"severity_{severity}": True}
        
        ex_results = self.exercises_collection.query(
            query_texts=[query],
            n_results=n_exercises,
            where=where_filter
        )
        
        edu_results = self.education_collection.query(
            query_texts=[query],
            n_results=2
        )
        
        qa_results = self.qa_collection.query(
            query_texts=[query],
            n_results=2
        )
        
        return {
            'exercises': ex_results,
            'education': edu_results,
            'qa': qa_results,
            'safety': self.loader.safety
        }
    
    def create_exercise_plan(self, patient_info: dict, context: dict) -> dict:
        """Create personalized exercise plan"""
        exercises = []
        
        for meta in context['exercises']['metadatas'][0][:4]:
            ex = self.loader.get_exercise_by_id(meta['exercise_id'])
            if ex:
                exercises.append({
                    'id': ex['exercise_id'],
                    'name': ex['name'],
                    'difficulty': ex['difficulty_level'],
                    'category': ex['category'],
                    'reps': ex['repetitions'],
                    'sets': ex['sets'],
                    'instructions': ex['instructions'],
                    'safety_cues': ex['safety_cues'],
                    'completed': False
                })
        
        return {
            'exercises': exercises,
            'created_at': datetime.now().isoformat(),
            'patient_severity': patient_info.get('severity', 3)
        }
    
    def format_context(self, context: dict) -> str:
        """Format context for LLM prompt"""
        formatted = ["RELEVANT EXERCISES:"]
        
        if context['exercises']['documents'][0]:
            for i, meta in enumerate(context['exercises']['metadatas'][0], 1):
                ex = self.loader.get_exercise_by_id(meta['exercise_id'])
                if ex:
                    formatted.append(f"\n{i}. {ex['name']}")
                    formatted.append(f"   Difficulty: {ex['difficulty_level']}/4")
                    formatted.append(f"   Reps: {ex['repetitions']}, Sets: {ex['sets']}")
                    formatted.append(f"   Instructions: {'; '.join(ex['instructions'][:3])}")
        
        formatted.append("\n\nSAFETY RULES:")
        if context['safety']:
            for rule in context['safety'].get('general_safety_rules', [])[:5]:
                formatted.append(f"- {rule}")
        
        return "\n".join(formatted)
    
    def generate_response(self, query: str, patient_info: dict, context: dict, conversation_history: List[dict]) -> str:
        """Generate response using GPT"""
        formatted_context = self.format_context(context)
        
        system_prompt = f"""You are an empathetic knee arthritis exercise coach.

PATIENT PROFILE:
- Age: {patient_info.get('age', 65)}
- Severity: {patient_info.get('severity', 3)}/4
- Pain Level: {patient_info.get('pain_level', 5)}/10
- Goals: {', '.join(patient_info.get('goals', []))}

Be supportive, encouraging, and safety-focused. Provide specific exercise recommendations."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        messages.extend(conversation_history[-6:])
        
        # Add current context
        messages.append({
            "role": "user",
            "content": f"{query}\n\nContext:\n{formatted_context}"
        })
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                max_tokens=1500,
                temperature=0.7,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
    
    def get_exercise_guidance(self, exercise_id: str) -> str:
        """Get detailed exercise guidance"""
        ex = self.loader.get_exercise_by_id(exercise_id)
        if not ex:
            return "❌ Exercise not found"
        
        guidance = f"""
### 🏋️ {ex['name']}

**Exercise Info:**
- Difficulty: {ex['difficulty_level']}/4
- Category: {ex['category']}
- Equipment: {ex['equipment_needed']}

**Instructions:**
"""
        for i, step in enumerate(ex['instructions'], 1):
            guidance += f"\n{i}. {step}"
        
        guidance += f"""

**How Many:**
- Repetitions: {ex['repetitions']}
- Sets: {ex['sets']}
- Frequency: {ex['frequency']}

**Safety Reminders:**
"""
        for cue in ex['safety_cues'][:3]:
            guidance += f"\n- {cue}"
        
        guidance += f"""

**Expected Feeling:**
{ex['expected_sensations']}

**Modifications:**
- Easier: {ex['modifications'].get('easier', 'Not available')}
- Harder: {ex['modifications'].get('harder', 'Not available')}
"""
        return guidance
