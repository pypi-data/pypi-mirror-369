#!/usr/bin/env python3
"""
Inspect a Flow task's SSH address resolution across layers.

Usage:
  python3 tools/ssh_task_inspect.py <task-name-or-id>

Prints:
  - Task view (cached resolver): ssh_host/ssh_port
  - Fresh provider.get_task(): ssh_host/ssh_port and instance IDs
  - API /v2/spot/bids and /v2/instances: instance statuses and ssh_destination
"""
from __future__ import annotations

import json
import sys

from flow.api.client import Flow
from flow.cli.utils.task_resolver import resolve_task_identifier


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 tools/ssh_task_inspect.py <task-name-or-id>")
        return 2

    ident = sys.argv[1]
    flow = Flow()

    # Resolver view
    task, err = resolve_task_identifier(flow, ident)
    if err or not task:
        print("[task] resolve failed:", err or "not found")
        return 1
    print(f"[task] id={task.task_id} name={getattr(task,'name','')}")
    print(f"[task] ssh_host={getattr(task,'ssh_host',None)} ssh_port={getattr(task,'ssh_port',22)}")

    # Fresh provider view
    try:
        fresh = flow.get_task(task.task_id)
        print(f"[fresh.get_task] ssh_host={fresh.ssh_host} ssh_port={fresh.ssh_port}")
        print(f"[fresh.get_task] instances={fresh.instances}")
        print(f"[resolver] host={fresh.ssh_host} port={fresh.ssh_port}")
    except Exception as e:
        print("[fresh.get_task] error:", e)
        fresh = None

    # Resolver view
    try:
        host, port = flow.provider.resolve_ssh_endpoint(task.task_id)
        print(f"[resolver] host={host} port={port}")
    except Exception as e:
        print("[resolver] error:", e)

    # API views
    http = flow.provider.http
    proj = None
    try:
        proj = flow.provider._get_project_id()
    except Exception:
        pass

    try:
        bids = http.request(method="GET", url="/v2/spot/bids", params={"id": task.task_id, **({"project": proj} if proj else {})})
        if isinstance(bids, dict):
            data = bids.get("data", bids)
        else:
            data = bids
        bid = data[0] if isinstance(data, list) and data else None
        print("[api.bids] instances:")
        if isinstance(bid, dict):
            for i, inst in enumerate(bid.get("instances", []) or []):
                if isinstance(inst, dict):
                    print(f"  - #{i} id={inst.get('fid') or inst.get('id')} status={inst.get('status')} ssh_destination={inst.get('ssh_destination')}")
                else:
                    print(f"  - #{i} id={inst}")
    except Exception as e:
        print("[api.bids] error:", e)

    # For each instance id (most recent first), show instance doc ssh_destination
    if fresh and fresh.instances:
        for inst_id in reversed(fresh.instances[-3:]):  # last few
            try:
                inst = http.request(method="GET", url="/v2/instances", params={"fid": inst_id, **({"project": proj} if proj else {})})
                if isinstance(inst, dict):
                    docs = inst.get("data", inst)
                else:
                    docs = inst
                if isinstance(docs, list) and docs:
                    doc = docs[0]
                elif isinstance(docs, dict):
                    doc = docs
                else:
                    doc = None
                if isinstance(doc, dict):
                    print(f"[api.instances] id={inst_id} status={doc.get('status')} ssh_destination={doc.get('ssh_destination')} public_ip={doc.get('public_ip')}")
            except Exception as e:
                print(f"[api.instances] id={inst_id} error: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


