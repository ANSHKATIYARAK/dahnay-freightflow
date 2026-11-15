"""
VentureOS: Central Management Dashboard & Web Server
Local FastAPI application to view, launch, and monitor all ventures, websites, and outbound campaigns.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from venture_os.engine import VentureOSEngine
from venture_os.archetypes import ARCHETYPES
from venture_os.agents.lead_sourcer import LeadSourcerAgent
from venture_os.generators.landing_page import LandingPageGenerator

app = FastAPI(title="VentureOS Local Hub", version="1.0.0")

# In-memory store of active ventures
VENTURES = {}
engine = VentureOSEngine()
sourcer = LeadSourcerAgent()
page_gen = LandingPageGenerator()

# Pre-seed with a primary venture
initial_prospects = sourcer.source_for_niche("Amazon.in / Meesho D2C Brand Sellers", count=2)
v1 = engine.run_lifecycle("Amazon.in / Meesho D2C Brand Sellers", initial_prospects, simulated_replies=1)
page_gen.generate(v1)
VENTURES[v1.venture_id] = v1

@app.get("/", response_class=HTMLResponse)
def index_dashboard():
    ventures_cards = ""
    for vid, v in VENTURES.items():
        spec = v.product_spec
        pain = v.pain_signal
        status_color = "emerald" if v.telemetry.status == "graduated" else "blue"
        
        ventures_cards += f"""
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl hover:border-slate-700 transition">
            <div class="flex items-center justify-between mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">{v.niche}</span>
                <span class="px-3 py-1 rounded-full text-xs font-bold bg-{status_color}-500/10 text-{status_color}-400 uppercase">{v.telemetry.status}</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-1">{spec.name if spec else 'Venture'}</h3>
            <p class="text-sm text-slate-400 mb-4">{spec.core_utility if spec else ''}</p>
            
            <div class="space-y-2 py-3 border-y border-slate-800/80 text-xs text-slate-300">
                <div class="flex justify-between"><span>Est. Inaction Loss:</span> <strong class="text-rose-400">₹{pain.estimated_monthly_loss_inr:,.0f}/mo</strong></div>
                <div class="flex justify-between"><span>Audits Pre-Computed:</span> <strong>{len(v.audits)} leads</strong></div>
                <div class="flex justify-between"><span>Outbound Hooks:</span> <strong>{len(v.outreach_campaign)} ready</strong></div>
            </div>

            <div class="mt-5 flex gap-3">
                <a href="/preview/{vid}" target="_blank" class="flex-1 text-center py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition">
                    View Live Landing Page
                </a>
                <a href="/venture/{vid}" class="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition">
                    Inspect Details
                </a>
            </div>
        </div>
        """

    archetype_options = "".join([f'<option value="{k}">{v.name} ({v.category})</option>' for k, v in ARCHETYPES.items()])

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>VentureOS Hub | Autonomous SaaS Engine</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 antialiased">
        <div class="max-w-6xl mx-auto">
            <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-8 mb-8 border-b border-slate-800 gap-4">
                <div>
                    <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">VentureOS Hub</h1>
                    <p class="text-sm text-slate-400 mt-1">Autonomous Multi-Agent Venture Pipeline & SaaS Factory</p>
                </div>
                <div class="flex items-center gap-3">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        Pipeline Engine Online
                    </span>
                </div>
            </header>

            <!-- Quick Launch Form -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 mb-10 shadow-2xl">
                <h2 class="text-lg font-bold text-white mb-2">Deploy New Autonomous Micro-SaaS Venture</h2>
                <p class="text-xs text-slate-400 mb-6">Mines friction, verifies economic defense, builds the code, generates landing page, and prepares pre-computed outbound audits in 5 seconds.</p>
                <form action="/create" method="post" class="grid sm:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 mb-1">Target Niche / Audience</label>
                        <input name="niche" type="text" placeholder="e.g. CA Firms & GST Filers" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 mb-1">Select Archetype</label>
                        <select name="archetype" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500">
                            {archetype_options}
                        </select>
                    </div>
                    <div class="flex items-end">
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl transition text-sm shadow-lg shadow-blue-600/30">
                            + Synthesize Venture
                        </button>
                    </div>
                </form>
            </div>

            <!-- Active Ventures Grid -->
            <div>
                <h2 class="text-xl font-bold text-white mb-6">Active Portfolio Ventures ({len(VENTURES)})</h2>
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {ventures_cards}
                </div>
            </div>
        </div>
    </body>
    </html>"""
    return html

from urllib.parse import parse_qs

@app.post("/create")
async def create_venture(request: Request):
    body = (await request.body()).decode("utf-8")
    data = parse_qs(body)
    niche = data.get("niche", ["B2B SaaS"])[0]
    prospects = sourcer.source_for_niche(niche, count=2)
    v = engine.run_lifecycle(niche, prospects, simulated_replies=1)
    page_gen.generate(v)
    VENTURES[v.venture_id] = v
    return HTMLResponse(f"""<script>window.location.href = '/venture/{v.venture_id}';</script>""")

@app.get("/preview/{vid}")
def preview_landing_page(vid: str):
    path = f"build/websites/{vid}_index.html"
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("<h1>Landing page file not found</h1>", status_code=404)

@app.get("/venture/{vid}", response_class=HTMLResponse)
def view_venture(vid: str):
    v = VENTURES.get(vid)
    if not v:
        return HTMLResponse("<h1>Venture not found</h1>", status_code=404)

    audits_html = ""
    for a in v.audits:
        audits_html += f"""
        <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs space-y-1">
            <div class="font-bold text-white">SKU: {a.product_identifier}</div>
            <div class="text-rose-400 font-semibold">Weekly Leak: ₹{a.estimated_weekly_revenue_leak_inr:,.0f}</div>
            <div class="text-slate-400">{a.audit_summary}</div>
        </div>
        """

    hooks_html = ""
    for h in v.outreach_campaign:
        hooks_html += f"""
        <div class="bg-slate-950 border border-slate-800 p-5 rounded-xl space-y-3">
            <div class="text-xs font-bold text-blue-400">Subject: {h.subject_line}</div>
            <pre class="text-xs text-slate-300 font-sans whitespace-pre-wrap leading-relaxed">{h.body_markdown}</pre>
        </div>
        """

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{v.product_spec.name if v.product_spec else 'Venture'} | Details</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 antialiased">
        <div class="max-w-5xl mx-auto space-y-8">
            <div class="flex items-center justify-between pb-6 border-b border-slate-800">
                <a href="/" class="text-xs font-bold text-blue-400 hover:text-blue-300">← Back to Hub</a>
                <a href="/preview/{vid}" target="_blank" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition">
                    Open Live Landing Page ↗
                </a>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-400">Venture ID: {v.venture_id}</span>
                    <h1 class="text-3xl font-extrabold mt-1">{v.product_spec.name if v.product_spec else 'Venture'}</h1>
                    <p class="text-sm text-slate-400 mt-1">{v.product_spec.core_utility if v.product_spec else ''}</p>
                </div>

                <div class="grid md:grid-cols-2 gap-6">
                    <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl">
                        <h3 class="text-sm font-bold text-white mb-3">Pre-Computed Trojan Audits</h3>
                        <div class="space-y-3">{audits_html}</div>
                    </div>
                    <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl">
                        <h3 class="text-sm font-bold text-white mb-3">Target Outbound Pitch</h3>
                        <div class="space-y-3">{hooks_html}</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>"""
    return html
