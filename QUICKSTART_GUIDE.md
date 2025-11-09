# Quick Start Guide: Building Your Knee Arthritis RAG Model

## Table of Contents
1. [Setup](#setup)
2. [Data Loading](#data-loading)
3. [Vector Database Setup](#vector-database-setup)
4. [RAG Implementation](#rag-implementation)
5. [Testing](#testing)
6. [Example Usage](#example-usage)

---

## Setup

### Required Dependencies

```bash
pip install --break-system-packages \
    sentence-transformers \
    chromadb \
    openai \
    anthropic \
    numpy \
    pandas
```

### File Organization

```
project/
├── data/
│   ├── exercises_detailed_20.json
│   ├── knee_arthritis_education.json
│   ├── knee_arthritis_qa.json
│   ├── knee_arthritis_patients.json
│   ├── knee_arthritis_safety.json
│   └── knee_arthritis_progressions.json
├── src/
│   ├── load_data.py
│   ├── embed_data.py
│   ├── rag_model.py
│   └── utils.py
└── main.py
```

---

## Data Loading

### `load_data.py`

```python
import json
from pathlib import Path

class KneeArthritisDataLoader:
    """Load and manage knee arthritis dataset components"""
    
    def __init__(self, data_dir="data/"):
        self.data_dir = Path(data_dir)
        self.exercises = None
        self.education = None
        self.qa_pairs = None
        self.patients = None
        self.safety = None
        self.progressions = None
        
    def load_all(self):
        """Load all dataset components"""
        self.exercises = self._load_json("exercises_detailed_20.json")
        self.education = self._load_json("knee_arthritis_education.json")
        self.qa_pairs = self._load_json("knee_arthritis_qa.json")
        self.patients = self._load_json("knee_arthritis_patients.json")
        self.safety = self._load_json("knee_arthritis_safety.json")
        self.progressions = self._load_json("knee_arthritis_progressions.json")
        
        return self
    
    def _load_json(self, filename):
        """Load a JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def get_exercises_by_difficulty(self, level):
        """Filter exercises by difficulty level"""
        return [ex for ex in self.exercises 
                if ex['difficulty_level'] == level]
    
    def get_exercises_by_severity(self, severity):
        """Filter exercises appropriate for severity level"""
        return [ex for ex in self.exercises 
                if severity in ex['severity_appropriate']]
    
    def get_progression_pathway(self, pathway_id):
        """Get specific progression pathway"""
        return next((p for p in self.progressions 
                    if p['progression_id'] == pathway_id), None)

# Usage
loader = KneeArthritisDataLoader()
loader.load_all()
exercises = loader.exercises
print(f"Loaded {len(exercises)} exercises")
```

---

## Vector Database Setup

### `embed_data.py`

```python
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class KneeArthritisVectorDB:
    """Create and manage vector database for RAG retrieval"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model_name)
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Create collections
        self.exercises_collection = self.client.get_or_create_collection(
            name="exercises",
            metadata={"description": "Knee exercise library"}
        )
        
        self.education_collection = self.client.get_or_create_collection(
            name="education",
            metadata={"description": "Patient education content"}
        )
        
        self.qa_collection = self.client.get_or_create_collection(
            name="qa_pairs",
            metadata={"description": "Question-answer pairs"}
        )
    
    def embed_exercises(self, exercises):
        """Embed and store exercise data"""
        documents = []
        metadatas = []
        ids = []
        
        for ex in exercises:
            # Create rich text representation
            text = f"{ex['name']}. Category: {ex['category']}. "
            text += f"Difficulty: {ex['difficulty_level']}/4. "
            text += f"Target muscles: {', '.join(ex['target_muscles'])}. "
            text += f"Instructions: {' '.join(ex['instructions'])} "
            text += f"Expected sensations: {ex['expected_sensations']} "
            text += f"Primary benefit: {ex['primary_benefit']}"
            
            documents.append(text)
            ids.append(ex['exercise_id'])
            
            # Store metadata for filtering
            metadatas.append({
                'exercise_id': ex['exercise_id'],
                'name': ex['name'],
                'category': ex['category'],
                'difficulty_level': ex['difficulty_level'],
                'severity_1': 1 in ex['severity_appropriate'],
                'severity_2': 2 in ex['severity_appropriate'],
                'severity_3': 3 in ex['severity_appropriate'],
                'severity_4': 4 in ex['severity_appropriate'],
                'pain_tolerance': ex['pain_tolerance_required'],
                'equipment': ex['equipment_needed']
            })
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.exercises_collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Embedded {len(exercises)} exercises")
    
    def embed_education(self, education_content):
        """Embed and store educational content"""
        documents = []
        metadatas = []
        ids = []
        
        for edu in education_content:
            text = f"{edu['title']}. {edu['content']} "
            text += f"Key takeaways: {' '.join(edu['key_takeaways'])}"
            
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
        
        print(f"Embedded {len(education_content)} educational topics")
    
    def embed_qa_pairs(self, qa_pairs):
        """Embed and store Q&A pairs"""
        documents = []
        metadatas = []
        ids = []
        
        for qa in qa_pairs:
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
        
        print(f"Embedded {len(qa_pairs)} Q&A pairs")
    
    def search_exercises(self, query, severity=None, difficulty_max=None, n_results=5):
        """Search for relevant exercises"""
        where_filter = {}
        
        if severity:
            where_filter[f'severity_{severity}'] = True
        
        if difficulty_max:
            # Note: ChromaDB doesn't support <= directly, so we'd need to handle this differently
            # For now, we'll filter post-retrieval
            pass
        
        results = self.exercises_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        return results
    
    def search_education(self, query, n_results=3):
        """Search for relevant educational content"""
        results = self.education_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def search_qa(self, query, n_results=3):
        """Search for relevant Q&A pairs"""
        results = self.qa_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

# Usage
loader = KneeArthritisDataLoader()
loader.load_all()

vector_db = KneeArthritisVectorDB()
vector_db.embed_exercises(loader.exercises)
vector_db.embed_education(loader.education)
vector_db.embed_qa_pairs(loader.qa_pairs)
```

---

## RAG Implementation

### `rag_model.py`

```python
import anthropic
import json

class KneeArthritisRAG:
    """RAG model for personalized knee arthritis exercise recommendations"""
    
    def __init__(self, vector_db, data_loader, anthropic_api_key):
        self.vector_db = vector_db
        self.data_loader = data_loader
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    def assess_patient(self, patient_input):
        """Extract patient information from natural language input"""
        prompt = f"""Extract patient information from this input: {patient_input}

Return JSON with:
- age (number)
- severity (1-4, where 4 is most severe)
- pain_level (0-10)
- activity_goal (string)
- current_limitations (list)

Return only valid JSON, no other text."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            patient_data = json.loads(response.content[0].text)
            return patient_data
        except:
            # Fallback defaults
            return {
                "age": 65,
                "severity": 3,
                "pain_level": 5,
                "activity_goal": "improve mobility",
                "current_limitations": ["pain with stairs"]
            }
    
    def retrieve_context(self, query, patient_data):
        """Retrieve relevant context from vector DB"""
        severity = patient_data.get('severity', 3)
        
        # Get exercises appropriate for severity
        exercises = self.vector_db.search_exercises(
            query=query,
            severity=severity,
            n_results=5
        )
        
        # Get educational content
        education = self.vector_db.search_education(
            query=query,
            n_results=2
        )
        
        # Get relevant Q&A
        qa = self.vector_db.search_qa(
            query=query,
            n_results=2
        )
        
        # Get safety guidelines
        safety = self.data_loader.safety
        
        return {
            'exercises': exercises,
            'education': education,
            'qa': qa,
            'safety': safety
        }
    
    def generate_response(self, query, patient_data, context):
        """Generate personalized response using Claude"""
        
        # Format context for prompt
        exercises_text = self._format_exercises(context['exercises'])
        education_text = self._format_education(context['education'])
        safety_text = self._format_safety(context['safety'])
        
        prompt = f"""You are a helpful assistant for knee arthritis patients. Based on the patient information and retrieved context, provide personalized exercise recommendations.

PATIENT INFORMATION:
{json.dumps(patient_data, indent=2)}

USER QUERY:
{query}

RELEVANT EXERCISES:
{exercises_text}

EDUCATIONAL CONTEXT:
{education_text}

SAFETY GUIDELINES:
{safety_text}

INSTRUCTIONS:
1. Provide a personalized exercise plan with 3-5 exercises appropriate for this patient
2. Include clear instructions for each exercise
3. Mention any important safety considerations
4. Set realistic expectations for progress
5. Be encouraging but realistic

CRITICAL SAFETY RULES:
- Always include appropriate disclaimers
- Mention when to stop or seek medical help
- Respect contraindications
- Recommend starting gently and progressing gradually

Provide your response in a warm, supportive tone."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _format_exercises(self, exercise_results):
        """Format exercise search results for prompt"""
        if not exercise_results or not exercise_results['documents']:
            return "No specific exercises retrieved."
        
        formatted = []
        for i, (doc, metadata) in enumerate(zip(
            exercise_results['documents'][0],
            exercise_results['metadatas'][0]
        )):
            formatted.append(f"Exercise {i+1}: {metadata['name']}")
            formatted.append(f"  Difficulty: {metadata['difficulty_level']}/4")
            formatted.append(f"  Category: {metadata['category']}")
            formatted.append(f"  Summary: {doc[:200]}...")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_education(self, education_results):
        """Format education search results for prompt"""
        if not education_results or not education_results['documents']:
            return "No educational content retrieved."
        
        formatted = []
        for doc, metadata in zip(
            education_results['documents'][0],
            education_results['metadatas'][0]
        ):
            formatted.append(f"Topic: {metadata['title']}")
            formatted.append(f"  {doc[:300]}...")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_safety(self, safety_guidelines):
        """Format safety guidelines for prompt"""
        red_flags = safety_guidelines.get('red_flags', [])
        general_rules = safety_guidelines.get('general_safety_rules', [])
        
        formatted = ["RED FLAGS (Stop and seek medical attention):"]
        for flag in red_flags[:3]:
            formatted.append(f"  - {flag['symptom']}: {flag['action']}")
        
        formatted.append("\nGENERAL SAFETY RULES:")
        for rule in general_rules[:5]:
            formatted.append(f"  - {rule}")
        
        return "\n".join(formatted)
    
    def chat(self, user_message, patient_data=None):
        """Main chat interface"""
        # If no patient data, try to extract from message
        if not patient_data:
            patient_data = self.assess_patient(user_message)
        
        # Retrieve relevant context
        context = self.retrieve_context(user_message, patient_data)
        
        # Generate response
        response = self.generate_response(user_message, patient_data, context)
        
        return response

# Usage
api_key = "your-anthropic-api-key"
rag = KneeArthritisRAG(vector_db, loader, api_key)

response = rag.chat(
    "I'm 68 with moderate knee arthritis. What exercises should I start with?"
)
print(response)
```

---

## Testing

### `test_rag.py`

```python
def test_rag_model():
    """Test RAG model with various scenarios"""
    
    # Initialize
    loader = KneeArthritisDataLoader()
    loader.load_all()
    
    vector_db = KneeArthritisVectorDB()
    vector_db.embed_exercises(loader.exercises)
    vector_db.embed_education(loader.education)
    vector_db.embed_qa_pairs(loader.qa_pairs)
    
    rag = KneeArthritisRAG(vector_db, loader, "your-api-key")
    
    # Test cases
    test_queries = [
        "I'm 68 with severe knee arthritis. What exercises should I start?",
        "My knee hurts when going downstairs, can you help?",
        "I've been doing quad sets for 2 weeks. What's next?",
        "Is it normal for my knee to hurt after exercise?",
        "How often should I do these exercises?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        
        response = rag.chat(query)
        print(response)
        print()

# Run tests
test_rag_model()
```

---

## Example Usage

### Basic Usage

```python
from load_data import KneeArthritisDataLoader
from embed_data import KneeArthritisVectorDB
from rag_model import KneeArthritisRAG

# Setup
loader = KneeArthritisDataLoader()
loader.load_all()

vector_db = KneeArthritisVectorDB()
vector_db.embed_exercises(loader.exercises)
vector_db.embed_education(loader.education)
vector_db.embed_qa_pairs(loader.qa_pairs)

rag = KneeArthritisRAG(vector_db, loader, api_key="your-api-key")

# Chat
response = rag.chat(
    "I'm a 70-year-old with moderate knee arthritis. "
    "I can walk but stairs are painful. What should I do?"
)
print(response)
```

### Advanced: Conversation History

```python
class ConversationalRAG(KneeArthritisRAG):
    """RAG with conversation memory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_history = []
        self.patient_data = None
    
    def chat_with_history(self, user_message):
        """Chat with conversation context"""
        # First message: extract patient data
        if not self.patient_data:
            self.patient_data = self.assess_patient(user_message)
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Retrieve context
        context = self.retrieve_context(user_message, self.patient_data)
        
        # Build prompt with history
        response = self.generate_response_with_history(
            user_message, 
            self.patient_data, 
            context,
            self.conversation_history[:-1]  # Exclude current message
        )
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response

# Usage
conversational_rag = ConversationalRAG(vector_db, loader, api_key)

# Multi-turn conversation
print(conversational_rag.chat_with_history(
    "I'm 68 with moderate arthritis, just starting out"
))

print(conversational_rag.chat_with_history(
    "Those exercises are getting easier. What's next?"
))

print(conversational_rag.chat_with_history(
    "What about pain after exercise?"
))
```

---

## Next Steps

1. **Add Error Handling:** Wrap API calls in try-except blocks
2. **Implement Logging:** Track queries and responses for improvement
3. **Add Validation:** Validate patient data and retrieved exercises
4. **Create UI:** Build a simple web interface (Streamlit, Gradio, or React)
5. **Monitor Performance:** Track retrieval accuracy and response quality
6. **Iterate:** Gather feedback and improve prompts and retrieval

---

## Production Considerations

Before deploying to real users:

1. ✅ **Medical Review:** Have licensed professionals review all content
2. ✅ **Legal Review:** Ensure proper disclaimers and liability protection
3. ✅ **Privacy:** Implement HIPAA compliance if storing patient data
4. ✅ **Testing:** Extensive testing with diverse scenarios
5. ✅ **Monitoring:** Track errors, edge cases, and user feedback
6. ✅ **Updates:** Plan for regular content updates and improvements

---

## Troubleshooting

### Common Issues

**Issue:** ChromaDB persistence errors  
**Solution:** Ensure write permissions in persist_directory

**Issue:** Poor retrieval results  
**Solution:** Try different embedding models or adjust n_results

**Issue:** API rate limits  
**Solution:** Implement caching and rate limiting

**Issue:** Out of memory with embeddings  
**Solution:** Process in batches or use smaller embedding model

---

## Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [RAG Best Practices](https://www.anthropic.com/index/contextual-retrieval)

---

**Remember:** This is a starting point for MVP development. Refine based on testing and feedback!
