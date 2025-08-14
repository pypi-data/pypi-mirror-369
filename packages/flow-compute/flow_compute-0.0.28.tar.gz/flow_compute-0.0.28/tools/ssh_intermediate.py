from __future__ import annotations

import argparse
import os
import sys
import subprocess
from pathlib import Path
import stat as _stat

from flow.api.client import Flow
from flow.api.models import Task
from flow.core.ssh_stack import SshStack


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Resolve and connect to a task's SSH endpoint using provider's fresh resolver.\n"
        "Prints the exact ssh command and can optionally execute it.",
    )
    parser.add_argument("task_identifier", help="Task ID or name (prefix allowed)")
    parser.add_argument("--node", type=int, default=None, help="Node index for multi-instance tasks")
    parser.add_argument("--cmd", dest="remote_cmd", default=None, help="Remote command to run")
    parser.add_argument("--connect", action="store_true", help="Execute ssh after printing the command")
    parser.add_argument("--fast", action="store_true", help="Enable fast path (skip wait, connect when TCP is open)")
    parser.add_argument("--debug", action="store_true", help="Enable extra SSH debug logging")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="TCP connect timeout seconds for readiness probe (default: 10)",
    )
    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Print provider metadata, instances and resolution details",
    )
    parser.add_argument(
        "--verify-key-trace",
        action="store_true",
        help="Verify platform→local key mapping, permissions, and provider choice",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit non-zero if key trace verification detects a mismatch",
    )
    return parser.parse_args()


def resolve_task(flow: Flow, identifier: str) -> Task:
    # Try by exact ID first
    try:
        return flow.get_task(identifier)
    except Exception:
        pass

    # Fallback: scan recent tasks and match by exact name or ID prefix
    tasks = flow.list_tasks(limit=50, force_refresh=True)
    for task in tasks:
        if task.name == identifier or task.task_id.startswith(identifier):
            return task
    # Second pass: case-insensitive name match
    for task in tasks:
        if task.name.lower() == identifier.lower():
            return task
    raise SystemExit(f"Task not found for identifier: {identifier}")


def main() -> None:
    args = parse_args()

    # Optional debug/fast env toggles for downstream components
    if args.debug:
        os.environ["FLOW_SSH_DEBUG"] = "1"
    if args.fast:
        os.environ["FLOW_SSH_FAST"] = "1"

    flow = Flow()
    task = resolve_task(flow, args.task_identifier)

    # Fresh endpoint via provider resolver; fall back to task.ssh_host
    provider = flow.provider
    host: str | None = None
    port: int = 22
    try:
        host, port = provider.resolve_ssh_endpoint(task.task_id, node=args.node)
    except Exception as e:
        # Fallback: use fresh task view
        try:
            fresh = flow.get_task(task.task_id)
            host = getattr(fresh, "ssh_host", None)
            port = int(getattr(fresh, "ssh_port", 22) or 22)
        except Exception:
            host = getattr(task, "ssh_host", None)
            port = int(getattr(task, "ssh_port", 22) or 22)
        if not host:
            print(f"Resolver error: {e}")
            raise SystemExit("No SSH endpoint available for this task yet.")

    # Resolve private key path via provider
    key_path, err = provider.get_task_ssh_connection_info(task.task_id)
    if not key_path:
        print(f"SSH key resolution failed: {err}")
        raise SystemExit(1)

    # TCP readiness probe
    is_open = SshStack.tcp_port_open(host, port, timeout_sec=float(args.timeout))

    # Build canonical ssh argv
    ssh_argv = SshStack.build_ssh_command(
        user=getattr(task, "ssh_user", "ubuntu"),
        host=host,
        port=port,
        key_path=Path(key_path),
        remote_command=args.remote_cmd,
    )

    print("Resolved SSH endpoint:")
    print(f"  task_id: {task.task_id}")
    print(f"  user:    {getattr(task, 'ssh_user', 'ubuntu')}")
    print(f"  host:    {host}")
    print(f"  port:    {port}")
    print(f"  key:     {key_path}")
    print(f"  tcp:     {'open' if is_open else 'closed'}")
    print("SSH command:")
    print("  " + " ".join(ssh_argv))

    # Optional: full key trace verification
    if args.verify_key_trace:
        mismatches = _verify_key_trace(provider, task, key_path)
        if mismatches:
            print("\nKey trace mismatches detected:")
            for m in mismatches:
                print(f"  - {m}")
            if args.fail_on_mismatch:
                sys.exit(2)

    if args.show_details:
        try:
            fresh = flow.get_task(task.task_id)
            print("\nDetails:")
            print(f"  status:  {fresh.status.value}")
            print(f"  message: {getattr(fresh, 'message', None)}")
            print(f"  instances: {getattr(fresh, 'instances', [])}")
            meta = getattr(fresh, 'provider_metadata', {}) or {}
            print(f"  provider_metadata.bid_status: {meta.get('bid_status')}")
            print(f"  provider_metadata.instance_status: {meta.get('instance_status')}")
        except Exception as e:
            print(f"  detail fetch error: {e}")

    if args.connect:
        try:
            result = subprocess.run(ssh_argv)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(130)

# ------------------------ helpers ------------------------

def _normalize_pub_key(public_key: str) -> str:
    try:
        parts = public_key.strip().split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        return public_key.strip()
    except Exception:
        return public_key.strip()


def _check_private_key_mode(path: Path) -> tuple[bool, str]:
    try:
        st = path.stat()
        mode = _stat.S_IMODE(st.st_mode)
        ok = mode & 0o077 == 0  # group/other have no perms
        return ok, oct(mode)
    except Exception as e:
        return False, f"error: {e}"


def _verify_key_trace(provider, task: Task, chosen_key_path: str) -> list[str]:
    """Return list of mismatch/error strings; empty when everything lines up."""
    issues: list[str] = []

    # 1) Fetch bid and its SSH key IDs
    bid = None
    try:
        # Private method; for diagnostics only
        bid = provider._get_bid(task.task_id)  # type: ignore[attr-defined]
    except Exception as e:
        issues.append(f"could not fetch bid: {e}")
        bid = None

    bid_keys: list[str] = []
    if isinstance(bid, dict):
        try:
            ls = bid.get("launch_specification", {}) or {}
            bk = ls.get("ssh_keys", []) or []
            if isinstance(bk, list):
                bid_keys = [str(x) for x in bk]
        except Exception:
            pass

    print("\nKey trace:")
    print(f"  platform key ids on bid: {bid_keys if bid_keys else '[]'}")

    # 2) Inspect platform keys and attempt local matches
    mgr = getattr(provider, "ssh_key_manager", None)
    if not mgr:
        issues.append("provider.ssh_key_manager not available")
        return issues

    key_used = Path(chosen_key_path).expanduser()
    key_used_pub = key_used.with_suffix(".pub")
    used_pub_norm = None
    if key_used_pub.exists():
        try:
            used_pub_norm = _normalize_pub_key(key_used_pub.read_text())
        except Exception:
            pass

    if bid_keys:
        for kid in bid_keys:
            k = mgr.get_key(kid)
            if not k:
                issues.append(f"platform key {kid} not found via API")
                continue
            local_match = mgr.find_matching_local_key(kid)
            print(
                f"  key {kid} ('{getattr(k, 'name', '')}') -> local: {local_match if local_match else '<none>'}"
            )
            if local_match:
                # Compare public key contents
                api_pub_norm = _normalize_pub_key(getattr(k, "public_key", ""))
                try:
                    lp = Path(local_match)
                    lppub = lp.with_suffix(".pub")
                    if not lppub.exists():
                        issues.append(f"local match for {kid} has no .pub: {lppub}")
                    else:
                        loc_pub_norm = _normalize_pub_key(lppub.read_text())
                        if api_pub_norm and loc_pub_norm and api_pub_norm != loc_pub_norm:
                            issues.append(
                                f"public key mismatch for {kid}: api != local ({lppub})"
                            )
                except Exception as e:
                    issues.append(f"failed reading pub for {kid}: {e}")

    # 3) Confirm provider-chosen key aligns with one of the matched keys
    if bid_keys:
        matched_paths = []
        for kid in bid_keys:
            try:
                mp = mgr.find_matching_local_key(kid)
                if mp:
                    matched_paths.append(str(Path(mp).expanduser()))
            except Exception:
                continue
        if matched_paths and str(key_used) not in matched_paths:
            issues.append(
                f"provider chose {key_used} but matched set is {matched_paths}"
            )

    # 4) Check file permissions of the chosen key
    ok_mode, mode_str = _check_private_key_mode(key_used)
    print(f"  chosen key: {key_used} (mode {mode_str})")
    if not ok_mode:
        issues.append(f"chosen key permissions too open (mode {mode_str}); expected 0600")

    # 5) If we have public key content for chosen key and any API key, compare
    if used_pub_norm and bid_keys:
        for kid in bid_keys:
            k = mgr.get_key(kid)
            if not k or not getattr(k, "public_key", None):
                continue
            api_pub_norm = _normalize_pub_key(getattr(k, "public_key", ""))
            if api_pub_norm == used_pub_norm:
                print(f"  chosen key's pub matches platform key {kid}")
                break
        else:
            issues.append("chosen key's public key does not match any platform key on bid")

    # 6) Consider env override
    env_key = os.environ.get("MITHRIL_SSH_KEY") or os.environ.get("FLOW_SSH_KEY_PATH")
    if env_key:
        env_path = str(Path(env_key).expanduser())
        if env_path != str(key_used):
            issues.append(
                f"env override set ({env_path}) but provider used {key_used}"
            )

    return issues

if __name__ == "__main__":
    main()
