"""
VentureOS: Local Web Dashboard Runner
Launches the web UI on http://localhost:8000
"""

import uvicorn
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🚀 VentureOS Hub is starting on http://localhost:8000")
    print(" Open your web browser to explore generated SaaS ventures,")
    print(" preview live landing pages, and launch new micro-products.")
    print("="*60 + "\n")
    uvicorn.run("venture_os.server:app", host="127.0.0.1", port=8000, reload=False)
