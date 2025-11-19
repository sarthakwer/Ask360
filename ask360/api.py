"""FastAPI endpoint for Ask360."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ask360.ask360_core import answer

app = FastAPI(title="Ask360 API", version="0.1.0")

# Enable CORS for localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    """Request model for /ask endpoint."""
    question: str


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Answer a natural-language question about FreshFoods yogurt.
    
    Returns the same structure as ask360_core.answer()
    """
    result = answer(request.question)
    return result


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Ask360 API - POST /ask with {'question': 'your question'}"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

