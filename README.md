# 🦵 Knee Arthritis Exercise Guide

AI-powered personalized exercise coach for knee arthritis patients.

## Features

- 🤖 AI-powered exercise recommendations
- 📋 Personalized exercise plans
- 💬 Interactive chat interface
- 📊 Progress tracking
- ⚠️ Safety-first approach

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your data files to the `data/` folder
4. Run: `streamlit run app.py`
5. Enter your OpenAI API key in the sidebar

## Data Files Required

Place these JSON files in the `data/` folder:
- exercises_detailed_20.json
- knee_arthritis_education.json
- knee_arthritis_qa.json
- knee_arthritis_patients.json
- knee_arthritis_safety.json
- knee_arthritis_progressions.json

## Deployment

### Deploy to Streamlit Cloud:

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `OPENAI_API_KEY` to secrets
5. Deploy!

## Disclaimer

⚠️ This tool provides educational information only. Always consult your healthcare provider before starting any exercise program.

## License

MIT License
