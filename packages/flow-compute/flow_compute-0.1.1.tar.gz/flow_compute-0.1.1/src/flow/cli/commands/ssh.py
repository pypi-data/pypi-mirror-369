"""SSH command for connecting to running GPU instances.

Provides secure shell access to running tasks for debugging and development.

Examples:
    Connect interactively:
        $ flow ssh task-abc123

    Execute remote command (two supported forms):
        $ flow ssh task-abc123 -c 'nvidia-smi'
        $ flow ssh task-abc123 -- nvidia-smi

    Check GPU utilization:
        $ flow ssh task-abc123 -c 'watch -n1 nvidia-smi'
"""

import os
import shlex

import click

from flow.api.client import Flow
from flow.api.models import Task
from flow.cli.commands.base import BaseCommand, console
from flow.cli.provider_resolver import ProviderResolver
from flow.cli.utils.task_formatter import TaskFormatter
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand


class SSHCommand(BaseCommand, TaskOperationCommand):
    """SSH command implementation.

    Handles both interactive sessions and remote command execution.
    Requires task to be in running state with SSH keys configured.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "ssh"

    @property
    def manages_own_progress(self) -> bool:
        """SSH manages its own progress display."""
        return True

    @property
    def help(self) -> str:
        return """SSH to running GPU instances - Interactive shell or remote command execution

Quick connect:
  flow ssh                         # Interactive task selector
  flow ssh my-training             # Connect by task name
  flow ssh abc-123                 # Connect by task ID

Remote commands:
  flow ssh task -c 'nvidia-smi'    # Check GPU status
  flow ssh task -- nvidia-smi      # Alternate syntax using '--'
  flow ssh task -c 'htop'          # Monitor system resources
  flow ssh task --node 1           # Connect to specific node (multi-instance)"""

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show tasks with SSH access."""
        return TaskFilter.with_ssh

    def get_selection_title(self) -> str:
        return "Select a running task to SSH into"

    def get_no_tasks_message(self) -> str:
        return "No running tasks available for SSH"

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute SSH connection on the selected task with a unified timeline."""
        command = kwargs.get("command")
        node = kwargs.get("node", 0)

        # Validate node parameter for multi-instance tasks (shared helper)
        from flow.cli.utils.task_utils import validate_node_index

        validate_node_index(task, node)
        task_display = (
            f"{self.task_formatter.format_task_display(task)} [node {node}]"
            if getattr(task, "num_instances", 1) > 1
            else self.task_formatter.format_task_display(task)
        )

        # Pre-check: if provider lacks remote ops, show guidance and exit
        try:
            _ = client.get_remote_operations()
        except Exception:
            console.print("[red]Error: Provider doesn't support remote operations[/red]")
            return

        # Unified timeline
        from flow.cli.utils.step_progress import SSHWaitProgressAdapter, StepTimeline

        timeline = StepTimeline(console, title="flow ssh", title_animation="auto")
        timeline.start()

        # Step 1: Ensure SSH readiness if needed (skip when FAST mode is enabled)
        fast_mode = os.environ.get("FLOW_SSH_FAST") == "1"
        if not fast_mode and not task.ssh_host:
            from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

            # Seed bar from existing instance age so resume after Ctrl+C is realistic
            baseline = 0
            try:
                baseline = int(getattr(task, "instance_age_seconds", None) or 0)
            except Exception:
                baseline = 0
            step_idx = timeline.add_step(
                f"Waiting for SSH (up to {DEFAULT_PROVISION_MINUTES}m)",
                show_bar=True,
                estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                baseline_elapsed_seconds=baseline,
            )
            adapter = SSHWaitProgressAdapter(
                timeline,
                step_idx,
                DEFAULT_PROVISION_MINUTES * 60,
                baseline_elapsed_seconds=baseline,
            )
            # Add an explicit, theme-aligned hint about safe interruption
            from flow.cli.utils.theme_manager import theme_manager

            hint_color = theme_manager.get_color("muted")
            accent = theme_manager.get_color("accent")
            from rich.text import Text

            hint = Text()
            hint.append("  Press ")
            hint.append("Ctrl+C", style=accent)
            hint.append(
                " to stop waiting. The instance continues provisioning; resume anytime with "
            )
            hint.append("flow ssh", style=accent)
            timeline.set_active_hint_text(hint)
            try:
                with adapter:
                    task = client.wait_for_ssh(
                        task_id=task.task_id,
                        timeout=DEFAULT_PROVISION_MINUTES * 60,  # standard wait for SSH
                        show_progress=False,
                        progress_adapter=adapter,
                    )
            except SSHNotReadyError as e:
                timeline.fail_step(str(e))
                timeline.finish()
                raise SystemExit(1)

        # Refresh task to ensure we have the freshest SSH endpoint/user right before connect
        try:
            task = client.get_task(task.task_id)
        except Exception:
            pass
        # Now we have an up-to-date view, update display
        task_display = self.task_formatter.format_task_display(task)

        # Fresh-resolve endpoint via provider resolver to avoid any stale Task views
        try:
            host, port = client.provider.resolve_ssh_endpoint(task.task_id, node=node)
            try:
                setattr(task, "ssh_host", host)
                setattr(task, "ssh_port", int(port or 22))
            except Exception:
                setattr(task, "ssh_port", 22)
        except Exception:
            # Best-effort; remote operations will still resolve before connecting
            pass

        # Step 2: Connect or execute
        try:
            if command:
                # Close the timeline before emitting remote output to avoid Live collisions
                step_idx = timeline.add_step("Executing remote command", show_bar=False)
                timeline.start_step(step_idx)
                timeline.complete_step()
                timeline.finish()
                client.shell(task.task_id, command=command, node=node, progress_context=None)
            else:
                # Close the timeline before handing terminal control to SSH to prevent overlay
                try:
                    timeline.finish()
                except Exception:
                    pass
                client.shell(task.task_id, node=node, progress_context=None)
        except Exception as e:
            # Show manual connection hint once
            try:
                provider_name = getattr(getattr(client, "config", None), "provider", None) or (
                    os.environ.get("FLOW_PROVIDER") or "mithril"
                )
            except Exception:
                provider_name = os.environ.get("FLOW_PROVIDER", "mithril")
            connection_cmd = ProviderResolver.get_connection_command(provider_name, task)
            if connection_cmd:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn

                warn = _tm_warn.get_color("warning")
                console.print(
                    f"\n[{warn}]Connection failed. You can try connecting manually with:[/{warn}]"
                )
                console.print(f"  {connection_cmd}\n")
            # If the error carries a request/correlation ID, include it in the failure line
            try:
                req_id = getattr(e, "request_id", None)
                if req_id:
                    timeline.fail_step(f"{str(e)}\nRequest ID: {req_id}")
                else:
                    timeline.fail_step(str(e))
            except Exception:
                timeline.fail_step(str(e))
            timeline.finish()
            raise

        # Show next actions after SSH session ends
        if not command:  # Only show after interactive sessions
            task_ref = task.name or task.task_id
            self.show_next_actions(
                [
                    f"View logs: [accent]flow logs {task_ref} --follow[/accent]",
                    f"Check status: [accent]flow status {task_ref}[/accent]",
                    f"Run nvidia-smi: [accent]flow ssh {task_ref} -c 'nvidia-smi'[/accent]",
                ]
            )
        # Finish timeline
        timeline.finish()

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--command",
            "-c",
            help="Command to run on remote host (deprecated; prefer trailing command after --)",
            hidden=True,
        )
        @click.option(
            "--node", type=int, default=0, help="Node index for multi-instance tasks (default: 0)"
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed help and examples")
        # @demo_aware_command()
        @click.argument("remote_cmd", nargs=-1)
        def ssh(
            task_identifier: str | None,
            command: str | None,
            node: int,
            verbose: bool,
            remote_cmd: tuple[str, ...],
        ):
            """SSH to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow ssh                    # Interactive task selector
                flow ssh my-training        # Connect by name
                flow ssh task-abc123        # Connect by ID
                flow ssh task -c 'nvidia-smi'           # Run command remotely (flag)
                flow ssh task -- nvidia-smi             # Run command remotely (after --)

            Use 'flow ssh --verbose' for troubleshooting and advanced examples.
            """
            if verbose:
                console.print("\n[bold]Advanced SSH Usage:[/bold]\n")
                console.print("Multi-instance tasks:")
                console.print("  flow ssh distributed-job --node 1    # Connect to worker node")
                console.print(
                    "  flow ssh task -c 'hostname' --node 2 # Run command on specific node\n"
                )

                console.print("File transfer:")
                console.print("  scp file.py $(flow ssh task -c 'echo $USER@$HOSTNAME'):~/")
                console.print(
                    "  rsync -av ./data/ $(flow ssh task -c 'echo $USER@$HOSTNAME'):/data/\n"
                )

                console.print("Port forwarding:")
                console.print(
                    "  ssh -L 8888:localhost:8888 $(flow ssh task -c 'echo $USER@$HOSTNAME')"
                )
                console.print(
                    "  ssh -L 6006:localhost:6006 $(flow ssh task -c 'echo $USER@$HOSTNAME')  # TensorBoard\n"
                )

                console.print("Monitoring:")
                console.print("  flow ssh task -c 'watch -n1 nvidia-smi'    # GPU usage")
                console.print("  flow ssh task -c 'htop'                     # System resources")
                console.print("  flow ssh task -c 'tail -f output.log'       # Stream logs\n")

                console.print("Troubleshooting:")
                console.print("  • No SSH info? Wait 2-5 minutes for instance provisioning")
                console.print("  • Permission denied? Run: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Connection refused? Check: flow health --task <name>")
                console.print("  • Task terminated? Check: flow status <name>\n")
                return

            # If a trailing command was provided after '--', prefer it over -c
            # but guard against both being set to avoid ambiguity.
            if remote_cmd:
                if command:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err3

                    err_color = _tm_err3.get_color("error")
                    console.print(
                        f"[{err_color}]Specify either -c/--command or a trailing command after '--', not both[/{err_color}]"
                    )
                    return
                # Reconstruct the remote command string with safe quoting
                try:
                    command = shlex.join(remote_cmd)
                except Exception:
                    command = " ".join(remote_cmd)

            # Selection support (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    err_color = _tm_err.get_color("error")
                    console.print(f"[{err_color}]{err}[/{err_color}]")
                    return
                if ids is not None:
                    if len(ids) != 1:
                        from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                        err_color = _tm_err2.get_color("error")
                        console.print(
                            f"[{err_color}]Selection must resolve to exactly one task for ssh[/{err_color}]"
                        )
                        return
                    task_identifier = ids[0]

            self._execute(task_identifier, command, node)

        return ssh

    def _execute(self, task_identifier: str | None, command: str | None, node: int = 0) -> None:
        """Execute SSH connection or command."""
        # For non-interactive commands, use standard flow
        if command:
            self.execute_with_selection(task_identifier, command=command, node=node)
            return

        # Delegate to selection without pre-animations; the timeline inside execute_on_task owns the UX
        self.execute_with_selection(
            task_identifier,
            command=command,
            node=node,
        )


# Export command instance
command = SSHCommand()
