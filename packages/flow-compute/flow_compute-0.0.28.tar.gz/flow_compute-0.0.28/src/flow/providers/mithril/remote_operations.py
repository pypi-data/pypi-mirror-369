"""Mithril-specific implementation of remote operations via SSH.

SSH-based remote operations for Mithril tasks implementing ``IRemoteOperations``.
"""

import logging
import subprocess
import time
from pathlib import Path
import shlex
from typing import TYPE_CHECKING
import uuid as _uuid

from flow.core.provider_interfaces import IRemoteOperations
from flow.errors import FlowError
from flow.providers.mithril.core.constants import (
    EXPECTED_PROVISION_MINUTES,
    SSH_QUICK_RETRY_ATTEMPTS,
    SSH_QUICK_RETRY_MAX_SECONDS,
    SSH_READY_WAIT_SECONDS,
)
from flow.api.ssh_utils import SSHNotReadyError, wait_for_task_ssh_info
from flow.core.ssh_stack import SshStack

if TYPE_CHECKING:
    from flow.providers.mithril.provider import MithrilProvider

logger = logging.getLogger(__name__)


class RemoteExecutionError(FlowError):
    """Raised when remote command execution fails."""

    pass


class TaskNotFoundError(FlowError):
    """Raised when task cannot be found."""

    pass


class MithrilRemoteOperations(IRemoteOperations):
    """Mithril remote operations via SSH."""

    def __init__(self, provider: "MithrilProvider"):
        """Initialize with provider reference.

        Args:
            provider: Mithril provider instance for task access
        """
        self.provider = provider

    # --- Formatting helpers -------------------------------------------------
    def _human_age(self, seconds: float | None) -> str | None:
        """Return compact human age like '1h 32m' or '7d'."""
        try:
            if seconds is None or seconds < 0:
                return None
            # Cap to 7 days for sanity; beyond this isn't actionable for SSH
            seconds = max(0.0, min(seconds, 7 * 24 * 3600))
            minutes = int(seconds // 60)
            if minutes < 1:
                return "<1m"
            hours, mins = divmod(minutes, 60)
            if hours < 24:
                return f"{hours}h {mins}m" if hours else f"{mins}m"
            days, rem = divmod(hours, 24)
            return f"{days}d" if rem == 0 else f"{days}d {rem}h"
        except Exception:
            return None

    # Correlation/Request ID helpers
    def _new_request_id(self, operation: str) -> str:
        """Generate a client-side correlation ID for non-HTTP operations.

        The ID is attached to errors and surfaced by the CLI as a Request ID
        to aid debugging and support even when no server-side request exists.
        """
        try:
            return f"{operation}-{_uuid.uuid4()}"
        except Exception:
            # Fallback to a timestamp-based ID if UUID generation fails
            return f"{operation}-{int(time.time()*1000)}"

    def _make_error(
        self, message: str, request_id: str, suggestions: list | None = None
    ) -> RemoteExecutionError:
        """Create a RemoteExecutionError with an attached request_id."""
        err = RemoteExecutionError(message, suggestions=suggestions)  # type: ignore[arg-type]
        try:
            setattr(err, "request_id", request_id)
        except Exception:
            # Best-effort; error still raised without correlation if setting fails
            pass
        return err

    def execute_command(self, task_id: str, command: str, timeout: int | None = None) -> str:
        """Execute command on remote task via SSH.

        Args:
            task_id: Task identifier
            command: Command to execute
            timeout: Optional timeout in seconds

        Returns:
            Command output (stdout)

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Command failed
            TimeoutError: Command timed out
        """
        request_id = self._new_request_id("ssh-exec")
        task = self.provider.get_task(task_id)

        # Always fresh-resolve endpoint to avoid stale task views
        try:
            host, port = self.provider.resolve_ssh_endpoint(task_id)
            setattr(task, "ssh_host", host)
            try:
                setattr(task, "ssh_port", int(port or 22))
            except Exception:
                setattr(task, "ssh_port", 22)
        except Exception:
            pass

        # First ensure task has SSH info using shared utility
        try:
            # For commands, use a shorter timeout than interactive SSH
            task = wait_for_task_ssh_info(
                task=task,
                provider=self.provider,
                timeout=SSH_QUICK_RETRY_MAX_SECONDS * 2,  # Give it a bit more time than quick retries
                show_progress=False,
            )
        except SSHNotReadyError as e:
            raise self._make_error(
                f"No SSH access for task {task_id}: {str(e)}",
                request_id,
                suggestions=e.suggestions,
            ) from e

        # Ensure SSH key manager has project scoping before resolution to avoid
        # provider API validation errors when listing keys.
        try:
            if getattr(self.provider, "ssh_key_manager", None) is not None and getattr(
                self.provider.ssh_key_manager, "project_id", None
            ) is None:
                self.provider.ssh_key_manager.project_id = self.provider.project_id
        except Exception:
            pass

        # Get the SSH key path for this task
        ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
        if not ssh_key_path:
            raise self._make_error(f"SSH key resolution failed: {error_msg}", request_id)

        # Now check if SSH service is ready (connection test)
        if not SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=getattr(task, "ssh_host"),
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
        ):
            # SSH info exists but service not ready - do quick retries
            start_time = time.time()
            for attempt in range(SSH_QUICK_RETRY_ATTEMPTS):
                elapsed = time.time() - start_time
                if elapsed > SSH_QUICK_RETRY_MAX_SECONDS:
                    break

                time.sleep(2 * (attempt + 1))  # Exponential backoff: 2, 4, 6, 8, 10 seconds
                if SshStack.is_ssh_ready(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=getattr(task, "ssh_host"),
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                ):
                    break
            else:
                # Still not ready after quick retries
                # Check instance age to provide better messaging
                # Compute a sane instance age; guard against bogus timestamps
                try:
                    instance_age_seconds = float(task.instance_age_seconds or 0)
                except Exception:
                    instance_age_seconds = 0.0
                # Cap to 7 days to avoid absurd numbers from bad metadata
                capped_seconds = max(0.0, min(instance_age_seconds, 7 * 24 * 3600))
                instance_age_minutes = int(capped_seconds // 60)

                # Check if we have instance status information
                instance_status = task.instance_status if hasattr(task, "instance_status") else None

                if instance_status == "STATUS_STARTING":
                    # Instance is explicitly in starting state
                    raise self._make_error(
                        "Instance is starting up. SSH will be available once startup completes. "
                        "Please try again in a moment or check 'flow status' for current state.",
                        request_id,
                    )
                elif instance_age_minutes < EXPECTED_PROVISION_MINUTES:
                    # Instance is still within normal startup time
                    raise self._make_error(
                        f"Instance is still starting up ({instance_age_minutes} minutes elapsed). "
                        f"SSH startup can take up to {EXPECTED_PROVISION_MINUTES} minutes. "
                        f"Please try again in a moment.",
                        request_id,
                    )
                else:
                    # Instance is older or age unknown - use generic message
                    raise self._make_error(
                        f"SSH service on {task.ssh_host} is not responding. "
                        f"The instance may still be starting up (can take up to {EXPECTED_PROVISION_MINUTES} minutes). "
                        f"Please try again in a moment.",
                        request_id,
                    )

        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=getattr(task, "ssh_host"),
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
            remote_command=command,
        )

        if timeout:
            ssh_cmd = ["timeout", str(timeout)] + ssh_cmd

        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Check for common SSH errors
                stderr = result.stderr.lower()
                if "connection closed" in stderr or "connection reset" in stderr:
                    raise self._make_error(
                        "SSH connection was closed. The instance may still be starting up. "
                        "Please wait a moment and try again.",
                        request_id,
                    )
                raise self._make_error(f"Command failed: {result.stderr}", request_id)
            return result.stdout
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out after {timeout} seconds") from e
        except Exception as e:
            raise self._make_error(f"SSH execution failed: {str(e)}", request_id) from e

    def retrieve_file(self, task_id: str, remote_path: str) -> bytes:
        """Retrieve file from remote task via SSH.

        Args:
            task_id: Task identifier
            remote_path: Path to file on remote system

        Returns:
            File contents as bytes

        Raises:
            TaskNotFoundError: Task doesn't exist
            FileNotFoundError: Remote file doesn't exist
            RemoteExecutionError: Retrieval failed
        """
        # Use SSH cat to retrieve file
        try:
            # Quote remote path to prevent remote shell injection
            safe_remote_path = shlex.quote(str(remote_path))
            output = self.execute_command(task_id, f"cat {safe_remote_path}")
            return output.encode("utf-8")
        except RemoteExecutionError as e:
            if "No such file" in str(e) or "cannot open" in str(e):
                raise FileNotFoundError(f"Remote file not found: {remote_path}") from e
            raise

    def open_shell(
        self,
        task_id: str,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
    ) -> None:
        """Open interactive SSH shell to remote task.

        Args:
            task_id: Task identifier
            command: Optional command to execute

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Shell access failed
        """
        # Obtain task and ssh key info from provider (no CLI cache coupling)
        task = self.provider.get_task(task_id)
        if not task:
            raise RemoteExecutionError(f"No SSH access for task {task_id}")

        # Always fresh-resolve the current endpoint to avoid stale Task views
        try:
            host, port = self.provider.resolve_ssh_endpoint(task_id, node=node)
            setattr(task, "ssh_host", host)
            try:
                setattr(task, "ssh_port", int(port or 22))
            except Exception:
                setattr(task, "ssh_port", 22)
        except Exception as e:
            # Fall back to existing task state if resolver fails, but do not proceed without host
            if not getattr(task, "ssh_host", None):
                raise RemoteExecutionError(str(e))

        # Select instance for multi-node if requested
        if node is not None and getattr(task, "instances", None):
            try:
                instances = self.provider.get_task_instances(task_id)
                if node < 0 or node >= len(instances):
                    raise RemoteExecutionError(
                        f"Invalid node index {node}; task has {len(instances)} nodes"
                    )
                selected = instances[node]
                if getattr(selected, "ssh_host", None):
                    setattr(task, "ssh_host", selected.ssh_host)
                # Keep port/user defaults from task if instance lacks them
            except Exception as e:
                raise RemoteExecutionError(str(e))

        # Get the SSH key path for this task
        ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
        if not ssh_key_path:
            raise RemoteExecutionError(f"SSH key resolution failed: {error_msg}")

        # Build a scoped cache key for recent-success heuristics
        recent_success = False
        cache_key = None
        try:
            try:
                project_id = self.provider.project_id
            except Exception:
                project_id = "default"
            cache_key = (
                project_id,
                task_id,
                int(node or -1),
                getattr(task, "ssh_host"),
                int(getattr(task, "ssh_port", 22)),
            )
            last_cache = getattr(self.provider, "_ssh_last_success", None)
            if last_cache and cache_key in last_cache:
                ts = float(last_cache[cache_key])
                recent_success = (time.time() - ts) < 60.0  # 60s TTL
        except Exception:
            recent_success = False

        # Check if SSH is ready first (fast path)
        request_id = self._new_request_id("ssh-connect")
        try:
            if __import__("os").environ.get("FLOW_SSH_DEBUG") == "1":
                logger.debug(
                    "SSH readiness probe for %s host=%s port=%s key=%s",
                    task_id,
                    getattr(task, "ssh_host"),
                    getattr(task, "ssh_port", 22),
                    str(ssh_key_path),
                )
        except Exception:
            pass
        # Perform a very fast probe first to avoid 5s pre-wait latency
        # Allow tuning via env var FLOW_SSH_PROBE_TIMEOUT (seconds)
        ssh_is_ready = SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=getattr(task, "ssh_host"),
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
        )

        # Immediate connect when explicitly requested or when TCP port is open
        try:
            import os as _os

            if command is None and (
                _os.environ.get("FLOW_SSH_FAST") == "1"
                or SshStack.tcp_port_open(getattr(task, "ssh_host"), getattr(task, "ssh_port", 22))
            ):
                ssh_cmd = SshStack.build_ssh_command(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=getattr(task, "ssh_host"),
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                )
                if _os.environ.get("FLOW_SSH_DEBUG") == "1":
                    logger.debug("SSH fast-path exec argv: %s", " ".join(ssh_cmd))
                subprocess.run(ssh_cmd)
                return
        except Exception:
            pass

        # Update progress message (timeline/animated-aware if provided)
        if progress_context and hasattr(progress_context, "update_message"):
            try:
                progress_context.update_message(
                    "SSH ready, connecting..." if ssh_is_ready else "Waiting for SSH to be ready..."
                )
            except Exception:
                pass

        # Enhanced SSH waiting delegated to core stack (skip when we recently succeeded)
        if not ssh_is_ready and not recent_success:
            start_time = time.time()
            timeout = SSH_READY_WAIT_SECONDS
            attempts = 0
            # Use shorter sleep/backoff to reduce the post-bar latency before connecting
            while time.time() - start_time < timeout:
                if SshStack.is_ssh_ready(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=getattr(task, "ssh_host"),
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                ):
                    break
                # Start with 200ms and grow to 2s maximum
                wait_time = min(0.2 * (1 + attempts), 2.0)
                time.sleep(wait_time)
                attempts += 1
            else:
                # Fallback: attempt direct SSH once (mirrors user's manual success path)
                try:
                    ssh_cmd = SshStack.build_ssh_command(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=getattr(task, "ssh_host"),
                        port=getattr(task, "ssh_port", 22),
                        key_path=Path(ssh_key_path),
                    )
                    if __import__("os").environ.get("FLOW_SSH_DEBUG") == "1":
                        logger.debug("SSH fallback exec argv: %s", " ".join(ssh_cmd))
                    # Try an immediate interactive connect; user can Ctrl+C if still not ready
                    subprocess.run(ssh_cmd)
                    return
                except Exception:
                    pass
                raise self._make_error("SSH connection timed out", request_id)

        # Prime SSH ControlMaster in the background to eliminate post-bar latency
        try:
            master_cmd = SshStack.build_ssh_command(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=getattr(task, "ssh_host"),
                port=getattr(task, "ssh_port", 22),
                key_path=Path(ssh_key_path),
                prefix_args=["-MNf", "-o", "ConnectTimeout=4", "-o", "ConnectionAttempts=1"],
            )
            # Suppress output; if it fails we'll fall back to normal connect
            with open("/dev/null", "w") as _null:
                subprocess.Popen(master_cmd, stdout=_null, stderr=_null)
        except Exception:
            pass

        # Now run the actual SSH command
        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=getattr(task, "ssh_host"),
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
        )
        try:
            if __import__("os").environ.get("FLOW_SSH_DEBUG") == "1":
                logger.debug("SSH exec argv: %s", " ".join(ssh_cmd))
        except Exception:
            pass
        if command:
            ssh_cmd.append(command)

        try:
            # For commands, capture output; for interactive shell, run normally
            if command:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    if result.stdout:
                        print(result.stdout, end="")
                    # Mark recent success to speed subsequent attaches
                    try:
                        if cache_key is not None:
                            cache = getattr(self.provider, "_ssh_last_success", None)
                            if cache is None:
                                cache = {}
                                setattr(self.provider, "_ssh_last_success", cache)
                            cache[cache_key] = time.time()
                    except Exception:
                        pass
                    return
            else:
                # Interactive shell - stop animation before taking over terminal
                # Only stop if we haven't already stopped it during SSH wait
                if progress_context and hasattr(progress_context, "_active"):
                    # Check if the progress context is still active
                    # AnimatedEllipsisProgress should have this attribute
                    if progress_context._active:
                        progress_context.__exit__(None, None, None)

                # Run SSH without capturing (takes over terminal)
                result = subprocess.run(ssh_cmd)
                # Mark recent success to speed subsequent attaches
                try:
                    if cache_key is not None:
                        cache = getattr(self.provider, "_ssh_last_success", None)
                        if cache is None:
                            cache = {}
                            setattr(self.provider, "_ssh_last_success", cache)
                        cache[cache_key] = time.time()
                except Exception:
                    pass
                return

            # Handle errors for command execution
            if result.returncode != 0:
                stderr = result.stderr.lower()
                # Provide helpful error messages based on SSH failure type
                if "connection timed out" in stderr or "operation timed out" in stderr:
                    # Check if instance was recently created
                    if hasattr(task, "created_at") and task.created_at:
                        from datetime import datetime, timezone

                        elapsed = task.instance_age_seconds or 0
                        if elapsed < EXPECTED_PROVISION_MINUTES * 60:
                            raise self._make_error(
                                f"SSH connection timed out. Instance may still be provisioning "
                                f"(elapsed: {elapsed / 60:.1f} minutes). Mithril instances can take up to "
                                f"{EXPECTED_PROVISION_MINUTES} minutes to become fully available. Please try again later.",
                                request_id,
                            )
                    # Bust recent-success on failure
                    try:
                        if cache_key is not None:
                            cache = getattr(self.provider, "_ssh_last_success", None)
                            if cache and cache_key in cache:
                                cache.pop(cache_key, None)
                    except Exception:
                        pass
                    raise self._make_error(
                        "SSH connection timed out. Possible causes:\n"
                        f"  - Instance is still provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)\n"
                        "  - Network connectivity issues\n"
                        "  - Security group/firewall blocking SSH (port 22)",
                        request_id,
                    )
            elif "connection refused" in stderr:
                # Bust recent-success on failure
                try:
                    if cache_key is not None:
                        cache = getattr(self.provider, "_ssh_last_success", None)
                        if cache and cache_key in cache:
                            cache.pop(cache_key, None)
                except Exception:
                    pass
                raise self._make_error(
                    "SSH connection refused. The instance is reachable but SSH service "
                    "is not ready yet. Please wait a few more minutes and try again.",
                    request_id,
                )
            elif "connection reset by peer" in stderr or "kex_exchange_identification" in stderr:
                # Bust recent-success on failure
                try:
                    if cache_key is not None:
                        cache = getattr(self.provider, "_ssh_last_success", None)
                        if cache and cache_key in cache:
                            cache.pop(cache_key, None)
                except Exception:
                    pass
                raise self._make_error(
                    "SSH connection was reset. The SSH service is still initializing.\n"
                    "This typically happens during the first few minutes after instance creation.\n"
                    "Please wait 1-2 minutes and try again.",
                    request_id,
                )
            elif "permission denied" in stderr:
                # This shouldn't happen now that we resolve SSH keys, but keep for safety
                error_msg = "SSH authentication failed despite key resolution.\n\n"
                error_msg += (
                    "This is unexpected - the SSH key was found but authentication failed.\n"
                )
                error_msg += "Possible causes:\n"
                error_msg += "  1. The private key file permissions are too open (should be 600)\n"
                error_msg += "  2. The key file is corrupted or invalid\n"
                error_msg += "  3. The instance was created with a different key than expected\n\n"
                error_msg += "Debug information:\n"
                error_msg += f"  - SSH command: {' '.join(ssh_cmd[:6])}...\n"
                error_msg += f"  - Task ID: {task_id}\n"
                # Extract SSH key path from command if available
                if "-i" in ssh_cmd:
                    key_idx = ssh_cmd.index("-i") + 1
                    if key_idx < len(ssh_cmd):
                        error_msg += f"  - Using SSH key: {ssh_cmd[key_idx]}\n"

                raise self._make_error(error_msg, request_id)
            else:
                raise self._make_error(f"SSH connection failed: {result.stderr}", request_id)
        except RemoteExecutionError:
            raise
        except Exception as e:
            raise self._make_error(f"SSH shell failed: {str(e)}", request_id) from e

