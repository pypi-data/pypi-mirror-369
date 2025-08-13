#!/usr/bin/env bash
set -euo pipefail

TASK="${1:?usage: ssh_diag.sh <task-id-or-name> [project]}"
PROJ="${2:-}"
API="${MITHRIL_API_URL:-https://api.mithril.ai}"
AUTH=("Authorization: Bearer ${MITHRIL_API_KEY:?set MITHRIL_API_KEY}")

echo "[ctx] API=$API PROJ=${PROJ:-<none>} TASK=$TASK"

# 1) Resolve task → id (uses flow)
python3 - "$TASK" <<'PY' || true
from flow.api.client import Flow
from flow.cli.utils.task_resolver import resolve_task_identifier
import sys
flow=Flow()
t,err=resolve_task_identifier(flow, sys.argv[1])
if err or not t:
  print(f"[task] resolve failed: {err or 'not found'}")
  sys.exit(1)
print(f"[task] id={t.task_id} name={getattr(t,'name','')} ssh_host={getattr(t,'ssh_host',None)} ssh_port={getattr(t,'ssh_port',22)}")
PY

# 2) Query bids for the task
BIDS_URL="$API/v2/spot/bids?id=$TASK"
[[ -n "$PROJ" ]] && BIDS_URL="$BIDS_URL&project=$PROJ"
echo -e "\n[curl] $BIDS_URL"
BIDS_JSON="$(curl -sS -H "${AUTH[@]}" "$BIDS_URL" || true)"
echo "$BIDS_JSON" | jq 'if type=="array" then . else (.data // .) end'

# Extract last instance id from bids
INST_ID="$(echo "$BIDS_JSON" | jq -r '(
  if type=="array" then .[0] else (.data[0] // .data // .) end
) as $doc |
  ($doc.instances // []) as $insts |
  if ($insts | length) > 0 then
    ($insts[-1] | if type=="string" then . else (.fid // .id // empty) end)
  else empty end')"
echo "[bids] inst_id=${INST_ID:-<none>}"
[[ -z "$INST_ID" ]] && { echo "[exit] no instances in bid"; exit 1; }

# 3) Query instance detail
INST_URL="$API/v2/instances?fid=$INST_ID"
[[ -n "$PROJ" ]] && INST_URL="$INST_URL&project=$PROJ"
echo -e "\n[curl] $INST_URL"
INST_JSON="$(curl -sS -H "${AUTH[@]}" "$INST_URL" || true)"
echo "$INST_JSON" | jq 'if type=="array" then .[0] else (.data[0] // .data // .) end'

# 4) Collect all IPv4 candidates from BOTH docs
CANDS="$( (echo "$BIDS_JSON"; echo "$INST_JSON") | jq -r '.. | strings | select(test("^([0-9]{1,3}\\.){3}[0-9]{1,3}$"))' | sort -u)"
echo -e "\n[candidates]\n$CANDS"

# 5) Probe port 22 to find the live host (use nc if /dev/tcp is unavailable)
LIVE=""
probe_tcp() {
  local ip="$1"; local port="${2:-22}"
  if exec 3<>/dev/tcp/"$ip"/"$port" 2>/dev/null; then exec 3>&-; return 0; fi
  nc -z -w2 "$ip" "$port" >/dev/null 2>&1
}

for ip in $CANDS; do
  if probe_tcp "$ip" 22; then echo "[open] $ip:22"; LIVE="$ip"; break; else echo "[closed] $ip:22"; fi
done
[[ -z "$LIVE" ]] && { echo "[exit] no open :22 among candidates"; exit 2; }

# 6) Resolve private key path via provider
KEY="$(python3 - "$TASK" <<'PY'
from flow.api.client import Flow
from flow.cli.utils.task_resolver import resolve_task_identifier
f=Flow()
import sys
t,err=resolve_task_identifier(f, sys.argv[1])
if not t: sys.exit(1)
kp, em = f.provider.get_task_ssh_connection_info(t.task_id)
print(kp or "")
PY
)"
[[ -z "$KEY" ]] && { echo "[exit] no key resolved (check flow ssh-keys)"; exit 3; }
echo "[key] $KEY"

# 7) Final suggested command
CMD=(ssh -i "$KEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "ubuntu@$LIVE")
echo -e "\n[ssh] ${CMD[*]} 'echo OK'"
"${CMD[@]}" 'echo OK' || true


