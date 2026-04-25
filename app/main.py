"""
Smart Recruitment Chatbot API
FastAPI application for student recruitment and guidance.
"""

import logging
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from database import init_db, get_db, health_check
from raq import RAGSystem
from crm import CRM
from sentiment import SentimentModel
from agents import RAGAgent, CRMAgent, AdvisorAgent
from orchestrator import Orchestrator
from memory import Memory
from human_fullback import send_to_human
from guardrails.rate_limiter import RateLimiter
from guardrails.input_guard import check_input
from guardrails.anomaly import SessionAnomaly
from guardrails.output_guard import redact, sanitize
from guardrails.judge import evaluate
from guardrails.audit import AuditLogger
from guardrails.monitoring import Monitoring
from config import ENVIRONMENT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Recruitment System",
    description="AI-powered student recruitment and guidance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize security/monitoring components
rate_limiter = RateLimiter()
anomaly = SessionAnomaly()
audit = AuditLogger()
monitor = Monitoring()

# Initialize models (lazy loaded)
rag = None
crm = None
sentiment = None
orchestrator = None


def init_models():
    """Initialize ML models and components"""
    global rag, crm, sentiment, orchestrator
    
    try:
        logger.info("Initializing models...")
        rag = RAGSystem("train-00000-of-00001.parquet")
        crm = CRM
        sentiment = SentimentModel()
        
        rag_agent = RAGAgent(rag)
        crm_agent = CRMAgent(crm)
        advisor_agent = AdvisorAgent()
        
        orchestrator = Orchestrator(rag_agent, crm_agent, advisor_agent, sentiment)
        logger.info("Models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        raise


# Request/Response models
class Req(BaseModel):
    """Chat request model"""
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User identifier"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User message"
    )
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user_id format"""
        if not all(c.isalnum() or c in '_-' for c in v):
            raise ValueError("user_id must be alphanumeric with - or _")
        return v


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    user_id: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    code: str
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize database and models on startup"""
    try:
        logger.info("Starting up Smart Recruitment System...")
        init_db()
        init_models()
        
        # Verify database connectivity
        if not health_check():
            logger.error("Database health check failed!")
        else:
            logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "database": health_check()
    }


@app.get("/metrics")
def metrics():
    """Get system metrics"""
    return monitor.report()


@app.post("/chat", response_model=ChatResponse)
def chat(req: Req, db: Session = Depends(get_db)):
    """
    Process user message and return AI response.
    
    Includes:
    - Rate limiting
    - Input validation
    - Anomaly detection
    - LLM processing
    - Output safety checks
    - Audit logging
    
    Args:
        req: Chat request
        db: Database session
        
    Returns:
        ChatResponse with AI-generated message
    """
    user_id = req.user_id
    message = req.message
    
    try:
        logger.info(f"Processing chat for user {user_id}")
        
        # 1. Rate limiting
        allowed, reason = rate_limiter.allow(user_id)
        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            monitor.record("rate_limit", user_id)
            return ChatResponse(
                response="Bạn gửi quá nhiều yêu cầu, vui lòng thử lại sau.",
                user_id=user_id,
                timestamp=audit._get_timestamp()
            )
        
        # 2. Input guard - validate for security threats
        ok, reason = check_input(message)
        if not ok:
            logger.warning(f"Input blocked for user {user_id}: {reason}")
            monitor.record("block", user_id, {"reason": reason})
            anomaly.flag(user_id, reason, {"message": message[:100]})
            
            return ChatResponse(
                response=f"Yêu cầu bị chặn ({reason}). Vui lòng kiểm tra lại.",
                user_id=user_id,
                timestamp=audit._get_timestamp()
            )
        
        # 3. Session anomaly check
        if anomaly.is_suspicious(user_id):
            logger.warning(f"Suspicious session detected for user {user_id}")
            monitor.record("anomaly", user_id)
            return ChatResponse(
                response="Session của bạn có dấu hiệu bất thường. Vui lòng liên hệ với chúng tôi.",
                user_id=user_id,
                timestamp=audit._get_timestamp()
            )
        
        # 4. Get conversation history
        memory = Memory(db)
        history = memory.get(user_id)
        
        # 5. Process through orchestrator (LLM)
        try:
            if orchestrator is None:
                logger.error("Orchestrator not initialized!")
                raise RuntimeError("System not ready")
            
            response = orchestrator.run(user_id, message, history)
            
            # Save user message to history
            memory.add(user_id, message, role="user")
            
        except Exception as e:
            logger.error(f"Orchestrator error for user {user_id}: {e}")
            monitor.record("llm_error", user_id, {"error": str(e)})
            return ChatResponse(
                response="Xin lỗi, hệ thống gặp lỗi. Vui lòng thử lại.",
                user_id=user_id,
                timestamp=audit._get_timestamp()
            )
        
        # 6. Output guard - redact sensitive info
        response = redact(response)
        response = sanitize(response)
        
        # 7. Safety evaluation (Judge)
        judge_result = evaluate(message, response)
        
        if not judge_result.get("pass", False):
            logger.warning(
                f"Judge rejected response for user {user_id}: "
                f"{judge_result.get('reason', 'unknown')}"
            )
            monitor.record("judge_fail", user_id, judge_result)
            response = "Xin lỗi, tôi chưa thể trả lời câu hỏi này một cách an toàn."
        else:
            monitor.record("success", user_id)
        
        # 8. Save assistant message to history
        memory.add(user_id, response, role="assistant")
        
        # 9. Audit logging
        audit.log({
            "user": user_id,
            "input": message,
            "output": response,
            "judge": judge_result
        })
        
        logger.info(f"Chat completed successfully for user {user_id}")
        
        return ChatResponse(
            response=response,
            user_id=user_id,
            timestamp=audit._get_timestamp()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        monitor.record("error", user_id, {"error": str(e)})
        
        return ChatResponse(
            response="Xin lỗi, hệ thống gặp lỗi không mong muốn.",
            user_id=user_id,
            timestamp=audit._get_timestamp()
        )


@app.get("/user/{user_id}/history")
def get_history(user_id: str, db: Session = Depends(get_db)):
    """
    Get conversation history for a user.
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        List of conversation messages
    """
    try:
        memory = Memory(db)
        history = memory.get_full_history(user_id)
        return {
            "user_id": user_id,
            "history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving history for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history"
        )


@app.get("/user/{user_id}/profile")
def get_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Get student profile from CRM.
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        Student profile information
    """
    try:
        crm_instance = CRM(db)
        profile = crm_instance.get_or_create(user_id)
        return profile
    except Exception as e:
        logger.error(f"Error retrieving profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@app.delete("/user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete user data (GDPR right to be forgotten).
    
    Args:
        user_id: User identifier
        db: Database session
        
    Returns:
        Confirmation
    """
    try:
        memory = Memory(db)
        memory.clear(user_id)
        
        crm_instance = CRM(db)
        crm_instance.delete(user_id)
        
        logger.info(f"Deleted user data for {user_id}")
        return {"message": f"User {user_id} data deleted", "status": "success"}
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


# Root endpoint
@app.get("/")
def root():
    """API documentation"""
    return {
        "name": "Smart Recruitment Chatbot",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send chat message",
            "GET /health": "Health check",
            "GET /metrics": "System metrics",
            "GET /user/{user_id}/history": "Get chat history",
            "GET /user/{user_id}/profile": "Get student profile",
            "DELETE /user/{user_id}": "Delete user data"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
