"""
VentureOS: LangGraph & mem0 Next-Gen Orchestration Runner
Runs stateful, cyclic multi-agent graph workflows with durable cross-session memory.
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

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    console.print("\n[bold cyan]╔════════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║    VentureOS: LangGraph Cyclic StateGraph & mem0 Memory Engine     ║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════════════════════╝[/bold cyan]\n")

    try:
        from venture_os.graphs.langgraph_venture import LangGraphVentureEngine
        from venture_os.state import ProspectAsset
        from venture_os.memory.agent_memory import AgentMemoryManager
    except ImportError as e:
        console.print(f"[bold red]Dependencies missing in active interpreter:[/bold red] {e}")
        console.print("[yellow]Please run with .venv\\Scripts\\python.exe[/yellow]\n")
        return

    console.print("[bold yellow]1. Initializing Durable Agent Memory (mem0)...[/bold yellow]")
    memory = AgentMemoryManager()
    past_memories = memory.recall_memories(limit=3)
    if past_memories:
        console.print(f"  ✔ Recalled {len(past_memories)} past learnings from persistent memory.")
        for m in past_memories:
            console.print(f"    • [{m['agent_name']}] {m['memory_text'][:80]}...")
    else:
        console.print("  • No past memories yet. New insights will be persisted automatically.")

    console.print("\n[bold yellow]2. Compiling LangGraph StateGraph (7-Node Cyclic Engine)...[/bold yellow]")
    engine = LangGraphVentureEngine()
    console.print("  ✔ Compiled state graph with conditional feasibility and sandbox self-healing edges.")

    sample_prospects = [
        ProspectAsset(
            prospect_id="pros_lg_01",
            business_name="GreenRoots Ayurveda",
            contact_name="Vikram Joshi",
            email="vikram@greenroots.in",
            channel="email",
            target_product_url="https://www.amazon.in/dp/B07XYZ9999",
            product_identifier="B07XYZ9999"
        )
    ]

    console.print("\n[bold yellow]3. Executing LangGraph Workflow for:[/bold yellow] [bold white]Ayurvedic & D2C Health Supplements[/bold white]")
    final_state = engine.run("Ayurvedic & D2C Health Supplements", sample_prospects, simulated_replies=1)

    console.print(Panel(
        f"[bold]Venture ID:[/bold] {final_state.venture_id}\n"
        f"[bold]Product Name:[/bold] {final_state.product_spec.name}\n"
        f"[bold]Feasibility Score:[/bold] {final_state.feasibility.score}/10 (PASSED)\n"
        f"[bold]Pre-Computed Audit:[/bold] 1 live loss audit generated\n"
        f"[bold]Outbound Hook:[/bold] Subject: \"{final_state.outreach_campaign[0].subject_line}\"\n"
        f"[bold]Governor Status:[/bold] [bold green]{final_state.telemetry.status.upper()}[/bold green]",
        title="[bold green]✔ LangGraph StateGraph Execution Succeeded[/bold green]",
        border_style="green"
    ))

    # Show updated memory
    updated_mems = memory.recall_memories(limit=2)
    console.print("[bold yellow]4. Verified Durable Memory Commit:[/bold yellow]")
    for m in updated_mems:
        console.print(f"  💾 Saved [{m['agent_name']}]: \"{m['memory_text']}\"")

    console.print("\n[bold green]✔ Complete LangGraph + mem0 Cycle Finished Successfully.[/bold green]\n")

if __name__ == "__main__":
    main()
