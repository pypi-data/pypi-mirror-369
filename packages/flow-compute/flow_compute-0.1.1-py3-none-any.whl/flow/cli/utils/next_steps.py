"""Helpers for building and rendering context-aware "Next steps" panels.

This module centralizes construction and presentation of follow-up
recommendations across CLI commands to ensure a consistent UX.

Design goals:
- Opinionated, minimal, context-aware suggestions
- One rendering style (panel) with muted border
- No command-specific knowledge beyond simple task state heuristics
"""

from typing import Iterable, List

from rich.console import Console
from rich.panel import Panel

from flow.api.models import Task
from flow.cli.utils.theme_manager import theme_manager


def build_empty_state_next_steps(has_history: bool) -> List[str]:
    """Recommendations when there are no active tasks.

    Args:
        has_history: True if any tasks exist historically (even if not recent)

    Returns:
        A short, ordered list of next steps to present to the user.
    """

    steps: List[str] = []

    # Always offer the fastest path to success
    steps.append("Create a task (quick): [accent]flow run -- 'nvidia-smi'[/accent]")
    steps.append(
        "Create from YAML: [accent]flow run examples/configs/basic.yaml[/accent]"
    )

    # If they already have history, nudge discovery; otherwise nudge examples
    if has_history:
        steps.append(
            "View task details: [accent]flow status <task-name>[/accent] or [accent]flow status 1[/accent]"
        )
    else:
        steps.append("Explore starters: [accent]flow example[/accent]")

    return steps


def build_generic_recommendations(*, index_help: str, active_tasks: int) -> List[str]:
    """Generic recommendations to append beneath listings.

    Args:
        index_help: A human-friendly index range (e.g., "1" or "1-5")
        active_tasks: Number of active (running/pending) tasks displayed

    Returns:
        A list of recommendations suitable for a compact "Next steps" panel.
    """

    recs: List[str] = []
    # Drill-down affordance – useful in every state
    recs.append(
        f"View task details: [accent]flow status <task-name>[/accent] or [accent]flow status {index_help}[/accent]"
    )

    # If nothing is running, offer a one-liner to create work
    if active_tasks == 0:
        recs.insert(0, "Create a task (quick): [accent]flow run -- 'nvidia-smi'[/accent]")

    return recs


def _is_flow_origin(task: Task) -> bool:
    """Return True if a task is from Flow CLI origin.

    Falls back to False when metadata is unavailable.
    """
    try:
        meta = getattr(task, "provider_metadata", {}) or {}
        return meta.get("origin") == "flow-cli"
    except Exception:
        return False


def _status_value(task: Task) -> str:
    """Return task status value resiliently (handles enums/mocks)."""
    try:
        status = getattr(task, "status", None)
        return getattr(status, "value", str(status))
    except Exception:
        return ""


def build_status_recommendations(
    tasks: Iterable[Task],
    *,
    max_count: int,
    index_example_single: str,
    index_example_multi: str,
) -> List[str]:
    """Build context-aware recommendations for the status view.

    Args:
        tasks: Tasks displayed to the user (already ordered as shown).
        max_count: Maximum number of recommendations to return.
        index_example_single: Index shortcut example for a single selection (e.g., "1").
        index_example_multi: Index shortcut example for multi/range (e.g., "1-3" or "1-3,5").

    Returns:
        A list of concise recommendation strings (top-N by priority).
    """

    task_list = list(tasks)

    has_running = any(_status_value(t) == "running" for t in task_list)
    has_pending = any(_status_value(t) == "pending" for t in task_list)
    has_active = has_running or has_pending
    has_flow_running = any(_is_flow_origin(t) and _status_value(t) == "running" for t in task_list)

    recs: List[str] = []

    # State-aware, highest value first
    if has_flow_running:
        recs.append(
            f"SSH into running task: [accent]flow ssh <task-name>[/accent] or [accent]flow ssh {index_example_single}[/accent]"
        )
        recs.append(
            f"View logs for a task: [accent]flow logs <task-name>[/accent] or [accent]flow logs {index_example_single}[/accent]"
        )

    if has_active:
        recs.append(
            f"Cancel tasks by index or range: [accent]flow cancel {index_example_multi}[/accent]"
        )
        recs.append("Watch updates: [accent]flow status --watch[/accent]")

    # Always include a creation path, but keep list short
    recs.append("Submit a new task: [accent]flow run task.yaml[/accent]")

    # When no active tasks, pivot to getting-started paths
    if not has_active:
        recs.append("Start development environment: [accent]flow dev[/accent]")
        recs.append("Explore starters: [accent]flow example[/accent]")

    # Deduplicate while preserving order
    deduped: List[str] = []
    seen = set()
    for r in recs:
        if r not in seen:
            deduped.append(r)
            seen.add(r)

    return deduped[: max(0, int(max_count))]


def render_next_steps_panel(
    console: Console, recommendations: Iterable[str], *, title: str = "Next steps"
) -> None:
    """Render a compact panel listing recommendations.

    Args:
        console: Rich console to render into.
        recommendations: Lines to display; each will be bullet-prefixed.
        title: Panel title (plain text; styling handled internally).
    """
    lines = [f"  • {str(r)}" for r in recommendations]
    body = "\n".join(lines)
    panel = Panel(
        body,
        title=f"[bold]{title}[/bold]",
        border_style=theme_manager.get_color("muted"),
        expand=False,
    )
    console.print("\n")
    console.print(panel)


