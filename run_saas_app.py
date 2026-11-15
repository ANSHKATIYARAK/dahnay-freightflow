"""
SaaS Platform Runner: Agent-as-a-Service Multi-Tenant Web App
Launches the full-stack SaaS portal with live Server-Sent Events (SSE) streaming on http://localhost:8080
"""

import uvicorn
import os
import sys

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🚀 Agent-as-a-Service (AaaS) Multi-Tenant SaaS App is Running!")
    print(" -------------------------------------------------------------")
    print(" • Multi-Tenant Workspace & Usage Metering (Credits Deduction)")
    print(" • Real-time Server-Sent Events (SSE) Progress Streaming")
    print(" • Stripe Subscription Webhook Integration (Free/Starter/Pro)")
    print(" • Connected to all 34 Specialized Studio Agents")
    print(" • Portal URL: http://localhost:8080")
    print("="*70 + "\n")
    uvicorn.run("saas_platform.api:app", host="127.0.0.1", port=8080, reload=False)
