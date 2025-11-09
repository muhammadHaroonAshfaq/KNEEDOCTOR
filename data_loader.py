# data_loader.py
"""Load and manage knee arthritis dataset"""

import json
from pathlib import Path
from typing import List, Dict, Optional

class KneeArthritisDataLoader:
    """Load and manage knee arthritis dataset"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.exercises = []
        self.education = []
        self.qa_pairs = []
        self.patients = []
        self.safety = {}
        self.progressions = []
        
    def load_json(self, filename: str) -> Optional[dict]:
        """Load a single JSON file"""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ File not found: {filename}")
            return None
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing {filename}: {e}")
            return None
    
    def load_all(self):
        """Load all dataset components"""
        self.exercises = self.load_json("exercises_detailed_20.json") or []
        self.education = self.load_json("knee_arthritis_education.json") or []
        self.qa_pairs = self.load_json("knee_arthritis_qa.json") or []
        self.patients = self.load_json("knee_arthritis_patients.json") or []
        self.safety = self.load_json("knee_arthritis_safety.json") or {}
        self.progressions = self.load_json("knee_arthritis_progressions.json") or []
        return self
    
    def get_exercise_by_id(self, exercise_id: str) -> Optional[dict]:
        """Get specific exercise by ID"""
        return next((ex for ex in self.exercises if ex['exercise_id'] == exercise_id), None)
    
    def filter_exercises(self, severity: int = None, difficulty_max: int = None) -> List[dict]:
        """Filter exercises by criteria"""
        filtered = self.exercises
        
        if severity:
            filtered = [ex for ex in filtered if severity in ex.get('severity_appropriate', [])]
        
        if difficulty_max:
            filtered = [ex for ex in filtered if ex.get('difficulty_level', 5) <= difficulty_max]
        
        return filtered
