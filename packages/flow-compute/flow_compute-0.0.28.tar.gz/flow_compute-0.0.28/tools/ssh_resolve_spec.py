#!/usr/bin/env python3
"""
Spec-aligned SSH resolver diagnostics for Mithril bids/instances.

- Pages /v2/spot/bids?project=<proj>&limit=100&sort_by=created_at&sort_dir=desc
  and filters locally by fid == <task_id>.
- Prints the bid.instances list as seen from the API.
- For each instance fid, fetches details via:
  1) /v2/spot/instances?id=<instance_fid>
  2) fallback: /v2/instances?fid=<instance_fid>&project=<proj>
- Extracts ssh_destination/public_ip, probes TCP:22, and proposes a selected host.

Usage:
  python3 tools/ssh_resolve_spec.py <task-name-or-id>
"""
from __future__ import annotations

import argparse
import json
import socket
from typing import Any

from flow.api.client import Flow
from flow.cli.utils.task_resolver import resolve_task_identifier


def tcp_open(host: str, port: int = 22, timeout: float = 2.0) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        r = sock.connect_ex((host, port))
        sock.close()
        return r == 0
    except Exception:
        return False


def get_data(obj: Any) -> Any:
    return obj.get("data", obj) if isinstance(obj, dict) else obj


def page_bids(http, project_id: str, target_fid: str) -> dict | None:
    next_cursor = None
    for _ in range(5):
        params = {
            "project": project_id,
            "limit": "100",
            "sort_by": "created_at",
            "sort_dir": "desc",
        }
        if next_cursor:
            params["next_cursor"] = next_cursor
        resp = http.request(method="GET", url="/v2/spot/bids", params=params)
        data = get_data(resp)
        if isinstance(data, list):
            for bid in data:
                if isinstance(bid, dict) and (bid.get("fid") or bid.get("id")) == target_fid:
                    return bid
        next_cursor = resp.get("next_cursor") if isinstance(resp, dict) else None
        if not next_cursor:
            break
    return None


def fetch_instance(http, project_id: str, inst_fid: str) -> dict | None:
    try:
        r = http.request(method="GET", url="/v2/spot/instances", params={"id": inst_fid})
        data = get_data(r)
        if isinstance(data, list) and data:
            return data[0]
    except Exception:
        pass
    try:
        r = http.request(
            method="GET",
            url="/v2/instances",
            params={"fid": inst_fid, "project": project_id},
        )
        data = get_data(r)
        if isinstance(data, list) and data:
            return data[0]
    except Exception:
        pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="Task name or fid (bid_...) to inspect")
    args = ap.parse_args()

    flow = Flow()
    task, err = resolve_task_identifier(flow, args.task)
    if err or not task:
        print("[task] resolve failed:", err or "not found")
        return 1

    project_id = None
    try:
        project_id = flow.provider._get_project_id()
    except Exception:
        pass
    if not project_id:
        print("[error] missing project context")
        return 2

    print(f"[task] id={task.task_id} name={getattr(task,'name','')}")

    http = flow.provider.http
    bid = page_bids(http, project_id, task.task_id)
    if not isinstance(bid, dict):
        print("[bids] not found via spec paging")
        return 3

    insts = bid.get("instances", []) or []
    print("[bid.instances] count=", len(insts), insts)

    candidates: list[tuple[str, int]] = []
    for ent in insts[::-1]:  # newest first if ordered
        inst_fid = ent.get("fid") or ent.get("id") if isinstance(ent, dict) else str(ent)
        if not inst_fid:
            continue
        doc = fetch_instance(http, project_id, inst_fid)
        status = doc.get("status") if isinstance(doc, dict) else None
        ssh_dest = doc.get("ssh_destination") if isinstance(doc, dict) else None
        public_ip = doc.get("public_ip") if isinstance(doc, dict) else None
        created_at = doc.get("created_at") if isinstance(doc, dict) else None
        print(f"[instance] {inst_fid} status={status} ssh_destination={ssh_dest} public_ip={public_ip} created_at={created_at}")
        host: str | None = None
        port = 22
        if ssh_dest and isinstance(ssh_dest, str):
            parts = ssh_dest.split(":")
            host = parts[0]
            if len(parts) > 1:
                try:
                    port = int(parts[1])
                except Exception:
                    port = 22
        elif public_ip:
            host = public_ip
        if host and (host, port) not in candidates:
            candidates.append((host, port))

    print("[candidates]", candidates or "<none>")
    for h, p in candidates:
        ok = tcp_open(h, p)
        print(f"[probe] {h}:{p} -> {'open' if ok else 'closed'}")
    sel = next(((h, p) for h, p in candidates if tcp_open(h, p)), candidates[0] if candidates else (None, None))
    print("[selected]", sel)

    # Show what the provider picks right now
    try:
        fresh = flow.get_task(task.task_id)
        print(f"[provider] ssh_host={fresh.ssh_host} ssh_port={fresh.ssh_port}")
    except Exception as e:
        print("[provider] get_task error:", e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


