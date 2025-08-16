#!/usr/bin/env python3
"""
Telemetry viewer for Nova CI-Rescue.
Parses and displays trace.jsonl files in a human-readable format.
"""

import json
import typer
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

app = typer.Typer(
    name="nova-telemetry",
    help="View Nova CI-Rescue telemetry traces",
    add_completion=False,
)
console = Console()


class TelemetryViewer:
    """Parse and display telemetry trace files."""
    
    def __init__(self, trace_file: Path):
        self.trace_file = trace_file
        self.events: List[Dict[str, Any]] = []
        self.run_info: Optional[Dict[str, Any]] = None
        self.artifacts: List[Dict[str, Any]] = []
        
    def load(self) -> None:
        """Load and parse the trace file."""
        if not self.trace_file.exists():
            raise FileNotFoundError(f"Trace file not found: {self.trace_file}")
        
        with open(self.trace_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    self.events.append(event)
                    
                    # Extract special events
                    if event.get("event") == "start":
                        self.run_info = event
                    elif event.get("event") == "artifact":
                        self.artifacts.append(event)
                except json.JSONDecodeError:
                    continue
    
    def display_summary(self) -> None:
        """Display run summary."""
        if not self.run_info:
            console.print("[red]No run information found in trace[/red]")
            return
        
        # Find end event
        end_event = None
        for event in self.events:
            if event.get("event") == "end":
                end_event = event
                break
        
        # Create summary panel
        summary_lines = []
        summary_lines.append(f"[bold]Run ID:[/bold] {self.run_info.get('run_id', 'Unknown')}")
        summary_lines.append(f"[bold]Repository:[/bold] {self.run_info.get('repo_path', 'Unknown')}")
        summary_lines.append(f"[bold]Started:[/bold] {self.run_info.get('ts', 'Unknown')}")
        
        if end_event:
            summary_lines.append(f"[bold]Ended:[/bold] {end_event.get('ts', 'Unknown')}")
            summary_lines.append(f"[bold]Success:[/bold] {'✅ Yes' if end_event.get('success') else '❌ No'}")
            
            if end_event.get('summary'):
                summary = end_event['summary']
                summary_lines.append(f"[bold]Status:[/bold] {summary.get('status', 'Unknown')}")
                summary_lines.append(f"[bold]Iterations:[/bold] {summary.get('iterations', 0)}")
                summary_lines.append(f"[bold]Patches Applied:[/bold] {summary.get('patches_applied', 0)}")
                
                if summary.get('duration_seconds'):
                    minutes, seconds = divmod(int(summary['duration_seconds']), 60)
                    summary_lines.append(f"[bold]Duration:[/bold] {minutes}m {seconds}s")
        
        panel = Panel("\n".join(summary_lines), title="Run Summary", border_style="green")
        console.print(panel)
    
    def display_timeline(self) -> None:
        """Display event timeline."""
        table = Table(title="Event Timeline", show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan", width=12)
        table.add_column("Event", style="yellow")
        table.add_column("Details", style="white", no_wrap=False)
        
        # Parse timestamps and sort events
        for event in self.events:
            # Skip artifacts from timeline
            if event.get("event") == "artifact":
                continue
            
            # Extract timestamp
            ts_str = event.get("ts", "")
            try:
                # Parse ISO format timestamp and format for display
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                time_str = ts.strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm
            except:
                time_str = "Unknown"
            
            event_type = event.get("event", "unknown")
            
            # Format details based on event type
            details = self._format_event_details(event_type, event)
            
            # Add row with appropriate styling
            if "error" in event_type.lower():
                table.add_row(time_str, f"[red]{event_type}[/red]", details)
            elif "complete" in event_type.lower() or "success" in event_type.lower():
                table.add_row(time_str, f"[green]{event_type}[/green]", details)
            elif "start" in event_type.lower():
                table.add_row(time_str, f"[cyan]{event_type}[/cyan]", details)
            else:
                table.add_row(time_str, event_type, details)
        
        console.print(table)
    
    def _format_event_details(self, event_type: str, event: Dict[str, Any]) -> str:
        """Format event details for display."""
        data = event.get("data", {})
        
        if event_type == "planner_start":
            return f"Iteration {data.get('iteration', 0)}, {data.get('failing_tests_count', 0)} failing tests"
        
        elif event_type == "planner_complete":
            plan = data.get("plan", {})
            return f"Approach: {plan.get('approach', 'Unknown')}"
        
        elif event_type == "actor_complete":
            metrics = data.get("patch_metrics", {})
            return f"+{metrics.get('added_lines', 0)}/-{metrics.get('removed_lines', 0)} lines, {metrics.get('affected_files_count', 0)} files"
        
        elif event_type == "critic_approved":
            return f"✓ {data.get('reason', 'Approved')}"
        
        elif event_type == "critic_rejected":
            return f"✗ {data.get('reason', 'Rejected')}"
        
        elif event_type == "patch_applied":
            return f"Step {data.get('step', 0)}, {len(data.get('files_changed', []))} files changed"
        
        elif event_type == "run_tests_complete":
            metrics = data.get("metrics", {})
            return f"{metrics.get('tests_fixed_count', 0)} fixed, {metrics.get('total_failures', 0)} remaining"
        
        elif event_type == "reflect_complete":
            return f"Decision: {data.get('decision', 'unknown')} ({data.get('reason', 'unknown')})"
        
        elif event_type == "test_discovery":
            return f"Found {data.get('total_failures', 0)} failing tests"
        
        elif event_type == "completion":
            return f"Status: {data.get('status', 'unknown')}"
        
        elif event_type == "error":
            return f"[red]{data.get('error', 'Unknown error')}[/red]"
        
        else:
            # Generic formatting for unknown events
            if data:
                # Pick the most interesting fields
                if "iteration" in data:
                    return f"Iteration {data['iteration']}"
                elif "reason" in data:
                    return data["reason"]
                elif "status" in data:
                    return f"Status: {data['status']}"
                else:
                    # Show first key-value pair
                    for key, value in list(data.items())[:1]:
                        return f"{key}: {value}"
            return ""
    
    def display_artifacts(self) -> None:
        """Display saved artifacts."""
        if not self.artifacts:
            console.print("[yellow]No artifacts found[/yellow]")
            return
        
        tree = Tree("📁 Artifacts", guide_style="dim")
        
        # Group artifacts by type
        patches = []
        reports = []
        other = []
        
        for artifact in self.artifacts:
            name = artifact.get("name", "")
            if "patch" in name:
                patches.append(artifact)
            elif "report" in name:
                reports.append(artifact)
            else:
                other.append(artifact)
        
        # Add patches
        if patches:
            patch_branch = tree.add("🔧 Patches")
            for patch in patches:
                name = Path(patch.get("name", "")).name
                size = patch.get("size", 0)
                patch_branch.add(f"{name} ({size} bytes)")
        
        # Add reports
        if reports:
            report_branch = tree.add("📊 Test Reports")
            for report in reports:
                name = Path(report.get("name", "")).name
                size = report.get("size", 0)
                report_branch.add(f"{name} ({size} bytes)")
        
        # Add other artifacts
        if other:
            other_branch = tree.add("📄 Other")
            for artifact in other:
                name = Path(artifact.get("name", "")).name
                size = artifact.get("size", 0)
                other_branch.add(f"{name} ({size} bytes)")
        
        console.print(tree)
    
    def display_iterations(self) -> None:
        """Display iteration details."""
        iterations = {}
        
        # Group events by iteration
        for event in self.events:
            data = event.get("data", {})
            iteration = data.get("iteration")
            if iteration is not None:
                if iteration not in iterations:
                    iterations[iteration] = []
                iterations[iteration].append(event)
        
        if not iterations:
            console.print("[yellow]No iteration data found[/yellow]")
            return
        
        for iter_num in sorted(iterations.keys()):
            console.print(f"\n[bold blue]Iteration {iter_num}[/bold blue]")
            
            iter_events = iterations[iter_num]
            
            # Find key events in this iteration
            planner = None
            actor = None
            critic = None
            tests = None
            reflect = None
            
            for event in iter_events:
                event_type = event.get("event", "")
                if "planner_complete" in event_type:
                    planner = event.get("data", {})
                elif "actor_complete" in event_type:
                    actor = event.get("data", {})
                elif event_type in ["critic_approved", "critic_rejected"]:
                    critic = event.get("data", {})
                elif "run_tests_complete" in event_type:
                    tests = event.get("data", {})
                elif "reflect_complete" in event_type:
                    reflect = event.get("data", {})
            
            # Display iteration summary
            if planner:
                plan = planner.get("plan", {})
                console.print(f"  [cyan]Plan:[/cyan] {plan.get('approach', 'Unknown')}")
            
            if actor:
                metrics = actor.get("patch_metrics", {})
                console.print(f"  [cyan]Patch:[/cyan] +{metrics.get('added_lines', 0)}/-{metrics.get('removed_lines', 0)} lines")
            
            if critic:
                approved = critic.get("approved", False)
                reason = critic.get("reason", "Unknown")
                if approved:
                    console.print(f"  [cyan]Critic:[/cyan] [green]✓ Approved[/green] - {reason}")
                else:
                    console.print(f"  [cyan]Critic:[/cyan] [red]✗ Rejected[/red] - {reason}")
            
            if tests:
                metrics = tests.get("metrics", {})
                console.print(f"  [cyan]Tests:[/cyan] {metrics.get('tests_fixed_count', 0)} fixed, {metrics.get('total_failures', 0)} remaining")
            
            if reflect:
                decision = reflect.get("decision", "unknown")
                reason = reflect.get("reason", "unknown")
                console.print(f"  [cyan]Decision:[/cyan] {decision} ({reason})")


@app.command()
def view(
    trace_file: Path = typer.Argument(
        ...,
        help="Path to trace.jsonl file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    summary: bool = typer.Option(
        True,
        "--summary/--no-summary",
        help="Show run summary",
    ),
    timeline: bool = typer.Option(
        False,
        "--timeline",
        "-t",
        help="Show event timeline",
    ),
    iterations: bool = typer.Option(
        False,
        "--iterations",
        "-i",
        help="Show iteration details",
    ),
    artifacts: bool = typer.Option(
        False,
        "--artifacts",
        "-a",
        help="Show saved artifacts",
    ),
    all: bool = typer.Option(
        False,
        "--all",
        help="Show all information",
    ),
):
    """View a telemetry trace file."""
    viewer = TelemetryViewer(trace_file)
    
    try:
        viewer.load()
    except Exception as e:
        console.print(f"[red]Error loading trace file: {e}[/red]")
        raise typer.Exit(1)
    
    # If --all is specified, show everything
    if all:
        summary = timeline = iterations = artifacts = True
    
    # Default to showing summary if nothing else specified
    if not any([timeline, iterations, artifacts]):
        summary = True
    
    if summary:
        viewer.display_summary()
        console.print()
    
    if timeline:
        viewer.display_timeline()
        console.print()
    
    if iterations:
        viewer.display_iterations()
        console.print()
    
    if artifacts:
        viewer.display_artifacts()
        console.print()


@app.command()
def list_runs(
    telemetry_dir: Path = typer.Option(
        Path(".nova"),
        "--dir",
        "-d",
        help="Telemetry directory",
    ),
):
    """List available telemetry runs."""
    if not telemetry_dir.exists():
        console.print(f"[red]Telemetry directory not found: {telemetry_dir}[/red]")
        raise typer.Exit(1)
    
    # Find all run directories
    runs = []
    for path in telemetry_dir.iterdir():
        if path.is_dir() and (path / "trace.jsonl").exists():
            runs.append(path)
    
    if not runs:
        console.print("[yellow]No telemetry runs found[/yellow]")
        return
    
    # Sort by modification time (newest first)
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    table = Table(title="Telemetry Runs", show_header=True, header_style="bold magenta")
    table.add_column("Run ID", style="cyan")
    table.add_column("Time", style="yellow")
    table.add_column("Status", style="white")
    table.add_column("Artifacts", style="dim")
    
    for run_dir in runs[:20]:  # Show last 20 runs
        run_id = run_dir.name
        
        # Get modification time
        mtime = datetime.fromtimestamp(run_dir.stat().st_mtime)
        time_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Try to get status from trace
        status = "Unknown"
        trace_file = run_dir / "trace.jsonl"
        try:
            with open(trace_file, 'r') as f:
                for line in f:
                    event = json.loads(line.strip())
                    if event.get("event") == "end":
                        status = "✅ Success" if event.get("success") else "❌ Failed"
                        break
        except:
            pass
        
        # Count artifacts
        artifact_count = sum(1 for p in run_dir.rglob("*") if p.is_file() and p.name != "trace.jsonl")
        
        table.add_row(run_id, time_str, status, str(artifact_count))
    
    console.print(table)
    
    if len(runs) > 20:
        console.print(f"\n[dim]Showing 20 most recent runs out of {len(runs)} total[/dim]")


if __name__ == "__main__":
    app()
