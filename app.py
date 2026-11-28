"""
DahNAY FreightFlow: Enterprise Application Server
Entry point for DahNAY FreightFlow Operations Platform and REST API.
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure root is in sys.path
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


@app.middleware("http")
async def vercel_path_normalization(request: Request, call_next):
    """
    Normalizes Vercel serverless request paths.
    When Vercel rewrites requests to /api/index.py, ASGI receives the destination path.
    This middleware reconstructs the real target path from Vercel forward headers.
    """
    raw_path = request.scope.get("path", "")
    fwd_uri = (
        request.headers.get("x-forwarded-uri")
        or request.headers.get("x-invoke-path")
        or request.headers.get("x-matched-path")
    )

    if raw_path in ["/api/index.py", "/api/index", "/api/index/", "/api", "/api/"]:
        if fwd_uri:
            target_path = fwd_uri.split("?")[0]
            request.scope["path"] = target_path if target_path else "/"
        else:
            request.scope["path"] = "/"
    elif raw_path.startswith("/api/index.py/"):
        request.scope["path"] = raw_path[len("/api/index.py"):]
    elif raw_path.startswith("/api/index/"):
        request.scope["path"] = raw_path[len("/api/index"):]

    return await call_next(request)


# Mount DahNAY FreightFlow API routes
app.include_router(dahnay_api_router)


@app.get("/", response_class=HTMLResponse)
@app.get("/dahnay", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
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
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dahnay_logistics", "datasets", "freightflow_demo.webm"))
    if not os.path.exists(video_path):
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DahNAY FreightFlow | 60-Second Walkthrough</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: { extend: { fontFamily: { sans: ['"Inter"', 'sans-serif'], mono: ['"JetBrains Mono"', 'monospace'] } } }
        }
    </script>
    <style>
        :root { --glass-bg: rgba(17,17,24,0.55); --glass-border: rgba(255,255,255,0.08); --glass-shadow: 0 20px 40px -10px rgba(0,0,0,0.5); }
        html.light { --glass-bg: rgba(248,250,252,0.6); --glass-border: rgba(0,0,0,0.06); --glass-shadow: 0 20px 40px -10px rgba(0,0,0,0.08); }
        * { box-sizing: border-box; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow-x: hidden; }
        body { background: #0a0a0f; color: #f8fafc; font-family: 'Inter', sans-serif; }
        html.light body { background: #fafafa; color: #0f172a; }
        #webgl { position: fixed; inset: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
        #webgl-scrim { position: fixed; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(15,23,42,0.55), rgba(10,10,15,0.85)); z-index: 1; pointer-events: none; }
        html.light #webgl-scrim { background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(255,255,255,0.35), rgba(250,250,250,0.7)); }
        .glass { background: var(--glass-bg); border: 1px solid var(--glass-border); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: var(--glass-shadow); }
        .btn-primary { background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%); border: none; color: white; transition: all 0.25s cubic-bezier(0.4,0,0.2,1); box-shadow: 0 10px 25px -5px rgba(37,99,235,0.35); }
        .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 15px 30px -5px rgba(37,99,235,0.5); filter: brightness(1.1); }
        .mode-toggle { width: 56px; height: 28px; border-radius: 999px; border: 1px solid var(--glass-border); background: var(--glass-bg); position: relative; cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
        .mode-toggle .knob { position: absolute; top: 2px; left: 2px; width: 24px; height: 24px; border-radius: 50%; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); }
        html.light .mode-toggle .knob { transform: translateX(28px); background: #f59e0b; }
        .mode-toggle .icon { position: absolute; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; opacity: 0.6; transition: opacity 0.3s; }
        .mode-toggle .sun { left: 8px; opacity: 0; } html.light .mode-toggle .sun { opacity: 1; }
        .mode-toggle .moon { right: 8px; opacity: 1; } html.light .mode-toggle .moon { opacity: 0; }
    </style>
</head>
<body class="font-sans min-h-screen antialiased overflow-hidden">
    <canvas id="webgl" class="fixed inset-0 z-0 pointer-events-none"></canvas>
    <div id="webgl-scrim" class="fixed inset-0 z-1 pointer-events-none"></div>

    <header class="relative z-40 sticky top-0 border-b border-white/5 bg-white/5 backdrop-blur-xl -webkit-backdrop-blur-xl shadow-lg px-4 sm:px-6 py-3">
        <div class="max-w-[1780px] mx-auto flex items-center justify-between">
            <div class="flex items-center gap-3 group cursor-pointer" onclick="toggleMode()">
                <div class="mode-toggle focus-ring">
                    <div class="knob"></div>
                    <svg class="icon sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                    <svg class="icon moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79"/></svg>
                </div>
                <div class="ml-2 flex flex-col">
                    <span class="text-xs font-semibold tracking-tight text-white">DahNAY FreightFlow</span>
                    <span class="text-[10px] font-mono text-blue-400 tracking-wider uppercase">EXIM OPERATIONS PLATFORM</span>
                </div>
            </div>
        </div>
    </header>

    <main class="relative z-40 max-w-[1780px] mx-auto px-4 sm:px-6 py-16 flex flex-col items-center justify-center h-[calc(100vh-140px)]">
        <div class="glass-elevated rounded-2xl p-8 md:p-12 max-w-4xl w-full text-center space-y-8 fade-in">
            <div class="flex items-center justify-between border-b border-white/10 pb-6">
                <div class="text-left">
                    <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3 justify-center">
                        <span class="w-3 h-3 rounded-full bg-emerald-400"></span> DahNAY FreightFlow: 60-Second Operational Walkthrough
                    </h1>
                    <p class="text-xs text-white/50 font-mono mt-2 text-center">Automated SI Ingestion, Container Checksum Audits & CargoWise XML Generation</p>
                </div>
            </div>

            <div class="rounded-xl overflow-hidden border border-white/10 bg-black/30 aspect-video flex items-center justify-center">
                <video controls autoplay class="w-full h-full" src="/demo-video" poster="">
                    Your browser does not support the video tag.
                </video>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
                <div class="p-4 rounded-xl bg-white/5 border border-white/10 glass">
                    <span class="text-blue-400 font-bold block mb-2">0:00 - 0:20</span>
                    <p class="text-white/80 leading-relaxed">Ingests raw Excel/PDF SI in < 0.8s, eliminating 20 mins of manual re-keying.</p>
                </div>
                <div class="p-4 rounded-xl bg-white/5 border border-white/10 glass">
                    <span class="text-rose-400 font-bold block mb-2">0:20 - 0:40</span>
                    <p class="text-white/80 leading-relaxed">Catches ISO 6346 check-digit typos and SOLAS VGM 2,800 KG overweight risk.</p>
                </div>
                <div class="p-4 rounded-xl bg-white/5 border border-white/10 glass">
                    <span class="text-emerald-400 font-bold block mb-2">0:40 - 1:00</span>
                    <p class="text-white/80 leading-relaxed">1-click waiver clears hold; exports validated CargoWise Universal XML.</p>
                </div>
            </div>

            <a href="/dahnay" class="btn-primary px-8 py-3 rounded-lg text-sm font-semibold inline-flex items-center gap-2 shadow-lg mt-4 transition-all hover:scale-[1.02] active:scale-[0.98]">
                <i data-lucide="arrow-right" class="w-4 h-4"></i> Launch Live App
            </a>
        </div>
    </main>

    <script>
        // Minimal Three.js background for demo page
        let scene, camera, renderer;
        const canvas = document.getElementById('webgl');
        if (typeof THREE !== 'undefined' && canvas) {
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x0a0a0f, 0.0015);
            camera = new THREE.PerspectiveCamera(60, innerWidth/innerHeight, 0.1, 200);
            camera.position.set(0, 5, 15);
            renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
            renderer.setSize(innerWidth, innerHeight);
            renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            scene.add(new THREE.AmbientLight(0xffffff, 0.4));
            const dl = new THREE.DirectionalLight(0x2563eb, 0.6); dl.position.set(10,20,10); scene.add(dl);
            const geo = new THREE.BoxGeometry(2.4, 2.6, 6);
            const mat = new THREE.MeshStandardMaterial({color:0x1e293b, metalness:0.3, roughness:0.7, transparent:true, opacity:0.6});
            const mesh = new THREE.InstancedMesh(geo, mat, 30);
            const dummy = new THREE.Object3D();
            for(let i=0;i<30;i++){
                const a = (i/30)*Math.PI*2*1.5, r = 12+Math.random()*8;
                dummy.position.set(Math.cos(a)*r, (Math.random()-0.5)*2, Math.sin(a)*r);
                dummy.rotation.y = a + Math.PI/2;
                dummy.scale.setScalar(0.8+Math.random()*0.4);
                dummy.updateMatrix(); mesh.setMatrixAt(i, dummy.matrix);
            }
            mesh.instanceMatrix.needsUpdate = true; scene.add(mesh);
            function animate(){ requestAnimationFrame(animate);
                const t = performance.now()*0.001;
                for(let i=0;i<30;i++){
                    mesh.getMatrixAt(i, dummy.matrix); dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale);
                    dummy.position.y += Math.sin(t+i)*0.002; dummy.rotation.y += 0.0002;
                    dummy.updateMatrix(); mesh.setMatrixAt(i, dummy.matrix);
                }
                mesh.instanceMatrix.needsUpdate = true; renderer.render(scene, camera);
            }
            animate();
            addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
        }

        function toggleMode() {
            document.documentElement.classList.toggle('light');
            localStorage.setItem('theme', document.documentElement.classList.contains('light') ? 'light' : 'dark');
        }
        (function(){ const s=localStorage.getItem('theme'); const p=matchMedia('(prefers-color-scheme: light)').matches; if(s==='light'||(!s&&p)) document.documentElement.classList.add('light'); })();
        lucide.createIcons();
    </script>
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
