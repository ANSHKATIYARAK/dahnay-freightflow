"""
StudioEngine: Enterprise Multi-Agent Web Control Center
Interactive visual dashboard to monitor 7 departments, 34 agents, and run cross-functional sprints.
Also hosts the LinkedIn Portfolio Hub & Ingestion Portal.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import json
from urllib.parse import parse_qs

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from studio_engine.registry import AgentRegistry
from studio_engine.dispatcher import AgentDispatcher, TaskRequest
from studio_engine.workflow import WorkflowOrchestrator
from tools.parse_linkedin import parse_linkedin_html
from tools.build_portfolio import build_portfolio
from dahnay_logistics.api.routes import router as dahnay_api_router
from dahnay_logistics.db.database import init_db, seed_default_bookings

# Initialize and seed DahNAY SQLite DB
init_db()
seed_default_bookings()

app = FastAPI(title="StudioEngine Enterprise Hub", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dahnay_api_router)

registry = AgentRegistry()
dispatcher = AgentDispatcher(registry)
orchestrator = WorkflowOrchestrator(registry, dispatcher)


@app.get("/portfolio", response_class=FileResponse)
def view_portfolio():
    path = "build/portfolio/index.html"
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("<h1>Portfolio file not found</h1>", status_code=404)


@app.get("/dahnay", response_class=HTMLResponse)
def dahnay_get(request: Request, source: str = "excel"):
    from dahnay_logistics.web.portal import render_dahnay_portal_html
    return render_dahnay_portal_html(selected_source=source)


@app.get("/dahnay/design-system", response_class=HTMLResponse)
@app.get("/dahnay/studio", response_class=HTMLResponse)
def dahnay_design_studio():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dahnay")


@app.post("/api/dahnay/sync-cargowise")
async def dahnay_sync_cargowise(request: Request):
    """Simulates production handshake with CargoWise One eAdaptor."""
    import uuid
    from datetime import datetime
    trx_id = f"CW-SHIP-{datetime.utcnow().strftime('%Y')}-MAA-{uuid.uuid4().hex[:6].upper()}"
    return {
        "status": "ACKNOWLEDGED",
        "system": "CargoWise One eAdaptor (PROD_IN)",
        "transaction_id": trx_id,
        "message": "UniversalShipment XML successfully ingested and validated. Booking status updated in ERP.",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/freightflow", response_class=HTMLResponse)
def freightflow_get():
    from freight_flow.portal import render_freightflow_html
    return render_freightflow_html()


@app.post("/freightflow", response_class=HTMLResponse)
async def freightflow_post(request: Request):
    from freight_flow.portal import render_freightflow_html
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    si_text = data.get("si_text", [""])[0]
    return render_freightflow_html(si_text if si_text else None)


@app.get("/ingest", response_class=HTMLResponse)
def ingest_page():
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sync LinkedIn Profile | StudioEngine Portfolio Builder</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/lucide@latest"></script>
        <style>body { font-family: 'Plus Jakarta Sans', sans-serif; }</style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-6 sm:p-12 antialiased">
        <div class="max-w-3xl mx-auto space-y-8">
            <div class="flex items-center justify-between border-b border-slate-800 pb-6">
                <div>
                    <a href="/portfolio" class="text-xs text-blue-400 hover:underline flex items-center gap-1 mb-2">
                        <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i> Back to Portfolio
                    </a>
                    <h1 class="text-2xl sm:text-3xl font-extrabold text-white">Automated Profile Ingestion Hub</h1>
                    <p class="text-sm text-slate-400 mt-1">Sync your live LinkedIn profile directly to your modern portfolio</p>
                </div>
                <a href="/portfolio" target="_blank" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center gap-2">
                    <i data-lucide="external-link" class="w-4 h-4"></i> View Portfolio
                </a>
            </div>

            <!-- Option 1: Instant Chrome Tab Sync (1-Click Bookmarklet / Console) -->
            <div class="bg-slate-900 border border-blue-500/30 rounded-3xl p-6 sm:p-8 space-y-4">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">1</span>
                    <h2 class="text-lg font-bold text-white">Instant Chrome 1-Click Sync</h2>
                </div>
                <p class="text-xs text-slate-400 leading-relaxed">
                    Open your LinkedIn profile tab in Chrome, press <kbd class="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">F12</kbd> (Console), paste this command, and press Enter:
                </p>
                <div class="relative bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-blue-300 overflow-x-auto">
                    <code>fetch('http://localhost:8000/api/ingest-profile', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({html: document.documentElement.outerHTML})}).then(r=>r.json()).then(d=>{alert('Portfolio Updated!'); window.open('http://localhost:8000/portfolio', '_blank');});</code>
                </div>
                <p class="text-[11px] text-slate-500">This automatically extracts your name, headline, experience, education, and skills directly from your authenticated Chrome tab into the portfolio.</p>
            </div>

            <!-- Option 2: Paste LinkedIn HTML or Text Directly -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-sm">2</span>
                    <h2 class="text-lg font-bold text-white">Direct HTML or Data Ingestion</h2>
                </div>
                <form action="/api/ingest-profile" method="post" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-2">Paste LinkedIn Page Source (Ctrl+U) or OuterHTML</label>
                        <textarea name="html" rows="6" class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500" placeholder="Paste <html> or <div id='profile'> here..."></textarea>
                    </div>
                    <div class="flex justify-end gap-3">
                        <button type="submit" class="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition shadow-lg shadow-blue-600/30 flex items-center gap-2">
                            <i data-lucide="sparkles" class="w-4 h-4"></i> Generate Portfolio from Data
                        </button>
                    </div>
                </form>
            </div>

        </div>
        <script>lucide.createIcons();</script>
    </body>
    </html>"""
    return html


@app.post("/api/ingest-profile")
async def ingest_profile_endpoint(request: Request):
    content_type = request.headers.get("content-type", "")
    html_content = ""
    profile_data = {}

    if "application/json" in content_type:
        try:
            body = await request.json()
            html_content = body.get("html", "")
            profile_data = body.get("profile", {})
        except Exception:
            pass
    else:
        raw_body = (await request.body()).decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw_body)
            html_content = parsed.get("html", "")
            profile_data = parsed.get("profile", {})
        except Exception:
            form = parse_qs(raw_body)
            html_content = form.get("html", [""])[0]

    if html_content:
        extracted = parse_linkedin_html(html_content)
        profile_data.update(extracted)

    if not profile_data:
        profile_data = {
            "name": "Muhammad Hudaifah Mubarak",
            "headline": "Full-Stack Software Engineer & AI Systems Architect",
            "url": "https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279"
        }

    os.makedirs("build/profile", exist_ok=True)
    with open("build/profile/extracted_linkedin.json", "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    build_portfolio(profile_data)

    if "text/html" in request.headers.get("accept", "") and "application/json" not in content_type:
        return HTMLResponse("<script>window.location.href = '/portfolio';</script>")

    return {
        "status": "success",
        "message": "Portfolio generated successfully!",
        "portfolio_url": "/portfolio",
        "profile": profile_data
    }


@app.get("/", response_class=HTMLResponse)
def index_view():
    dept_colors = {
        "engineering": "blue",
        "product": "amber",
        "marketing": "rose",
        "design": "purple",
        "project-management": "indigo",
        "studio-operations": "emerald",
        "testing": "cyan"
    }

    departments_html = ""
    for dept, agent_names in registry.departments.items():
        color = dept_colors.get(dept, "slate")
        agent_chips = ""
        for name in agent_names:
            agent = registry.get_agent(name)
            status_dot = "bg-emerald-400" if agent.status == "completed" else ("bg-amber-400 animate-pulse" if agent.status == "working" else "bg-slate-500")
            agent_chips += f"""
            <div class="p-3 bg-slate-950 border border-slate-800 rounded-xl hover:border-slate-700 transition flex items-center justify-between">
                <div>
                    <div class="font-bold text-xs text-white flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full {status_dot}"></span>
                        {agent.name}
                    </div>
                    <div class="text-[10px] text-slate-400 mt-0.5">{agent.role}</div>
                </div>
            </div>
            """

        departments_html += f"""
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-{color}-400">{dept.replace('-', ' ')}</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-{color}-500/10 text-{color}-300 border border-{color}-500/20">{len(agent_names)} Agents</span>
                </div>
                <div class="space-y-2">{agent_chips}</div>
            </div>
        </div>
        """

    agent_options = "".join([f'<option value="{name}">{name} ({registry.get_agent(name).department})</option>' for name in sorted(registry.agents.keys())])

    recent_tasks_html = ""
    for task in reversed(dispatcher.history[-5:]):
        recent_tasks_html += f"""
        <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs space-y-2">
            <div class="flex items-center justify-between">
                <span class="font-bold text-blue-400">Agent: {task.agent_name} ({task.department})</span>
                <span class="text-slate-500 text-[10px]">{task.execution_time_ms} ms</span>
            </div>
            <pre class="text-slate-300 font-sans whitespace-pre-wrap leading-relaxed">{task.output_text}</pre>
        </div>
        """

    if not recent_tasks_html:
        recent_tasks_html = "<div class='text-xs text-slate-500 italic p-4'>No agent tasks dispatched yet. Use the console above to run a task or launch a full venture sprint.</div>"

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StudioEngine | Enterprise Multi-Agent Control Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 antialiased">
        <div class="max-w-7xl mx-auto space-y-10">

            <!-- Top Header -->
            <header class="flex flex-col md:flex-row items-start md:items-center justify-between pb-8 border-b border-slate-800 gap-4">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
                        Enterprise Autonomous Studio
                    </div>
                    <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">StudioEngine Operations Center</h1>
                    <p class="text-sm text-slate-400 mt-1">Governing 7 Departments, 34 Specialized Autonomous Agents, and End-to-End Delivery</p>
                </div>
                <div class="flex items-center gap-4 text-xs font-semibold">
                    <a href="/portfolio" target="_blank" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center gap-2">
                        View Portfolio
                    </a>
                    <a href="/ingest" class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 font-semibold text-xs transition flex items-center gap-2">
                        Sync LinkedIn
                    </a>
                    <div class="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        34 Agents Ready
                    </div>
                </div>
            </header>

            <!-- Department Matrix -->
            <div>
                <h2 class="text-lg font-bold text-white mb-4">Autonomous Organization Grid</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">{departments_html}</div>
            </div>

            <!-- Dispatches -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
                <h2 class="text-lg font-bold text-white">Manual Agent Dispatch</h2>
                <form action="/dispatch-task" method="post" class="space-y-4">
                    <div class="grid sm:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1">Target Agent</label>
                            <select name="agent_name" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500">
                                {agent_options}
                            </select>
                        </div>
                        <div class="sm:col-span-2">
                            <label class="block text-xs font-semibold text-slate-400 mb-1">Direct Task Prompt</label>
                            <input type="text" name="prompt" placeholder="Specify requirements for this specialized agent..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500" required>
                        </div>
                    </div>
                    <div class="flex justify-end">
                        <button type="submit" class="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition shadow-lg shadow-blue-600/30">
                            Dispatch Task
                        </button>
                    </div>
                </form>
            </div>

            <!-- Recent Task Output Stream -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4">
                    <h3 class="text-lg font-bold text-white">Live Execution Feed & Deliverables</h3>
                    <span class="text-xs text-slate-400">Latest completed tasks</span>
                </div>
                <div class="space-y-4">{recent_tasks_html}</div>
            </div>

        </div>
    </body>
    </html>"""
    return html


@app.post("/api/dispatch")
async def api_dispatch_endpoint(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    agent_name = data.get("agent_name", "ai-engineer")
    prompt = data.get("prompt", "Analyze architecture")
    req = TaskRequest(agent_name=agent_name, prompt=prompt)
    res = dispatcher.dispatch(req)
    return {
        "status": "success",
        "agent_name": res.agent_name,
        "department": res.department,
        "execution_time_ms": res.execution_time_ms,
        "output_text": res.output_text
    }


@app.post("/dispatch-task")
async def dispatch_task_endpoint(request: Request):
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    agent_name = data.get("agent_name", [""])[0]
    prompt = data.get("prompt", [""])[0]
    req = TaskRequest(agent_name=agent_name, prompt=prompt)
    dispatcher.dispatch(req)
    return HTMLResponse("<script>window.location.href = '/';</script>")


@app.post("/run-sprint")
async def run_sprint_endpoint(request: Request):
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    project_name = data.get("project_name", ["Enterprise Venture"])[0]
    target_niche = data.get("target_niche", ["SaaS Founders"])[0]
    orchestrator.run_full_venture_sprint(project_name=project_name, target_niche=target_niche)
    return HTMLResponse("<script>window.location.href = '/';</script>")
