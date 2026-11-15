"""
FreightFlow AI: Web Interface & Operations Portal
Interactive dashboard for DahNAY Logistics & freight forwarders:
- Side-by-side document review
- Real-time discrepancy detection & VGM overload flags
- Automated commercial freight invoice generation & ERP sync
"""

from fastapi.responses import HTMLResponse
import json
from freight_flow.models import MasterJobRecord
from freight_flow.extractor import ShippingInstructionExtractor
from freight_flow.validator import FreightReconciliationEngine
from freight_flow.invoice_builder import FreightInvoiceBuilder

DEFAULT_SI_TEXT = """SHIPPING INSTRUCTIONS (DRAFT)
Booking Ref: BKG-MAA-992104
Shipper: Tirupur Garments Export Ltd, Plot 14, SIDCO Industrial Estate, Tirupur, Tamil Nadu
Consignee: Gulf Retail Fashion LLC, Dubai Mall, Downtown Dubai, UAE
Port of Loading: Chennai Port (INMAA)
Port of Discharge: Jebel Ali Port (AEJEA)
Vessel: MSC EMANUELA Voyage: 2408W
Gross Weight: 26800 KGS
Volume: 64.2 CBM
Packages: 920 Cartons
Cargo Description: 100% Cotton Knitted Finished T-Shirts
HS Code: 6109.10
Containers:
MSCU9081245 / SL982103
MEDU4091823 / SL982104
"""

DEFAULT_JOB = MasterJobRecord(
    job_id="JOB-2026-CHN-048",
    booking_reference="BKG-MAA-992104",
    customer_account="Tirupur Garments Export Ltd",
    expected_shipper="Tirupur Garments Export Ltd",
    expected_consignee="Gulf Retail Fashion LLC",
    pol="Chennai Port (INMAA)",
    pod="Jebel Ali Port (AEJEA)",
    approved_weight_limit_kg=24000.0,
    agreed_ocean_freight_usd=1650.0,
    terminal_handling_charges_inr=11500.0,
    documentation_fee_inr=4500.0,
    expected_containers_count=2
)


def render_freightflow_html(si_text: str = DEFAULT_SI_TEXT) -> str:
    si, confidence = ShippingInstructionExtractor.extract_from_text(si_text)
    audit = FreightReconciliationEngine.audit_shipping_instruction(si, DEFAULT_JOB)
    invoice = FreightInvoiceBuilder.generate_invoice(si, DEFAULT_JOB, audit)

    # Discrepancy flags badges
    flags_html = ""
    for f in audit.flags:
        color = "red" if f.severity == "CRITICAL" else "amber"
        flags_html += f"""
        <div class="p-4 rounded-2xl bg-{color}-500/10 border border-{color}-500/20 space-y-1.5">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold uppercase tracking-wider text-{color}-400">[{f.severity}] {f.field_name}</span>
                <span class="text-[10px] font-mono text-slate-400">Action Required</span>
            </div>
            <p class="text-xs text-white font-medium">{f.issue_description}</p>
            <p class="text-[11px] text-{color}-300/80">▸ <span class="font-semibold">Remedy:</span> {f.remedy_suggestion}</p>
        </div>
        """

    if not flags_html:
        flags_html = """
        <div class="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-center space-y-1">
            <i data-lucide="check-circle" class="w-8 h-8 text-emerald-400 mx-auto mb-2"></i>
            <div class="text-sm font-bold text-emerald-400">Zero Documentation Discrepancies</div>
            <p class="text-xs text-slate-400">All fields match Master Booking. Ready for instant BL transmission.</p>
        </div>
        """

    # Line items
    items_html = ""
    for it in invoice.line_items:
        items_html += f"""
        <tr class="border-b border-slate-800/80 text-xs">
            <td class="py-3 text-slate-300 font-medium">{it.description}</td>
            <td class="py-3 font-mono text-slate-400 text-center">{it.currency} {it.rate:,.2f}</td>
            <td class="py-3 font-mono text-slate-400 text-center">{it.quantity}</td>
            <td class="py-3 font-mono text-white text-right font-bold">{it.currency} {it.amount:,.2f}</td>
        </tr>
        """

    status_badge = (
        '<span class="px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/20">Critical Mismatch</span>'
        if audit.match_status == "CRITICAL_REJECT"
        else (
            '<span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">Pending Review</span>'
            if audit.match_status == "FLAGGED_FOR_REVIEW"
            else '<span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">100% Match</span>'
        )
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FreightFlow AI | Autonomous Document-to-Invoice Pre-Fill Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        code, pre, .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
        .glass-card {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased p-6 sm:p-10 space-y-8">

    <!-- Top Navigation -->
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
                EXIM Logistics Automation • Built for DahNAY & Indian Freight Forwarders
            </div>
            <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-300 to-white bg-clip-text text-transparent">
                FreightFlow AI: Document-to-Invoice Engine
            </h1>
            <p class="text-xs text-slate-400 mt-1">
                Reads inbound Shipping Instructions (PDF/Text/WhatsApp), extracts entities, cross-checks ERP booking records, and auto-generates error-free freight invoices.
            </p>
        </div>
        <div class="flex items-center gap-3">
            <a href="/portfolio" class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-semibold transition flex items-center gap-1.5">
                <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i> Muhammad's Portfolio
            </a>
            <div class="px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Engine Active
            </div>
        </div>
    </header>

    <!-- Pitch & ROI Header Banner -->
    <section class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="glass-card p-5 rounded-2xl border border-slate-800/80">
            <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Target Client</span>
            <div class="text-xl font-extrabold text-white mt-1">DahNAY Logistics</div>
            <div class="text-xs text-slate-500">Chennai Headquarters (2,500+ TEU/mo)</div>
        </div>
        <div class="glass-card p-5 rounded-2xl border border-slate-800/80">
            <span class="text-[11px] font-bold uppercase tracking-wider text-amber-400">Bottleneck Solved</span>
            <div class="text-xl font-extrabold text-amber-300 mt-1">BL Amendment Fees</div>
            <div class="text-xs text-slate-500">Saves $50–$150 USD per documentation error</div>
        </div>
        <div class="glass-card p-5 rounded-2xl border border-slate-800/80">
            <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-400">Annual Loss Prevented</span>
            <div class="text-xl font-extrabold text-emerald-400 mt-1">₹1.56 Crore / Yr</div>
            <div class="text-xs text-slate-500">Based on 8% error rate across 30,000 TEU</div>
        </div>
        <div class="glass-card p-5 rounded-2xl border border-slate-800/80">
            <span class="text-[11px] font-bold uppercase tracking-wider text-blue-400">SaaS Pitch Price</span>
            <div class="text-xl font-extrabold text-blue-400 mt-1">₹75,000 / Month</div>
            <div class="text-xs text-slate-500">Or ₹35 per processed Bill of Lading</div>
        </div>
    </section>

    <!-- 3-Column Reconciliation Workspace -->
    <main class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Column 1: Inbound Document Input -->
        <div class="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
                <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    <div class="flex items-center gap-2">
                        <i data-lucide="file-text" class="w-4 h-4 text-blue-400"></i>
                        <h3 class="font-bold text-sm text-white">1. Inbound Shipping Instruction</h3>
                    </div>
                    <span class="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">Confidence: {confidence * 100}%</span>
                </div>
                
                <form action="/freightflow" method="post" class="space-y-3">
                    <label class="block text-xs text-slate-400 font-medium">Raw SI Text / OCR Payload (Test different weights or ports)</label>
                    <textarea name="si_text" rows="12" class="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-blue-500 leading-relaxed">{si_text}</textarea>
                    
                    <button type="submit" class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i> Re-Audit & Extract
                    </button>
                </form>
            </div>

            <div class="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
                <div class="font-semibold text-slate-300">Extracted Key Attributes:</div>
                <div>• Vessel: <span class="text-white font-mono">{si.vessel_name} ({si.voyage_number})</span></div>
                <div>• Containers: <span class="text-white font-mono">{len(si.containers)} x 40HC</span></div>
                <div>• Gross Weight: <span class="text-white font-mono">{si.total_gross_weight_kg:,.1f} KGS</span></div>
                <div>• Cargo: <span class="text-white">{si.cargo_description}</span></div>
            </div>
        </div>

        <!-- Column 2: Discrepancy & Audit Queue -->
        <div class="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div class="space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div class="flex items-center gap-2">
                        <i data-lucide="shield-alert" class="w-4 h-4 text-amber-400"></i>
                        <h3 class="font-bold text-sm text-white">2. Discrepancy & Exception Queue</h3>
                    </div>
                    {status_badge}
                </div>

                <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-xs space-y-2">
                    <div class="flex justify-between">
                        <span class="text-slate-400">Job Reference:</span>
                        <span class="font-mono text-white font-bold">{DEFAULT_JOB.job_id}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">Approved Slot Weight:</span>
                        <span class="font-mono text-emerald-400 font-bold">{DEFAULT_JOB.approved_weight_limit_kg:,.0f} kg</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-slate-400">Booking Ports:</span>
                        <span class="font-mono text-slate-300">{DEFAULT_JOB.pol} → {DEFAULT_JOB.pod}</span>
                    </div>
                </div>

                <div class="space-y-3">
                    <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Automated Audit Findings:</div>
                    <div class="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                        {flags_html}
                    </div>
                </div>
            </div>

            <div class="pt-4 border-t border-slate-800 flex items-center justify-between text-xs">
                <span class="text-slate-400">Audit Status:</span>
                <span class="font-mono text-white font-bold">{audit.match_status}</span>
            </div>
        </div>

        <!-- Column 3: Commercial Invoice Pre-fill -->
        <div class="glass-card p-6 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div class="space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div class="flex items-center gap-2">
                        <i data-lucide="receipt" class="w-4 h-4 text-emerald-400"></i>
                        <h3 class="font-bold text-sm text-white">3. Pre-Filled Commercial Invoice</h3>
                    </div>
                    <span class="text-[10px] font-mono text-slate-400">{invoice.invoice_number}</span>
                </div>

                <div class="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-1">
                    <div class="text-slate-400">Bill-To Customer:</div>
                    <div class="text-white font-bold">{invoice.bill_to_party}</div>
                    <div class="text-slate-500 font-mono text-[10px]">GSTIN: {invoice.tax_id_gstin}</div>
                </div>

                <!-- Invoice Line Items Table -->
                <div class="space-y-2">
                    <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Calculated Line Items:</div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="text-[10px] font-mono uppercase text-slate-500 border-b border-slate-800">
                                    <th class="py-1.5">Charge</th>
                                    <th class="py-1.5 text-center">Rate</th>
                                    <th class="py-1.5 text-center">Qty</th>
                                    <th class="py-1.5 text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Invoice Totals -->
                <div class="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
                    <div class="flex justify-between text-xs">
                        <span class="text-slate-400">Total USD Equivalent:</span>
                        <span class="font-mono text-white font-bold">${invoice.total_amount_usd:,.2f} USD</span>
                    </div>
                    <div class="flex justify-between text-sm border-t border-slate-800/80 pt-2">
                        <span class="font-bold text-white">Total Invoice (INR):</span>
                        <span class="font-mono text-emerald-400 font-extrabold text-base">₹{invoice.total_amount_inr:,.2f}</span>
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="space-y-2 pt-4 border-t border-slate-800">
                <button onclick="alert('Successfully pushed Invoice {invoice.invoice_number} to CargoWise / Logisys ERP API!');" class="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2">
                    <i data-lucide="check" class="w-4 h-4"></i> Approve & Push to CargoWise ERP
                </button>
                <button onclick="navigator.clipboard.writeText(JSON.stringify({json.dumps(invoice.dict())}, null, 2)); alert('Export JSON copied to clipboard!');" class="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-xs transition border border-slate-700/60 flex items-center justify-center gap-2">
                    <i data-lucide="copy" class="w-3.5 h-3.5"></i> Export Invoice Payload (JSON)
                </button>
            </div>
        </div>

    </main>

    <footer class="max-w-7xl mx-auto pt-6 border-t border-slate-900 text-center text-xs text-slate-600">
        © 2026 FreightFlow AI. Engineered by Muhammad Hudaifah Mubarak for Indian Freight Operations.
    </footer>

    <script>lucide.createIcons();</script>
</body>
</html>"""
