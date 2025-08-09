# SkinSage - Personalized Skincare Analyzer

SkinSage is an AI-powered skincare analysis platform that provides personalized product recommendations, ingredient analysis, and skincare routines tailored to your unique skin profile.
## Features 
- **Product Analysis**: Upload product images or search by name for instant ingredient analysis
- **Personalized Routine**: AI-generated AM/PM skincare routines
- **Product Comparison**: Compare two products side-by-side
- **Skin Profile**: Save your skin type and concerns for personalized results
- **AI Assistant**: Chat with skincare expert AI

## Tech Stack 🚀
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **Database**: MongoDB (Docker)
- **AI Services**: Groq API
- **OCR**: SpaceOCR
- **Web Scraping**: BeautifulSoup

## How It Works 🛠

## Getting Started

### Running the Application

```bash
# 1) Install dependencies

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt

# 2) Start MongoDB with Docker
cd ../backend
docker compose up -d

# 3) Run the Backend (FastAPI)
uvicorn backend.app.main:app --reload --port 8000

# 4) Run the Frontend (Streamlit) in a NEW terminal
cd frontend
streamlit run main.py

