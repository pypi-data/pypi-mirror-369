# Flow CLI Command Reference

List of available `flow` commands and their short descriptions.

- `flow tutorial`: Guided setup
- `flow init`: Configure credentials
- `flow demo`: Control demo mode
  - See also: docs/cli/demo-mode-catalog.md for full demo-mode UX and fixtures
- `flow status`: List and monitor tasks
- `flow dev`: Development environment
- `flow run`: Submit task from YAML or command
- `flow grab`: Quick resource selection
- `flow cancel`: Cancel tasks
- `flow ssh`: SSH into task
- `flow logs`: View task logs
- `flow volumes`: Manage volumes
- `flow ssh-keys`: Manage SSH keys (list/upload/delete). Required project keys are indicated and auto-included on launch.
- `flow mount`: Attach volumes
- `flow upload-code`: Upload code to task
- `flow reservations`: Manage capacity reservations (create/list/show)
- `flow health`: Run health checks
- `flow colab`: Colab local runtime
- `flow theme`: Manage CLI color themes
- `flow update`: Update Flow (see docs/cli/update.md)

See: `docs/cli/update-command.md` for detailed options and examples.
- `flow daemon`: Manage local background agent
- `flow example`: Run or show example configs

Tips:
- Use `--help` on any command for details, e.g., `flow run --help`.
- Configure credentials via `flow init` or set `MITHRIL_API_KEY`.


