"""
StudioEngine CLI: Command-Line Management for 34 Autonomous Agents
"""

import sys
import os
import argparse

# Ensure Windows terminal handles UTF-8 gracefully
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from studio_engine.registry import AgentRegistry
from studio_engine.dispatcher import AgentDispatcher, TaskRequest
from studio_engine.workflow import WorkflowOrchestrator

console = Console()

def list_agents_cmd():
    registry = AgentRegistry()
    table = Table(title=f"StudioEngine: {registry.total_count()} Agents Across {len(registry.departments)} Departments", border_style="cyan")
    table.add_column("Department", style="bold magenta")
    table.add_column("Agent Name", style="bold cyan")
    table.add_column("Role", style="white")
    table.add_column("Core Capabilities", style="dim")

    for dept, agents in registry.departments.items():
        for name in agents:
            spec = registry.get_agent(name)
            table.add_row(
                dept.upper(),
                spec.name,
                spec.role,
                ", ".join(spec.capabilities[:3])
            )
    console.print(table)

def dispatch_cmd(agent_name: str, prompt: str):
    registry = AgentRegistry()
    dispatcher = AgentDispatcher(registry)
    console.print(f"[bold yellow]▶ Dispatching Agent:[/bold yellow] [bold cyan]{agent_name}[/bold cyan]")
    console.print(f"[bold]Prompt:[/bold] {prompt}\n")
    
    req = TaskRequest(agent_name=agent_name, prompt=prompt)
    result = dispatcher.dispatch(req)
    
    console.print(Panel(
        f"{result.output_text}\n\n"
        f"[bold slate-500]Time: {result.execution_time_ms} ms | Task ID: {result.task_id}[/bold slate-500]",
        title=f"[bold green]✔ Deliverable from {result.agent_name} ({result.department.upper()})[/bold green]",
        border_style="green"
    ))

def sprint_cmd(project_name: str, target_niche: str):
    registry = AgentRegistry()
    dispatcher = AgentDispatcher(registry)
    orchestrator = WorkflowOrchestrator(registry, dispatcher)
    
    console.print(f"\n[bold yellow]🚀 Launching 7-Stage Studio Sprint for:[/bold yellow] [bold cyan]{project_name}[/bold cyan] ([bold white]{target_niche}[/bold white])\n")
    sprint = orchestrator.run_full_venture_sprint(project_name=project_name, target_niche=target_niche)
    
    for i, step in enumerate(sprint.steps, 1):
        console.print(f"[bold cyan]Stage {i}:[/bold cyan] [bold green]{step.agent_name}[/bold green] ({step.department.upper()}) completed in {step.execution_time_ms}ms")
    
    console.print(f"\n[bold green]✔ Studio Sprint {sprint.sprint_id} Completed Successfully with 7 Artifacts Generated.[/bold green]\n")

def main():
    parser = argparse.ArgumentParser(description="StudioEngine Enterprise CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("list", help="List all 34 specialized agents by department")

    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch a task to a specialized agent")
    dispatch_parser.add_argument("--agent", required=True, help="Agent name (e.g. backend-architect)")
    dispatch_parser.add_argument("--prompt", required=True, help="Task instructions")

    sprint_parser = subparsers.add_parser("sprint", help="Run cross-department venture sprint")
    sprint_parser.add_argument("--project", default="VentureOS Core", help="Project name")
    sprint_parser.add_argument("--niche", default="B2B E-Commerce", help="Target niche")

    args = parser.parse_args()

    if args.command == "list":
        list_agents_cmd()
    elif args.command == "dispatch":
        dispatch_cmd(args.agent, args.prompt)
    elif args.command == "sprint":
        sprint_cmd(args.project, args.niche)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
