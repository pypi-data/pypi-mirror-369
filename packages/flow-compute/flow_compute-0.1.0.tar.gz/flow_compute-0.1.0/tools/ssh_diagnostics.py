#!/usr/bin/env python3
"""
SSH diagnostics for Flow/Mithril.

Usage:
  python3 tools/ssh_diagnostics.py <task-name-or-id> [--project PROJ] [--api-url URL] [--key ~/.flow/keys/<key>] [--run-ssh]

This script probes multiple layers to discover the public IP used for SSH and
verifies connectivity:
  1) Task object view (task.ssh_host / ssh_port)
  2) Direct API: /v2/spot/bids?id=<task_id>&project=<proj>
  3) Direct API: /v2/instances?fid=<instance_id>&project=<proj>
  4) Candidate IP extraction across common fields; TCP:22 probing
  5) Optional: direct ssh -i <key> 'echo OK' to the best candidate

It also prints curl commands you can run directly.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any


def add_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


add_src_to_path()

from flow.api.client import Flow  # noqa: E402
from flow.cli.utils.task_resolver import resolve_task_identifier  # noqa: E402


def tcp_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_sec)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def extract_ipv4_candidates(obj: Any) -> list[str]:
    candidates: list[str] = []

    def add(val: Any) -> None:
        import re

        if isinstance(val, str) and re.fullmatch(r"\d+\.\d+\.\d+\.\d+", val):
            if val not in candidates:
                candidates.append(val)
        elif isinstance(val, list):
            for v in val:
                add(v)
        elif isinstance(val, dict):
            for v in val.values():
                add(v)

    add(obj)
    return candidates


def main() -> int:
    ap = argparse.ArgumentParser(description="Flow SSH diagnostics")
    ap.add_argument("task", help="Task name or ID")
    ap.add_argument("--project", dest="project", default=None)
    ap.add_argument("--api-url", dest="api_url", default=os.getenv("MITHRIL_API_URL", "https://api.mithril.ai"))
    ap.add_argument("--key", dest="key_path", default=None, help="Explicit private key path")
    ap.add_argument("--run-ssh", dest="run_ssh", action="store_true", help="Attempt ssh echo OK")
    args = ap.parse_args()

    flow = Flow()
    # Resolve task
    task, err = resolve_task_identifier(flow, args.task)
    if err or not task:
        print(f"[!] Failed to resolve task: {err or 'not found'}")
        return 2
    print(f"[task] id={task.task_id} name={getattr(task, 'name', '')}")
    print(f"[task] ssh_host={getattr(task, 'ssh_host', None)} ssh_port={getattr(task, 'ssh_port', 22)}")

    provider = flow.provider
    http = getattr(provider, "http", None)
    if http is None:
        print("[!] Provider has no HTTP client")
        return 2

    # Discover project id for scoping
    try:
        project_id = provider._get_project_id()  # type: ignore[attr-defined]
    except Exception:
        project_id = None
    if args.project:
        project_id = args.project
    print(f"[ctx] api_url={getattr(http, 'base_url', args.api_url)} project={project_id}")

    # Curl commands to reproduce
    task_id = task.task_id
    proj_q = f"&project={project_id}" if project_id else ""
    print("\n# curl reproduction (assumes MITHRIL_API_KEY in env)")
    print(f"curl -sS -H 'Authorization: Bearer $MITHRIL_API_KEY' '{args.api_url}/v2/spot/bids?id={task_id}{proj_q}' | jq . | less")
    print("# After selecting an instance ID (inst_X), run:")
    print(f"curl -sS -H 'Authorization: Bearer $MITHRIL_API_KEY' '{args.api_url}/v2/instances?fid=inst_X{proj_q}' | jq . | less\n")

    # API: bids
    try:
        bid_resp = http.request(method="GET", url="/v2/spot/bids", params={"id": task_id, **({"project": project_id} if project_id else {})})
        bids = bid_resp.get("data", bid_resp) if isinstance(bid_resp, dict) else bid_resp
        bid = bids[0] if isinstance(bids, list) and bids else None
    except Exception as e:
        print(f"[!] GET /v2/spot/bids failed: {e}")
        bid = None

    inst_id = None
    if isinstance(bid, dict):
        insts = bid.get("instances", []) or []
        print(f"[bids] instances={len(insts)}")
        for i, inst in enumerate(insts):
            if isinstance(inst, dict):
                print(f"  - #{i} id={inst.get('fid') or inst.get('id')} status={inst.get('status')} public_ip={inst.get('public_ip')}")
        if insts:
            last = insts[-1]
            if isinstance(last, dict):
                inst_id = last.get("fid") or last.get("id")

    # API: instance
    instance_doc = None
    if inst_id:
        try:
            inst_resp = http.request(method="GET", url="/v2/instances", params={"fid": inst_id, **({"project": project_id} if project_id else {})})
            items = inst_resp.get("data", inst_resp) if isinstance(inst_resp, dict) else inst_resp
            instance_doc = items[0] if isinstance(items, list) and items else None
        except Exception as e:
            print(f"[!] GET /v2/instances failed: {e}")

    # Candidate IPs from both docs and task
    candidates = []
    if instance_doc:
        candidates += extract_ipv4_candidates(instance_doc)
    if isinstance(bid, dict):
        candidates += extract_ipv4_candidates(bid.get("instances", []))
    if getattr(task, "ssh_host", None):
        candidates.append(task.ssh_host)
    # De-dup
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    candidates = uniq

    print("[candidates]", candidates or "<none>")

    # Probe TCP 22
    open_hosts = []
    port = int(getattr(task, "ssh_port", 22) or 22)
    for ip in candidates:
        is_open = tcp_open(ip, port)
        print(f"  - {ip}:{port} -> {'open' if is_open else 'closed'}")
        if is_open:
            open_hosts.append(ip)

    # Resolve SSH key
    key_path = args.key_path
    if not key_path:
        key, err = provider.get_task_ssh_connection_info(task.task_id)
        if key:
            key_path = str(key)
        else:
            print(f"[!] key resolution error: {err}")

    if key_path:
        print(f"[key] {key_path}")

    # Optional ssh test
    if args.run_ssh and key_path and open_hosts:
        target = open_hosts[0]
        argv = [
            "ssh",
            "-p",
            str(port),
            "-i",
            key_path,
            "-o",
            "IdentitiesOnly=yes",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"{getattr(task, 'ssh_user', 'ubuntu')}@{target}",
            "echo OK",
        ]
        print("[ssh] exec:", " ".join(argv))
        try:
            subprocess.run(argv, check=False)
        except KeyboardInterrupt:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


