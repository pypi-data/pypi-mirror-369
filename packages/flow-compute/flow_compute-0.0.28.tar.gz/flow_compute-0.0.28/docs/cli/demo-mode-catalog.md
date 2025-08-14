### Flow CLI demo mode: command catalog, architecture, and fixtures

This document specifies demo-mode behavior for every `flow` command and centralizes the architecture, paths, and fixtures required to deliver a polished, offline, non‑leaky experience. It is the single source of truth for demo-mode UX and coverage tracking.

Goals
- Ensure a consistent, delightful demo across all commands without touching real infrastructure
- Keep mock/demo logic out of core runtime paths (SOLID, DRY; no leaks into provider/runtime internals)
- Centralize mock configuration, fixtures, and paths
- Be testable and deterministic; snapshot tests validate console output where practical

Key principles
- Demo mode is opt-in via env/CLI and resolves to provider `mock`
- No remote side-effects or network dependencies in demo mode
- Minimal coupling: CLI owns demo orchestration; provider `mock` owns data semantics; core code remains unaware
- Performance: artificial latency is configurable to keep UX snappy but realistic

Global configuration and paths
- Environment flags
  - `FLOW_DEMO_MODE=1` enables demo mode for the current process
  - `FLOW_PROVIDER=mock` selects the in-memory provider
  - Latency controls (applied by mock provider)
    - `FLOW_MOCK_LATENCY_MS` base latency in ms (default: 0)
    - `FLOW_MOCK_LATENCY_<OP>_MS` per-op override (SUBMIT, LIST, STATUS, GET_TASK, INSTANCES, VOLUME_CREATE, VOLUME_DELETE, VOLUME_LIST, MOUNT, UPLOAD, LOGS, CANCEL)
    - `FLOW_MOCK_LATENCY_JITTER_MS` absolute jitter in ms
    - `FLOW_MOCK_LATENCY_JITTER_PCT` percent jitter of the op latency (e.g., 0.1)
    - `FLOW_MOCK_LATENCY_INITIAL_MS` one-time banner delay to surface animations
- Persisted env file (loaded automatically by the CLI)
  - `~/.flow/demo.env` (KEY=VALUE lines; does not override explicitly-set env)
- Persisted mock state
  - `~/.flow/demo_state.json` (seeded and maintained by the mock provider; stores tasks/volumes/log tails)
- CLI caches and local stores
  - `~/.flow/cache/` (general CLI cache)
  - `~/.flow/colab_local_runtime.json` (Colab tokenized URL store)

Centralization and non-leak design
- Demo-mode resolution and banner: `flow.cli.utils.mode`
- Demo behavior toggles are environmental and contained to CLI + `providers/mock`
- Seed data lives in `providers/mock` and can be extended without changing core client/runtime
- No imports from demo-specific modules inside core runtime or non-mock providers

Proposed fixture organization (non-code)
- Keep seed specification owned by `providers/mock` (current: programmatic seed in `MockProvider._seed_demo_tasks`)
- Optional future extension: allow alternative seed “scenarios” (e.g., empty, busy, failures) via `FLOW_DEMO_SCENARIO=<name>` with well-defined additions; backed by a JSON fixture in the mock provider package
- Snapshot expectations captured in tests (see Testing section) rather than hardcoding strings in production code

Command catalog: expected demo-mode behavior

Getting started
- tutorial
  - Behavior: Guided setup. Starts in demo by default; shows banner and indicates provider `mock`. Skips real auth; prints next steps for switching to real provider.
  - Output highlights: Demo banner, provider=mock, project/region placeholders.
  - Notes: Respects `--demo/--no-demo`.
- init
  - Behavior: With `--demo`, sets env/provider to `mock` and skips credential prompts. Writes minimal config if needed.
  - Output highlights: Confirms demo setup; hints to `flow status` and `flow run` examples.
- docs
  - Behavior: Same in demo; prints documentation links.
- demo (status | start | stop | profile | set | refresh)
  - Behavior: Control demo env; does not touch core config unless asked. `refresh` clears `demo_state.json` and cache; `profile` applies latency presets.
  - Output highlights: Current state; applied profile vars; cleanup confirmation.

Run and development
- run
  - Behavior: Uses mock provider to submit a task; shows compact progress and quick lifecycle transitions; task appears in `status` and produces synthetic logs.
  - Output highlights: Submission confirmation; task id/name; quick progress; next steps (logs/ssh/cancel).
- dev
  - Behavior: Not supported in demo (requires remote ops). Print graceful guidance to switch provider or disable demo for the run.
  - Output highlights: Clear “not supported in demo” message with next-step suggestions.
- example
  - Behavior: Displays/run examples; in demo, ensure examples that require remote ops are skipped with a helpful note.
- grab / release
  - Behavior: `grab` selects capacity using catalog from mock provider; allocates a running resource (a named task, e.g., `grab-...`). `release` cancels such tasks and shows cost summary derived from mock task fields.
  - Output highlights: Available instance options, selected GPU summary, confirmation prompts, and cleanup success.

Observe
- status
  - Behavior: Lists seeded tasks across groups (active, pending, external/history). Two youngest running tasks show “starting” (no ssh_host) to simulate provisioning. Includes multi-node entries for realism.
  - Output highlights: Rich table with name, GPU, price/hour, project, age; one external cluster section; totals.
- logs
  - Behavior: Fetches last N lines and supports `-f` streaming. In demo, uses synthetic log tails; follows lifecycle transitions for newly submitted tasks.
  - Output highlights: Log header with task info; lines with optional node prefix; graceful when no logs.

Manage
- cancel
  - Behavior: Cancels tasks by id/name/pattern. Works fully in demo.
  - Output highlights: Cancel confirmation and next steps.
- ssh
  - Behavior: Not supported in demo; prints clear guidance and alternatives; exits without error code.
- ports (open | close | list | tunnel)
  - Behavior: Not supported in demo (requires remote ops). All subcommands print guidance and next steps.
- volumes (list | create | delete | delete-all)
  - Behavior: Full support using mock volumes and attachments. `list --details` resolves task names from mock instances.
  - Output highlights: Table with name/region/size/interface/status; confirmations and success messages.
- mount
  - Behavior: Full support; updates mock volume attachments across task instances.
  - Output highlights: Attachment summary and next steps.
- upload-code
  - Behavior: Simulates transfers and returns a plausible summary (counts/bytes/rate). No remote effects.
  - Output highlights: Transfer summary and next steps.
- ssh-keys (group)
  - Behavior: Lists local/platform/configured keys via provider init interface. In demo, returns a minimal, coherent view; operations like `upload/delete/require` are no-ops or surface provider “not supported” gracefully.
  - Output highlights: Clear tables, legends, and “next step” hints.

Advanced/Utilities
- pricing
  - Behavior: Default view shows merged limit prices. `--market` shows a small, realistic catalog from mock `find_instances()`; sorted with price/availability.
  - Output highlights: Region/type/price per inst and per GPU; availability; provider console link note.
- health
  - Behavior: Explicitly demo-friendly; marks connectivity OK; SSH checks skipped with explanatory notes.
- reservations (create | list | show)
  - Behavior: Not supported in mock; commands print guidance to switch providers.
- slurm (submit | status | cancel | ssh)
  - Behavior: Requires reservations and remote ops; not supported in demo. Commands print guidance.
- colab (up | list | url | down | tunnel)
  - Behavior: Requires remote ops; not supported in demo. Print clear guidance.
- theme
  - Behavior: Same in demo; persists theme to config.
- update
  - Behavior: Same in demo.
- completion
  - Behavior: Same in demo.
- daemon
  - Behavior: Same in demo; manages local `flowd` process.
- alloc (hidden)
  - Behavior: Internal/advanced; in demo, restrict to catalog browsing and hints.
- innit (alias)
  - Behavior: Alias of `init`.

Coverage tracker (spec → fixtures → tests)
- Getting started
  - [x] tutorial → [x] spec  [x] fixtures (banner/env)  [ ] tests
  - [x] init → [x] spec  [x] fixtures  [ ] tests
  - [x] docs → [x] spec  [x] fixtures  [ ] tests
  - [x] demo → [x] spec  [x] fixtures  [ ] tests
- Run/dev
  - [x] run → [x] spec  [x] fixtures  [ ] tests
  - [x] dev → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] example → [x] spec  [x] fixtures  [ ] tests
  - [x] grab/release → [x] spec  [x] fixtures  [ ] tests
- Observe
  - [x] status → [x] spec  [x] fixtures  [ ] tests
  - [x] logs → [x] spec  [x] fixtures  [ ] tests
- Manage
  - [x] cancel → [x] spec  [x] fixtures  [ ] tests
  - [x] ssh → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] ports → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] volumes → [x] spec  [x] fixtures  [ ] tests
  - [x] mount → [x] spec  [x] fixtures  [ ] tests
  - [x] upload-code → [x] spec  [x] fixtures  [ ] tests
  - [x] ssh-keys → [x] spec  [x] fixtures  [ ] tests
- Advanced/utilities
  - [x] pricing → [x] spec  [x] fixtures  [ ] tests
  - [x] health → [x] spec  [x] fixtures  [ ] tests
  - [x] reservations → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] slurm → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] colab → [x] spec  [x] fixtures (guidance)  [ ] tests
  - [x] theme/update/completion/daemon → [x] spec  [x] fixtures  [ ] tests

Testing strategy (to be implemented)
- Unit and snapshot tests run with demo-mode env
  - Use `uv run pytest` and set `FLOW_DEMO_MODE=1`, `FLOW_PROVIDER=mock`, `FLOW_PREFETCH=0`
  - Golden snapshots for: `status`, `logs`, `volumes list`, `run` (submit + quick lifecycle), `cancel`, `grab/release`
  - Explicit assertions (not snapshots) for “not supported in demo” guidance commands (`ssh`, `ports`, `dev`, `reservations`, `slurm`, `colab`)
- Determinism
  - Persisted state reset via `flow demo refresh` before suites
  - Avoid time‑varying fields in snapshots (e.g., mask timestamps or assert structure only)

Action items (engineering)
- Short term
  - [ ] Add CLI snapshot tests for the high-traffic commands listed above
  - [ ] Add an optional `FLOW_DEMO_SCENARIO` control to MockProvider for alternate seeds (no core changes)
  - [ ] Document all demo env keys in `docs/cli/demo-mode-catalog.md` (this file) and keep in sync with `flow.cli.commands.demo`
- Medium term
  - [ ] Consider externalizing mock seed data into versioned JSON files within `flow/providers/mock/fixtures/` (keep provider-local)
  - [ ] Add a minimal path helper dedicated to demo files shared by CLI and mock provider (module local to `flow/providers/mock/` to avoid cross‑layer imports)
  - [ ] Expand demo-mode coverage docs with per-command example snippets where helpful

Appendix: quick reference of key demo commands
- `flow demo start|stop|status|profile realistic|quick|slow_network|set KEY=VALUE|refresh`
- `flow tutorial --demo` (defaults ON)
- `flow init --demo`
- `flow status` (watch or snapshot)
- `flow run examples/configs/basic.yaml` (fast lifecycle)
- `flow logs <task>` (follow or tail)
- `flow volumes list|create|delete`
- `flow cancel <task>`
- Unsupported in demo (print guidance): `ssh`, `ports`, `dev`, `colab`, `reservations`, `slurm`


