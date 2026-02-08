"""
CypherIt - Simple, Clean Extraction
Core value: Deliver execution with simplicity and action.
"""

# Category and subcategory definitions
CATEGORIES = {
    "home": {
        "name": "Home Fixes",
        "keywords": ["house", "home", "repair", "diy", "wall", "floor", "room"],
        "subcategories": {
            "toilet": ["toilet", "flush", "flapper", "wax ring", "cistern"],
            "faucet": ["faucet", "sink", "drain", "tap", "leak", "clog"],
            "door": ["door", "window", "hinge", "lock", "frame", "screen"],
            "electrical": ["outlet", "switch", "wire", "breaker", "light fixture"],
            "plumbing": ["pipe", "plumbing", "water heater", "valve", "pvc"],
            "hvac": ["hvac", "furnace", "ac", "air conditioning", "thermostat", "heating"],
            "flooring": ["floor", "tile", "hardwood", "laminate", "carpet", "grout"],
            "wall": ["drywall", "paint", "wall", "patch", "plaster", "stucco"]
        }
    },
    "tech": {
        "name": "Tech Setup",
        "keywords": ["code", "programming", "software", "developer", "computer", "install"],
        "subcategories": {
            "python": ["python", "pip", "django", "flask", "pandas", "numpy"],
            "javascript": ["javascript", "node", "npm", "react", "vue", "typescript"],
            "git": ["git", "github", "gitlab", "commit", "branch", "merge", "clone"],
            "devops": ["docker", "kubernetes", "aws", "azure", "cloud", "deploy", "ci/cd"],
            "ide": ["vscode", "ide", "editor", "terminal", "extension", "debug"],
            "database": ["database", "sql", "mysql", "postgres", "mongodb", "redis"],
            "os": ["macos", "windows", "linux", "ubuntu", "boot", "usb", "partition"]
        }
    },
    "phone": {
        "name": "Phone & Tablet",
        "keywords": ["phone", "mobile", "tablet", "smartphone", "cellular"],
        "subcategories": {
            "iphone": ["iphone", "ios", "apple", "imessage", "facetime"],
            "android": ["android", "samsung", "pixel", "galaxy", "google play"],
            "ipad": ["ipad", "tablet", "surface"],
            "battery": ["battery", "charge", "charging", "power"],
            "screen": ["screen", "display", "cracked", "replacement"],
            "apps": ["app", "settings", "notification", "update", "storage"]
        }
    },
    "auto": {
        "name": "Auto & Motor",
        "keywords": ["car", "vehicle", "truck", "auto", "motor", "driving"],
        "subcategories": {
            "brakes": ["brake", "rotor", "caliper", "pad", "drum", "cylinder"],
            "engine": ["engine", "motor", "spark plug", "timing", "gasket"],
            "tires": ["tire", "wheel", "rim", "rotation", "flat", "pressure"],
            "electrical": ["battery", "alternator", "starter", "fuse", "headlight"],
            "interior": ["seat", "dashboard", "radio", "ac vent", "upholstery"],
            "exterior": ["bumper", "fender", "dent", "scratch", "paint", "rust"],
            "fluids": ["oil", "coolant", "transmission", "brake fluid", "power steering"]
        }
    },
    "gaming": {
        "name": "Gaming",
        "keywords": ["game", "gaming", "xbox", "playstation", "nintendo", "steam"],
        "subcategories": {
            "pc": ["pc gaming", "graphics card", "gpu", "cpu", "ram", "fps"],
            "console": ["console", "xbox", "playstation", "ps5", "nintendo", "switch"],
            "performance": ["performance", "lag", "fps", "optimize", "settings"],
            "streaming": ["stream", "twitch", "obs", "capture", "broadcast"],
            "peripherals": ["controller", "keyboard", "mouse", "headset", "monitor"]
        }
    },
    "kitchen": {
        "name": "Kitchen & Appliances",
        "keywords": ["kitchen", "appliance", "cook", "food"],
        "subcategories": {
            "fridge": ["refrigerator", "fridge", "freezer", "ice maker"],
            "oven": ["oven", "stove", "range", "burner", "bake"],
            "dishwasher": ["dishwasher", "dish"],
            "microwave": ["microwave"],
            "washer": ["washer", "dryer", "laundry", "washing machine"],
            "small": ["coffee", "toaster", "blender", "mixer", "instant pot"]
        }
    }
}


def detect_category(title: str, transcript: str) -> tuple[str, str]:
    """Detect category and subcategory from content.
    Returns (category_id, subcategory_id) or (category_id, None)."""
    text = (title + " " + transcript[:3000]).lower()
    
    best_category = "tech"  # default
    best_subcategory = None
    best_score = 0
    
    for cat_id, cat_data in CATEGORIES.items():
        # Check main category keywords
        cat_score = sum(1 for kw in cat_data["keywords"] if kw in text)
        
        # Check subcategory keywords (weighted higher)
        for sub_id, sub_keywords in cat_data["subcategories"].items():
            sub_score = sum(2 for kw in sub_keywords if kw in text)
            total_score = cat_score + sub_score
            
            if total_score > best_score:
                best_score = total_score
                best_category = cat_id
                if sub_score > 0:
                    best_subcategory = sub_id
    
    return best_category, best_subcategory


def get_extraction_prompt(category: str, transcript: str, max_steps: int = 10, language: str = "en") -> str:
    """Simple extraction - let it execute naturally.
    
    Args:
        category: Detected content category
        transcript: Video transcript
        max_steps: Maximum steps to extract
        language: ISO language code (e.g., 'en', 'es', 'fr', 'de', 'pt')
    """
    
    # Get subcategory list for the detected category
    cat_data = CATEGORIES.get(category, CATEGORIES["tech"])
    subcategory_list = ", ".join(cat_data["subcategories"].keys())
    
    # Language mapping for natural output
    LANGUAGE_NAMES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "pt": "Portuguese",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ru": "Russian",
        "ar": "Arabic",
        "hi": "Hindi",
    }
    output_language = LANGUAGE_NAMES.get(language[:2].lower(), "English")
    
    return f"""You are CypherIt. Extract the essential steps from this video.

OUTPUT LANGUAGE: Respond in {output_language}. All text fields (title, problem, action, detail, summary, warnings, tips) must be in {output_language}.

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
5. Size the clip to fit the content — include the full explanation

GUIDELINES:
• Skip intros, outros, sponsors, and filler
• End with a key takeaway or action item
• Be concise — only include what's truly needed

The transcript has timestamps in [MM:SS] format. USE THESE TIMESTAMPS — they mark where each part of the video occurs.

Transcript:
{transcript[:12000]}

IMPORTANT: For each step, include "transcript_quote" — a short phrase from the transcript that proves you found the right timestamp.

CATEGORY DETECTION:
Main category is "{category}".
Pick the most relevant subcategory from: {subcategory_list}
If none fit well, use null for subcategory.

Respond with ONLY valid JSON:
{{
    "title": "Clear title of what this teaches",
    "problem": "What you'll be able to do after watching",
    "category": "{category}",
    "subcategory": "most_relevant_subcategory_or_null",
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
