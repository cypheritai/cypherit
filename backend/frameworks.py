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
    
    return f"""You are CypherIt. Extract COMPLETE, SAFE, step-by-step instructions from this video.

OUTPUT LANGUAGE: Respond in {output_language}. All text fields (title, problem, action, detail, summary, warnings, tips) must be in {output_language}.

Your job: Turn a long video into clear, actionable steps that a COMPLETE BEGINNER with ZERO experience can follow SAFELY.

CRITICAL - COMPLETENESS OVER BREVITY:
- Include EVERY step, even ones that seem "obvious" to experts
- A skipped step could cause damage, injury, or failure
- Example: For an oil change, you MUST include "Add new oil" - forgetting this destroys the engine
- Example: For electrical work, you MUST include "Turn off power at breaker"
- When in doubt, INCLUDE the step

INCLUDE THESE ESSENTIAL STEPS:
- Setup/preparation steps (gather tools, safety precautions)
- The main action steps
- Verification steps (how to check if you did it right)
- Completion steps (cleanup, reassembly, testing)
- Safety warnings (what could go wrong if skipped)

FOR EACH STEP:
- "action" = What to do (clear, actionable, specific)  
- "detail" = Why it matters, what could go wrong if skipped, or helpful context
- "timestamp" = When this specific point is discussed in the video
- "end_timestamp" = When to stop (MUST be AFTER timestamp)

CRITICAL TIMESTAMP RULES:
- Look at the transcript timestamps [MM:SS] - find where THIS EXACT topic is discussed
- The timestamp you return MUST be from the transcript where the speaker says this
- If the step is about "synthesis abilities", find where they SAY "synthesis" in the transcript
- Don't guess timestamps - only use timestamps that appear in the transcript
- end_timestamp should be 10-30 seconds after timestamp

HOW TO FIND THE RIGHT TIMESTAMP:
1. Read your extracted step (e.g., "Develop synthesis abilities...")
2. Search the transcript for where this is actually discussed
3. Use THAT timestamp from the transcript
4. The clip will loop this section, so it MUST match the content
5. Size the clip to fit the content - include the full explanation

FULL VIDEO COVERAGE - MANDATORY:
- Extract ALL steps from START to FINISH of the video
- Do NOT limit yourself - include every meaningful step
- Timestamps MUST span the entire video duration
- If the video is 15 minutes, your steps should go from ~0:30 to ~14:30
- The FIRST step should be near the beginning (after intro)
- The LAST step MUST be from the final 1-2 minutes of the video
- MUST include completion steps: refilling, reassembly, testing, verification
- A task is NOT complete until it's tested and working
- Example: Oil change MUST end with "Add new oil" and "Check oil level" - not just draining!

GUIDELINES:
- Skip intros, outros, sponsors, and filler
- NEVER skip safety steps, verification steps, or "obvious" steps
- End with verification: how does the user know they succeeded?
- Think: "What would a first-timer need to know?"

The transcript has timestamps in [MM:SS] format. USE THESE TIMESTAMPS - they mark where each part of the video occurs.

Transcript:
{transcript[:12000]}

IMPORTANT: For each step, include "transcript_quote" - a short phrase from the transcript that proves you found the right timestamp.

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
        "tools_needed": ["Everything needed before starting"],
        "time_estimate": "How long the task takes",
        "difficulty": "beginner/intermediate/advanced",
        "warnings": ["CRITICAL safety warnings - what could go wrong"],
        "tips": ["Pro tips for better results"]
    }},
    "steps": [
        {{
            "number": 1,
            "action": "Clear, specific action to take",
            "detail": "Why this matters / what goes wrong if skipped",
            "timestamp": "2:15",
            "end_timestamp": "2:45",
            "transcript_quote": "the exact words from transcript at this timestamp"
        }}
    ],
    "verify": [
        "How to check step 1 was done correctly",
        "How to check step 2 was done correctly",
        "Final verification: how do you know the whole task succeeded?"
    ],
    "summary": "Brief summary + what the user should see/experience if done correctly"
}}"""
