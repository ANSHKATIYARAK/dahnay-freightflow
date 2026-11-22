"""
DahNAY FreightFlow: Enterprise Application Server
Entry point for DahNAY FreightFlow Operations Platform and REST API.
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
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


@app.get("/demo-video")
def serve_demo_video():
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets", "freightflow_demo.webm"))
    if not os.path.exists(video_path):
        return HTMLResponse("<h1>Demo video is currently being generated.</h1>", status_code=404)
    return FileResponse(video_path, media_type="video/webm", filename="freightflow_demo.webm")


@app.get("/watch-demo", response_class=HTMLResponse)
def watch_demo_page():
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <title>FreightFlow | 60-Second Video Walkthrough</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
</head>
<body class="bg-[#090D16] text-slate-100 font-sans min-h-screen flex flex-col items-center justify-center p-4">
    <div class="max-w-4xl w-full bg-[#0E1424] border border-slate-800 rounded-xl p-6 shadow-2xl space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
                <h1 class="text-lg font-bold text-white flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> FreightFlow: 60-Second Operational Walkthrough
                </h1>
                <p class="text-xs text-slate-400 font-mono mt-0.5">Automated SI Ingestion, Container Checksum Audits & CargoWise XML Generation</p>
            </div>
            <a href="/dahnay" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold">Launch Live App →</a>
        </div>
        <div class="rounded-lg overflow-hidden border border-slate-800 bg-black aspect-video flex items-center justify-center">
            <video controls autoplay class="w-full h-full" src="/demo-video">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
            <div class="p-3 rounded bg-slate-900/60 border border-slate-800">
                <span class="text-blue-400 font-bold block mb-1">0:00 - 0:20</span>
                Ingests raw Excel/PDF SI in < 0.8s, eliminating 20 mins of manual re-keying.
            </div>
            <div class="p-3 rounded bg-slate-900/60 border border-slate-800">
                <span class="text-rose-400 font-bold block mb-1">0:20 - 0:40</span>
                Catches ISO 6346 check-digit typos and SOLAS VGM 2,800 KG overweight risk.
            </div>
            <div class="p-3 rounded bg-slate-900/60 border border-slate-800">
                <span class="text-emerald-400 font-bold block mb-1">0:40 - 1:00</span>
                1-click waiver clears hold; exports validated CargoWise Universal XML.
            </div>
        </div>
    </div>
</body>
</html>"""


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
