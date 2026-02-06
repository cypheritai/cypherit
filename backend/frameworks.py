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
• "timestamp" = When this specific point is discussed in the video
• "end_timestamp" = When to stop (MUST be AFTER timestamp)

CRITICAL TIMESTAMP RULES:
• Look at the transcript timestamps [MM:SS] — find where THIS EXACT topic is discussed
• The timestamp you return MUST be from the transcript where the speaker says this
• If the step is about "synthesis abilities", find where they SAY "synthesis" in the transcript
• Don't guess timestamps — only use timestamps that appear in the transcript
• end_timestamp should be 10-30 seconds after timestamp

HOW TO FIND THE RIGHT TIMESTAMP:
1. Read your extracted step (e.g., "Develop synthesis abilities...")
2. Search the transcript for where this is actually discussed
3. Use THAT timestamp from the transcript
4. The clip will loop this section, so it MUST match the content

GUIDELINES:
• Skip intros, outros, sponsors, and filler
• End with a key takeaway or action item
• Be concise — only include what's truly needed

The transcript has timestamps in [MM:SS] format. USE THESE TIMESTAMPS — they mark where each part of the video occurs.

Transcript:
{transcript[:12000]}

IMPORTANT: For each step, include "transcript_quote" — a short phrase from the transcript that proves you found the right timestamp.

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
            "end_timestamp": "2:45",
            "transcript_quote": "the exact words from transcript at this timestamp"
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
