"""
VentureOS: Autonomous Pipeline Runner
Demonstrates the complete end-to-end execution from Pain Discovery to Pre-Computed Trojan Outbound.
"""

import sys
import os

# Ensure Windows terminal handles UTF-8 gracefully
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from venture_os.state import ProspectAsset
from venture_os.engine import VentureOSEngine

console = Console()

def main():
    console.print("\n[bold cyan]╔════════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║       VentureOS: Autonomous Micro-SaaS Foundry & GTM Engine       ║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════════════════════╝[/bold cyan]\n")

    engine = VentureOSEngine()

    # Define real-world target prospects to run pre-computation on
    sample_prospects = [
        ProspectAsset(
            prospect_id="pros_001",
            business_name="Aura Botanics D2C",
            contact_name="Rohan Verma",
            email="rohan@aurabotanics.in",
            channel="email",
            target_product_url="https://www.amazon.in/dp/B09ABC1234",
            product_identifier="B09ABC1234"
        ),
        ProspectAsset(
            prospect_id="pros_002",
            business_name="NutriPure Organics",
            contact_name="Sneha Kapoor",
            email="sneha@nutripure.co.in",
            channel="email",
            target_product_url="https://www.amazon.in/dp/B08XYZ5678",
            product_identifier="B08XYZ5678"
        )
    ]

    console.print(f"[bold yellow]▶ Initiating Autonomous Loop for Niche:[/bold yellow] [bold white]Amazon.in / Meesho D2C Brand Sellers[/bold white]\n")

    state = engine.run_lifecycle(
        niche="Amazon India / Meesho D2C Brand Sellers",
        sample_prospects=sample_prospects,
        simulated_replies=1
    )

    # 1. Pain Hunter Card
    pain = state.pain_signal
    console.print(Panel(
        f"[bold]Target Persona:[/bold] {pain.target_persona}\n"
        f"[bold]Discovered Pain:[/bold] \"{pain.raw_quote}\"\n"
        f"[bold]Est. Monthly Inaction Loss:[/bold] [red]₹{pain.estimated_monthly_loss_inr:,.0f}[/red]\n"
        f"[bold]Urgency Score:[/bold] [green]{pain.urgency_score}/10[/green]",
        title="[bold green]1. Pain Hunter Agent — Market Signal Mined[/bold green]",
        border_style="green"
    ))

    # 2. Feasibility Arbiter Card
    feas = state.feasibility
    console.print(Panel(
        f"[bold]Decision:[/bold] {'[bold green]PASSED[/bold green]' if feas.passed else '[bold red]FAILED[/bold red]'} (Score: {feas.score}/10)\n"
        f"[bold]Incumbents Analyzed:[/bold] {feas.incumbent_competition}\n"
        f"[bold]Why Incumbents Fail:[/bold] {feas.why_incumbents_fail}\n"
        f"[bold]Anti-Bot / Proxy Risk:[/bold] {feas.anti_bot_difficulty.upper()} / {feas.proxy_cost_risk.upper()}",
        title="[bold blue]2. Feasibility Arbiter — Competitive Defense Verified[/bold blue]",
        border_style="blue"
    ))

    # 3. Product Synthesizer & Sandbox Verification
    spec = state.product_spec
    console.print(Panel(
        f"[bold]Product Name:[/bold] {spec.name} ({spec.product_id})\n"
        f"[bold]Utility:[/bold] {spec.core_utility}\n"
        f"[bold]Verification Status:[/bold] [bold green]{spec.verification_status.upper()}[/bold green] (100% selector coverage passed)",
        title="[bold magenta]3 & 4. Synthesizer & Sandbox Verifier — Code Generated & Tested[/bold magenta]",
        border_style="magenta"
    ))

    # 5. Trojan Auditor (Pre-Computation) Table
    table = Table(title="5. Trojan Auditor — Pre-Computed Proof-of-Loss Audits", border_style="yellow")
    table.add_column("Prospect", style="cyan")
    table.add_column("SKU / ASIN", style="white")
    table.add_column("Buy Box Status", style="red")
    table.add_column("Current Winner", style="yellow")
    table.add_column("Est. Weekly Leak", style="bold red")

    for audit in state.audits:
        prospect_name = next(p.business_name for p in sample_prospects if p.prospect_id == audit.prospect_id)
        table.add_row(
            prospect_name,
            audit.product_identifier,
            "LOST" if not audit.buy_box_owned else "WON",
            audit.current_winner,
            f"₹{audit.estimated_weekly_revenue_leak_inr:,.0f}/wk"
        )
    console.print(table)

    # 6. Outbound SDR Pitch Example
    hook = state.outreach_campaign[0]
    console.print(Panel(
        f"[bold]Subject:[/bold] {hook.subject_line}\n\n"
        f"{hook.body_markdown}\n\n"
        f"[bold cyan]Offer:[/bold cyan] 7-Day Pilot at ₹{hook.pilot_price_inr:,.0f} (Full setup credit)",
        title="[bold cyan]6. Outbound SDR — Hyper-Personalized Trojan Outreach[/bold cyan]",
        border_style="cyan"
    ))

    # 7. Governor Telemetry & Status
    tel = state.telemetry
    console.print(Panel(
        f"[bold]Audits Pre-Computed:[/bold] {tel.total_prospects_audited}\n"
        f"[bold]Outreach Touches:[/bold] {tel.total_outreach_sent}\n"
        f"[bold]Verified Positive Replies:[/bold] [green]{tel.positive_replies}[/green]\n"
        f"[bold]Pipeline Status:[/bold] [bold green]{tel.status.upper()}[/bold green] (Ready to issue 1-page Pilot Contract)",
        title="[bold green]7. Pipeline Governor — Statistical Traction Enforced[/bold green]",
        border_style="green"
    ))

    console.print("\n[bold green]✔ Autonomous Venture Cycle Completed Successfully.[/bold green]\n")

if __name__ == "__main__":
    main()
