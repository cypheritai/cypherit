"""
CypherIt - Golden Nugget Extraction
Total extraction ≤ 60 seconds. Final step = verification.
"""

def get_extraction_prompt(category: str, transcript: str, max_steps: int = 6) -> str:
    """Extract golden nuggets - total time ≤ 60 seconds."""
    
    return f"""You are CypherIt. Extract the essential moments from this video in 60 SECONDS OR LESS total.

RULES:
1. Find the KEY MOMENTS that deliver the value (not explanations, the actual demonstrations)
2. TOTAL clip time must be ≤ 60 seconds combined
3. Each clip: 8-20 seconds (find the tightest moment)
4. FINAL step MUST be VERIFICATION (how to confirm it worked)
5. Quality over quantity — fewer great clips beats more mediocre ones

WHAT TO EXTRACT:
• The moment the technique is SHOWN (not explained)
• The "trick" or insight that makes it work
• Any "don't do this" warnings shown
• The verification/proof it worked (ALWAYS include this last)

SKIP:
• Intros, outros, sponsors
• Long explanations (find the demo instead)
• Repetition or filler

The transcript has timestamps in [MM:SS] format.

Transcript:
{transcript[:12000]}

Respond with ONLY valid JSON:
{{
    "title": "Clear title of what this teaches",
    "problem": "One sentence: what you'll be able to do after watching",
    "category": "{category}",
    "quick_info": {{
        "tools_needed": ["What you need"],
        "time_estimate": "How long the actual task takes",
        "warnings": ["Key safety/important warnings"],
        "tips": ["Helpful tips mentioned"]
    }},
    "steps": [
        {{
            "number": 1,
            "action": "What happens in this moment",
            "detail": "Why this moment matters (optional)",
            "timestamp": "2:15",
            "end_timestamp": "2:28"
        }},
        {{
            "number": 2,
            "action": "Verify: How to confirm it worked",
            "detail": "What to check",
            "timestamp": "5:30",
            "end_timestamp": "5:42"
        }}
    ],
    "summary": "2-3 sentence summary: what was covered and the key takeaway"
}}

CRITICAL: Total of all clips (end_timestamp - timestamp) must be ≤ 60 seconds!
CRITICAL: Last step must be verification/confirmation!"""


def detect_category(title: str, transcript: str) -> str:
    """Simple category detection."""
    text = (title + " " + transcript[:2000]).lower()
    
    if any(kw in text for kw in ["oil change", "brake", "tire", "car", "engine", "vehicle", "automotive"]):
        return "auto_maintenance"
    elif any(kw in text for kw in ["wifi", "computer", "error", "troubleshoot", "fix", "not working"]):
        return "tech_troubleshooting"
    elif any(kw in text for kw in ["install", "setup", "download", "software", "app"]):
        return "software_setup"
    elif any(kw in text for kw in ["plumbing", "electrical", "repair", "leak", "wall", "pipe"]):
        return "home_repair"
    elif any(kw in text for kw in ["recipe", "cook", "bake", "food"]):
        return "cooking"
    
    return "general"
