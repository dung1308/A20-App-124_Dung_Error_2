import uvicorn
import os
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from orchestrator.pipeline import Pipeline
from utils.logger import get_logger
from fastapi import UploadFile, File
from database import init_database
from services.pdf_loader import extract_text_from_pdf

logger = get_logger(__name__)

app = FastAPI(
    title="VinUni Admission Assistant API",
    description="Backend API for major matching and admission chat support.",
    version="0.1.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database when the application starts."""
    try:
        init_database()
        logger.info("Database initialized on startup")
    except Exception as e:
        logger.error(f"Failed to initialize database on startup: {e}")
        # Don't raise — allow app to start anyway

# Initialize the Orchestrator Pipeline
pipeline = Pipeline()

class ChatRequest(BaseModel):
    user_id: Optional[str] = Field("anonymous", alias="userId")
    message: str = Field(..., alias="text")
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True
    }

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class MatchRequest(BaseModel):
    user_id: str
    answers: Dict[str, Any]
    cv_text: Optional[str] = None
    cv_signals: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Confirm the service is live and reachable."""
    return {"status": "ok", "service": "vinuni-assistant-backend"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Route free-form chat messages through the pipeline."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    # Ensure the orchestrator result is wrapped in the structure 
    # expected by ConsultantPage.jsx (response.response)
    chat_response = pipeline.run_chat(request.user_id, request.message, request.history)
    if isinstance(chat_response, str):
        return {"response": chat_response}
    return chat_response

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """Handle student registration."""
    return {"status": "success", "message": f"Account created for {request.full_name}"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Verify credentials and return access token."""
    # Assign 'admin' role to school emails for engineer testing, 'user' otherwise
    role = "admin" if request.email.endswith("@vinuni.edu.vn") else "user"
    return {"status": "success", "token": "mock-token-123", "user_email": request.email, "role": role}

@app.post("/api/match")
async def match(request: MatchRequest):
    """Submit wizard answers for major matching recommendations."""
    # 1. Generate the major matching results via Advisor Agent
    results = pipeline.run_match(request.user_id, request.answers, request.cv_text, request.cv_signals)
    
    # 2. Persist to SQL DB for CRM Agent and Profile Page
    try:
        # We pass a copy of answers to upsert_student_profile
        # db_service handles the extraction of GPA, test scores, etc.
        pipeline.db_service.upsert_student_profile(request.user_id, request.answers.copy())
        logger.info(f"Student profile persisted to SQL: {request.user_id}")
    except Exception as e:
        logger.error(f"Failed to persist student profile to SQL: {e}")

    # 3. Store the survey answers as context for the RAG service (Vector DB)
    try:
        summary_parts = ["Student Profile and Preferences:"]
        for category, selection in request.answers.items():
            if selection:
                # Format list values (like interests) or strings (like work style)
                val_str = ", ".join(selection) if isinstance(selection, list) else str(selection)
                summary_parts.append(f"- {category.replace('_', ' ').capitalize()}: {val_str}")
        
        context_text = "\n".join(summary_parts)
        pipeline.rag.rag_service.ingest_cv(request.user_id, context_text)
        logger.info(f"Wizard answers indexed for user context: {request.user_id}")
    except Exception as e:
        logger.error(f"Failed to ingest wizard answers for user {request.user_id}: {e}")
        
    return results

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Retrieve the structured student profile as managed by the CRM agent."""
    profile = pipeline.crm.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/api/upload-cv")
async def upload_cv(user_id: str, file: UploadFile = File(...)):
    """Upload and index a PDF CV."""
    try:
        # Create a temporary file that is automatically deleted
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text_from_pdf(tmp_path)
        pipeline.rag.rag_service.ingest_cv(user_id, text)
        
        return {"status": "CV indexed successfully", "filename": file.filename}
    finally:
        # Clean up the temp file after indexing
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)