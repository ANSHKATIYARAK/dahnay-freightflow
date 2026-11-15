"""
SaaS Platform: Unified Multi-Tenant FastAPI Gateway
Provides Auth, Billing, Usage Metering, Agent Job Queue, and Live SSE Streaming.
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from urllib.parse import parse_qs
import json
import os
import sys

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from saas_platform.models import DatabaseManager, Workspace
from saas_platform.billing import BillingManager, PLANS
from saas_platform.stream import JobQueueManager
from studio_engine.registry import AgentRegistry
from studio_engine.dispatcher import AgentDispatcher

app = FastAPI(title="Enterprise Agent-as-a-Service (AaaS) Gateway", version="3.0.0")

db = DatabaseManager()
billing = BillingManager(db)
registry = AgentRegistry()
dispatcher = AgentDispatcher(registry)
job_queue = JobQueueManager(db, registry, dispatcher)

# Pre-seed a default demo workspace
demo_ws = db.create_workspace("Aura Botanics D2C Workspace", "rohan@aurabotanics.in")


@app.get("/", response_class=HTMLResponse)
def saas_portal_view():
    ws = db.get_workspace(demo_ws.workspace_id)
    plans_cards = ""
    for k, v in PLANS.items():
        is_active = (k == ws.plan_tier)
        badge = "<span class='px-2 py-0.5 rounded-full text-[10px] bg-blue-500/20 text-blue-300 font-bold'>ACTIVE</span>" if is_active else ""
        plans_cards += f"""
        <div class="bg-slate-950 border {'border-blue-500' if is_active else 'border-slate-800'} p-5 rounded-2xl flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-center mb-2">
                    <span class="font-bold text-sm text-white">{v['name']}</span>
                    {badge}
                </div>
                <div class="text-2xl font-extrabold text-blue-400 mb-1">${v['price_usd']}<span class="text-xs text-slate-500 font-normal">/mo</span></div>
                <div class="text-xs text-slate-400">{v['credits']} Credits / month</div>
                <div class="text-xs text-slate-400">{v['max_monitors']} Active Monitors</div>
            </div>
            <form action="/billing/upgrade" method="post" class="mt-4">
                <input type="hidden" name="plan" value="{k}">
                <button type="submit" class="w-full py-2 rounded-xl {'bg-blue-600 hover:bg-blue-500 text-white' if not is_active else 'bg-slate-800 text-slate-400 cursor-not-allowed'} font-bold text-xs transition">
                    {'Current Plan' if is_active else 'Select ' + v['name']}
                </button>
            </form>
        </div>
        """

    agent_options = "".join([f'<option value="{name}">{name} ({registry.get_agent(name).department})</option>' for name in sorted(registry.agents.keys())])

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{ws.name} | Agent-as-a-Service SaaS Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 antialiased">
        <div class="max-w-6xl mx-auto space-y-8">
            
            <!-- Header & Tenant Usage Meter -->
            <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Workspace ID: {ws.workspace_id}</span>
                    <h1 class="text-3xl font-extrabold tracking-tight mt-1">{ws.name}</h1>
                    <p class="text-xs text-slate-400">Owner: {ws.owner_email} • Subscription: <span class="capitalize text-white font-semibold">{ws.plan_tier}</span></p>
                </div>
                <div class="flex items-center gap-4">
                    <div class="bg-slate-900 border border-slate-800 px-5 py-3 rounded-2xl flex items-center gap-4 shadow-lg">
                        <div>
                            <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Credits Available</div>
                            <div class="text-2xl font-black text-emerald-400 mt-0.5">{ws.credits_balance} <span class="text-xs text-slate-500 font-normal">pts</span></div>
                        </div>
                        <a href="#plans" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition">+ Refill</a>
                    </div>
                </div>
            </header>

            <!-- Agent Run Submission Console with Live SSE Streaming -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Live SSE Agent Dispatcher</span>
                    <h2 class="text-2xl font-bold text-white mt-1">Execute Agent Job with Real-Time Streaming</h2>
                    <p class="text-xs text-slate-400 mt-1">Dispatches asynchronous task to background worker, streams token-by-token progress via Server-Sent Events, and deducts 1 credit upon success.</p>
                </div>

                <div class="grid sm:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 mb-1">Target Agent</label>
                        <select id="agentSelect" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                            {agent_options}
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 mb-1">Domain</label>
                        <input id="domainInput" type="text" value="E-Commerce / Amazon" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 mb-1">Instructions / Task</label>
                        <input id="promptInput" type="text" value="Audit Buy Box on SKU B09XYZ and detect price undercuts" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                </div>

                <div class="flex items-center gap-4">
                    <button id="submitJobBtn" class="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition shadow-lg shadow-blue-600/30">
                        ⚡ Dispatch Job & Stream Output
                    </button>
                    <span id="jobStatusBadge" class="hidden text-xs font-bold px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        Processing...
                    </span>
                </div>

                <!-- Live SSE Terminal Output -->
                <div class="bg-slate-950 border border-slate-800 rounded-2xl p-6 font-mono text-xs space-y-2">
                    <div class="flex justify-between text-slate-500 border-b border-slate-800 pb-2">
                        <span>LIVE EVENT STREAM (Server-Sent Events)</span>
                        <span id="streamIndicator" class="text-slate-500">DISCONNECTED</span>
                    </div>
                    <div id="terminalStream" class="h-44 overflow-y-auto space-y-1.5 text-slate-300">
                        <div class="text-slate-600 italic">Ready to stream. Click Dispatch above.</div>
                    </div>
                </div>
            </div>

            <!-- Stripe Subscription Plans -->
            <div id="plans" class="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Subscription & Metering</span>
                    <h2 class="text-2xl font-bold text-white mt-1">Upgrade Workspace Plan (Stripe Webhook Synced)</h2>
                </div>
                <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {plans_cards}
                </div>
            </div>

        </div>

        <script>
            const submitBtn = document.getElementById('submitJobBtn');
            const agentSelect = document.getElementById('agentSelect');
            const domainInput = document.getElementById('domainInput');
            const promptInput = document.getElementById('promptInput');
            const terminal = document.getElementById('terminalStream');
            const badge = document.getElementById('jobStatusBadge');
            const indicator = document.getElementById('streamIndicator');

            submitBtn.addEventListener('click', async () => {{
                submitBtn.disabled = true;
                badge.classList.remove('hidden');
                badge.textContent = 'Submitting Job...';
                terminal.innerHTML = '';
                indicator.textContent = 'CONNECTING...';
                indicator.className = 'text-amber-400 font-bold';

                // 1. Submit Job
                const res = await fetch('/api/v1/jobs', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        workspace_id: '{ws.workspace_id}',
                        agent_name: agentSelect.value,
                        domain: domainInput.value,
                        prompt: promptInput.value
                    }})
                }});

                const data = await res.json();
                const jobId = data.job_id;

                // 2. Open EventSource for SSE streaming
                const evtSource = new EventSource('/api/v1/jobs/' + jobId + '/stream');
                indicator.textContent = 'LIVE STREAMING';
                indicator.className = 'text-emerald-400 font-bold animate-pulse';

                evtSource.addEventListener('status', (e) => {{
                    const payload = JSON.parse(e.data);
                    const line = document.createElement('div');
                    line.className = 'text-blue-400';
                    line.textContent = '▶ [' + payload.progress + '%] ' + payload.step;
                    terminal.appendChild(line);
                    terminal.scrollTop = terminal.scrollHeight;
                }});

                evtSource.addEventListener('artifact', (e) => {{
                    const payload = JSON.parse(e.data);
                    const line = document.createElement('div');
                    line.className = 'text-purple-400';
                    line.textContent = '📦 Artifact Generated: ' + JSON.stringify(payload);
                    terminal.appendChild(line);
                    terminal.scrollTop = terminal.scrollHeight;
                }});

                evtSource.addEventListener('complete', (e) => {{
                    const payload = JSON.parse(e.data);
                    const line = document.createElement('div');
                    line.className = 'text-emerald-400 font-bold mt-2';
                    line.textContent = '✔ Task Completed Successfully in ' + payload.execution_time_ms + 'ms';
                    terminal.appendChild(line);
                    terminal.scrollTop = terminal.scrollHeight;

                    badge.textContent = 'Completed (1 Credit Deducted)';
                    badge.className = 'text-xs font-bold px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
                    submitBtn.disabled = false;
                    indicator.textContent = 'COMPLETED';
                    indicator.className = 'text-emerald-400';
                    evtSource.close();
                }});

                evtSource.onerror = () => {{
                    indicator.textContent = 'STREAM CLOSED';
                    indicator.className = 'text-slate-500';
                    evtSource.close();
                    submitBtn.disabled = false;
                }};
            }});
        </script>
    </body>
    </html>"""
    return html


@app.post("/api/v1/jobs")
async def create_job(request: Request):
    body = await request.json()
    ws_id = body.get("workspace_id")
    agent_name = body.get("agent_name")
    prompt = body.get("prompt")
    domain = body.get("domain", "General")

    if not billing.check_has_credits(ws_id, 1):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits balance. Please refill your workspace.")

    job = job_queue.submit_job(workspace_id=ws_id, agent_name=agent_name, prompt=prompt, domain=domain)
    return {"status": "queued", "job_id": job.job_id, "workspace_id": ws_id}


@app.get("/api/v1/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    return StreamingResponse(job_queue.stream_job_events(job_id), media_type="text/event-stream")


@app.post("/billing/upgrade")
async def upgrade_plan(request: Request):
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    new_plan = data.get("plan", ["starter"])[0]

    # Simulate Stripe Webhook checkout.session.completed
    credits_to_add = PLANS.get(new_plan, {}).get("credits", 500)
    db.add_credits(demo_ws.workspace_id, credits_to_add)

    conn = db._init_db() # sync
    import sqlite3
    con = sqlite3.connect(db.db_path)
    con.execute("UPDATE workspaces SET plan_tier = ? WHERE workspace_id = ?", (new_plan, demo_ws.workspace_id))
    con.commit()
    con.close()

    return HTMLResponse("<script>window.location.href = '/';</script>")


@app.post("/api/v1/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("type", "")
    result = billing.handle_stripe_webhook(event_type, payload)
    return result
