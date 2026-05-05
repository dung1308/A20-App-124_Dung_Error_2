# VinUni Backend Quick Start Guide

This guide helps you set up and run the VinUni Admission Assistant backend.

## 1. Prerequisites
- Python 3.9 or higher
- `pip` (Python package installer)

## 2. Environment Setup

Navigate to the backend directory and create a virtual environment:

```bash
cd backend
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install fastapi uvicorn python-dotenv sqlalchemy google-generativeai pydantic python-multipart
```

## 3. Configuration

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_api_key_here
USE_MOCK=True
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./vinuni_match.db
```

### Key Setting: `USE_MOCK`
- **`USE_MOCK=True` (Default for Dev)**: No Gemini API key required. Uses local keyword search and deterministic responses. Ideal for frontend development and testing logic.
- **`USE_MOCK=False`**: Connects to Google Gemini. Requires a valid `GEMINI_API_KEY`.

## 4. Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`.

## 5. Verification
- **Health Check**: Visit `http://localhost:8000/health` to confirm the service is live.
- **API Docs**: Explore the interactive Swagger UI at `http://localhost:8000/docs`.
- **Mock Test**: Try a POST request to `/api/chat` with `{"user_id": "test", "message": "Chào bạn"}` to see the mock response.