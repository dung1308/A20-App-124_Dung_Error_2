# Backend Implementation & Troubleshooting Guide: VinUni Major Match

This guide provides targeted prompts for Gemini Code Assist to build, evaluate, and troubleshoot the FastAPI backend, ensuring alignment with the security standards and architecture defined in `CODE_REVIEW_SUMMARY.md`.

## 🚀 MVP Development Prompts

### 1. Implement the Core Match Endpoint
> "Based on `PRD.md` and the `VINUNI_MAJORS` data, implement the `POST /api/match` endpoint in `main.py`. Ensure it accepts the `answers` schema, uses a dedicated `MajorMatchAgent` to process logic via Gemini 1.5 Flash, and returns the structured JSON response including `top3` matches and the `fallback` flag."

### 2. Create the Major Match Agent
> "Create a `MajorMatchAgent` class in `agents.py`. This agent should take the student's interests, strengths, and dislikes, compare them against the `VINUNI_MAJORS` constants, and generate a personalized `match_reason` for each of the top 3 majors. Use a strict system prompt to ensure the output is valid JSON."

### 3. Extend Database Models for Sessions
> "Modify `models.py` to add a `MajorMatchSession` table. It should store the `session_id` (UUID), the raw `answers` JSON, and the final AI `result`. Update `database.py` to ensure this new model is initialized on startup."

## 🛡️ Evaluation & Security Prompts

### 4. Verify Safety Judge Fail-Safes
> "Evaluate the `evaluate` function in `guardrails/judge.py`. Verify that it implements the 'Fail-safe REJECTS' logic from the Code Review Summary, ensuring that any LLM error or timeout during safety checking results in a `pass: False` response to prevent leaked unsafe content."

### 5. Audit PII Redaction
> "Review the `redact` function in `guardrails/output_guard.py`. Test it against Vietnamese-specific PII formats, such as phone numbers starting with '0' or '+84' and common ID formats. Suggest improvements to the regex patterns to ensure no student data is leaked in logs."

### 6. Stress Test Rate Limiting
> "Analyze `guardrails/rate_limiter.py` for potential memory leaks. Specifically, verify if the `_cleanup_old_entries` method effectively handles thousands of unique `user_id` entries as described in the P1 fix of the code review. Suggest a strategy to move this to Redis for production scalability."

### 7. Evaluate Intent Routing Accuracy
> "Evaluate the `llm_router.py` logic. Provide a set of 5 test prompts (e.g., 'Tôi muốn tìm ngành học', 'GPA của tôi là 3.5') and check if the router correctly assigns them to 'advisor', 'crm', or 'rag' agents. Suggest improvements to the routing system prompt."

## 🛠️ Troubleshooting Prompts

### 8. Debug Database Connection Issues
> "I am encountering a `SQLAlchemy` connection error in `database.py`. Help me troubleshoot the `DATABASE_URL` parsing logic and ensure that the engine correctly handles connection pooling and 'server closed the connection' errors common in Docker environments."

### 9. Troubleshoot Orchestrator Context Loss
> "The `Orchestrator` is losing message history when switching between the `RAGAgent` and `AdvisorAgent`. Debug the conversation history retrieval in `orchestrator.py` to ensure the full context is passed to the LLM on every turn."

### 10. Fix Gemini API Timeouts
> "The backend is hanging when the Gemini API is slow. Implement an async timeout for the `get_gemini_model` calls in `config.py` and ensure the main `chat` endpoint returns a friendly 'Hệ thống đang bận' message instead of a 500 error."

## 📝 Implementation Notes
- **Hinge Rule:** Always use `config.get_gemini_model()` to instantiate models; do not initialize the SDK in individual agent files.
- **Logging:** Ensure every agent uses the centralized `logger` for debugging.
- **Types:** Maintain strict Pydantic models for all Request/Response bodies in `main.py`.
```

### Key Considerations Included:

<!--
[PROMPT_SUGGESTION]Generate a React component for the Major Match Wizard using the Copilot_guide.md specifications.[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Create the FastAPI endpoint in main.py to handle the /api/match request as described in the PRD and Copilot_guide.[/PROMPT_SUGGESTION]
