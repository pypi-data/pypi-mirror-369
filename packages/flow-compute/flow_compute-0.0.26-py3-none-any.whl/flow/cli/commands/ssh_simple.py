from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

import click

from flow.api.client import Flow
from flow.api.models import Task
from flow.cli.commands.base import BaseCommand


@dataclass
class SimpleSSHOptions:
    key_path: str | None = None
    command: str | None = None


class SimpleSSHCommand(BaseCommand):
    """A minimal, parallel SSH command with zero progress UI.

    Goals:
    - Resolve task by name/ID
    - Resolve private key deterministically (platform key -> local key)
    - Connect immediately when TCP is open; no animated waits
    - Mirror manual CLI behavior: ssh -i <key> -o IdentitiesOnly=yes ubuntu@host
    """

    @property
    def name(self) -> str:
        return "ssh-simple"

    @property
    def help(self) -> str:
        return "Minimal SSH: no timeline; direct connect with resolved key"

    def _resolve_task(self, flow: Flow, identifier: str | None) -> Task:
        if identifier:
            try:
                from flow.cli.utils.task_resolver import resolve_task_identifier as _res

                t, err = _res(flow, identifier)
                if err:
                    raise click.ClickException(err)
                if t is None:
                    raise click.ClickException("Task not found")
                return t
            except Exception as e:
                raise click.ClickException(str(e))
        tasks = flow.list_tasks(limit=20)
        for t in tasks:
            if getattr(t, "ssh_host", None):
                return t
        raise click.ClickException("No SSH-accessible task found. Use: flow ssh-simple <task-name-or-id>")

    def _resolve_private_key(self, flow: Flow, task_id: str, override: str | None) -> str:
        if override:
            return os.path.expanduser(override)
        provider = flow.provider
        key_path, err = provider.get_task_ssh_connection_info(task_id)
        if not key_path:
            raise click.ClickException(f"SSH key resolution failed: {err}")
        return str(key_path)

    def _resolve_fresh_host_port(self, flow: Flow, task_id: str) -> tuple[str, int]:
        """Freshly resolve the current SSH endpoint via provider resolver (authoritative)."""
        try:
            host, port = flow.provider.resolve_ssh_endpoint(task_id)
            return str(host), int(port or 22)
        except Exception as e:
            # Fallback to fresh Task view as a backup
            try:
                fresh = flow.get_task(task_id)
                host = getattr(fresh, "ssh_host", None)
                port = int(getattr(fresh, "ssh_port", 22) or 22)
                if host:
                    return str(host), port
            except Exception:
                pass
            raise click.ClickException(str(e))

    def _build_ssh_argv(self, host: str, user: str, port: int, key_path: str, remote_cmd: str | None) -> list[str]:
        argv = [
            "ssh", 
            "-p",
            str(port or 22),
            "-i",
            key_path,
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"{user or 'ubuntu'}@{host}",
        ]
        if remote_cmd:
            argv.append(remote_cmd)
        return argv

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False)
        @click.option("--key", "key_path", metavar="PATH", help="Explicit private key path")
        @click.option("-c", "command", help="Remote command to run")
        def ssh_simple(task_identifier: str | None, key_path: str | None, command: str | None):
            flow = Flow()
            task = self._resolve_task(flow, task_identifier)
            if not getattr(task, "ssh_host", None):
                try:
                    task = flow.wait_for_ssh(task.task_id, timeout=60, show_progress=False)
                except Exception:
                    pass
            if not getattr(task, "ssh_host", None):
                raise click.ClickException("Task has no SSH host yet. Try again shortly.")

            # Always re-resolve host/port fresh to avoid stale Task objects
            host, port = self._resolve_fresh_host_port(flow, task.task_id)
            key = self._resolve_private_key(flow, task.task_id, key_path)
            argv = self._build_ssh_argv(
                host,
                getattr(task, "ssh_user", "ubuntu"),
                port,
                key,
                command,
            )

            try:
                if command:
                    result = subprocess.run(argv, capture_output=False)
                    if result.returncode != 0:
                        raise click.ClickException(f"Remote command failed with exit {result.returncode}")
                else:
                    subprocess.run(argv, check=False)
            except KeyboardInterrupt:
                return

        return ssh_simple


command = SimpleSSHCommand()


