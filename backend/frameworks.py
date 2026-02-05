"""
CypherIt - Simple Golden Nugget Extraction
Universal steps that work broadly, not overly specific.
"""

def get_extraction_prompt(category: str, transcript: str, max_steps: int = 6) -> str:
    """Simple, universal extraction prompt focused on golden nuggets."""
    
    return f"""You are CypherIt. Extract the UNIVERSAL, ESSENTIAL steps from this how-to video.

GOAL: Someone watching should be able to follow these steps for ANY similar task, not just one specific case.

RULES:
1. Extract 4-6 KEY STEPS that apply broadly (not vehicle-specific, not software-version-specific)
2. Each step = ONE clear action, described universally
3. Find the EXACT 8-20 second clip showing that action
4. Skip intros, outros, sponsors, tangents
5. Final step should confirm success (verify it worked)

BAD (too specific): "Remove 14mm drain plug on 2015 Honda Civic"
GOOD (universal): "Remove drain plug and let oil drain completely"

BAD: "Install filter part #XYZ123"  
GOOD: "Install new oil filter (hand-tighten, then 1/4 turn)"

The transcript has timestamps in [MM:SS] format. Find the golden nugget moment for each step.

Transcript:
{transcript[:12000]}

Respond with ONLY valid JSON:
{{
    "title": "How to [Do Thing]",
    "problem": "What this accomplishes",
    "category": "auto_maintenance",
    "quick_info": {{
        "tools_needed": ["Basic tools needed"],
        "time_estimate": "X minutes",
        "warnings": ["Key safety warnings"],
        "tips": ["Helpful universal tips"]
    }},
    "steps": [
        {{"number": 1, "action": "Clear universal action", "detail": "Brief helpful context", "timestamp": "2:15", "end_timestamp": "2:30"}},
        {{"number": 2, "action": "Next key action", "detail": null, "timestamp": "4:10", "end_timestamp": "4:25"}}
    ],
    "verify": ["How to confirm it worked"]
}}"""


def detect_category(title: str, transcript: str) -> str:
    """Simple category detection for badge display."""
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
