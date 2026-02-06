"""
CypherIt - Simple, Clean Extraction
Core value: Deliver execution with simplicity and action.
"""

def get_extraction_prompt(category: str, transcript: str, max_steps: int = 10) -> str:
    """Simple extraction - let it execute naturally."""
    
    return f"""You are CypherIt. Extract the essential steps from this video.

Your job: Turn a long video into clear, actionable steps someone can follow.

FOR EACH STEP:
• "action" = What to do (clear, actionable)
• "detail" = Why it matters or helpful context

GUIDELINES:
• Find the moments that SHOW the action, not just explain it
• Each step should be self-contained and valuable
• Skip intros, outros, sponsors, and filler
• End with a verification step (how to confirm it worked)
• Be concise — only include what's truly needed

The transcript has timestamps in [MM:SS] format. Find the best clip for each step.

Transcript:
{transcript[:12000]}

Respond with ONLY valid JSON:
{{
    "title": "Clear title of what this teaches",
    "problem": "What you'll be able to do after watching",
    "category": "{category}",
    "quick_info": {{
        "tools_needed": ["What you need"],
        "time_estimate": "How long the task takes",
        "warnings": ["Important warnings if any"],
        "tips": ["Helpful tips if any"]
    }},
    "steps": [
        {{
            "number": 1,
            "action": "Clear action to take",
            "detail": "Why this matters",
            "timestamp": "2:15",
            "end_timestamp": "2:30"
        }}
    ],
    "summary": "Brief summary of what was covered and the key takeaway"
}}"""


def detect_category(title: str, transcript: str) -> str:
    """Simple category detection for display."""
    text = (title + " " + transcript[:2000]).lower()
    
    if any(kw in text for kw in ["oil", "brake", "tire", "car", "engine", "vehicle"]):
        return "auto_maintenance"
    elif any(kw in text for kw in ["wifi", "computer", "error", "fix", "not working"]):
        return "tech_troubleshooting"
    elif any(kw in text for kw in ["install", "setup", "download", "software"]):
        return "software_setup"
    elif any(kw in text for kw in ["plumbing", "electrical", "repair", "leak"]):
        return "home_repair"
    elif any(kw in text for kw in ["recipe", "cook", "bake", "food"]):
        return "cooking"
    
    return "how_to"
