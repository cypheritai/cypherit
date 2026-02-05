"""
CypherIt Category Frameworks
Each framework defines the essential structure for complete extractions.
"""

FRAMEWORKS = {
    "auto_maintenance": {
        "name": "Auto Maintenance",
        "keywords": ["oil change", "brake", "tire", "car", "vehicle", "engine", "transmission", 
                     "coolant", "filter", "spark plug", "battery", "wiper", "headlight", "automotive"],
        "required_phases": [
            {"phase": "safety", "description": "Secure vehicle, safety precautions"},
            {"phase": "preparation", "description": "Gather tools and materials needed"},
            {"phase": "access", "description": "Access the component being serviced"},
            {"phase": "removal", "description": "Remove old part/fluid"},
            {"phase": "installation", "description": "Install new part/add new fluid"},
            {"phase": "verification", "description": "Verify the job is complete and working"},
        ],
        "must_include": [
            "Safety step (vehicle secured, engine state)",
            "Verification step (check for leaks, test function)",
        ],
        "common_tools": ["jack/stands", "wrench set", "drain pan", "gloves", "shop towels"],
        "common_warnings": ["Hot engine danger", "Proper vehicle support", "Correct fluid type"],
    },
    
    "tech_troubleshooting": {
        "name": "Tech Troubleshooting",
        "keywords": ["wifi", "internet", "computer", "phone", "not working", "fix", "error",
                     "troubleshoot", "slow", "crash", "freeze", "connect", "printer", "bluetooth"],
        "required_phases": [
            {"phase": "identify", "description": "Identify the specific problem/symptom"},
            {"phase": "diagnose", "description": "Find the root cause"},
            {"phase": "fix", "description": "Apply the solution"},
            {"phase": "verification", "description": "Confirm the issue is resolved"},
        ],
        "must_include": [
            "Clear problem identification",
            "Verification that fix worked",
        ],
        "common_tools": ["device access", "admin password", "internet connection"],
        "common_warnings": ["Backup data first", "Note current settings before changing"],
    },
    
    "software_setup": {
        "name": "Software Setup",
        "keywords": ["install", "setup", "download", "configure", "app", "software", "program",
                     "windows", "mac", "linux", "update", "upgrade", "python", "node", "docker"],
        "required_phases": [
            {"phase": "prerequisites", "description": "Check system requirements, dependencies"},
            {"phase": "download", "description": "Get the correct installer/files"},
            {"phase": "install", "description": "Run installation process"},
            {"phase": "configure", "description": "Initial setup and configuration"},
            {"phase": "verification", "description": "Verify installation works correctly"},
        ],
        "must_include": [
            "Prerequisites/requirements check",
            "Verification step (launch, test basic function)",
        ],
        "common_tools": ["admin access", "internet connection", "disk space"],
        "common_warnings": ["Check compatibility", "Backup before major installs"],
    },
    
    "home_repair": {
        "name": "Home Repair",
        "keywords": ["plumbing", "electrical", "drywall", "paint", "faucet", "toilet", "drain",
                     "leak", "hole", "wall", "outlet", "switch", "door", "window", "caulk"],
        "required_phases": [
            {"phase": "safety", "description": "Turn off water/power, safety gear"},
            {"phase": "assessment", "description": "Assess the damage/scope of work"},
            {"phase": "preparation", "description": "Gather materials, prep the area"},
            {"phase": "repair", "description": "Perform the actual repair"},
            {"phase": "finishing", "description": "Clean up, finishing touches"},
            {"phase": "verification", "description": "Test that repair holds/works"},
        ],
        "must_include": [
            "Safety step (utilities off if needed)",
            "Verification step (test for leaks, function check)",
        ],
        "common_tools": ["basic hand tools", "safety glasses", "work gloves"],
        "common_warnings": ["Turn off utilities", "Check for permits if needed", "Know your limits"],
    },
    
    "cooking": {
        "name": "Cooking & Recipes",
        "keywords": ["recipe", "cook", "bake", "food", "meal", "ingredient", "kitchen",
                     "oven", "stove", "grill", "sauce", "prep", "chop", "mix"],
        "required_phases": [
            {"phase": "ingredients", "description": "List and prep all ingredients"},
            {"phase": "preparation", "description": "Prep work (chopping, measuring, etc.)"},
            {"phase": "cooking", "description": "Main cooking steps"},
            {"phase": "finishing", "description": "Final touches, plating"},
            {"phase": "verification", "description": "Check doneness, taste, presentation"},
        ],
        "must_include": [
            "Ingredients/prep overview",
            "Doneness check or serving suggestion",
        ],
        "common_tools": ["cooking utensils", "measuring tools", "appropriate cookware"],
        "common_warnings": ["Food safety temps", "Allergy considerations"],
    },
    
    "general": {
        "name": "General How-To",
        "keywords": [],  # Fallback category
        "required_phases": [
            {"phase": "overview", "description": "What we're doing and why"},
            {"phase": "steps", "description": "Main action steps"},
            {"phase": "verification", "description": "How to know it worked"},
        ],
        "must_include": [
            "Clear end state or verification",
        ],
        "common_tools": [],
        "common_warnings": [],
    },
}


def detect_category(title: str, transcript: str) -> str:
    """Detect the best matching category from title and transcript."""
    text = (title + " " + transcript[:2000]).lower()
    
    best_match = "general"
    best_score = 0
    
    for category_id, framework in FRAMEWORKS.items():
        if category_id == "general":
            continue
            
        score = sum(1 for kw in framework["keywords"] if kw in text)
        if score > best_score:
            best_score = score
            best_match = category_id
    
    return best_match


def get_framework(category: str) -> dict:
    """Get the framework for a category."""
    return FRAMEWORKS.get(category, FRAMEWORKS["general"])


def build_framework_prompt(category: str) -> str:
    """Build the framework-specific part of the extraction prompt."""
    fw = get_framework(category)
    
    phases = "\n".join([f"  {i+1}. {p['phase'].upper()}: {p['description']}" 
                        for i, p in enumerate(fw["required_phases"])])
    
    must_include = "\n".join([f"  - {item}" for item in fw["must_include"]])
    
    return f"""
CATEGORY DETECTED: {fw['name']}

This type of content MUST follow this structure:
{phases}

CRITICAL - Your extraction MUST include:
{must_include}

The FINAL STEP must ALWAYS be verification - how does the user know it worked?
"""
