"""
CypherIt - Golden Nugget Extraction
Find the treasure, skip the dirt.
"""

def get_extraction_prompt(category: str, transcript: str, max_steps: int = 5) -> str:
    """Extract golden nuggets - the moments that deliver the value."""
    
    return f"""You are a GOLDEN NUGGET MINER. Your job is to find the treasure buried in this video.

A golden nugget is a 15-45 second moment that:
• Delivers the "hit" — the viewer goes "wait, that's it!" or "oh, I get it now"
• Stands ALONE — you don't need the full video to understand it
• Is the REASON someone would watch this video
• Contains the core technique, the key insight, or the actionable tip

The rest of the video is the "dirt" — setup, explanations, tangents, filler. Skip it.

YOUR MISSION:
Find 3-5 golden nuggets in this video. Each one should be:
1. SELF-CONTAINED — Someone watching just this clip "gets it"
2. VALUABLE — It's the part that actually matters
3. TIGHT — 15-45 seconds max, no fat
4. VISUAL — The moment where the action/technique is SHOWN, not explained

For how-to content, nuggets are usually:
• The moment the technique is demonstrated (not explained)
• The "trick" or hack that makes it easier
• The before/after or the proof it works
• The "don't make this mistake" warning shown

DON'T extract:
• Intros, outros, sponsor reads
• Long explanations (find the demo instead)
• Filler or repetition
• Setup without payoff

The transcript has timestamps in [MM:SS] format. Find the nuggets.

Transcript:
{transcript[:12000]}

Respond with ONLY valid JSON:
{{
    "title": "What this video teaches",
    "hook": "The one-sentence reason to watch (the core insight)",
    "category": "{category}",
    "nuggets": [
        {{
            "number": 1,
            "moment": "What happens in this nugget",
            "why_valuable": "Why this moment matters",
            "timestamp": "2:15",
            "end_timestamp": "2:45"
        }}
    ],
    "verify": "How you know you did it right"
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
