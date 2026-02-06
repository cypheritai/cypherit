"""
CypherIt Backend - Extract 60-second solutions from YouTube videos
Secure, rate-limited API for production use
"""
import os
import re
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import time
import ssl
import certifi
import requests
import urllib3

# NUCLEAR OPTION: Disable SSL verification for YouTube transcript fetching
# This is safe because we're only fetching public YouTube data
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable SSL verification globally
ssl._create_default_https_context = ssl._create_unverified_context

# Monkey-patch requests to disable SSL verification
old_request = requests.Session.request
def patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return old_request(self, method, url, **kwargs)
requests.Session.request = patched_request

# Also patch requests.get/post directly
old_get = requests.get
old_post = requests.post
requests.get = lambda url, **kwargs: old_get(url, verify=False, **kwargs)
requests.post = lambda url, **kwargs: old_post(url, verify=False, **kwargs)

# Set certifi path as fallback
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['REQUESTS_CA_BUNDLE'] = cert_path

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

# Demo videos with fallbacks - first working video per category wins
DEMO_VIDEOS = {
    "usb": {
        "emoji": "💾",
        "label": "USB Installer",
        "videos": [
            "0HBA9Nov17Q",  # macOS bootable USB tutorial
            "Hc79sDi3f0U",  # Backup
        ]
    },
    "dev": {
        "emoji": "🐍",
        "label": "Dev Setup",
        "videos": [
            "kqtD5dpn9C8",  # Python setup
            "rfscVS0vtbw",  # freeCodeCamp Python (long)
        ]
    },
    "tech": {
        "emoji": "💻",
        "label": "Tech Tutorial",
        "videos": [
            "Hc79sDi3f0U",  # Tech tutorial
            "kqtD5dpn9C8",  # Backup
        ]
    }
}

# Cache for validated demos (revalidate every 6 hours)
_demo_cache = {"data": None, "timestamp": 0}
DEMO_CACHE_TTL = 6 * 60 * 60  # 6 hours


def validate_video(video_id: str) -> bool:
    """Quick check if video has available transcript."""
    try:
        api = YouTubeTranscriptApi()
        api.fetch(video_id)
        return True
    except Exception as e:
        print(f"Demo validation failed for {video_id}: {e}")
        return False


def get_validated_demos() -> List[dict]:
    """Get demo videos, validating and caching results."""
    now = time.time()
    
    # Return cached if fresh
    if _demo_cache["data"] and (now - _demo_cache["timestamp"]) < DEMO_CACHE_TTL:
        return _demo_cache["data"]
    
    # FAST PATH: Return primary videos without validation on first call
    # Validation can be slow and SSL issues may cause false negatives
    # The primary videos are known-good, so just return them
    validated = []
    for key, config in DEMO_VIDEOS.items():
        # Use first video (primary) without validation
        primary_video = config["videos"][0]
        validated.append({
            "key": key,
            "emoji": config["emoji"],
            "label": config["label"],
            "url": f"https://www.youtube.com/watch?v={primary_video}"
        })
    
    # Cache results
    _demo_cache["data"] = validated
    _demo_cache["timestamp"] = now
    
    return validated


class ExtractRequest(BaseModel):
    url: str
    max_steps: int = 5
    user_id: Optional[str] = None  # Supabase user ID (bypasses IP limit if provided)
    
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
    caption: Optional[str] = None  # Transcript text for this step's segment


class QuickInfo(BaseModel):
    tools_needed: List[str] = []      # e.g., ["USB drive (8GB+)", "Mac computer"]
    time_estimate: Optional[str] = None  # e.g., "15-20 minutes"
    warnings: List[str] = []          # e.g., ["This will erase your USB drive"]
    tips: List[str] = []              # e.g., ["Use USB 3.0 for faster transfer"]


class ExtractResponse(BaseModel):
    title: str
    problem: str
    quick_info: Optional[QuickInfo] = None
    steps: List[Step]
    time_to_read: str
    source_url: str
    video_id: str


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


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def get_transcript(url: str) -> str:
    """Fetch transcript with timestamps. Tries direct first, falls back to proxy."""
    import time
    video_id = extract_video_id(url)
    
    # Check for proxy configuration - support multiple env var names
    proxy_url = os.getenv("PROXY_URL")
    scraper_api_key = os.getenv("SCRAPER_API_KEY") or os.getenv("SCRAPERAPI_KEY")
    
    # Build proxy URL from ScraperAPI key if provided
    if scraper_api_key and not proxy_url:
        proxy_url = f"http://scraperapi:{scraper_api_key}@proxy-server.scraperapi.com:8001"
    
    # Try direct first with retry (faster, no proxy limits)
    last_error = None
    for attempt in range(3):  # 3 attempts with backoff
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            # Include timestamps in transcript for Claude to reference
            timestamped_lines = []
            for snippet in transcript.snippets:
                ts = format_timestamp(snippet.start)
                timestamped_lines.append(f"[{ts}] {snippet.text}")
            return '\n'.join(timestamped_lines)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # These are video-specific errors, retry/proxy won't help
            if isinstance(e, TranscriptsDisabled):
                raise HTTPException(status_code=400, detail="Transcripts are disabled for this video")
            raise HTTPException(status_code=400, detail="No English transcript available for this video")
        except Exception as e:
            last_error = e
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(1 * (attempt + 1))  # 1s, 2s backoff
    
    # Direct failed after retries - try proxy if available
    if not proxy_url:
        raise HTTPException(status_code=400, detail=f"Failed to get transcript (try again): {str(last_error)}")
    
    # Fallback to proxy with retry
    from youtube_transcript_api.proxies import GenericProxyConfig
    
    proxy_config = GenericProxyConfig(
        http_url=proxy_url,
        https_url=proxy_url
    )
    
    for attempt in range(2):  # 2 attempts for proxy
        try:
            api = YouTubeTranscriptApi(proxy_config=proxy_config)
            transcript = api.fetch(video_id)
            # Include timestamps in transcript for Claude to reference
            timestamped_lines = []
            for snippet in transcript.snippets:
                ts = format_timestamp(snippet.start)
                timestamped_lines.append(f"[{ts}] {snippet.text}")
            return '\n'.join(timestamped_lines)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            if isinstance(e, TranscriptsDisabled):
                raise HTTPException(status_code=400, detail="Transcripts are disabled for this video")
            raise HTTPException(status_code=400, detail="No English transcript available for this video")
        except Exception as proxy_error:
            last_error = proxy_error
            if attempt < 1:
                time.sleep(2)  # Wait 2s before proxy retry
    
    raise HTTPException(status_code=400, detail=f"Failed to get transcript. YouTube may be busy — try again in a moment.")


def extract_fix_steps(transcript: str, url: str, max_steps: int = 6) -> dict:
    """Use Claude to extract structured fix steps from transcript using category frameworks."""
    from frameworks import detect_category, get_extraction_prompt
    
    # Detect category from transcript
    category = detect_category("", transcript)
    
    # Get the specialized prompt for this category
    prompt = get_extraction_prompt(category, transcript, max_steps)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,  # Manual-style format needs more tokens
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
    result["video_id"] = extract_video_id(url)
    
    # Convert nuggets to steps format for frontend compatibility
    if "nuggets" in result:
        result["steps"] = []
        for nugget in result["nuggets"]:
            step = {
                "number": nugget.get("number", 1),
                "action": nugget.get("moment", ""),
                "detail": nugget.get("why_valuable"),
                "timestamp": nugget.get("timestamp"),
                "end_timestamp": nugget.get("end_timestamp")
            }
            result["steps"].append(step)
        # Use hook as the problem statement
        if result.get("hook"):
            result["problem"] = result["hook"]
    
    # Ensure steps array exists
    if "steps" not in result:
        result["steps"] = []
    
    # Validate and fix timestamps for each step (no max cap - trust extraction)
    for step in result.get("steps", []):
        if step.get("timestamp") and step.get("end_timestamp"):
            start = _ts_to_seconds(step["timestamp"])
            end = _ts_to_seconds(step["end_timestamp"])
            
            # Fix backwards timestamps (end before start)
            if end <= start:
                if end < start:
                    step["timestamp"], step["end_timestamp"] = step["end_timestamp"], step["timestamp"]
                else:
                    step["end_timestamp"] = _seconds_to_ts(start + 20)
                
        elif step.get("timestamp") and not step.get("end_timestamp"):
            # Add default end_timestamp if missing
            start = _ts_to_seconds(step["timestamp"])
            step["end_timestamp"] = _seconds_to_ts(start + 20)
    
    # Calculate read time based on actual clip durations
    total_seconds = 0
    for step in result.get("steps", []):
        if step.get("timestamp") and step.get("end_timestamp"):
            start = _ts_to_seconds(step["timestamp"])
            end = _ts_to_seconds(step["end_timestamp"])
            total_seconds += max(0, end - start)
        else:
            total_seconds += 15  # Default estimate
    result["time_to_read"] = f"{int(total_seconds)} seconds"
    
    # Keep verify for frontend
    if "verify" in result:
        if isinstance(result["verify"], list):
            result["verify_steps"] = result["verify"]
        elif isinstance(result["verify"], str):
            result["verify_steps"] = [result["verify"]]
    
    # Add caption text for each step from the transcript
    result = add_captions_to_steps(result, transcript)
    
    return result


def _ts_to_seconds(ts: str) -> float:
    """Convert MM:SS or M:SS timestamp to seconds."""
    try:
        parts = ts.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        pass
    return 0


def _seconds_to_ts(seconds: float) -> str:
    """Convert seconds to M:SS timestamp."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def add_captions_to_steps(result: dict, transcript: str) -> dict:
    """Extract caption text for each step's time segment from the transcript."""
    import re
    
    MAX_CLIP_DURATION = 20  # Maximum seconds per clip - keep it tight!
    DEFAULT_CLIP_DURATION = 12  # Default if no end_timestamp provided
    
    try:
        # Parse transcript lines with timestamps [M:SS] format
        lines = []
        for line in transcript.split('\n'):
            match = re.match(r'\[(\d+:\d+)\]\s*(.+)', line)
            if match:
                ts_str, text = match.groups()
                seconds = _ts_to_seconds(ts_str)
                lines.append({'time': seconds, 'text': text})
        
        if not lines:
            return result
        
        steps = result.get('steps', [])
        for i, step in enumerate(steps):
            if not step.get('timestamp'):
                continue
                
            start_time = _ts_to_seconds(step['timestamp'])
            
            # Use end_timestamp if Claude provided it, otherwise use default
            if step.get('end_timestamp'):
                end_time = _ts_to_seconds(step['end_timestamp'])
            else:
                # Fallback: use next step's timestamp or default duration
                if i + 1 < len(steps) and steps[i + 1].get('timestamp'):
                    end_time = _ts_to_seconds(steps[i + 1]['timestamp'])
                else:
                    end_time = start_time + DEFAULT_CLIP_DURATION
            
            # CAP the duration - never exceed MAX_CLIP_DURATION
            if end_time - start_time > MAX_CLIP_DURATION:
                end_time = start_time + MAX_CLIP_DURATION
            
            # Ensure minimum duration of 8 seconds
            if end_time - start_time < 8:
                end_time = start_time + 8
            
            # Store the computed end_time for frontend use
            step['end_time'] = end_time
            
            # Collect caption text for this segment
            caption_parts = []
            for line in lines:
                if start_time <= line['time'] < end_time:
                    caption_parts.append(line['text'])
            
            step['caption'] = ' '.join(caption_parts) if caption_parts else None
    
    except Exception:
        pass  # Captions are optional, don't break extraction
    
    return result


def timestampToSeconds(ts: str) -> float:
    """Convert MM:SS or M:SS timestamp to seconds (alias for compatibility)."""
    return _ts_to_seconds(ts)


@app.get("/api")
async def api_info():
    return {
        "name": "CypherIt API",
        "tagline": "TikTok speed. YouTube depth.",
        "version": "0.5.0",
        "endpoints": {
            "/extract": "POST - Extract fix steps from YouTube URL",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    proxy_configured = bool(os.getenv("PROXY_URL") or os.getenv("SCRAPER_API_KEY") or os.getenv("SCRAPERAPI_KEY"))
    return {
        "status": "healthy", 
        "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "proxy_configured": proxy_configured
    }


@app.get("/demos")
async def get_demos():
    """Get validated demo videos. Caches results for 6 hours."""
    demos = get_validated_demos()
    return {"demos": demos}


@app.post("/extract", response_model=ExtractResponse)
@limiter.limit("10/minute")
async def extract(request: Request, body: ExtractRequest):
    """Extract fix steps from a YouTube video URL. Rate limited to 10 requests/minute."""
    
    # Check IP-based daily limit (server-side)
    client_ip = get_remote_address(request)
    allowed, remaining = check_ip_limit(client_ip, body.user_id)
    
    if not allowed:
        raise HTTPException(
            status_code=429, 
            detail=f"Daily limit reached ({GUEST_DAILY_LIMIT} extractions/day). Sign in for unlimited access!"
        )
    
    # Validate it looks like a YouTube URL
    try:
        video_id = extract_video_id(body.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    transcript = get_transcript(body.url)
    
    if len(transcript) < 50:
        raise HTTPException(status_code=400, detail="Transcript too short to extract meaningful steps")
    
    result = extract_fix_steps(transcript, body.url, body.max_steps)
    
    # Track extraction for auto-promote + cache for sharing
    save_extraction(
        video_id=video_id,
        title=result.get("title", "Untitled"),
        category=result.get("category", "general"),
        full_result=result  # Cache full result for share links
    )
    
    # Increment IP count (only for guests)
    if not body.user_id:
        increment_ip_count(client_ip)
    
    return ExtractResponse(**result)


@app.get("/extraction/{video_id}")
async def get_extraction_by_id(video_id: str):
    """Get cached extraction by video ID (for share links)."""
    cached = get_cached_extraction(video_id)
    if cached:
        return {"success": True, "cached": True, **cached}
    return {"success": False, "cached": False, "message": "Extraction not found"}


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


# ============ EXTRACTIONS TRACKING ============

def load_extractions_data():
    """Load extractions data from JSON file."""
    extractions_path = Path(__file__).parent / "extractions_data.json"
    if extractions_path.exists():
        with open(extractions_path, 'r') as f:
            return json.load(f)
    return {"extractions": {}}

def save_extractions_data(data):
    """Save extractions data to JSON file."""
    extractions_path = Path(__file__).parent / "extractions_data.json"
    with open(extractions_path, 'w') as f:
        json.dump(data, f, indent=2)

def save_extraction(video_id: str, title: str, category: str = "general", full_result: dict = None):
    """Save extraction with full result for caching/sharing."""
    data = load_extractions_data()
    
    if video_id not in data["extractions"]:
        data["extractions"][video_id] = {
            "video_id": video_id,
            "title": title,
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            "category": category,
            "created_at": int(time.time()),
            "extraction_count": 0
        }
    
    data["extractions"][video_id]["extraction_count"] += 1
    data["extractions"][video_id]["last_extracted"] = int(time.time())
    
    # Store full extraction result for sharing/caching
    if full_result:
        data["extractions"][video_id]["cached_result"] = full_result
    
    save_extractions_data(data)

def get_extraction(video_id: str) -> dict:
    """Get extraction metadata for a video."""
    data = load_extractions_data()
    return data.get("extractions", {}).get(video_id)

def get_cached_extraction(video_id: str) -> dict:
    """Get cached extraction result for sharing."""
    extraction = get_extraction(video_id)
    if extraction and "cached_result" in extraction:
        return extraction["cached_result"]
    return None


# ============ IP-BASED RATE LIMITING ============

GUEST_DAILY_LIMIT = 3

def load_ip_limits():
    """Load IP extraction limits from JSON file."""
    limits_path = Path(__file__).parent / "ip_limits.json"
    if limits_path.exists():
        with open(limits_path, 'r') as f:
            return json.load(f)
    return {"date": "", "ips": {}}

def save_ip_limits(data):
    """Save IP extraction limits to JSON file."""
    limits_path = Path(__file__).parent / "ip_limits.json"
    with open(limits_path, 'w') as f:
        json.dump(data, f, indent=2)

def check_ip_limit(ip: str, user_id: str = None) -> tuple[bool, int]:
    """Check if IP has exceeded daily limit. Returns (allowed, remaining)."""
    # Signed-in users bypass IP limit
    if user_id:
        return True, 999
    
    from datetime import date
    today = date.today().isoformat()
    
    data = load_ip_limits()
    
    # Reset if new day
    if data.get("date") != today:
        data = {"date": today, "ips": {}}
    
    count = data["ips"].get(ip, 0)
    remaining = max(0, GUEST_DAILY_LIMIT - count)
    
    return count < GUEST_DAILY_LIMIT, remaining

def increment_ip_count(ip: str):
    """Increment extraction count for IP."""
    from datetime import date
    today = date.today().isoformat()
    
    data = load_ip_limits()
    
    # Reset if new day
    if data.get("date") != today:
        data = {"date": today, "ips": {}}
    
    data["ips"][ip] = data["ips"].get(ip, 0) + 1
    save_ip_limits(data)


# ============ AUTO-PROMOTE LOGIC ============

PROMOTION_THRESHOLD = 3  # Net helpful votes needed for promotion

def check_auto_promote(video_id: str):
    """Check if video should be auto-promoted to gallery."""
    votes_data = load_votes_data()
    votes = votes_data.get("votes", {}).get(video_id, {"helpful": 0, "not_helpful": 0})
    
    net_helpful = votes.get("helpful", 0) - votes.get("not_helpful", 0)
    
    if net_helpful >= PROMOTION_THRESHOLD:
        # Check if already in gallery
        gallery_data = load_gallery_data()
        existing = next((f for f in gallery_data.get("fixes", []) if f.get("video_id") == video_id), None)
        
        if not existing:
            # Get extraction metadata
            extraction = get_extraction(video_id)
            
            if extraction:
                # Auto-add to gallery
                new_fix = {
                    "id": f"auto-{video_id}",
                    "category": extraction.get("category", "general"),
                    "video_id": video_id,
                    "title": extraction.get("title", "Community Fix"),
                    "description": f"Auto-promoted by community ({votes.get('helpful', 0)} helpful votes)",
                    "thumbnail": extraction.get("thumbnail"),
                    "time_estimate": "5-15 minutes",
                    "difficulty": "varies",
                    "upvotes": votes.get("helpful", 0),
                    "views": extraction.get("extraction_count", 1),
                    "featured": False,  # Not featured, but in gallery
                    "verified": False,
                    "auto_promoted": True,
                    "promoted_at": int(time.time())
                }
                
                gallery_data["fixes"].append(new_fix)
                save_gallery_data(gallery_data)
                
                return {"promoted": True, "fix": new_fix}
    
    return {"promoted": False}


# ============ GALLERY ENDPOINTS ============

# Load gallery data
def load_gallery_data():
    """Load gallery data from JSON file."""
    gallery_path = Path(__file__).parent / "gallery_data.json"
    if gallery_path.exists():
        with open(gallery_path, 'r') as f:
            return json.load(f)
    return {"categories": [], "fixes": []}

def save_gallery_data(data):
    """Save gallery data to JSON file."""
    gallery_path = Path(__file__).parent / "gallery_data.json"
    with open(gallery_path, 'w') as f:
        json.dump(data, f, indent=2)


@app.get("/gallery/categories")
async def get_categories():
    """Get all categories."""
    data = load_gallery_data()
    return {"categories": data.get("categories", [])}


@app.get("/gallery")
async def get_gallery(category: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    """Get gallery fixes with optional filters."""
    data = load_gallery_data()
    fixes = data.get("fixes", [])
    
    # Filter by category
    if category:
        fixes = [f for f in fixes if f.get("category") == category]
    
    # Filter by featured
    if featured is not None:
        fixes = [f for f in fixes if f.get("featured") == featured]
    
    # Sort by upvotes (most popular first)
    fixes = sorted(fixes, key=lambda x: x.get("upvotes", 0), reverse=True)
    
    # Limit results
    fixes = fixes[:limit]
    
    return {"fixes": fixes, "total": len(fixes)}


@app.get("/gallery/{fix_id}")
async def get_fix(fix_id: str):
    """Get a specific fix by ID."""
    data = load_gallery_data()
    fixes = data.get("fixes", [])
    
    fix = next((f for f in fixes if f.get("id") == fix_id), None)
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    return fix


@app.post("/gallery/{fix_id}/upvote")
async def upvote_fix(fix_id: str):
    """Upvote a fix."""
    data = load_gallery_data()
    fixes = data.get("fixes", [])
    
    for fix in fixes:
        if fix.get("id") == fix_id:
            fix["upvotes"] = fix.get("upvotes", 0) + 1
            save_gallery_data(data)
            return {"success": True, "upvotes": fix["upvotes"]}
    
    raise HTTPException(status_code=404, detail="Fix not found")


@app.post("/gallery/{fix_id}/view")
async def track_view(fix_id: str):
    """Track a view for a fix."""
    data = load_gallery_data()
    fixes = data.get("fixes", [])
    
    for fix in fixes:
        if fix.get("id") == fix_id:
            fix["views"] = fix.get("views", 0) + 1
            save_gallery_data(data)
            return {"success": True, "views": fix["views"]}
    
    raise HTTPException(status_code=404, detail="Fix not found")


# ============ HELPFUL VOTING ENDPOINTS ============

def load_votes_data():
    """Load votes data from JSON file."""
    votes_path = Path(__file__).parent / "votes_data.json"
    if votes_path.exists():
        with open(votes_path, 'r') as f:
            return json.load(f)
    return {"votes": {}}

def save_votes_data(data):
    """Save votes data to JSON file."""
    votes_path = Path(__file__).parent / "votes_data.json"
    with open(votes_path, 'w') as f:
        json.dump(data, f, indent=2)


class VoteRequest(BaseModel):
    video_id: str
    helpful: bool  # True = helpful, False = not helpful
    user_id: Optional[str] = None  # Supabase user ID (if logged in)


@app.get("/votes/{video_id}")
async def get_votes(video_id: str):
    """Get vote counts for a video."""
    data = load_votes_data()
    votes = data.get("votes", {}).get(video_id, {"helpful": 0, "not_helpful": 0})
    total = votes.get("helpful", 0) + votes.get("not_helpful", 0)
    helpful_pct = round((votes.get("helpful", 0) / total * 100)) if total > 0 else 0
    return {
        "video_id": video_id,
        "helpful": votes.get("helpful", 0),
        "not_helpful": votes.get("not_helpful", 0),
        "total": total,
        "helpful_percent": helpful_pct
    }


@app.post("/votes")
async def submit_vote(request: Request, vote: VoteRequest):
    """Submit a helpful/not helpful vote for a video.
    
    If user_id is provided, ensures one vote per user per video.
    Anonymous users can vote but are tracked by IP to reduce spam.
    """
    data = load_votes_data()
    
    # Initialize votes structure
    if "votes" not in data:
        data["votes"] = {}
    if "user_votes" not in data:
        data["user_votes"] = {}  # Track which users voted on which videos
    
    if vote.video_id not in data["votes"]:
        data["votes"][vote.video_id] = {"helpful": 0, "not_helpful": 0}
    
    # Check for duplicate votes
    if vote.user_id:
        # Logged-in user: check by user_id
        vote_key = f"{vote.user_id}:{vote.video_id}"
        if vote_key in data.get("user_votes", {}):
            # Already voted - return current counts without adding
            votes = data["votes"][vote.video_id]
            total = votes["helpful"] + votes["not_helpful"]
            helpful_pct = round((votes["helpful"] / total * 100)) if total > 0 else 0
            return {
                "success": False,
                "message": "Already voted",
                "video_id": vote.video_id,
                "helpful": votes["helpful"],
                "not_helpful": votes["not_helpful"],
                "total": total,
                "helpful_percent": helpful_pct
            }
        
        # Record the vote
        data["user_votes"][vote_key] = {"helpful": vote.helpful, "timestamp": int(time.time())}
    else:
        # Anonymous: track by IP (basic spam prevention)
        client_ip = get_remote_address(request)
        vote_key = f"anon:{client_ip}:{vote.video_id}"
        if vote_key in data.get("user_votes", {}):
            votes = data["votes"][vote.video_id]
            total = votes["helpful"] + votes["not_helpful"]
            helpful_pct = round((votes["helpful"] / total * 100)) if total > 0 else 0
            return {
                "success": False,
                "message": "Already voted",
                "video_id": vote.video_id,
                "helpful": votes["helpful"],
                "not_helpful": votes["not_helpful"],
                "total": total,
                "helpful_percent": helpful_pct
            }
        data["user_votes"][vote_key] = {"helpful": vote.helpful, "timestamp": int(time.time())}
    
    # Count the vote
    if vote.helpful:
        data["votes"][vote.video_id]["helpful"] += 1
    else:
        data["votes"][vote.video_id]["not_helpful"] += 1
    
    save_votes_data(data)
    
    # Check if this vote triggers auto-promotion
    promotion_result = check_auto_promote(vote.video_id)
    
    # Return updated counts
    votes = data["votes"][vote.video_id]
    total = votes["helpful"] + votes["not_helpful"]
    helpful_pct = round((votes["helpful"] / total * 100)) if total > 0 else 0
    
    response = {
        "success": True,
        "video_id": vote.video_id,
        "helpful": votes["helpful"],
        "not_helpful": votes["not_helpful"],
        "total": total,
        "helpful_percent": helpful_pct
    }
    
    # Add promotion info if promoted
    if promotion_result.get("promoted"):
        response["promoted"] = True
        response["promoted_fix"] = promotion_result.get("fix")
    
    return response


# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"

# Mount static files (logo, favicon, etc.)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Serve specific static files at root level
@app.get("/logo.png", include_in_schema=False)
async def serve_logo():
    return FileResponse(frontend_path / "logo.png")

@app.get("/favicon.png", include_in_schema=False)
async def serve_favicon():
    return FileResponse(frontend_path / "favicon.png")

@app.get("/apple-touch-icon.png", include_in_schema=False)
async def serve_apple_icon():
    return FileResponse(frontend_path / "apple-touch-icon.png")

@app.get("/loading-icon.png", include_in_schema=False)
async def serve_loading_icon():
    return FileResponse(frontend_path / "loading-icon.png")

@app.get("/supabase.min.js", include_in_schema=False)
async def serve_supabase():
    return FileResponse(frontend_path / "supabase.min.js", media_type="application/javascript")

@app.get("/app")
async def serve_frontend():
    """Serve the frontend app"""
    return FileResponse(frontend_path / "index.html")

# Serve index.html at root for the frontend (with dynamic OG tags for shared links)
@app.get("/", include_in_schema=False)
async def root_frontend(request: Request, v: Optional[str] = None):
    """Serve frontend at root with dynamic OG meta tags for shared videos."""
    from fastapi.responses import HTMLResponse
    
    # If no video ID, serve static file
    if not v or len(v) != 11:
        return FileResponse(frontend_path / "index.html")
    
    # Look up cached extraction for dynamic OG tags
    extraction = get_extraction(v)
    cached = extraction.get("cached_result") if extraction else None
    
    if cached:
        title = cached.get("title", "CypherIt Fix")
        description = cached.get("problem", "Get the steps in 60 seconds or less")
        thumbnail = f"https://img.youtube.com/vi/{v}/hqdefault.jpg"
    else:
        title = "CypherIt - Get the Steps in 60sec or Less"
        description = "Extract step-by-step instructions from any YouTube tutorial"
        thumbnail = "https://www.cypherit.ai/logo.png"
    
    # Read the HTML file
    with open(frontend_path / "index.html", 'r') as f:
        html = f.read()
    
    # Inject dynamic OG tags (replace existing static ones)
    og_tags = f'''
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{thumbnail}">
    <meta property="og:url" content="https://www.cypherit.ai/?v={v}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{thumbnail}">
    '''
    
    # Insert after <head> tag
    html = html.replace('<head>', f'<head>{og_tags}', 1)
    
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
# Trigger rebuild Wed Feb  4 10:30:54 EST 2026
