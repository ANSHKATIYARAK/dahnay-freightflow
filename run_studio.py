"""
StudioEngine: Enterprise Multi-Agent Studio Server Runner
Launches the 7-department, 34-agent control center at http://localhost:8000
"""

import uvicorn
import os
import sys

# Ensure Windows terminal handles UTF-8 gracefully
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" [ONLINE] StudioEngine Enterprise Multi-Agent Hub is Online!")
    print(" -------------------------------------------------------------")
    print(" * 7 Departments (Engineering, Product, Marketing, Design,")
    print("   Project Management, Studio Operations, Testing)")
    print(" * 34 Autonomous Specialized Agents Loaded from .claude/agents")
    print(" * Live Studio URL: http://localhost:8000")
    print(" * Portfolio URL:   http://localhost:8000/portfolio")
    print("="*70 + "\n")
    uvicorn.run("studio_engine.server:app", host="0.0.0.0", port=8000, reload=False)
