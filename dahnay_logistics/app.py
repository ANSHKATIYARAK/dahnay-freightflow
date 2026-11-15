"""
DahNAY FreightFlow: Enterprise Application Server
Entry point for DahNAY FreightFlow Operations Platform and REST API.
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure root and module directory are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dahnay_logistics.api.routes import router as dahnay_api_router
from dahnay_logistics.web.portal import render_dahnay_portal_html
from dahnay_logistics.db.database import init_db, seed_default_bookings

# Initialize SQLite database and seed Master Bookings
init_db()
seed_default_bookings()

app = FastAPI(
    title="DahNAY FreightFlow Enterprise Platform",
    description="Automated Document-to-Invoice Pre-Fill & CargoWise One EDI Bridge for DahNAY Logistics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount DahNAY FreightFlow API routes
app.include_router(dahnay_api_router)


@app.get("/", response_class=HTMLResponse)
@app.get("/dahnay", response_class=HTMLResponse)
def dahnay_operations_portal(request: Request, source: str = "excel"):
    """Serves the primary DahNAY FreightFlow high-density operations platform."""
    return render_dahnay_portal_html(selected_source=source)


@app.get("/health")
def health_check():
    """Service telemetry and health check endpoint."""
    return {
        "status": "healthy",
        "service": "DahNAY FreightFlow Operations Engine",
        "version": "1.0.0",
        "database": "SQLite Connected",
        "edi_bridge": "CargoWise One eAdaptor Ready"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print(" 🚢 DahNAY FreightFlow Enterprise Operations Platform Starting...")
    print(" -------------------------------------------------------------")
    print(" * Web Platform:  http://localhost:8000")
    print(" * REST API:      http://localhost:8000/api/v1/shipments")
    print(" * API Docs:      http://localhost:8000/docs")
    print("="*70 + "\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
