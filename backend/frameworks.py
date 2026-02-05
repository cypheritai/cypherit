"""
CypherIt Category Frameworks - Manual Style
Standardized extraction formats based on real-world documentation.
"""

FRAMEWORKS = {
    "auto_maintenance": {
        "name": "Auto Maintenance",
        "keywords": ["oil change", "brake", "tire", "car", "vehicle", "engine", "transmission", 
                     "coolant", "filter", "spark plug", "battery", "wiper", "headlight", "automotive",
                     "fluid", "radiator", "alternator", "belt", "hose", "gasket", "rotor", "caliper"],
        "output_format": "shop_manual",
        "sections": ["specifications", "tools_required", "warnings", "procedure", "verify"],
        "prompt_template": """
Extract this automotive procedure in SHOP MANUAL format.

You must extract these sections:

SPECIFICATIONS (extract ANY mentioned):
- Fluid type and amount (e.g., "0W-20 Full Synthetic, 4.5 quarts")
- Part numbers if mentioned
- Torque values (e.g., "drain plug: 25 ft-lbs")
- Measurements or sizes

TOOLS REQUIRED:
- List every tool mentioned or clearly needed
- Include sizes (e.g., "14mm socket" not just "socket")

WARNINGS (⚠️):
- Safety warnings (hot engine, jack stands, etc.)
- Things that can go wrong
- "Do NOT" instructions

PROCEDURE:
- Numbered steps, each ONE action
- Include specific values in steps (torque specs, amounts)
- 8-15 second video clips per step
- Find the EXACT timestamp where action is shown

VERIFY (✓):
- How to confirm the job is done right
- What to check for (leaks, levels, function)
- Expected outcome

Output JSON format:
{
    "title": "Oil Change - [Vehicle/Engine if mentioned]",
    "problem": "What this procedure accomplishes",
    "category": "auto_maintenance",
    "specifications": {
        "fluid_type": "0W-20 Full Synthetic",
        "capacity": "4.5 quarts with filter",
        "torque_specs": {"drain_plug": "25 ft-lbs", "filter": "hand tight + 1/4 turn"},
        "parts": ["Oil filter #XYZ"]
    },
    "tools_required": ["14mm socket", "Oil filter wrench", "Drain pan 6qt", "Funnel", "Torque wrench"],
    "warnings": ["Engine must be cool before starting", "Always use jack stands - never work under car on jack alone"],
    "steps": [
        {"number": 1, "action": "Remove drain plug and drain oil completely", "detail": "Let drain 5 minutes minimum", "timestamp": "2:15", "end_timestamp": "2:27"},
        {"number": 2, "action": "Remove old oil filter", "detail": "Turn counterclockwise", "timestamp": "4:30", "end_timestamp": "4:42"}
    ],
    "verify": ["Check oil level at FULL mark on dipstick", "Start engine and inspect for leaks around drain plug and filter", "Re-check level after running 1 minute"]
}

If a specification isn't mentioned in the video, omit it (don't guess).
""",
    },
    
    "tech_troubleshooting": {
        "name": "Tech Troubleshooting", 
        "keywords": ["wifi", "internet", "computer", "phone", "not working", "fix", "error",
                     "troubleshoot", "slow", "crash", "freeze", "connect", "printer", "bluetooth",
                     "network", "router", "modem", "password", "reset", "restart"],
        "output_format": "troubleshooting_guide",
        "sections": ["symptoms", "requirements", "diagnosis", "solution", "verify"],
        "prompt_template": """
Extract this tech troubleshooting guide in SUPPORT MANUAL format.

SYMPTOMS:
- What problem is being fixed
- Error messages if mentioned

REQUIREMENTS:
- Device/OS requirements
- Access needed (admin, passwords)
- Prerequisite conditions

DIAGNOSIS (if shown):
- How to identify the root cause
- Settings to check

SOLUTION:
- Numbered steps, each ONE action
- Include exact menu paths (Settings > Network > WiFi)
- Note any values to enter or options to select
- 8-15 second video clips per step

VERIFY (✓):
- How to confirm the fix worked
- Expected result

Output JSON format:
{
    "title": "Fix [Problem]",
    "problem": "What symptom this resolves",
    "category": "tech_troubleshooting",
    "symptoms": ["WiFi shows connected but no internet", "Error: DNS_PROBE_FINISHED"],
    "requirements": ["Windows 10/11", "Admin access", "Router access (optional)"],
    "diagnosis": "The issue is usually caused by...",
    "steps": [
        {"number": 1, "action": "Open Network Settings", "detail": "Settings > Network & Internet", "timestamp": "0:45", "end_timestamp": "0:55"}
    ],
    "verify": ["Open browser and navigate to google.com", "Speed test shows expected speeds"]
}
""",
    },
    
    "software_setup": {
        "name": "Software Setup",
        "keywords": ["install", "setup", "download", "configure", "app", "software", "program",
                     "windows", "mac", "linux", "update", "upgrade", "python", "node", "docker",
                     "IDE", "VS Code", "terminal", "command", "npm", "pip", "brew"],
        "output_format": "installation_guide",
        "sections": ["requirements", "downloads", "installation", "configuration", "verify"],
        "prompt_template": """
Extract this software installation in SETUP GUIDE format.

SYSTEM REQUIREMENTS:
- OS version
- Disk space
- RAM/CPU if mentioned
- Dependencies (other software needed first)

DOWNLOADS:
- What to download
- Where to get it (URL/source)
- Version if mentioned

INSTALLATION:
- Numbered steps
- Exact buttons to click, options to select
- Command line commands if any (exact syntax)
- 8-15 second video clips per step

CONFIGURATION:
- Initial setup steps after install
- Settings to change
- Accounts to create/connect

VERIFY (✓):
- How to confirm it's working
- First thing to try

Output JSON format:
{
    "title": "Install [Software Name]",
    "problem": "What you'll be able to do after",
    "category": "software_setup",
    "requirements": {"os": "Windows 10+", "disk_space": "2GB", "dependencies": ["Node.js 18+"]},
    "downloads": [{"name": "VS Code", "source": "code.visualstudio.com", "version": "latest"}],
    "steps": [
        {"number": 1, "action": "Download installer from official site", "detail": "Click Download button", "timestamp": "0:30", "end_timestamp": "0:40"}
    ],
    "configuration": ["Sign in with GitHub account", "Install recommended extensions"],
    "verify": ["Open VS Code", "Create new file and save - confirms it's working"]
}
""",
    },
    
    "home_repair": {
        "name": "Home Repair",
        "keywords": ["plumbing", "electrical", "drywall", "paint", "faucet", "toilet", "drain",
                     "leak", "hole", "wall", "outlet", "switch", "door", "window", "caulk",
                     "pipe", "valve", "wire", "breaker", "stud", "anchor", "screw"],
        "output_format": "repair_manual",
        "sections": ["materials", "tools", "safety", "procedure", "verify"],
        "prompt_template": """
Extract this home repair in REPAIR MANUAL format.

MATERIALS NEEDED:
- Parts with sizes/specs
- Consumables (tape, caulk, etc.)
- Quantities if mentioned

TOOLS REQUIRED:
- Every tool needed with sizes
- Safety equipment

⚠️ SAFETY:
- Turn off water/power warnings
- Safety gear needed
- Permit requirements if mentioned

PROCEDURE:
- Numbered steps, ONE action each
- Include measurements and specs
- Note waiting times (dry time, cure time)
- 8-15 second video clips per step

VERIFY (✓):
- How to test the repair
- What to check for (leaks, function)
- When to re-check

Output JSON format:
{
    "title": "Repair [Problem]",
    "problem": "What issue this fixes",
    "category": "home_repair",
    "materials": ["1/2 inch PVC coupling", "PVC primer", "PVC cement"],
    "tools_required": ["PVC cutter", "Measuring tape", "Marker", "Safety glasses"],
    "safety": ["Turn off main water supply", "Wear safety glasses when cutting"],
    "steps": [
        {"number": 1, "action": "Turn off water at main shutoff", "detail": "Usually near water meter", "timestamp": "1:00", "end_timestamp": "1:12"}
    ],
    "verify": ["Turn water back on slowly", "Check all connections for leaks", "Re-check after 24 hours"]
}
""",
    },
    
    "general": {
        "name": "General How-To",
        "keywords": [],
        "output_format": "standard",
        "sections": ["overview", "requirements", "procedure", "verify"],
        "prompt_template": """
Extract this how-to in STANDARD GUIDE format.

OVERVIEW:
- What this accomplishes

REQUIREMENTS:
- What you need before starting

PROCEDURE:
- Numbered steps
- 8-15 second video clips per step

VERIFY:
- How to confirm success

Output JSON format:
{
    "title": "How to [Do Thing]",
    "problem": "What this accomplishes",
    "category": "general",
    "requirements": ["Item 1", "Item 2"],
    "steps": [
        {"number": 1, "action": "First action", "detail": "Extra context", "timestamp": "0:30", "end_timestamp": "0:42"}
    ],
    "verify": ["Expected outcome"]
}
""",
    },
}


def detect_category(title: str, transcript: str) -> str:
    """Detect the best matching category from title and transcript."""
    text = (title + " " + transcript[:3000]).lower()
    
    best_match = "general"
    best_score = 0
    
    for category_id, framework in FRAMEWORKS.items():
        if category_id == "general":
            continue
            
        score = sum(1 for kw in framework["keywords"] if kw in text)
        # Boost score for exact phrase matches
        score += sum(2 for kw in framework["keywords"] if f" {kw} " in f" {text} ")
        
        if score > best_score:
            best_score = score
            best_match = category_id
    
    return best_match


def get_framework(category: str) -> dict:
    """Get the framework for a category."""
    return FRAMEWORKS.get(category, FRAMEWORKS["general"])


def get_extraction_prompt(category: str, transcript: str, max_steps: int = 6) -> str:
    """Build the complete extraction prompt for a category."""
    fw = get_framework(category)
    
    return f"""You are CypherIt, an expert at extracting PRECISE, COMPLETE procedures from video transcripts.

The transcript below has timestamps in [MM:SS] format. Your job is to extract the procedure in standardized manual format.

CATEGORY: {fw['name']}

{fw['prompt_template']}

CRITICAL TIMESTAMP RULES:
- Find the EXACT moment each action is SHOWN, not just mentioned
- Each clip: 8-15 seconds (minimum needed to see the action)
- Never exceed 20 seconds per step
- Skip intros, tangents, sponsor reads — just the ACTION

CRITICAL STRUCTURE RULES:
- Every procedure MUST end with VERIFY section
- If something important isn't in the video, note it in verify as "Not shown: [thing]"
- Max {max_steps} procedure steps — combine minor actions, keep major ones

Transcript:
{transcript[:12000]}

Respond with ONLY valid JSON (no markdown, no explanation):"""
