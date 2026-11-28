"""
DahNAY FreightFlow Operations Platform — Industrial Luxury UI
Enterprise EXIM Document-to-Invoice & CargoWise One EDI Bridge.

Design Direction: "Industrial Luxury" — dark charcoal canvas, warm amber/gold accents,
sharp geometric glass panels, premium noise textures, cinematic Three.js scene.
Not a template. Not generic. Built for DahNAY's identity: serious, precise, premium.

Accessibility: WCAG 2.2 AA compliant — ARIA labels, live regions, contrast, keyboard,
focus management, reduced motion, skip link, semantic HTML.
"""

import json
import os
from typing import Dict, Any, List
from dahnay_logistics.backend.service import FreightFlowService


def render_dahnay_portal_html(selected_source: str = "excel") -> str:
    # Ensure default data is initialized
    shipments = FreightFlowService.list_shipments()
    active_booking_ref = "BKG-MAA-992104"
    detail = FreightFlowService.get_shipment_detail(active_booking_ref)

    if not detail or not detail.get("document"):
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "sample_dahnay_si.xlsx"))
        if os.path.exists(sample_path):
            detail = FreightFlowService.ingest_document(sample_path, "sample_dahnay_si.xlsx")
            shipments = FreightFlowService.list_shipments()

    booking = detail.get("booking", {}) if detail else {}
    document = detail.get("document", {}) if detail else {}
    containers = detail.get("containers", []) if detail else []
    discrepancies = detail.get("discrepancies", []) if detail else []
    invoice = detail.get("invoice", {}) if detail else {}
    audit_trail = detail.get("audit_trail", []) if detail else {}

    # 1. Shipments Table Rows
    shipments_rows = []
    for s in shipments:
        is_sel = (s['booking_reference'] == active_booking_ref)
        color = "blue" if s['status'] == "CARGOWISE_SYNCED" else ("rose" if s['unresolved_discrepancies'] > 0 else "emerald")
        badge_text = s['status'].replace("_", " ")
        sel_cls = "bg-white/10 border-l-2 border-l-blue-400 font-medium" if is_sel else "border-l-2 border-l-transparent hover:bg-white/5"

        # Precompute to avoid f-string quote nesting
        disc_count = s['unresolved_discrepancies']
        if disc_count > 0:
            flag_badge = f'<span class="inline-flex items-center justify-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20" aria-label="{disc_count} discrepancies on hold">{disc_count} HOLD</span>'
        else:
            flag_badge = '<span class="inline-flex items-center justify-center px-2 py-0.5 rounded text-[11px] font-mono font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20" aria-label="No discrepancies">CLEAR</span>'

        bkg_ref = s['booking_reference']
        cust_acc = s['customer_account']
        pol = s['pol']
        pod = s['pod']
        vessel = s['vessel']
        invoice_total = s['invoice_total_inr']
        idx = shipments.index(s)

        shipments_rows.append(f"""
        <tr onclick="loadShipment('{bkg_ref}')" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();loadShipment('{bkg_ref}')}}" tabindex="0" role="button" aria-label="Load shipment {bkg_ref}" class="table-row border-b border-white/5 text-xs transition-all duration-200 cursor-pointer {sel_cls} fade-in" style="animation-delay: {idx * 40}ms">
            <td class="py-3 px-4 font-mono font-bold text-blue-400">{bkg_ref}</td>
            <td class="py-3 px-4 font-medium text-white">{cust_acc}</td>
            <td class="py-3 px-4 font-mono text-white/70">{pol} <span class="text-white/40">→</span> {pod}</td>
            <td class="py-3 px-4 text-white/70">{vessel}</td>
            <td class="py-3 px-4">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-{color}-500/10 text-{color}-400 border border-{color}-500/30">
                    <span class="w-1.5 h-1.5 rounded-full bg-{color}-400" aria-hidden="true"></span> {badge_text}
                </span>
            </td>
            <td class="py-3 px-4 text-center">{flag_badge}</td>
            <td class="py-3 px-4 font-mono text-right font-semibold text-white tabular-nums">
                ₹{invoice_total:,.2f}
            </td>
        </tr>
        """)
    shipments_rows_html = "".join(shipments_rows)

    # 2. Discrepancy Exception Items
    discrepancy_cards = []
    for f in discrepancies:
        is_res = bool(f.get("is_resolved"))
        sev = f.get("severity", "WARNING")
        fn = f.get("field_name", "")

        btn = ""
        if not is_res:
            if "CONTAINER" in fn.upper():
                btn = f"""<button onclick="resolveFlag('{f.get('id')}', 'AUTO_FIX')" class="btn-magnetic btn-primary px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-lg" aria-label="Auto-correct container check-digit for {fn.replace('_', ' ')}">
                    <i data-lucide="check" class="w-3.5 h-3.5"></i> Auto-Correct Check-Digit
                    <span class="ripple" aria-hidden="true"></span>
                </button>"""
            elif "WEIGHT" in fn.upper():
                btn = f"""<button onclick="resolveFlag('{f.get('id')}', 'MANAGER_WAIVER')" class="btn-magnetic btn-primary px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-lg" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);" aria-label="Record shipper weight waiver for {fn.replace('_', ' ')}">
                    <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> Record Shipper Weight Waiver
                    <span class="ripple" aria-hidden="true"></span>
                </button>"""
            else:
                btn = f"""<button onclick="resolveFlag('{f.get('id')}', 'MANUAL_EDIT')" class="btn-magnetic btn-glass px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5" aria-label="Mark {fn.replace('_', ' ')} as checked">
                    <i data-lucide="edit-2" class="w-3.5 h-3.5"></i> Mark Checked
                    <span class="ripple" aria-hidden="true"></span>
                </button>"""

        if is_res:
            item_html = f"""
            <div class="p-4 rounded-xl glass border-emerald-500/20 opacity-60 text-xs space-y-2 fade-in" role="status" aria-live="polite">
                <div class="flex items-center justify-between">
                    <span class="font-mono text-emerald-400 font-semibold flex items-center gap-1.5">
                        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400" aria-hidden="true"></i> {fn.replace('_', ' ')}
                    </span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">RESOLVED</span>
                </div>
                <p class="text-white/60">{f.get('issue_description', '')}</p>
            </div>
            """
        else:
            border_col = "border-rose-500/40 bg-rose-500/5" if sev == "CRITICAL" else "border-amber-500/40 bg-amber-500/5"
            text_col = "text-rose-400" if sev == "CRITICAL" else "text-amber-400"
            badge_col = "bg-rose-500/10 text-rose-300 border-rose-500/30" if sev == "CRITICAL" else "bg-amber-500/10 text-amber-300 border-amber-500/30"
            pulse = "animate-pulse" if sev == "CRITICAL" else ""

            item_html = f"""
            <div class="p-4 rounded-xl border {border_col} text-xs space-y-3 fade-in" role="alert" aria-live="assertive">
                <div class="flex items-center justify-between">
                    <span class="font-mono font-bold {text_col} flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full {text_col.replace('text-', 'bg-')} {pulse}" aria-hidden="true"></span>
                        [{sev}] {fn.replace('_', ' ')}
                    </span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold {badge_col} border">
                        ACTION REQUIRED
                    </span>
                </div>
                <p class="text-white font-medium leading-relaxed">{f.get('issue_description', '')}</p>
                <div class="p-3 rounded bg-black/30 border border-white/10 text-[11px] text-white/60 space-y-1 glass">
                    <div class="text-white/40 uppercase text-[9px] font-mono font-semibold">Standard Operating Procedure</div>
                    <div>{f.get('remedy_suggestion', '')}</div>
                </div>
                <div class="pt-1">{btn}</div>
            </div>
            """
        discrepancy_cards.append(item_html)
    discrepancies_cards_html = "".join(discrepancy_cards)

    # 3. Container Equipment Rows
    cntr_rows = []
    for c in containers:
        is_val = bool(c.get("is_checksum_valid"))
        badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">ISO Valid</span>' if is_val else f'<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">Typo (Exp: {c.get("expected_check_digit")})</span>'
        cntr_rows.append(f"""
        <tr class="table-row border-b border-white/5 text-xs hover:bg-white/5 transition-colors">
            <td class="py-3 px-3 font-mono font-bold text-blue-400">{c.get('container_number')}</td>
            <td class="py-3 px-2">{badge}</td>
            <td class="py-3 px-3 font-mono text-white/70">{c.get('seal_number')}</td>
            <td class="py-3 px-2 text-white/70">{c.get('container_type')}</td>
            <td class="py-3 px-3 font-mono text-right text-white tabular-nums">{c.get('gross_weight_kg', 0):,.1f} KGS</td>
            <td class="py-3 px-2 font-mono text-right text-white/70 tabular-nums">{c.get('packages_count')} pkgs</td>
            <td class="py-3 px-3 font-mono text-right text-white/70 tabular-nums">{c.get('cbm', 0):,.2f}</td>
        </tr>
        """)
    containers_rows_html = "".join(cntr_rows)

    # 4. Invoice Line Items
    inv_rows = []
    for item in (invoice.get("line_items") or []):
        cur = item.get("currency", "INR")
        amt_sym = "$" if cur == "USD" else "₹"
        amt_val = item.get("amount", 0)
        inv_rows.append(f"""
        <tr class="border-b border-white/5 text-xs hover:bg-white/5 transition-colors">
            <td class="py-2 px-3 text-white">{item.get('description')}</td>
            <td class="py-2 px-2 font-mono text-center text-white/50">{cur}</td>
            <td class="py-2 px-2 font-mono text-right text-white/70 tabular-nums">{item.get('rate', 0):,.2f}</td>
            <td class="py-2 px-2 font-mono text-center text-white/70">{item.get('quantity', 1)}</td>
            <td class="py-2 px-3 font-mono text-right font-bold text-white tabular-nums">{amt_sym}{amt_val:,.2f}</td>
        </tr>
        """)
    invoice_items_rows_html = "".join(inv_rows)

    # Status Pill formatting
    is_synced = (document.get("lifecycle_state") == "CARGOWISE_SYNCED")
    has_flags = any(f.get("is_resolved") == 0 for f in discrepancies)
    if is_synced:
        status_pill_cls = "px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30 flex items-center gap-2 backdrop-blur-sm"
        status_pill_text = '<span class="w-2 h-2 rounded-full bg-blue-400" aria-hidden="true"></span> CARGOWISE_SYNCED'
    elif has_flags:
        status_pill_cls = "px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-2 backdrop-blur-sm"
        status_pill_text = '<span class="w-2 h-2 rounded-full bg-rose-400 animate-pulse" aria-hidden="true"></span> EXCEPTION_HOLD'
    else:
        status_pill_cls = "px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-2 backdrop-blur-sm"
        status_pill_text = '<span class="w-2 h-2 rounded-full bg-emerald-400" aria-hidden="true"></span> APPROVED_FOR_EDI'

    gst_half = invoice.get("gst_amount_inr", 0) / 2.0

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="DahNAY FreightFlow — Automated EXIM Document-to-Invoice Pre-Fill & CargoWise One EDI Bridge">
    <title>DahNAY FreightFlow | Operations Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/postprocessing/EffectComposer.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/postprocessing/RenderPass.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/postprocessing/UnrealBloomPass.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.0/shaders/CopyShader.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Syne"', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }},
                }}
            }}
        }}
    </script>
    <style>
        :root {{
            --glass-bg: rgba(22, 24, 28, 0.65);
            --glass-border: rgba(255, 255, 255, 0.06);
            --glass-border-hover: rgba(245, 158, 11, 0.5);
            --glass-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            --gold: #f59e0b;
            --gold-dim: #d97706;
            --ink: #fafafa;
            --ink-muted: rgba(250, 250, 250, 0.6);
            --ink-dim: rgba(250, 250, 250, 0.4);
        }}
        html.light {{
            --glass-bg: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(0, 0, 0, 0.05);
            --glass-border-hover: rgba(217, 119, 6, 0.4);
            --glass-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
            --ink: #0f172a;
            --ink-muted: rgba(15, 23, 42, 0.6);
            --ink-dim: rgba(15, 23, 42, 0.4);
        }}
        * {{ box-sizing: border-box; }}
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow-x: hidden; }}
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }}
        }}
        body {{
            background: #0a0a0f;
            color: var(--ink);
            font-family: 'Syne', sans-serif;
            font-variant-numeric: tabular-nums;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        html.light body {{ background: #fafafa; color: var(--ink); }}

        /* Noise texture overlay */
        body::before {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: 1;
            pointer-events: none;
            opacity: 0.03;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            animation: noise-shift 8s linear infinite;
        }}
        @keyframes noise-shift {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(256px, 256px); }}
        }}
        html.light body::before {{ opacity: 0.015; }}

        /* Gradient mesh background */
        .mesh-gradient {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(ellipse 60% 40% at 20% 10%, rgba(245, 158, 11, 0.08), transparent 70%),
                radial-gradient(ellipse 50% 50% at 80% 90%, rgba(99, 102, 241, 0.06), transparent 60%),
                radial-gradient(ellipse 40% 60% at 50% 50%, rgba(245, 158, 11, 0.03), transparent 80%);
            animation: mesh-drift 20s ease-in-out infinite alternate;
        }}
        @keyframes mesh-drift {{
            0% {{ background-position: 0% 0%, 100% 100%, 50% 50%; }}
            100% {{ background-position: 10% 10%, 90% 90%, 55% 55%; }}
        }}
        html.light .mesh-gradient {{
            background:
                radial-gradient(ellipse 60% 40% at 20% 10%, rgba(217, 119, 6, 0.05), transparent 70%),
                radial-gradient(ellipse 50% 50% at 80% 90%, rgba(79, 70, 229, 0.04), transparent 60%),
                radial-gradient(ellipse 40% 60% at 50% 50%, rgba(217, 119, 6, 0.02), transparent 80%);
        }}

        /* WebGL canvas layer */
        #webgl {{
            position: fixed;
            inset: 0;
            z-index: 2;
            pointer-events: none;
        }}

        /* Glassmorphism system */
        .glass {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            box-shadow: var(--glass-shadow);
            position: relative;
            overflow: hidden;
        }}
        .glass::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 50%, rgba(255,255,255,0.01) 100%);
            pointer-events: none;
        }}
        .glass:hover {{
            border-color: var(--glass-border-hover);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), 0 0 0 1px var(--glass-border-hover);
        }}
        html.light .glass:hover {{
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.12), 0 0 0 1px var(--glass-border-hover);
        }}
        .glass-elevated {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(32px);
            -webkit-backdrop-filter: blur(32px);
            box-shadow: 0 35px 70px -15px rgba(0, 0, 0, 0.85);
        }}
        html.light .glass-elevated {{ box-shadow: 0 35px 70px -15px rgba(0, 0, 0, 0.15); }}

        /* Buttons */
        .btn-glass {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--glass-border);
            color: var(--ink);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .btn-glass:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--glass-border-hover);
            transform: translateY(-1px);
        }}
        .btn-glass:active {{ transform: translateY(0) scale(0.98); }}
        html.light .btn-glass {{ background: rgba(0, 0, 0, 0.03); color: var(--ink); }}
        html.light .btn-glass:hover {{ background: rgba(0, 0, 0, 0.07); }}

        .btn-primary {{
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dim) 100%);
            border: none;
            color: #0a0a0f;
            font-weight: 600;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 30px -8px rgba(245, 158, 11, 0.45), inset 0 1px 0 rgba(255,255,255,0.2);
            position: relative;
            overflow: hidden;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 40px -10px rgba(245, 158, 11, 0.6), inset 0 1px 0 rgba(255,255,255,0.3);
            filter: brightness(1.05);
        }}
        .btn-primary:active {{ transform: translateY(0) scale(0.97); }}
        .btn-primary:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}

        .btn-magnetic {{
            will-change: transform;
        }}

        /* Ripple effect */
        .ripple {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-anim 0.5s ease-out forwards;
            pointer-events: none;
        }}
        @keyframes ripple-anim {{
            to {{ transform: scale(4); opacity: 0; }}
        }}

        /* Theme Toggle */
        .mode-toggle {{
            width: 60px; height: 30px;
            border-radius: 999px;
            border: 1px solid var(--glass-border);
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            flex-shrink: 0;
        }}
        .mode-toggle:focus-visible {{
            outline: 2px solid var(--gold);
            outline-offset: 3px;
        }}
        .mode-toggle .knob {{
            position: absolute; top: 2.5px; left: 2.5px;
            width: 25px; height: 25px;
            border-radius: 50%;
            background: linear-gradient(180deg, #fff 0%, #f0f0f0 100%);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.1);
            transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.3s;
            z-index: 2;
        }}
        html.light .mode-toggle .knob {{
            transform: translateX(30px);
            background: linear-gradient(180deg, var(--gold) 0%, var(--gold-dim) 100%);
            box-shadow: 0 2px 12px rgba(245, 158, 11, 0.5), 0 0 0 1px rgba(255,255,255,0.2);
        }}
        .mode-toggle .icon {{
            position: absolute; top: 50%; transform: translateY(-50%);
            width: 16px; height: 16px; opacity: 0.5;
            transition: opacity 0.3s, stroke 0.3s;
            pointer-events: none;
        }}
        .mode-toggle .sun {{ left: 10px; stroke: var(--gold); opacity: 0; }}
        html.light .mode-toggle .sun {{ opacity: 1; }}
        .mode-toggle .moon {{ right: 10px; stroke: var(--ink-muted); opacity: 1; }}
        html.light .mode-toggle .moon {{ opacity: 0; }}

        /* Table rows */
        .table-row {{
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .table-row:hover {{
            background: rgba(255, 255, 255, 0.02);
            transform: translateX(4px);
        }}
        html.light .table-row:hover {{ background: rgba(0, 0, 0, 0.02); }}
        .table-row:focus-visible {{
            outline: 2px solid var(--gold);
            outline-offset: -2px;
            background: rgba(245, 158, 11, 0.1);
        }}

        /* Animations */
        .fade-in {{
            animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .skeleton {{
            background: linear-gradient(90deg, var(--glass-border) 25%, rgba(255,255,255,0.05) 50%, var(--glass-border) 75%);
            background-size: 200% 100%;
            animation: skeleton-shimmer 1.5s ease-in-out infinite;
            border-radius: 4px;
        }}
        html.light .skeleton {{
            background: linear-gradient(90deg, rgba(0,0,0,0.04) 25%, rgba(0,0,0,0.01) 50%, rgba(0,0,0,0.04) 75%);
            background-size: 200% 100%;
        }}
        @keyframes skeleton-shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        .toast-enter {{ animation: toastEnter 0.4s cubic-bezier(0.16, 1, 0.3, 1); }}
        .toast-exit {{ animation: toastExit 0.3s cubic-bezier(0.4, 0, 1, 1) forwards; }}
        @keyframes toastEnter {{
            from {{ opacity: 0; transform: translateY(16px) scale(0.95); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
        @keyframes toastExit {{
            to {{ opacity: 0; transform: translateY(-8px) scale(0.95); }}
        }}
        .modal-overlay {{
            animation: modalOverlayIn 0.2s ease-out;
        }}
        .modal-content {{
            animation: modalContentIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        @keyframes modalOverlayIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes modalContentIn {{
            from {{ opacity: 0; transform: translateY(16px) scale(0.96); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}

        /* Focus ring */
        .focus-ring:focus-visible {{
            outline: 2px solid var(--gold);
            outline-offset: 2px;
        }}

        /* Scrollbars */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.12); border-radius: 4px; border: 2px solid transparent; background-clip: content-box; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.2); border: 2px solid transparent; background-clip: content-box; }}
        html.light ::-webkit-scrollbar-thumb {{ background: rgba(0,0,0,0.12); }}
        html.light ::-webkit-scrollbar-thumb:hover {{ background: rgba(0,0,0,0.2); }}

        /* Selection */
        ::selection {{ background: var(--gold); color: #0a0a0f; }}

        /* Skip link */
        .skip-link {{
            position: absolute; top: -100%; left: 1rem; z-index: 9999;
            padding: 0.75rem 1.25rem; background: var(--gold); color: #0a0a0f;
            font-weight: 600; border-radius: 0 0 8px 8px;
            transform: translateY(-100%);
            transition: top 0.2s, transform 0.2s;
        }}
        .skip-link:focus {{ top: 0; transform: translateY(0); }}

        /* Command palette */
        .cmd-palette {{
            position: fixed; top: 20%; left: 50%; transform: translateX(-50%) scale(0.95);
            width: min(720px, 90vw); z-index: 10000;
            opacity: 0; visibility: hidden; pointer-events: none;
            transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
        }}
        .cmd-palette.open {{ opacity: 1; visibility: visible; pointer-events: auto; transform: translateX(-50%) scale(1); }}

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {{
            .mesh-gradient {{ animation: none; }}
            body::before {{ animation: none; }}
            .skeleton {{ animation: none; }}
            .mode-toggle .knob {{ transition: transform 0.01ms; }}
        }}
    </style>
</head>
<body class="font-sans min-h-screen antialiased overflow-hidden">

    <!-- Skip link for accessibility -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Layers: mesh gradient -> noise -> WebGL -> UI -->
    <div class="mesh-gradient" aria-hidden="true"></div>
    <canvas id="webgl" class="fixed inset-0 z-10 pointer-events-none" aria-hidden="true"></canvas>

    <!-- Glassmorphism Header -->
    <header class="relative z-50 sticky top-0 border-b border-white/5 bg-white/5 backdrop-blur-2xl -webkit-backdrop-blur-2xl shadow-[0_1px_0_rgba(255,255,255,0.05)] px-4 sm:px-6 py-3">
        <div class="max-w-[1780px] mx-auto flex items-center justify-between gap-4">
            <!-- Brand + Theme Toggle -->
            <div class="flex items-center gap-3">
                <button onclick="toggleMode()" class="mode-toggle focus-ring" aria-label="Toggle dark/light mode" aria-pressed="false" role="switch">
                    <div class="knob" aria-hidden="true"></div>
                    <svg class="icon sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                    <svg class="icon moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79"/></svg>
                </button>
                <div class="ml-2">
                    <span class="text-xs font-bold tracking-tight text-white">DahNAY FreightFlow</span>
                    <span class="block text-[10px] font-mono text-gold tracking-wider uppercase">EXIM OPERATIONS PLATFORM</span>
                </div>
            </div>

            <!-- Live Telemetry -->
            <div class="hidden lg:flex items-center gap-3">
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-mono">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true"></span>
                    <span>Engine: <span class="text-white font-semibold">ISO 6346 / SOLAS</span></span>
                </div>
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-mono">
                    <span class="w-1.5 h-1.5 rounded-full bg-gold" aria-hidden="true"></span>
                    <span>CargoWise: <span class="text-white font-semibold">Universal XML</span></span>
                </div>
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-mono">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-400" aria-hidden="true"></span>
                    <span>Security: <span class="text-white font-semibold">Zero Retention</span></span>
                </div>
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-mono" id="fps-display">
                    <span class="w-1.5 h-1.5 rounded-full bg-purple-400" aria-hidden="true"></span>
                    <span>WebGL: <span class="text-white font-semibold" id="webgl-fps">60 FPS</span></span>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2">
                <button onclick="openCommandPalette()" class="btn-glass px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5" aria-label="Open command palette (⌘K)">
                    <i data-lucide="command" class="w-3.5 h-3.5"></i>
                    <span class="hidden sm:inline">Command</span>
                    <kbd class="hidden md:inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono bg-white/10 border border-white/10">⌘K</kbd>
                </button>
                <button onclick="runGuidedDemo()" class="btn-glass px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 hover:shadow-[0_0_30px_rgba(245,158,11,0.3)]" aria-label="Run guided 60-second demo">
                    <i data-lucide="play" class="w-3.5 h-3.5"></i>
                    <span class="hidden sm:inline">Run Demo</span>
                </button>
                <input type="file" id="upload-input" onchange="uploadFile(event)" class="hidden" accept=".xlsx,.xls,.pdf,.json,.txt" aria-label="Upload shipping instruction document">
                <button onclick="document.getElementById('upload-input').click()" class="btn-primary px-4 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg hover:scale-[1.02] active:scale-[0.98]" aria-label="Ingest shipping instruction document">
                    <i data-lucide="upload-cloud" class="w-3.5 h-3.5"></i>
                    <span class="hidden sm:inline">Ingest SI</span>
                </button>
                <div id="upload-status-text" class="hidden text-[10px] font-mono text-white/60 ml-2" aria-live="polite"></div>
            </div>
        </div>
    </header>

    <!-- Main Operational Workspace -->
    <main id="main-content" class="relative z-50 max-w-[1780px] mx-auto px-4 sm:px-6 py-8 space-y-8 overflow-y-auto h-[calc(100vh-140px)]">

        <!-- WebGL Stage Indicator -->
        <div class="glass rounded-xl p-4 fade-in" style="animation-delay: 0ms">
            <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-gold animate-pulse" aria-hidden="true"></div>
                    <span class="text-xs font-mono font-semibold text-white">WebGL Stage: Active</span>
                </div>
                <div class="text-right">
                    <span class="block text-[10px] font-mono text-white/40 uppercase tracking-wider">Live Container Fleet</span>
                    <span class="block text-xs font-mono text-gold" id="container-count">{len(containers)} Units</span>
                </div>
            </div>
        </div>

        <!-- 1. ACTIVE EXIM SHIPMENTS WORKLIST QUEUE -->
        <div class="glass-elevated rounded-xl p-5 fade-in" style="animation-delay: 40ms">
            <div class="flex items-center justify-between border-b border-white/5 pb-3 mb-4">
                <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded bg-gold/20 flex items-center justify-center text-gold">
                        <i data-lucide="list" class="w-4 h-4" aria-hidden="true"></i>
                    </div>
                    <div>
                        <h2 class="text-xs font-semibold tracking-tight text-white uppercase">Active EXIM Shipments Queue</h2>
                        <span class="text-[10px] font-mono text-white/50">({len(shipments)} Bookings Loaded)</span>
                    </div>
                </div>
                <span class="text-[10px] font-mono text-white/40">Click or press Enter to load dossier</span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left" role="grid" aria-label="Shipments queue">
                    <thead>
                        <tr class="text-[10px] uppercase font-bold text-white/40 border-b border-white/5">
                            <th class="pb-3 px-4 font-mono" scope="col">Booking Ref</th>
                            <th class="pb-3 px-4 font-mono" scope="col">Customer Account</th>
                            <th class="pb-3 px-4 font-mono" scope="col">Routing (POL → POD)</th>
                            <th class="pb-3 px-4 font-mono" scope="col">Carrier & Vessel</th>
                            <th class="pb-3 px-4 font-mono" scope="col">Lifecycle State</th>
                            <th class="pb-3 px-4 text-center font-mono" scope="col">Discrepancy Status</th>
                            <th class="pb-3 px-4 text-right font-mono" scope="col">Pre-Filled Invoice</th>
                        </tr>
                    </thead>
                    <tbody id="shipments-table-body" class="divide-y divide-white/5">
                        {shipments_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. DUAL-PANE OPERATIONAL WORKSPACE FOR SELECTED SHIPMENT -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

            <!-- LEFT PANE: AUTHENTIC SHIPPING INSTRUCTION DOCUMENT -->
            <div class="lg:col-span-5 space-y-4">
                <div class="glass-elevated rounded-xl p-5 fade-in" style="animation-delay: 80ms">
                    <div class="flex items-center justify-between border-b border-white/5 pb-3 mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded bg-blue-500/20 flex items-center justify-center text-blue-400">
                                <i data-lucide="file-text" class="w-4 h-4" aria-hidden="true"></i>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold tracking-tight text-white uppercase">Inbound Shipping Instruction</h3>
                                <span id="doc-filename" class="text-[10px] font-mono text-white/50">{document.get('original_filename', 'sample.xlsx')}</span>
                            </div>
                        </div>
                        <div class="w-1 h-6 bg-blue-500/30 rounded-full" aria-hidden="true"></div>
                    </div>

                    <!-- Authentic Maritime Manifest Sheet -->
                    <div class="glass p-5 rounded-xl border-white/5 text-xs space-y-4">
                        <div class="border-b border-white/5 pb-3 flex justify-between items-start">
                            <div>
                                <span class="text-[9px] font-mono text-white/50 uppercase block font-semibold tracking-wider">Maritime Export Shipping Instruction</span>
                                <div id="doc-shipper-name" class="text-sm font-semibold text-white">{document.get('shipper_name', 'Tirupur Garments Export Ltd')}</div>
                                <div id="doc-shipper-addr" class="text-[10px] text-white/60">{document.get('shipper_address', '')}</div>
                            </div>
                            <div class="text-right">
                                <span class="text-[9px] font-mono text-white/50 block uppercase font-semibold">Master Booking</span>
                                <span id="display-booking-ref" class="text-xs font-mono font-bold text-gold">{booking.get('booking_reference', 'BKG-MAA-992104')}</span>
                            </div>
                        </div>

                        <!-- Parties Grid -->
                        <div class="grid grid-cols-2 gap-3 text-[11px]">
                            <div class="p-3 rounded-lg bg-white/5 border border-white/5">
                                <span class="text-[9px] font-bold uppercase text-white/50 block font-mono tracking-wider">Shipper Compliance</span>
                                <div class="font-mono text-[10px] text-white/80 mt-1">
                                    IEC: <b id="doc-shipper-iec" class="text-white">{document.get('shipper_iec', '0401019283')}</b><br>
                                    GSTIN: <b id="doc-shipper-gstin" class="text-white">{document.get('shipper_gstin', '33AABCT9981E1Z4')}</b>
                                </div>
                            </div>
                            <div class="p-3 rounded-lg bg-white/5 border border-white/5">
                                <span class="text-[9px] font-bold uppercase text-white/50 block font-mono tracking-wider">Consignee Destination</span>
                                <div id="doc-consignee-name" class="font-bold text-white">{document.get('consignee_name', 'Gulf Retail Fashion LLC')}</div>
                                <div id="doc-consignee-addr" class="text-[10px] text-white/60">{document.get('consignee_address', '')}</div>
                                <div class="font-mono text-[10px] text-white/70 mt-0.5">TRN: <b id="doc-consignee-tax" class="text-white">{document.get('consignee_tax_id', 'TRN-100293819200003')}</b></div>
                            </div>
                        </div>

                        <!-- Routing Grid -->
                        <div class="grid grid-cols-3 gap-3 p-3 rounded-lg bg-white/5 border border-white/5 text-[10px]">
                            <div>
                                <span class="text-white/50 block uppercase font-mono text-[9px]">Vessel / Voyage</span>
                                <b id="doc-vessel" class="text-white">{document.get('vessel_name', 'MSC EMANUELA')} / {document.get('voyage_number', '2408W')}</b>
                            </div>
                            <div>
                                <span class="text-white/50 block uppercase font-mono text-[9px]">Port of Loading</span>
                                <b id="doc-pol" class="text-white">{document.get('port_of_loading', 'Chennai Port (INMAA)')}</b>
                            </div>
                            <div>
                                <span class="text-white/50 block uppercase font-mono text-[9px]">Port of Discharge</span>
                                <b id="doc-pod" class="text-white">{document.get('port_of_discharge', 'Jebel Ali Port (AEJEA)')}</b>
                            </div>
                        </div>

                        <!-- Cargo Particulars -->
                        <div class="grid grid-cols-2 gap-3 text-[10px]">
                            <div class="p-3 rounded-lg bg-white/5 border border-white/5">
                                <span class="text-white/50 block uppercase font-mono text-[9px]">Cargo Description</span>
                                <div id="doc-cargo-desc" class="font-medium text-white">{document.get('cargo_description', '100% Cotton Knitted Finished T-Shirts')}</div>
                                <div id="doc-packages" class="text-white/60 mt-1 font-mono">{document.get('total_packages', 920)} Cartons</div>
                            </div>
                            <div class="p-3 rounded-lg bg-white/5 border border-white/5">
                                <span class="text-white/50 block uppercase font-mono text-[9px]">Gross Weight & Slot Audit</span>
                                <div id="display-si-weight" class="text-sm font-bold text-white tabular-nums">{document.get('total_gross_weight_kg', 26800.0):,.1f} KGS</div>
                                <div class="text-[9px] text-white/60 mt-0.5 font-mono">Approved Slot: <b id="display-slot-weight" class="text-white">{booking.get('approved_weight_limit_kg', 24000.0):,.1f} KGS</b></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RIGHT PANE: DISCREPANCY GATE, CONTAINERS, INVOICE & CARGOWISE EDI -->
            <div class="lg:col-span-7 space-y-6">

                <!-- Header Dossier Summary -->
                <div class="glass rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 fade-in" style="animation-delay: 120ms">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-mono text-white/50">Job Reference:</span>
                            <span id="display-job-id" class="text-xs font-bold text-white font-mono">{booking.get('job_id', 'JOB-2026-CHN-048')}</span>
                            <span class="text-white/40" aria-hidden="true">•</span>
                            <span class="text-xs text-white/50">Carrier: <b id="display-carrier" class="text-white">{booking.get('carrier_line', 'MSC')}</b></span>
                        </div>
                        <div class="text-[10px] text-white/50 mt-1">
                            Account: <b id="display-customer" class="text-white">{booking.get('customer_account', 'Tirupur Garments Export Ltd')}</b> | Routing: <span id="display-routing" class="font-mono text-white/80">{booking.get('pol_code', 'INMAA')} → {booking.get('pod_code', 'AEJEA')}</span>
                        </div>
                    </div>
                    <div id="shipment-status-pill" class="{status_pill_cls}" role="status" aria-live="polite">
                        {status_pill_text}
                    </div>
                </div>

                <!-- 1. Discrepancy Exception Gate -->
                <div class="glass rounded-xl p-5 fade-in" style="animation-delay: 160ms">
                    <div class="flex items-center justify-between border-b border-white/5 pb-3 mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded bg-rose-500/20 flex items-center justify-center text-rose-400">
                                <i data-lucide="shield-alert" class="w-4 h-4" aria-hidden="true"></i>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold tracking-tight text-white uppercase">Discrepancy Exception Gate</h3>
                                <span class="text-[10px] font-mono text-white/50">Reconciles SI vs Carrier Booking</span>
                            </div>
                        </div>
                        <div class="w-1 h-6 bg-rose-500/30 rounded-full" aria-hidden="true"></div>
                    </div>

                    <div id="discrepancies-list" class="space-y-3" role="region" aria-label="Discrepancy exceptions" aria-live="polite">
                        {discrepancies_cards_html}
                    </div>
                </div>

                <!-- 2. Container Equipment & ISO 6346 Audit -->
                <div class="glass rounded-xl p-5 fade-in" style="animation-delay: 200ms">
                    <div class="flex items-center justify-between border-b border-white/5 pb-3 mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded bg-blue-500/20 flex items-center justify-center text-blue-400">
                                <i data-lucide="box" class="w-4 h-4" aria-hidden="true"></i>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold tracking-tight text-white uppercase">Container Equipment & ISO 6346 Audit</h3>
                                <span class="text-[10px] font-mono text-white/50">{len(containers)} Unit(s)</span>
                            </div>
                        </div>
                        <div class="w-1 h-6 bg-blue-500/30 rounded-full" aria-hidden="true"></div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left" role="grid" aria-label="Container audit">
                            <thead>
                                <tr class="text-[10px] uppercase font-bold text-white/40 border-b border-white/5">
                                    <th class="pb-3 px-3 font-mono" scope="col">Container #</th>
                                    <th class="pb-3 px-2 font-mono" scope="col">ISO Status</th>
                                    <th class="pb-3 px-3 font-mono" scope="col">Seal #</th>
                                    <th class="pb-3 px-2 font-mono" scope="col">Type</th>
                                    <th class="pb-3 px-3 text-right font-mono" scope="col">Gross Wt</th>
                                    <th class="pb-3 px-2 text-right font-mono" scope="col">Pkgs</th>
                                    <th class="pb-3 px-3 text-right font-mono" scope="col">CBM</th>
                                </tr>
                            </thead>
                            <tbody id="containers-table-body" class="divide-y divide-white/5">
                                {containers_rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 3. Pre-Filled Commercial Freight Invoice -->
                <div class="glass rounded-xl p-5 fade-in" style="animation-delay: 240ms">
                    <div class="flex items-center justify-between border-b border-white/5 pb-3 mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                                <i data-lucide="credit-card" class="w-4 h-4" aria-hidden="true"></i>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold tracking-tight text-white uppercase">Commercial Freight Invoice Pre-Fill</h3>
                                <span id="inv-number" class="text-[10px] font-mono text-white/50">{invoice.get('invoice_number', '')}</span>
                            </div>
                        </div>
                        <span class="text-xs font-mono text-emerald-400 px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">FX Rate: 1 USD = ₹86.50</span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left" role="grid" aria-label="Invoice line items">
                            <thead>
                                <tr class="text-[10px] uppercase font-bold text-white/40 border-b border-white/5">
                                    <th class="pb-3 px-3 font-mono" scope="col">Charge Description</th>
                                    <th class="pb-3 px-2 text-center font-mono" scope="col">Cur</th>
                                    <th class="pb-3 px-2 text-right font-mono" scope="col">Rate</th>
                                    <th class="pb-3 px-2 text-center font-mono" scope="col">Qty</th>
                                    <th class="pb-3 px-3 text-right font-mono" scope="col">Amount</th>
                                </tr>
                            </thead>
                            <tbody id="inv-items-tbody" class="divide-y divide-white/5">
                                {invoice_items_rows_html}
                            </tbody>
                        </table>
                    </div>

                    <!-- Tax Summary -->
                    <div class="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2 text-xs font-mono mt-4 fade-in" style="animation-delay: 280ms">
                        <div class="flex justify-between text-white/60">
                            <span>Billed To</span>
                            <span id="inv-billto" class="text-white">{invoice.get('bill_to_party', '')}</span>
                        </div>
                        <div class="flex justify-between text-white/60">
                            <span>Base Value (Excl. GST)</span>
                            <span id="inv-base" class="tabular-nums text-white">₹{invoice.get('total_inr_base', 0):,.2f}</span>
                        </div>
                        <div class="flex justify-between text-white/60">
                            <span>Central GST (CGST @ 9%)</span>
                            <span id="inv-cgst" class="tabular-nums text-white">₹{gst_half:,.2f}</span>
                        </div>
                        <div class="flex justify-between text-white/60">
                            <span>State GST (SGST @ 9%)</span>
                            <span id="inv-sgst" class="tabular-nums text-white">₹{gst_half:,.2f}</span>
                        </div>
                        <div class="flex justify-between pt-2 border-t border-white/5 text-sm font-bold text-white">
                            <span>Grand Total (INR)</span>
                            <span id="inv-grand" class="text-emerald-400 tabular-nums">₹{invoice.get('grand_total_inr', 0):,.2f}</span>
                        </div>
                    </div>
                </div>

                <!-- 4. CargoWise One UniversalShipment EDI Bridge -->
                <div class="glass rounded-xl p-5 fade-in" style="animation-delay: 320ms">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/5 pb-3 mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-8 h-8 rounded bg-purple-500/20 flex items-center justify-center text-purple-400">
                                <i data-lucide="database" class="w-4 h-4" aria-hidden="true"></i>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold tracking-tight text-white uppercase">CargoWise One UniversalShipment EDI Bridge</h3>
                                <p class="text-[10px] text-white/50">UniversalInterchange 1.1 XML Schema for ERP ingestion</p>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <button onclick="downloadXml()" class="btn-glass px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5" aria-label="Download CargoWise UniversalShipment XML">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> CargoWise XML
                            </button>
                            <button onclick="downloadDcsa()" class="btn-glass px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5" aria-label="Download DCSA eBL 3.0 JSON">
                                <i data-lucide="file-json" class="w-3.5 h-3.5"></i> DCSA eBL JSON
                            </button>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <button onclick="transmitCargoWise()" id="transmit-btn" class="btn-primary px-5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-xl" aria-label="Export validated UniversalShipment XML to CargoWise One">
                            <i data-lucide="send" class="w-3.5 h-3.5"></i> Export CargoWise XML
                        </button>
                        <span class="text-xs font-mono text-white/50">Format: UniversalShipment v1.1 XML</span>
                    </div>

                    <div id="edi-log-terminal" class="hidden mt-4 p-4 rounded-xl bg-black/50 border border-white/5 font-mono text-[11px] space-y-1.5 glass" role="log" aria-label="EDI transmission log" aria-live="polite">
                    </div>
                </div>

            </div>
        </div>
    </main>

    <!-- Toast Container -->
    <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none" aria-live="polite" aria-label="Notifications"></div>

    <!-- Command Palette -->
    <div id="cmd-palette" class="cmd-palette glass-elevated rounded-xl p-0 overflow-hidden" role="dialog" aria-label="Command palette" aria-modal="true">
        <div class="p-4 border-b border-white/5">
            <div class="flex items-center gap-3">
                <i data-lucide="command" class="w-5 h-5 text-gold" aria-hidden="true"></i>
                <input type="text" id="cmd-input" placeholder="Type a command..." class="flex-1 bg-transparent border-none outline-none text-white font-mono text-sm" aria-label="Command search" autocomplete="off" spellcheck="false">
                <kbd class="px-2 py-0.5 rounded text-[9px] font-mono bg-white/10 border border-white/10 text-white/50">Esc</kbd>
            </div>
        </div>
        <div id="cmd-results" class="max-h-96 overflow-y-auto"></div>
    </div>

    <!-- Custom Cursor -->
    <div id="custom-cursor" class="fixed inset-0 pointer-events-none z-40" aria-hidden="true">
        <div class="cursor-dot" style="position:absolute;width:8px;height:8px;border-radius:50%;background:var(--gold);mix-blend-mode:difference;transform:translate(-50%,-50%);transition:width 0.15s,height 0.15s,background 0.15s;pointer-events:none;"></div>
        <div class="cursor-ring" style="position:absolute;width:36px;height:36px;border-radius:50%;border:1px solid var(--gold);transform:translate(-50%,-50%);transition:width 0.3s,height 0.3s,border-color 0.3s;pointer-events:none;opacity:0.6;"></div>
    </div>

    <!-- Demo Guide Toast (legacy compatibility) -->
    <div id="demo-guide-toast" class="hidden fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl glass text-xs font-mono shadow-2xl text-white"></div>

    <script>
        // ============================================================================
        // DAHNAY FREIGHTFLOW — INDUSTRIAL LUXURY UI
        // Vanilla JS, no framework dependencies, ~2000 lines
        // ============================================================================

        // ---- GLOBAL STATE ----
        let currentBookingRef = '{{active_booking_ref}}';
        let threeScene = null;
        let animationId = null;
        let customCursor = {{ dot: null, ring: null, mouseX: 0, mouseY: 0, dotX: 0, dotY: 0, ringX: 0, ringY: 0 }};
        let reducedMotion = false;
        let toasts = [];

        // ---- INITIALIZATION ----
        document.addEventListener('DOMContentLoaded', async () => {{
            initTheme();
            initCustomCursor();
            initCommandPalette();
            initReducedMotion();
            await initThreeJS();
            lucide.createIcons();
            // Load initial shipment
            await loadShipment(currentBookingRef);
            // Start staggered entrance
            document.querySelectorAll('.fade-in').forEach((el, i) => {{
                el.style.animationDelay = '{{(i * 40)}}ms';
            }});
        }});

        // Cleanup on unload
        window.addEventListener('beforeunload', cleanupThreeJS);

        // ---- THEME SYSTEM ----
        function initTheme() {{
            const saved = localStorage.getItem('theme');
            const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
            if (saved === 'light' || (!saved && prefersLight)) {{
                document.documentElement.classList.add('light');
            }}
            updateModeUI();
        }}

        function toggleMode() {{
            const html = document.documentElement;
            const isLight = html.classList.toggle('light');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            updateModeUI();
            // Announce to screen readers
            announceToScreenReader(isLight ? 'Light mode activated' : 'Dark mode activated');
        }}

        function updateModeUI() {{
            const isLight = document.documentElement.classList.contains('light');
            const toggle = document.querySelector('.mode-toggle');
            if (toggle) {{
                toggle.setAttribute('aria-pressed', isLight);
                toggle.querySelectorAll('.icon').forEach(el => {{
                    el.style.opacity = isLight ? (el.classList.contains('sun') ? '1' : '0') : (el.classList.contains('sun') ? '0' : '1');
                }});
            }}
        }}

        // ---- CUSTOM CURSOR ----
        function initCustomCursor() {{
            if (reducedMotion || window.matchMedia('(pointer: coarse)').matches) return;
            customCursor.dot = document.querySelector('.cursor-dot');
            customCursor.ring = document.querySelector('.cursor-ring');
            document.addEventListener('mousemove', e => {{
                customCursor.mouseX = e.clientX;
                customCursor.mouseY = e.clientY;
            }});
            // Magnetic elements
            document.addEventListener('mouseover', e => {{
                const magnetic = e.target.closest('.btn-magnetic, .table-row[tabindex="0'], .mode-toggle');
                if (magnetic) {{
                    customCursor.dot.style.width = '16px';
                    customCursor.dot.style.height = '16px';
                    customCursor.dot.style.background = 'var(--gold)';
                    customCursor.ring.style.width = '60px';
                    customCursor.ring.style.height = '60px';
                    customCursor.ring.style.borderColor = 'var(--gold)';
                    customCursor.ring.style.opacity = '0.8';
                }}
            }});
            document.addEventListener('mouseout', e => {{
                const magnetic = e.target.closest('.btn-magnetic, .table-row[tabindex="0'], .mode-toggle');
                if (magnetic) {{
                    customCursor.dot.style.width = '8px';
                    customCursor.dot.style.height = '8px';
                    customCursor.dot.style.background = 'var(--gold)';
                    customCursor.ring.style.width = '36px';
                    customCursor.ring.style.height = '36px';
                    customCursor.ring.style.borderColor = 'var(--gold)';
                    customCursor.ring.style.opacity = '0.6';
                }}
            }});
            animateCursor();
        }}

        function animateCursor() {{
            if (!customCursor.dot) return;
            // Smooth follow with easing
            customCursor.dotX += (customCursor.mouseX - customCursor.dotX) * 0.3;
            customCursor.dotY += (customCursor.mouseY - customCursor.dotY) * 0.3;
            customCursor.ringX += (customCursor.mouseX - customCursor.ringX) * 0.15;
            customCursor.ringY += (customCursor.mouseY - customCursor.ringY) * 0.15;
            customCursor.dot.style.transform = `translate(${{customCursor.dotX - 4}}px, ${{customCursor.dotY - 4}}px)`;
            customCursor.ring.style.transform = `translate(${{customCursor.ringX - 18}}px, ${{customCursor.ringY - 18}}px)`;
            requestAnimationFrame(animateCursor);
        }}

        // ---- COMMAND PALETTE ----
        const COMMANDS = [
            {{ id: 'demo', label: 'Run Guided Demo', keys: '⌘D', action: () => runGuidedDemo(), icon: 'play' }},
            {{ id: 'ingest', label: 'Ingest Shipping Instruction', keys: '⌘I', action: () => document.getElementById('upload-input').click(), icon: 'upload-cloud' }},
            {{ id: 'transmit', label: 'Export CargoWise XML', keys: '⌘E', action: () => transmitCargoWise(), icon: 'send' }},
            {{ id: 'download-xml', label: 'Download CargoWise XML', keys: '⌘X', action: () => downloadXml(), icon: 'download' }},
            {{ id: 'download-dcsa', label: 'Download DCSA eBL JSON', keys: '⌘J', action: () => downloadDcsa(), icon: 'file-json' }},
            {{ id: 'toggle-theme', label: 'Toggle Dark/Light Mode', keys: '⌘L', action: () => toggleMode(), icon: 'sun' }},
            {{ id: 'refresh', label: 'Refresh Shipments', keys: '⌘R', action: () => refreshShipmentsTable(), icon: 'refresh-cw' }},
        ];

        function initCommandPalette() {{
            const palette = document.getElementById('cmd-palette');
            const input = document.getElementById('cmd-input');
            const results = document.getElementById('cmd-results');

            function renderResults(filter = '') {{
                const filtered = COMMANDS.filter(c =>
                    c.label.toLowerCase().includes(filter.toLowerCase()) ||
                    c.keys.toLowerCase().includes(filter.toLowerCase())
                );
                results.innerHTML = filtered.map(c => `
                    <button onclick="executeCommand('${{c.id}}'); closeCommandPalette()" class="cmd-item w-full px-4 py-3 text-left flex items-center gap-3 hover:bg-white/5 transition-colors focus-ring focus-visible:outline-none" role="option">
                        <i data-lucide="${{c.icon}}" class="w-5 h-5 text-white/60"></i>
                        <span class="flex-1 text-white font-medium">${{c.label}}</span>
                        <kbd class="px-2 py-0.5 rounded text-[9px] font-mono bg-white/10 border border-white/10 text-white/50">${{c.keys}}</kbd>
                    </button>
                `).join('');
                lucide.createIcons();
            }}

            window.openCommandPalette = () => {{
                palette.classList.add('open');
                input.value = '';
                renderResults();
                input.focus();
            }};
            window.closeCommandPalette = () => {{
                palette.classList.remove('open');
                input.blur();
            }};
            window.executeCommand = (id) => {{
                const cmd = COMMANDS.find(c => c.id === id);
                if (cmd) cmd.action();
            }};

            input.addEventListener('input', e => renderResults(e.target.value));
            input.addEventListener('keydown', e => {{
                if (e.key === 'Escape') closeCommandPalette();
                if (e.key === 'ArrowDown') {{ e.preventDefault(); results.querySelector('button')?.focus(); }}
            }});
            document.addEventListener('keydown', e => {{
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{ e.preventDefault(); openCommandPalette(); }}
                if (e.key === 'Escape' && palette.classList.contains('open')) closeCommandPalette();
            }});
            // Click outside to close
            palette.addEventListener('click', e => {{ if (e.target === palette) closeCommandPalette(); }});
        }}

        // ---- REDUCED MOTION ----
        function initReducedMotion() {{
            reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (reducedMotion) document.documentElement.classList.add('reduce-motion');
            window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', e => {{
                reducedMotion = e.matches;
                document.documentElement.classList.toggle('reduce-motion', reducedMotion);
            }});
        }}

        // ---- THREE.JS WEBGL SCENE ----
        async function initThreeJS() {{
            if (typeof THREE === 'undefined') {{
                console.warn('Three.js not loaded');
                document.getElementById('webgl').style.display = 'none';
                return;
            }}

            // Scene
            threeScene = {{
                scene: new THREE.Scene(),
                camera: null,
                renderer: null,
                composer: null,
                containers: null,
                containerEdges: null,
                particles: null,
                spotlight: null,
                spotlightTarget: null,
                ground: null,
                containerData: [],
                clock: new THREE.Clock(),
            }};

            const canvas = document.getElementById('webgl');
            const width = window.innerWidth;
            const height = window.innerHeight;

            // Camera
            threeScene.camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 300);
            threeScene.camera.position.set(0, 8, 22);

            // Renderer
            threeScene.renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' }});
            threeScene.renderer.setSize(width, height);
            threeScene.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            threeScene.renderer.toneMapping = THREE.ACESFilmicToneMapping;
            threeScene.renderer.toneMappingExposure = 1.1;
            threeScene.renderer.shadowMap.enabled = true;
            threeScene.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            // Post-processing composer
            threeScene.composer = new THREE.EffectComposer(threeScene.renderer);
            threeScene.composer.addPass(new THREE.RenderPass(threeScene.scene, threeScene.camera));

            // Unreal Bloom Pass for premium glow
            const bloomPass = new THREE.UnrealBloomPass(
                new THREE.Vector2(width, height),
                0.4,  // strength
                0.3,  // radius
                0.85  // threshold
            );
            threeScene.composer.addPass(bloomPass);

            // Fog
            threeScene.scene.fog = new THREE.FogExp2(0x0a0a0f, 0.0008);

            // Lights
            const ambient = new THREE.AmbientLight(0xffffff, 0.35);
            threeScene.scene.add(ambient);

            const dir1 = new THREE.DirectionalLight(0xf59e0b, 0.7);
            dir1.position.set(20, 40, 20);
            dir1.castShadow = true;
            dir1.shadow.mapSize.width = 2048;
            dir1.shadow.mapSize.height = 2048;
            dir1.shadow.camera.near = 1;
            dir1.shadow.camera.far = 100;
            dir1.shadow.camera.left = -30;
            dir1.shadow.camera.right = 30;
            dir1.shadow.camera.top = 30;
            dir1.shadow.camera.bottom = -30;
            dir1.shadow.bias = -0.0005;
            threeScene.scene.add(dir1);

            const dir2 = new THREE.DirectionalLight(0x6366f1, 0.4);
            dir2.position.set(-20, 30, -20);
            threeScene.scene.add(dir2);

            const hemi = new THREE.HemisphereLight(0xfef3c7, 0x0a0a0f, 0.25);
            threeScene.scene.add(hemi);

            // Spotlight following mouse
            threeScene.spotlight = new THREE.SpotLight(0xf59e0b, 0.5);
            threeScene.spotlight.angle = Math.PI / 3.5;
            threeScene.spotlight.penumbra = 0.4;
            threeScene.spotlight.decay = 1.5;
            threeScene.spotlight.distance = 120;
            threeScene.spotlight.position.set(0, 50, 0);
            threeScene.spotlight.castShadow = true;
            threeScene.spotlight.shadow.mapSize.width = 1024;
            threeScene.spotlight.shadow.mapSize.height = 1024;

            threeScene.spotlightTarget = new THREE.Object3D();
            threeScene.spotlightTarget.position.set(0, 0, 0);
            threeScene.scene.add(threeScene.spotlight);
            threeScene.scene.add(threeScene.spotlight.target);

            // ---- CONTAINERS (Instanced) ----
            const containerGeo = new THREE.BoxGeometry(2.4, 2.6, 6);
            // Beveled edges for premium look
            const containerMat = new THREE.MeshStandardMaterial({{
                color: 0x111827,
                metalness: 0.25,
                roughness: 0.65,
                transparent: true,
                opacity: 0.85,
            }});

            const edgeGeo = new THREE.EdgesGeometry(containerGeo);
            const edgeMat = new THREE.LineBasicMaterial({{ color: 0xf59e0b, transparent: true, opacity: 0.35 }});

            const containerCount = 50;
            threeScene.containers = new THREE.InstancedMesh(containerGeo, containerMat, containerCount);
            threeScene.containers.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
            threeScene.containers.castShadow = true;
            threeScene.containers.receiveShadow = true;
            threeScene.scene.add(threeScene.containers);

            threeScene.containerEdges = new THREE.InstancedMesh(edgeGeo, edgeMat, containerCount);
            threeScene.containerEdges.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
            threeScene.scene.add(threeScene.containerEdges);

            const dummy = new THREE.Object3D();
            // Position containers in a spiral formation
            for (let i = 0; i < containerCount; i++) {{
                const angle = (i / containerCount) * Math.PI * 2 * 2.5;
                const radius = 10 + (i / containerCount) * 20;
                const x = Math.cos(angle) * radius;
                const z = Math.sin(angle) * radius;
                const y = (Math.random() - 0.5) * 3;
                const rotY = angle + Math.PI / 2 + (Math.random() - 0.5) * 0.3;

                dummy.position.set(x, y, z);
                dummy.rotation.y = rotY;
                dummy.scale.setScalar(0.7 + Math.random() * 0.5);
                dummy.updateMatrix();
                threeScene.containers.setMatrixAt(i, dummy.matrix);
                threeScene.containerEdges.setMatrixAt(i, dummy.matrix);

                threeScene.containerData[i] = {{
                    baseY: y,
                    baseX: x,
                    baseZ: z,
                    baseRotY: rotY,
                    speed: 0.0003 + Math.random() * 0.0008,
                    phase: Math.random() * Math.PI * 2,
                    rotSpeed: (Math.random() - 0.5) * 0.0002,
                    floatAmp: 0.08 + Math.random() * 0.12,
                }};
            }}
            threeScene.containers.instanceMatrix.needsUpdate = true;
            threeScene.containerEdges.instanceMatrix.needsUpdate = true;

            // ---- PARTICLE FIELD ----
            const particleCount = 5000;
            const particleGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const sizes = new Float32Array(particleCount);
            const alphas = new Float32Array(particleCount);
            const colors = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount; i++) {{
                const r = 5 + Math.random() * 55;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                positions[i * 3 + 1] = (Math.random() - 0.5) * 25;
                positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
                sizes[i] = Math.random() * 2 + 0.5;
                alphas[i] = Math.random() * 0.6 + 0.15;
                // Gold to white gradient
                const t = Math.random();
                colors[i * 3] = 1.0;     // R
                colors[i * 3 + 1] = 0.62 + t * 0.38; // G
                colors[i * 3 + 2] = t * 0.2;         // B
            }}

            particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            particleGeo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
            particleGeo.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));
            particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const particleMat = new THREE.PointsMaterial({{
                size: 1,
                transparent: true,
                opacity: 0.5,
                sizeAttenuation: true,
                vertexColors: true,
                depthWrite: false,
            }});

            threeScene.particles = new THREE.Points(particleGeo, particleMat);
            threeScene.scene.add(threeScene.particles);

            // ---- GROUND PLANE ----
            const groundGeo = new THREE.PlaneGeometry(400, 400, 50, 50);
            const groundMat = new THREE.MeshStandardMaterial({{
                color: 0x0a0a0f,
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide,
                metalness: 0,
                roughness: 1,
            }});
            threeScene.ground = new THREE.Mesh(groundGeo, groundMat);
            threeScene.ground.rotation.x = -Math.PI / 2;
            threeScene.ground.position.y = -6;
            threeScene.ground.receiveShadow = true;
            threeScene.scene.add(threeScene.ground);

            // Event listeners
            window.addEventListener('resize', onResize);
            document.addEventListener('mousemove', onMouseMove);

            // Start animation
            animateThreeJS();
        }}

        function onResize() {{
            if (!threeScene || !threeScene.camera || !threeScene.renderer) return;
            const width = window.innerWidth;
            const height = window.innerHeight;
            threeScene.camera.aspect = width / height;
            threeScene.camera.updateProjectionMatrix();
            threeScene.renderer.setSize(width, height);
            threeScene.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            if (threeScene.composer) threeScene.composer.setSize(width, height);
        }}

        function onMouseMove(e) {{
            if (!threeScene) return;
            // Normalized device coordinates for spotlight
            threeScene.mouseNDC = {{
                x: (e.clientX / window.innerWidth) * 2 - 1,
                y: -(e.clientY / window.innerHeight) * 2 + 1
            }};
        }}

        function animateThreeJS() {{
            if (!threeScene) return;
            animationId = requestAnimationFrame(animateThreeJS);

            const delta = threeScene.clock.getDelta();
            const elapsed = threeScene.clock.getElapsedTime();

            // Animate containers
            if (threeScene.containers && threeScene.containerData.length) {{
                const dummy = new THREE.Object3D();
                for (let i = 0; i < threeScene.containers.count; i++) {{
                    const cd = threeScene.containerData[i];
                    threeScene.containers.getMatrixAt(i, dummy.matrix);
                    dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale);

                    // Gentle floating
                    dummy.position.y = cd.baseY + Math.sin(elapsed * cd.speed * 1000 + cd.phase) * cd.floatAmp;
                    // Subtle rotation
                    dummy.rotation.y = cd.baseRotY + elapsed * cd.rotSpeed;
                    // Subtle orbital drift
                    dummy.position.x = cd.baseX + Math.sin(elapsed * 0.1 + cd.phase) * 0.3;
                    dummy.position.z = cd.baseZ + Math.cos(elapsed * 0.1 + cd.phase) * 0.3;

                    dummy.updateMatrix();
                    threeScene.containers.setMatrixAt(i, dummy.matrix);
                    threeScene.containerEdges.setMatrixAt(i, dummy.matrix);
                }}
                threeScene.containers.instanceMatrix.needsUpdate = true;
                threeScene.containerEdges.instanceMatrix.needsUpdate = true;
            }}

            // Animate particles
            if (threeScene.particles) {{
                threeScene.particles.rotation.y += 0.00003;
                threeScene.particles.rotation.x += 0.00001;
                const positions = threeScene.particles.geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {{
                    positions[i + 1] += Math.sin(elapsed * 0.5 + i * 0.01) * 0.0008;
                }}
                threeScene.particles.geometry.attributes.position.needsUpdate = true;
            }}

            // Spotlight follows mouse with smooth lerp
            if (threeScene.spotlight && threeScene.spotlightTarget && threeScene.mouseNDC) {{
                const targetX = threeScene.mouseNDC.x * 25;
                const targetZ = threeScene.mouseNDC.y * 25;
                threeScene.spotlightTarget.position.x += (targetX - threeScene.spotlightTarget.position.x) * 0.04;
                threeScene.spotlightTarget.position.z += (targetZ - threeScene.spotlightTarget.position.z) * 0.04;
                threeScene.spotlight.position.x += (targetX - threeScene.spotlight.position.x) * 0.02;
                threeScene.spotlight.position.z += (targetZ - threeScene.spotlight.position.z) * 0.02;
            }}

            // FPS counter
            const fps = Math.round(1 / delta);
            const fpsEl = document.getElementById('webgl-fps');
            if (fpsEl) fpsEl.textContent = fps + ' FPS';

            // Render via composer (with bloom)
            if (threeScene.composer) {{
                threeScene.composer.render();
            }} else if (threeScene.renderer && threeScene.scene && threeScene.camera) {{
                threeScene.renderer.render(threeScene.scene, threeScene.camera);
            }}
        }}

        function cleanupThreeJS() {{
            if (animationId) {{
                cancelAnimationFrame(animationId);
                animationId = null;
            }}
            if (threeScene) {{
                window.removeEventListener('resize', onResize);
                document.removeEventListener('mousemove', onMouseMove);

                // Dispose geometries
                if (threeScene.containers) {{
                    threeScene.containers.geometry?.dispose();
                    threeScene.containers.material?.dispose();
                }}
                if (threeScene.containerEdges) {{
                    threeScene.containerEdges.geometry?.dispose();
                    threeScene.containerEdges.material?.dispose();
                }}
                if (threeScene.particles) {{
                    threeScene.particles.geometry?.dispose();
                    threeScene.particles.material?.dispose();
                }}
                if (threeScene.ground) {{
                    threeScene.ground.geometry?.dispose();
                    threeScene.ground.material?.dispose();
                }}

                // Dispose lights (they don't have dispose but remove from scene)
                threeScene.scene?.remove(threeScene.spotlight);
                threeScene.scene?.remove(threeScene.spotlightTarget);

                // Dispose renderer
                threeScene.renderer?.dispose();
                threeScene.composer?.dispose();

                threeScene = null;
            }}
        }}

        // ---- ACCESSIBILITY HELPERS ----
        function announceToScreenReader(message) {{
            const live = document.createElement('div');
            live.setAttribute('role', 'status');
            live.setAttribute('aria-live', 'polite');
            live.setAttribute('aria-atomic', 'true');
            live.className = 'sr-only';
            live.textContent = message;
            document.body.appendChild(live);
            setTimeout(() => live.remove(), 1000);
        }}

        function setText(id, text) {{
            const el = document.getElementById(id);
            if (el) el.textContent = (text !== undefined && text !== null) ? text : '';
        }}

        // ---- SHIPMENT LOADING & RENDERING ----
        async function loadShipment(bookingRef) {{
            currentBookingRef = bookingRef;
            // Show skeleton loaders
            showSkeletonLoaders(true);
            try {{
                const res = await fetch('/api/v1/shipments/' + bookingRef);
                const json = await res.json();
                if (json.status === 'success') {{
                    renderShipmentView(json.data);
                }}
            }} catch (err) {{
                console.warn('Error loading shipment:', err);
                showToast('Failed to load shipment', 'error');
            }} finally {{
                showSkeletonLoaders(false);
            }}
        }}

        function showSkeletonLoaders(show) {{
            const ids = ['display-booking-ref', 'display-job-id', 'display-customer', 'display-carrier',
                         'display-routing', 'display-vessel', 'display-slot-weight',
                         'display-si-weight', 'doc-shipper-name', 'doc-shipper-addr',
                         'doc-shipper-iec', 'doc-shipper-gstin', 'doc-consignee-name',
                         'doc-consignee-addr', 'doc-consignee-tax', 'doc-cargo-desc',
                         'doc-packages', 'doc-vessel', 'doc-pol', 'doc-pod',
                         'inv-number', 'inv-billto', 'inv-base', 'inv-cgst',
                         'inv-sgst', 'inv-grand'];
            ids.forEach(id => {{
                const el = document.getElementById(id);
                if (el) {{
                    if (show) {{
                        el.dataset.originalContent = el.textContent;
                        el.classList.add('skeleton');
                        el.style.minWidth = '80px';
                        el.style.height = '1em';
                        el.textContent = '';
                    }} else {{
                        el.classList.remove('skeleton');
                        el.style.minWidth = '';
                        el.style.height = '';
                        if (el.dataset.originalContent) el.textContent = el.dataset.originalContent;
                    }}
                }}
            }});
            // Table skeletons
            ['discrepancies-list', 'containers-table-body', 'inv-items-tbody'].forEach(tbodyId => {{
                const tbody = document.getElementById(tbodyId);
                if (tbody && show) {{
                    tbody.innerHTML = Array(4).fill('<tr><td colspan="7" class="py-3"><div class="skeleton h-4 w-3/4"></div></tr>').join('');
                }}
            }});
        }}

        function renderShipmentView(data) {{
            const doc = data.document;
            const bkg = data.booking;
            const inv = data.invoice;
            const flags = data.discrepancies || [];
            const cntrs = data.containers || [];

            setText('display-booking-ref', bkg.booking_reference);
            setText('display-job-id', bkg.job_id);
            setText('display-customer', bkg.customer_account);
            setText('display-carrier', bkg.carrier_line);
            setText('display-routing', bkg.pol_code + ' → ' + bkg.pod_code);
            setText('display-vessel', bkg.vessel_scheduled + ' (' + bkg.voyage_scheduled + ')');
            setText('display-slot-weight', Number(bkg.approved_weight_limit_kg).toLocaleString() + ' KGS');

            if (doc) {{
                setText('display-si-weight', Number(doc.total_gross_weight_kg).toLocaleString() + ' KGS');
                setText('doc-shipper-name', doc.shipper_name);
                setText('doc-shipper-addr', doc.shipper_address || '');
                setText('doc-shipper-iec', doc.shipper_iec || 'N/A');
                setText('doc-shipper-gstin', doc.shipper_gstin || 'N/A');
                setText('doc-consignee-name', doc.consignee_name);
                setText('doc-consignee-addr', doc.consignee_address || '');
                setText('doc-consignee-tax', doc.consignee_tax_id || 'N/A');
                setText('doc-cargo-desc', doc.cargo_description || '');
                setText('doc-packages', (doc.total_packages || 0) + ' ' + (doc.package_type || 'Cartons'));
                setText('doc-vessel', doc.vessel_name + ' / ' + doc.voyage_number);
                setText('doc-pol', doc.port_of_loading);
                setText('doc-pod', doc.port_of_discharge);
                setText('doc-filename', doc.original_filename);

                const statusEl = document.getElementById('shipment-status-pill');
                if (statusEl) {{
                    if (doc.lifecycle_state === 'CARGOWISE_SYNCED') {{
                        statusEl.className = 'px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30 flex items-center gap-2 backdrop-blur-sm';
                        statusEl.innerHTML = '<span class="w-2 h-2 rounded-full bg-blue-400" aria-hidden="true"></span> CARGOWISE_SYNCED';
                    }} else if (flags.some(f => f.is_resolved === 0)) {{
                        statusEl.className = 'px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-2 backdrop-blur-sm';
                        statusEl.innerHTML = '<span class="w-2 h-2 rounded-full bg-rose-400 animate-pulse" aria-hidden="true"></span> EXCEPTION_HOLD';
                    }} else {{
                        statusEl.className = 'px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-2 backdrop-blur-sm';
                        statusEl.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400" aria-hidden="true"></span> APPROVED_FOR_EDI';
                    }}
                }}
            }}

            renderFlagsList(flags);
            renderContainersList(cntrs);
            if (inv) renderInvoice(inv);
            lucide.createIcons();
            announceToScreenReader(`Loaded shipment ${{bkg.booking_reference}}`);
        }}

        function renderFlagsList(flags) {{
            const container = document.getElementById('discrepancies-list');
            if (!flags || flags.length === 0) {{
                container.innerHTML = `
                    <div class="p-6 rounded-xl glass border-emerald-500/20 text-center space-y-2" role="status">
                        <div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto text-base font-bold" aria-hidden="true">✓</div>
                        <div class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Zero Documentation Exceptions</div>
                        <p class="text-[11px] text-white/50">ISO 6346 checksums valid. Declared gross weight matches carrier slot limit and IMO SOLAS VGM tolerance.</p>
                    </div>
                `;
                return;
            }}

            let html = '';
            flags.forEach((f, i) => {{
                const isResolved = (f.is_resolved === 1);
                const sev = f.severity || 'WARNING';
                const fn = f.field_name.toUpperCase();

                let actionBtn = '';
                if (!isResolved) {{
                    if (fn.includes('CONTAINER')) {{
                        actionBtn = `<button onclick="resolveFlag('${{f.id}}', 'AUTO_FIX')" class="btn-magnetic btn-primary px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-lg" aria-label="Auto-correct container check-digit for ${{f.field_name.replace(/_/g, ' ')}}">
                            <i data-lucide="check" class="w-3.5 h-3.5"></i> Auto-Correct Check-Digit
                            <span class="ripple" aria-hidden="true"></span>
                        </button>`;
                    }} else if (fn.includes('WEIGHT')) {{
                        actionBtn = `<button onclick="resolveFlag('${{f.id}}', 'MANAGER_WAIVER')" class="btn-magnetic btn-primary px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-lg" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);" aria-label="Record shipper weight waiver for ${{f.field_name.replace(/_/g, ' ')}}">
                            <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> Record Shipper Weight Waiver
                            <span class="ripple" aria-hidden="true"></span>
                        </button>`;
                    }} else {{
                        actionBtn = `<button onclick="resolveFlag('${{f.id}}', 'MANUAL_EDIT')" class="btn-magnetic btn-glass px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5" aria-label="Mark ${{f.field_name.replace(/_/g, ' ')}} as checked">
                            <i data-lucide="edit-2" class="w-3.5 h-3.5"></i> Mark Checked
                            <span class="ripple" aria-hidden="true"></span>
                        </button>`;
                    }}
                }}

                if (isResolved) {{
                    html += `
                    <div class="p-4 rounded-xl glass border-emerald-500/20 opacity-60 text-xs space-y-2 fade-in" style="animation-delay: ${{i * 30}}ms" role="status" aria-live="polite">
                        <div class="flex items-center justify-between">
                            <span class="font-mono text-emerald-400 font-semibold flex items-center gap-1.5">
                                <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400" aria-hidden="true"></i> ${{f.field_name.replace(/_/g, ' ')}}
                            </span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">RESOLVED</span>
                        </div>
                        <p class="text-white/60">${{f.issue_description}}</p>
                    </div>`;
                }} else {{
                    const borderCol = (sev === 'CRITICAL') ? 'border-rose-500/40 bg-rose-500/5' : 'border-amber-500/40 bg-amber-500/5';
                    const textCol = (sev === 'CRITICAL') ? 'text-rose-400' : 'text-amber-400';
                    const badgeCol = (sev === 'CRITICAL') ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' : 'bg-amber-500/10 text-amber-300 border-amber-500/30';
                    const pulse = (sev === 'CRITICAL') ? 'animate-pulse' : '';

                    html += `
                    <div class="p-4 rounded-xl border ${{borderCol}} text-xs space-y-3 fade-in" style="animation-delay: ${{i * 30}}ms" role="alert" aria-live="assertive">
                        <div class="flex items-center justify-between">
                            <span class="font-mono font-bold ${{textCol}} flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full ${{sev === 'CRITICAL' ? 'bg-rose-400' : 'bg-amber-400'}} ${{pulse}}" aria-hidden="true"></span>
                                [${{sev}}] ${{f.field_name.replace(/_/g, ' ')}}
                            </span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${{badgeCol}} border">
                                ACTION REQUIRED
                            </span>
                        </div>
                        <p class="text-white font-medium leading-relaxed">${{f.issue_description}}</p>
                        <div class="p-3 rounded bg-black/30 border border-white/5 text-[11px] text-white/60 space-y-1 glass">
                            <div class="text-white/40 uppercase text-[9px] font-mono font-semibold">Standard Operating Procedure</div>
                            <div>${{f.remedy_suggestion}}</div>
                        </div>
                        <div class="pt-1">${{actionBtn}}</div>
                    </div>`;
                }}
            }});
            container.innerHTML = html;
            lucide.createIcons();
        }}

        function renderContainersList(cntrs) {{
            const tbody = document.getElementById('containers-table-body');
            let html = '';
            cntrs.forEach(c => {{
                const isValid = (c.is_checksum_valid === 1);
                const badge = isValid
                    ? '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">ISO Valid</span>'
                    : `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">Typo (Exp: ${{c.expected_check_digit}})</span>`;
                html += `
                <tr class="table-row border-b border-white/5 text-xs hover:bg-white/5 transition-colors cursor-pointer">
                    <td class="py-3 px-3 font-mono font-bold text-blue-400">${{c.container_number}}</td>
                    <td class="py-3 px-2">${{badge}}</td>
                    <td class="py-3 px-3 font-mono text-white/70">${{c.seal_number}}</td>
                    <td class="py-3 px-2 text-white/70">${{c.container_type}}</td>
                    <td class="py-3 px-3 font-mono text-right text-white tabular-nums">${{Number(c.gross_weight_kg).toLocaleString()}} KGS</td>
                    <td class="py-3 px-2 font-mono text-right text-white/70 tabular-nums">${{c.packages_count}} pkgs</td>
                    <td class="py-3 px-3 font-mono text-right text-white/70 tabular-nums">${{Number(c.cbm).toFixed(2)}}</td>
                </tr>
                `;
            }});
            tbody.innerHTML = html;
        }}

        function renderInvoice(inv) {{
            setText('inv-number', inv.invoice_number);
            setText('inv-billto', inv.bill_to_party);
            setText('inv-base', '₹' + Number(inv.total_inr_base || 0).toLocaleString('en-IN', {{minimumFractionDigits: 2}}));
            setText('inv-cgst', '₹' + Number((inv.gst_amount_inr || 0) / 2.0).toLocaleString('en-IN', {{minimumFractionDigits: 2}}));
            setText('inv-sgst', '₹' + Number((inv.gst_amount_inr || 0) / 2.0).toLocaleString('en-IN', {{minimumFractionDigits: 2}}));
            setText('inv-grand', '₹' + Number(inv.grand_total_inr || 0).toLocaleString('en-IN', {{minimumFractionDigits: 2}}));

            const itemsTbody = document.getElementById('inv-items-tbody');
            let html = '';
            (inv.line_items || []).forEach(item => {{
                const amountDisp = item.currency === 'USD' ? '$' + Number(item.amount).toLocaleString('en-US', {{minimumFractionDigits: 2}}) : '₹' + Number(item.amount).toLocaleString('en-IN', {{minimumFractionDigits: 2}});
                html += `
                <tr class="border-b border-white/5 text-xs hover:bg-white/5 transition-colors">
                    <td class="py-2 px-3 text-white">${{item.description}}</td>
                    <td class="py-2 px-2 font-mono text-center text-white/50">${{item.currency}}</td>
                    <td class="py-2 px-2 font-mono text-right text-white/70 tabular-nums">${{Number(item.rate).toLocaleString()}}</td>
                    <td class="py-2 px-2 font-mono text-center text-white/70">${{item.quantity}}</td>
                    <td class="py-2 px-3 font-mono text-right font-bold text-white tabular-nums">${{amountDisp}}</td>
                </tr>
                `;
            }});
            itemsTbody.innerHTML = html;
        }}

        // ---- DISCREPANCY RESOLUTION ----
        async function resolveFlag(flagId, resType) {{
            let notes = "Auto-corrected via ISO 6346 Modulo 11 check-digit algorithm";
            if (resType === 'MANAGER_WAIVER') {{
                const modal = createWaiverModal();
                notes = await modal;
                if (!notes) return;
            }}

            const btn = event.target.closest('button');
            if (btn) {{ btn.disabled = true; btn.innerHTML = '<i data-lucide=\"loader\" class=\"w-3.5 h-3.5 animate-spin\"></i> Resolving...'; lucide.createIcons(); }}

            try {{
                const res = await fetch('/api/v1/discrepancies/' + flagId + '/resolve', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ resolution_type: resType, notes: notes }})
                }});
                const json = await res.json();
                if (json.status === 'success') {{
                    showToast('Discrepancy resolved', 'success');
                    await loadShipment(currentBookingRef);
                    await refreshShipmentsTable();
                }} else {{
                    showToast('Resolution failed: ' + json.detail, 'error');
                    if (btn) {{ btn.disabled = false; lucide.createIcons(); }}
                }}
            }} catch (err) {{
                showToast('API Error: ' + err.message, 'error');
                if (btn) {{ btn.disabled = false; lucide.createIcons(); }}
            }}
        }}

        function createWaiverModal() {{
            return new Promise(resolve => {{
                const overlay = document.createElement('div');
                overlay.className = 'fixed inset-0 z-50 modal-overlay bg-black/60 backdrop-blur-sm flex items-center justify-center p-4';
                overlay.innerHTML = `
                    <div class="modal-content glass-elevated rounded-xl p-6 w-full max-w-md animate-in">
                        <h3 class="text-lg font-semibold text-white mb-4">Manager Weight Waiver</h3>
                        <p class="text-white/60 text-sm mb-4">Enter Operations Manager reason for weight variance waiver:</p>
                        <textarea id="waiver-notes" class="w-full px-4 py-3 rounded-lg glass border-white/10 bg-white/5 text-white font-mono text-sm resize-none focus-ring focus-visible:outline-none" rows="4" placeholder="Verified certified weighbridge slip matches carrier safe tolerance..."></textarea>
                        <div class="flex gap-3 mt-4 justify-end">
                            <button onclick="closeWaiverModal(null)" class="btn-glass px-4 py-2 rounded-lg font-medium">Cancel</button>
                            <button onclick="closeWaiverModal(document.getElementById('waiver-notes').value)" class="btn-primary px-4 py-2 rounded-lg font-medium">Confirm Waiver</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(overlay);
                const textarea = overlay.querySelector('#waiver-notes');
                textarea.focus();

                window.closeWaiverModal = (value) => {{
                    overlay.remove();
                    delete window.closeWaiverModal;
                    resolve(value);
                }};
                overlay.addEventListener('click', e => {{ if (e.target === overlay) closeWaiverModal(null); }});
                document.addEventListener('keydown', function esc(e) {{ if (e.key === 'Escape') {{ closeWaiverModal(null); document.removeEventListener('keydown', esc); }} }});
            }});
        }}

        // ---- CARGOWISE TRANSMISSION ----
        async function transmitCargoWise() {{
            const terminal = document.getElementById('edi-log-terminal');
            const btn = document.getElementById('transmit-btn');
            terminal.classList.remove('hidden');
            terminal.innerHTML = '<div class="text-white/60 font-mono">[XML/EDI] Validating UniversalShipment XML schema against CargoWise eAdaptor standard...</div>';

            if (btn) {{ btn.disabled = true; btn.innerHTML = '<i data-lucide=\"loader\" class=\"w-3.5 h-3.5 animate-spin\"></i> Transmitting...'; lucide.createIcons(); }}

            try {{
                const res = await fetch('/api/v1/shipments/' + currentBookingRef + '/cargowise-sync', {{ method: 'POST' }});
                const json = await res.json();
                if (json.status === 'success') {{
                    terminal.innerHTML += '<div class="text-blue-400 font-mono">[XML/EDI] CargoWise UniversalInterchange v1.1 payload mapped and validated.</div>';
                    terminal.innerHTML += '<div class="text-emerald-400 font-mono font-bold">[XML/EDI] READY FOR IMPORT: Transaction ' + json.data.transaction_id + ' validated.</div>';
                    terminal.innerHTML += '<div class="text-white/70 font-mono">[XML/EDI] Shipment reconciled and approved. Zero manual data re-entry required.</div>';
                    showToast('CargoWise XML exported successfully', 'success');
                    await loadShipment(currentBookingRef);
                    await refreshShipmentsTable();
                }} else {{
                    terminal.innerHTML += '<div class="text-rose-400 font-mono font-bold">[EDI] REJECTED: ' + json.detail + '</div>';
                    showToast('Export rejected: ' + json.detail, 'error');
                }}
            }} catch (err) {{
                terminal.innerHTML += '<div class="text-rose-400 font-mono font-bold">[EDI] Transmission failure: ' + err.message + '</div>';
                showToast('Transmission failed: ' + err.message, 'error');
            }} finally {{
                if (btn) {{ btn.disabled = false; btn.innerHTML = '<i data-lucide=\"send\" class=\"w-3.5 h-3.5\"></i> Export CargoWise XML'; lucide.createIcons(); }}
            }}
        }}

        // ---- FILE UPLOAD ----
        async function uploadFile(e) {{
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            const uploadStatus = document.getElementById('upload-status-text');
            uploadStatus.classList.remove('hidden');
            uploadStatus.innerText = 'Parsing ' + file.name + '...';

            try {{
                const res = await fetch('/api/v1/shipments/upload', {{ method: 'POST', body: formData }});
                const json = await res.json();
                if (json.status === 'success') {{
                    uploadStatus.innerText = '✔ Ingested: ' + file.name;
                    setTimeout(() => uploadStatus.classList.add('hidden'), 3500);
                    await refreshShipmentsTable();
                    if (json.data && json.data.booking) {{
                        await loadShipment(json.data.booking.booking_reference);
                    }}
                    showToast('Document ingested successfully', 'success');
                }} else {{
                    uploadStatus.innerText = '✖ Ingestion error: ' + json.detail;
                    showToast('Ingestion failed: ' + json.detail, 'error');
                }}
            }} catch (err) {{
                uploadStatus.innerText = '✖ Upload error: ' + err.message;
                showToast('Upload failed: ' + err.message, 'error');
            }}
            e.target.value = '';
        }}

        // ---- SHIPMENTS TABLE REFRESH ----
        async function refreshShipmentsTable() {{
            try {{
                const res = await fetch('/api/v1/shipments');
                const json = await res.json();
                if (json.status === 'success') {{
                    const tbody = document.getElementById('shipments-table-body');
                    let html = '';
                    json.data.forEach(s => {{
                        const isSelected = (s.booking_reference === currentBookingRef);
                        const color = (s.status === 'CARGOWISE_SYNCED') ? 'blue' : (s.unresolved_discrepancies > 0 ? 'rose' : 'emerald');
                        const badgeText = s.status.replace(/_/g, ' ');
                        const selCls = isSelected ? 'bg-white/10 border-l-2 border-l-blue-400 font-medium' : 'border-l-2 border-l-transparent hover:bg-white/5';
                        const flagBadge = (s.unresolved_discrepancies > 0)
                            ? `<span class="inline-flex items-center justify-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20" aria-label="${{s.unresolved_discrepancies}} discrepancies on hold">${{s.unresolved_discrepancies}} HOLD</span>`
                            : `<span class="inline-flex items-center justify-center px-2 py-0.5 rounded text-[11px] font-mono font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20" aria-label="No discrepancies">CLEAR</span>`;

                        html += `
                        <tr onclick="loadShipment('${{s.booking_reference}}')" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();loadShipment('${{s.booking_reference}}')}}" tabindex="0" role="button" aria-label="Load shipment ${{s.booking_reference}}" class="table-row border-b border-white/5 text-xs transition-all duration-200 cursor-pointer ${{selCls}} fade-in">
                            <td class="py-3 px-4 font-mono font-bold text-blue-400">${{s.booking_reference}}</td>
                            <td class="py-3 px-4 font-medium text-white">${{s.customer_account}}</td>
                            <td class="py-3 px-4 font-mono text-white/70">${{s.pol}} <span class="text-white/40">→</span> ${{s.pod}}</td>
                            <td class="py-3 px-4 text-white/70">${{s.vessel}}</td>
                            <td class="py-3 px-4">
                                <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-${{color}}-500/10 text-${{color}}-400 border border-${{color}}-500/30">
                                    <span class="w-1.5 h-1.5 rounded-full bg-${{color}}-400" aria-hidden="true"></span> ${{badgeText}}
                                </span>
                            </td>
                            <td class="py-3 px-4 text-center">${{flagBadge}}</td>
                            <td class="py-3 px-4 font-mono text-right font-semibold text-white tabular-nums">
                                ₹${{Number(s.invoice_total_inr).toLocaleString('en-IN', {{minimumFractionDigits: 2}})}}
                            </td>
                        </tr>
                        `;
                    }});
                    tbody.innerHTML = html;
                    lucide.createIcons();
                }}
            }} catch (err) {{
                console.error('Failed to refresh shipments:', err);
            }}
        }}

        // ---- GUIDED DEMO ----
        async function runGuidedDemo() {{
            const banner = document.getElementById('demo-guide-toast');
            if (banner) {{
                banner.classList.remove('hidden');
                banner.innerHTML = '<span class="font-bold text-blue-400">[1/3] Step 1</span>: Ingesting raw Shipping Instruction. Checking ISO 6346 checksums & SOLAS weights...';
            }}

            await loadShipment('BKG-MAA-992104');
            window.scrollTo({{ top: 380, behavior: 'smooth' }});
            await new Promise(r => setTimeout(r, 2000));

            if (banner) banner.innerHTML = '<span class="font-bold text-amber-400">[2/3] Step 2</span>: Discrepancy Caught! Auto-fixing container check-digit typo & recording slot waiver...';

            try {{
                const res = await fetch('/api/v1/shipments/BKG-MAA-992104');
                const json = await res.json();
                if (json.status === 'success' && json.data.discrepancies) {{
                    for (const f of json.data.discrepancies) {{
                        if (f.is_resolved === 0) {{
                            await fetch('/api/v1/discrepancies/' + f.id + '/resolve', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{ resolution_type: 'AUTO_FIX', notes: 'Auto-resolved via FreightFlow 60s Demo Suite' }})
                            }});
                        }}
                    }}
                    await loadShipment('BKG-MAA-992104');
                    await refreshShipmentsTable();
                }}
            }} catch (e) {{ console.error(e); }}

            await new Promise(r => setTimeout(r, 1500));
            window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
            if (banner) banner.innerHTML = '<span class="font-bold text-emerald-400">[3/3] Step 3</span>: Exporting validated UniversalShipment XML for CargoWise One eAdaptor...';
            await new Promise(r => setTimeout(r, 1200));
            await transmitCargoWise();

            if (banner) {{
                banner.innerHTML = '<span class="font-bold text-emerald-300">✔ Demo Complete</span>: Manual entry eliminated. CargoWise XML ready to import.';
            }}
        }}

        // ---- DOWNLOAD HELPERS ----
        function downloadXml() {{ window.open('/api/v1/shipments/' + currentBookingRef + '/cargowise-xml', '_blank'); }}
        function downloadDcsa() {{ window.open('/api/v1/shipments/' + currentBookingRef + '/dcsa-json', '_blank'); }}

        // ---- TOAST SYSTEM ----
        function showToast(message, type = 'info') {{
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast-enter glass-elevated rounded-xl px-4 py-3 flex items-center gap-3 shadow-2xl pointer-events-auto min-w-[280px] max-w-md`;
            const icons = {{
                success: '<i data-lucide="check-circle" class="w-5 h-5 text-emerald-400"></i>',
                error: '<i data-lucide="alert-circle" class="w-5 h-5 text-rose-400"></i>',
                info: '<i data-lucide="info" class="w-5 h-5 text-blue-400"></i>',
            }};
            toast.innerHTML = `${{icons[type] || icons.info}} <span class="text-white font-medium text-sm">${{message}}</span>`;
            container.appendChild(toast);
            lucide.createIcons();
            setTimeout(() => {{
                toast.classList.remove('toast-enter');
                toast.classList.add('toast-exit');
                toast.addEventListener('animationend', () => toast.remove());
            }}, 4000);
        }}

        // Initialize Lucide icons
        lucide.createIcons();
    </script>
</body>
</html>"""
    return html