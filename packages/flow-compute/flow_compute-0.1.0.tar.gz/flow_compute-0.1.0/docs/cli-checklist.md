# Flow CLI Review Checklist

Use this document to track verification of every Flow CLI command and option. Check items as you validate behavior, help text, edge cases, and error handling.

Notes
- Some commands exist in the codebase but may be hidden from the primary help or not wired by default; they are included for completeness.
- Global options apply to the `flow` root command regardless of subcommand.

## Global (root: `flow`)
- [ ] `--version` Show the version and exit
- [ ] `--theme [NAME]` Set color theme (env `FLOW_THEME`)
- [ ] `--no-color` Disable color output (env `NO_COLOR`)
- [ ] `--hyperlinks/--no-hyperlinks` Enable/disable hyperlinks (env `FLOW_HYPERLINKS`)
- [ ] `--simple/--no-simple` Simple output for CI/logs (env `FLOW_SIMPLE_OUTPUT`)

## Commands

<!-- tutorial deferred for initial release -->
<!--
### flow tutorial
- [ ] `--provider [NAME]` (env `FLOW_PROVIDER`)
- [ ] `--demo/--no-demo` (default: on)
- [ ] `--example [gpu-test]` (default: gpu-test)
- [ ] `--skip-init`
- [ ] `--force-init`
- [ ] `--skip-health`
- [ ] `--skip-example`
-- [ ] `--yes` (alias: `--y`)
-->

### flow init
- [ ] `--provider [NAME]` (env `FLOW_PROVIDER`)
- [ ] `--api-key [KEY]`
- [ ] `--project [NAME]`
- [ ] `--region [NAME]`
- [ ] `--api-url [URL]`
- [ ] `--dry-run`
- [ ] `--output [FILE]` (with `--dry-run`)
- [ ] `--verbose, -v`
- [ ] `--reset`
- [ ] `--show`
- [ ] `--yes` (non-interactive)

<!-- demo deferred for initial release -->
<!--
### flow demo (group)
- status
  - [ ] (no options)
- start
  - [ ] (no options)
- stop
  - [ ] (no options)
- profile
  - [ ] `name` one of quick|realistic|slow_network
- set
  - [ ] `assignment` as `KEY=VALUE`
- refresh
  - [ ] `--cache/--no-cache` (default: on)
  - [ ] `--reseed/--no-reseed` (default: on)
-->

### flow docs
- [ ] `--verbose, -v`

### flow status
- [ ] `task_identifier` (optional)
- [ ] `--all`
- [ ] `--state, -s` pending|running|paused|preempting|completed|failed|cancelled
- [ ] `--status` (alias of --state; hidden)
- [ ] `--limit [INT]` (default: 20)
- [ ] `--force-refresh`
- [ ] `--json`
- [ ] `--since [STR]` (e.g., 2h or ISO8601)
- [ ] `--until [STR]`
- [ ] `--verbose, -v`
- [ ] `--watch, -w`
- [ ] `--compact`
- [ ] `--refresh-rate [FLOAT]` (default: 3.0)
- [ ] `--wide` (hidden)
- [ ] `--project [NAME]`
- [ ] `--no-origin-group`
- [ ] `--show-reservations` (may be no-op if reservations are disabled)

### flow dev
- [ ] `cmd_arg` (optional positional)
- [ ] `--command, -c` (deprecated; hidden)
- [ ] `--env, -e [NAME]` (default: default)
- [ ] `--instance-type, -i`
- [ ] `--region, -r`
- [ ] `--image`
- [ ] `--ssh-keys, -k` (repeatable)
- [ ] `--reset, -R`
- [ ] `--stop, -S`
- [ ] `--info` (alias: `--status` hidden)
- [ ] `--force-new`
- [ ] `--max-price-per-hour, -m [FLOAT]`
- [ ] `--upload/--no-upload` (default: upload)
- [ ] `--upload-path [PATH]` (default: .)
- [ ] `--no-unique`
- [ ] `--json` (with `--info`)
- [ ] `--verbose, -v`

### flow run
- [ ] `config_file` (optional)
- [ ] `extra_args...` (positional passthrough)
- [ ] `--instance-type, -i`
- [ ] `--region, -r`
- [ ] `--ssh-keys, -k` (repeatable)
- [ ] `--image [NAME]` (default: nvidia/cuda:12.1.0-runtime-ubuntu22.04)
- [ ] `--name, -n`
- [ ] `--no-unique`
- [ ] `--command, -c` (deprecated; hidden)
- [ ] `--priority, -p` low|med|high
- [ ] `--on-name-conflict` error|suffix
- [ ] `--force-new` (alias of suffix)
- [ ] `--wait/--no-wait` (default: wait)
- [ ] `--dry-run, -d`
- [ ] `--watch, -w`
- [ ] `--json`
- [ ] `--allocation` spot|reserved|auto
- [ ] `--reservation-id [ID]`
- [ ] `--start [ISO8601]` (reserved mode)
- [ ] `--duration [HOURS int]` (reserved mode)
- [ ] `--env KEY=VALUE` (repeatable)
- [ ] `--pricing`
- [ ] `--compact`
- [ ] `--slurm`
- [ ] `--mount [SPEC]` (repeatable)
- [ ] `--port [INT]` (repeatable; >=1024)
- [ ] `--upload-strategy` auto|embedded|scp|none (default: auto)
- [ ] `--upload-timeout [INT]` (default: 600)
- [ ] `--code-root [PATH]`
- [ ] `--on-upload-failure` continue|fail (default: continue)
- [ ] `--max-price-per-hour, -m [FLOAT]`
- [ ] `--num-instances, -N [INT]` (default: 1)
- [ ] `--distributed` auto|manual
- [ ] `--verbose, -v`

### flow grab
- [ ] `count [INT]`
- [ ] `gpu_type` (optional)
- [ ] `--hours [FLOAT]`
- [ ] `--days, -d [FLOAT]`
- [ ] `--weeks, -w [FLOAT]`
- [ ] `--months, -m [FLOAT]`
- [ ] `--max-price, -p [FLOAT]` (USD/GPU/hour)
- [ ] `--ssh-keys, -k` (repeatable)
- [ ] `--region, -r`
- [ ] `--run [CMD]`
- [ ] `--name, -n`
- [ ] `--no-unique`
- [ ] `--json`
- [ ] `--verbose, -v`

### flow cancel
- [ ] `task_identifier` (optional)
- [ ] `--yes, -y`
- [ ] `--all`
- [ ] `--name-pattern, -n [PATTERN]`
- [ ] `--regex`
- [ ] `--verbose, -v`
- [ ] `--interactive/--no-interactive`

### flow ssh
- [ ] `task_identifier` (optional)
- [ ] trailing `remote_cmd...` after `--`
- [ ] `--command, -c` (deprecated; hidden)
- [ ] `--node [INT]` (default: 0)
- [ ] `--verbose, -v`

### flow logs
- [ ] `task_identifier` (optional)
- [ ] `--follow, -f`
- [ ] `--tail, -n [INT]` (default: 100)
- [ ] `--stderr`
- [ ] `--node [INT]`
- [ ] `--since [STR]` (e.g., 5m, 1h, ISO)
- [ ] `--grep [REGEX]`
- [ ] `--no-prefix`
- [ ] `--full-prefix`
- [ ] `--json`
- [ ] `--verbose, -v`

### flow volumes (group)
- group
  - [ ] `--verbose, -v`
- list
  - [ ] `--details, -d`
- create
  - [ ] `--size, -s [INT]` (required; GB)
  - [ ] `--name, -n [STR]`
  - [ ] `--interface, -i` block|file (default: block)
- delete
  - [ ] `volume_identifier`
  - [ ] `--yes, -y`
- delete-all
  - [ ] `--pattern, -p [PATTERN]`
  - [ ] `--dry-run`
  - [ ] `--yes, -y`

### flow mount
- [ ] `volume_identifier` (optional)
- [ ] `task_identifier` (optional)
- [ ] `--volume, -v [ID|NAME]`
- [ ] `--task, -t [ID|NAME]`
- [ ] `--instance, -i [INT]`
- [ ] `--mount-point, -m [PATH]`
- [ ] `--dry-run`
- [ ] `--verbose, -V`

### flow ssh-keys (group)
- group
  - [ ] `--verbose, -v`
- list
  - [ ] `--sync`
  - [ ] `--show-auto`
  - [ ] `--legend`
  - [ ] `--verbose, -v`
- details
  - [ ] `key_id`
  - [ ] `--verbose, -v`
- require
  - [ ] `key_id`
  - [ ] `--unset`
- delete
  - [ ] `key_identifier`
- upload
  - [ ] `key_path`
  - [ ] `--name [STR]`
- alias
  - [ ] `add` (alias of upload)

### flow ports (group)
- open
  - [ ] `task_identifier`
  - [ ] `--port [INT]` (>=1024; required)
  - [ ] `--persist/--no-persist` (default: persist)
- close
  - [ ] `task_identifier`
  - [ ] `--port [INT]` (required)
- list
  - [ ] `task_identifier`
- tunnel
  - [ ] `task_identifier`
  - [ ] `--remote [INT]` (required)
  - [ ] `--local [INT]` (default: 0 auto)
  - [ ] `--print-only`

### flow upload-code
- [ ] `task_identifier` (optional)
- [ ] `--source, -s [DIR]`
- [ ] `--timeout, -t [INT]` (default: 600)
- [ ] `--dest [STR]` (default: /workspace)
- [ ] `--verbose, -v`

### flow theme (group)
- list
  - [ ] (no options)
- get
  - [ ] (no options)
- set
  - [ ] `name`
- clear
  - [ ] (no options)

### flow update
- [ ] `--check`
- [ ] `--force`
- [ ] `--version [STR]`
- [ ] `--rollback [FILE]`
- [ ] `--yes, -y`
- [ ] `--json`

<!-- daemon deferred for initial release -->
<!--
### flow daemon (group)
- start
  - [ ] `--idle-ttl [INT]` (default: 1800)
- stop
  - [ ] (no options)
-->
- status
  - [ ] (no options)

### flow example
- [ ] `example_name` (optional)
- [ ] `--show`
- [ ] `--verbose, -v`
- [ ] `--pricing`

## Additional commands present (may be hidden or not wired by default)

### flow pricing
- [ ] `--compact`
- [ ] `--market`
- [ ] `--region [NAME]`

### flow release
- [ ] `task_identifier` (optional)
- [ ] `--all, -a`
- [ ] `--force, -f`
- [ ] `--verbose, -v`

<!-- reservations deferred for initial release -->
<!--
### flow reservations (group)
- create
  - [ ] `--instance-type [STR]` (required)
  - [ ] `--region [STR]`
  - [ ] `--quantity [INT]` (default: 1)
  - [ ] `--start [ISO8601]` (required)
  - [ ] `--duration [HOURS int]` (required)
  - [ ] `--name [STR]`
  - [ ] `--ssh-key [ID]` (repeatable)
  - [ ] `--with-slurm`
  - [ ] `--slurm-version [STR]`
  - [ ] `--json`
-->
- list
  - [ ] `--json`
  - [ ] `--slurm-only`
- show
  - [ ] `reservation_id`
  - [ ] `--json`

<!-- slurm deferred for initial release -->
<!--
### flow slurm (group)
- submit
  - [ ] `reservation_id`
-->
  - [ ] `script_path`
  - [ ] `--env KEY=VALUE` (repeatable)
  - [ ] `--account [STR]`
  - [ ] `--partition [STR]`
  - [ ] `--array [STR]`
  - [ ] `--name [STR]`
- status
  - [ ] `reservation_id`
  - [ ] `--user [STR]`
  - [ ] `--state [STR]`
- cancel
  - [ ] `reservation_id`
  - [ ] `job_id`
- ssh
  - [ ] `reservation_id`

### flow alloc
- [ ] `--watch, -w`
- [ ] `--gpus [INT]` (future)
- [ ] `--type [STR]` (GPU model)
- [ ] `--refresh-rate [FLOAT]` (default: 2.0)

### flow completion (group)
- generate
  - [ ] `shell` (bash|zsh|fish; optional)
- install
  - [ ] `--shell [bash|zsh|fish]`
  - [ ] `--path [FILE]`
- uninstall
  - [ ] `--shell [bash|zsh|fish]`
  - [ ] `--path [FILE]`

<!-- colab deferred for initial release -->
<!--
### flow colab (group)
- group
  - [ ] `--verbose`
- up
  - [ ] `instance_type` (optional)
  - [ ] `--hours [FLOAT]`
  - [ ] `--name [STR]`
  - [ ] `--local-port [INT]` (default: 8888; 0=auto)
  - [ ] `--workspace/--no-workspace` (default: on)
  - [ ] `--workspace-size [INT]` (default: 50 GB)
  - [ ] `--workspace-name [STR]`
- list
  - [ ] `--local-port [INT]` (default: 8888)
- url
  - [ ] `task_identifier`
  - [ ] `--local-port [INT]` (default: 8888)
- down
  - [ ] `task_identifier`
- tunnel
  - [ ] `task_identifier`
  - [ ] `--local-port [INT]` (default: 8888)
  - [ ] `--print-only`
-->

<!-- innit alias deferred for initial release -->
<!--
### flow innit (alias for init)
- [ ] Alias behavior matches `flow init` flags/options
-->


