"""
CypherIt Backend - Extract 60-second solutions from YouTube videos
Secure, rate-limited API for production use
"""
import os
import re
import json
import subprocess
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, field_validator
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CypherIt API",
    description="TikTok speed. YouTube depth. Extract fixes in 60 seconds.",
    version="0.1.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url=None
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - restrict in production
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable required")
client = Anthropic(api_key=api_key)


class ExtractRequest(BaseModel):
    url: str
    max_steps: int = 5
    
    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v):
        youtube_patterns = [
            r'(youtube\.com|youtu\.be)',
        ]
        if not any(re.search(p, v) for p in youtube_patterns):
            raise ValueError('Must be a valid YouTube URL')
        return v
    
    @field_validator('max_steps')
    @classmethod  
    def validate_max_steps(cls, v):
        if v < 1 or v > 10:
            raise ValueError('max_steps must be between 1 and 10')
        return v


class Step(BaseModel):
    number: int
    action: str
    detail: Optional[str] = None
    timestamp: Optional[str] = None


class ExtractResponse(BaseModel):
    title: str
    problem: str
    steps: List[Step]
    time_to_read: str
    source_url: str


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not extract video ID from URL")


def get_transcript(url: str) -> str:
    """Fetch transcript using the summarize CLI tool."""
    try:
        result = subprocess.run(
            ["summarize", "--extract", url],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Failed to get transcript: {result.stderr}")
        
        transcript = result.stdout.strip()
        
        # Remove the timing footer line
        lines = transcript.split('\n')
        if lines and '·' in lines[-1]:
            lines = lines[:-1]
        
        transcript = '\n'.join(lines)
        if transcript.lower().startswith('transcript:'):
            transcript = transcript[11:].strip()
            
        return transcript
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Transcript extraction timed out")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Transcript service unavailable")


def extract_fix_steps(transcript: str, url: str, max_steps: int = 5) -> dict:
    """Use Claude to extract structured fix steps from transcript."""
    prompt = f"""You are CypherIt, an expert at extracting actionable fix steps from video transcripts.

Given this transcript from a how-to/tutorial video, extract:
1. A clear, short title (what's being taught/fixed)
2. The problem being solved or topic being taught (one sentence)
3. Step-by-step instructions (max {max_steps} key steps, each should be actionable)

Rules:
- Be concise - each step should be ONE clear action
- Use imperative verbs (Open, Click, Navigate, Install, Create, etc.)
- Skip intros/outros/tangents - just the core steps
- Focus on the most important steps if there are many

Transcript:
{transcript[:8000]}

Respond in this exact JSON format (no markdown, just JSON):
{{
    "title": "How to [Do Thing]",
    "problem": "Brief description of what this teaches/fixes",
    "steps": [
        {{"number": 1, "action": "First key action", "detail": "Optional extra context"}},
        {{"number": 2, "action": "Second key action", "detail": null}}
    ]
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.content[0].text.strip()
    
    # Handle potential markdown wrapping
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        lines = [l for l in lines if not l.startswith('```')]
        response_text = '\n'.join(lines)
    
    result = json.loads(response_text)
    result["source_url"] = url
    result["time_to_read"] = f"{len(result['steps']) * 12} seconds"
    return result


@app.get("/")
async def root():
    return {
        "name": "CypherIt API",
        "tagline": "TikTok speed. YouTube depth.",
        "version": "0.1.0",
        "endpoints": {
            "/extract": "POST - Extract fix steps from YouTube URL",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY"))
    }


@app.post("/extract", response_model=ExtractResponse)
@limiter.limit("10/minute")
async def extract(request: Request, body: ExtractRequest):
    """Extract fix steps from a YouTube video URL. Rate limited to 10 requests/minute."""
    # Validate it looks like a YouTube URL
    try:
        extract_video_id(body.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    transcript = get_transcript(body.url)
    
    if len(transcript) < 50:
        raise HTTPException(status_code=400, detail="Transcript too short to extract meaningful steps")
    
    result = extract_fix_steps(transcript, body.url, body.max_steps)
    return ExtractResponse(**result)


@app.post("/demo")
@limiter.limit("20/minute")
async def demo_extract(request: Request):
    """Demo endpoint with sample output (no API call needed)."""
    return {
        "title": "How to Fix iPhone Not Charging",
        "problem": "iPhone shows connected but won't charge past current percentage",
        "steps": [
            {"number": 1, "action": "Check the Lightning port for debris", "detail": "Use a flashlight to inspect, gently clean with wooden toothpick", "timestamp": "0:32"},
            {"number": 2, "action": "Try a different cable and power adapter", "detail": "Eliminates cable/adapter as the issue", "timestamp": "1:15"},
            {"number": 3, "action": "Force restart your iPhone", "detail": "Hold Volume Down + Side button until Apple logo appears", "timestamp": "2:08"},
            {"number": 4, "action": "Reset all settings", "detail": "Settings > General > Reset > Reset All Settings", "timestamp": "3:22"},
            {"number": 5, "action": "Contact Apple Support if issue persists", "detail": "May indicate hardware failure", "timestamp": "4:45"}
        ],
        "time_to_read": "60 seconds",
        "source_url": "https://youtube.com/watch?v=demo123"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
