# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+
- PostgreSQL (hoặc Docker)
- Git

## 1️⃣ Setup Database

### Option A: Docker (Recommended)
```bash
docker run -d \
  --name recruitment_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=recruitment_db \
  -p 5432:5432 \
  postgres:15
```

### Option B: Local PostgreSQL
```bash
# Create database
createdb recruitment_db
createuser admin -P  # Then enter password
```

## 2️⃣ Configure Environment

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://admin:secure_password@localhost:5432/recruitment_db

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
REDIS_URL=redis://localhost:6379/0
HUMAN_WEBHOOK=http://localhost:9000/handoff
ENVIRONMENT=development
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60

# LLM Cost Budget
DAILY_LLM_BUDGET=100
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Run Application

```bash
# Development (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 5️⃣ Test the System

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_001",
    "message": "Trường có ngành Công nghệ thông tin không?"
  }'
```

### Get User History
```bash
curl http://localhost:8000/user/student_001/history
```

### Get User Profile
```bash
curl http://localhost:8000/user/student_001/profile
```

### Get System Metrics
```bash
curl http://localhost:8000/metrics
```

## 📚 API Documentation

Interactive API docs available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📊 Monitoring

Monitor file: `audit_log.json`
Contains all system events with timestamps.

## 🐛 Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG uvicorn main:app --reload
```

## 📦 Project Structure

```
app/
├── main.py                  # FastAPI app entry point
├── config.py               # Configuration management
├── models.py               # SQLAlchemy ORM models
├── database.py             # Database connection
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
│
├── agents.py               # RAG, CRM, Advisor agents
├── orchestrator.py         # Agent coordination
├── llm_router.py           # Intent routing
├── raq.py                  # RAG system
├── crm.py                  # Student profiles
├── memory.py               # Conversation history
├── sentiment.py            # Sentiment analysis
│
├── guardrails/             # Security guardrails
│   ├── rate_limiter.py
│   ├── input_guard.py
│   ├── output_guard.py
│   ├── judge.py            # Safety evaluation (FAIL-SAFE)
│   ├── anomaly.py
│   ├── audit.py
│   └── monitoring.py
│
└── CODE_REVIEW_SUMMARY.md  # Detailed review report
```

## 🔐 Security Features

✅ **Rate Limiting** - 10 requests/min per user  
✅ **Input Validation** - Max 5000 chars, injection detection  
✅ **Output Redaction** - PII masked (SSN, email, phone)  
✅ **Anomaly Detection** - Flags suspicious patterns  
✅ **Audit Logging** - All events recorded  
✅ **Judge Safety** - Fail-safe rejects unsafe responses  

## 📞 Support

For issues or questions:
1. Check `audit_log.json` for event details
2. Review system logs: `LOG_LEVEL=DEBUG`
3. Verify `.env` configuration
4. Check database connectivity: `curl http://localhost:8000/health`

## 🎯 Next Steps

- [ ] Load training data: `train-00000-of-00001.parquet`
- [ ] Configure production database
- [ ] Setup CORS for frontend domain
- [ ] Deploy to production (Docker/Kubernetes)
- [ ] Setup monitoring (Sentry, DataDog)
- [ ] Add unit tests
- [ ] Setup CI/CD pipeline
