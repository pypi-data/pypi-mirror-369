### CLI documentation index

- Command reference: command-reference.md
- Demo mode catalog and architecture: demo-mode-catalog.md
- Update command: update-command.md (if present)
- Getting started: see docs/getting-started/

# CLI Reference

Command-line usage for Flow. Each command shows purpose, common flags, and examples. For full help, run `flow <command> --help`.

## run

- Purpose: Submit a task from YAML or a direct command
- Common flags:
  - `-i, --instance-type`: GPU type (e.g., `a100`, `8xa100`, `h100`)
  - `-k, --ssh-keys`: Inject SSH keys
  - `--image`: Docker image (default: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`)
  - `--code-root`: Local project directory to upload and map to `/workspace` (defaults to CWD)
  - `-n, --name`: Task name
  - `-m, --max-price-per-hour`: Price cap in USD/hr
  - `-N, --num-instances`: Multi-node count
  - `--mount`: Data mount (e.g., `s3://bucket/path`)
  - `--port`: Expose a high port (>=1024) on the instance public IP (repeatable)
  - `--watch`: Watch progress
- Examples:
  ```bash
  flow run "python train.py" -i a100
  flow run job.yaml --watch
  flow run -i 8xh100 -c "torchrun --nproc_per_node=8 train.py"
  # Expose a simple HTTP server on port 8080
  flow run "python -m http.server 8080" --port 8080
  # Reserved capacity examples
  flow run training.yaml --allocation reserved --start 2025-01-31T18:00:00Z --duration 6
  flow run training.yaml --allocation reserved --reservation-id rsv_abc123
  # Upload only a subdirectory and use a specific image
  flow run -i a100 --code-root ./src --image pytorch/pytorch:2.2.2-cuda12.1-cudnn8 -c "python tasks/train.py"
  ```

## status

- Purpose: Show task status (optionally all tasks)
- Examples:
  ```bash
  flow status
  flow status my-task-name
  flow status --all
  ```

## logs

- Purpose: View task logs
- Examples:
  ```bash
  flow logs my-task-name
  flow logs my-task-name --follow
  ```

## cancel

- Purpose: Cancel a running task
- Examples:
  ```bash
  flow cancel my-task-name
  ```

## ssh

- Purpose: Open an SSH shell or run a remote command
- Examples:
  ```bash
  flow ssh my-task-name
  flow ssh my-task-name -- nvidia-smi
  ```

## ssh-keys

- Purpose: Manage SSH keys with the provider
- Examples:
  ```bash
  flow ssh-keys list
  flow ssh-keys upload ~/.ssh/id_ed25519.pub
  flow ssh-keys require sshkey_ABC123         # Mark a key as required (admin)
  flow ssh-keys require --unset sshkey_ABC123 # Clear required flag (admin)
  ```

Notes:
- SSH keys are project-scoped. Project administrators may set required keys; these are automatically included in launches and shown with a "(required)" tag in listings.

## ssh-keys

- Purpose: Manage SSH keys with the provider
- Examples:
  ```bash
  flow ssh-keys list
  flow ssh-keys upload ~/.ssh/id_ed25519.pub
  flow ssh-keys require sshkey_ABC123         # Mark a key as required (admin)
  flow ssh-keys require --unset sshkey_ABC123 # Clear required flag (admin)
  ```

## reservations

- Purpose: Manage capacity reservations (create/list/show)
- Examples:
  ```bash
  # Create a reservation window
  flow reservations create \
    --instance-type 8xh100 \
    --region us-central1-b \
    --quantity 4 \
    --start 2025-01-31T18:00:00Z \
    --duration 12 \
    --name my-window

  # List reservations
  flow reservations list

  # Show details
  flow reservations show rsv_abc123
  ```

## volumes

- Purpose: Manage persistent volumes
- Examples:
  ```bash
  flow volumes list
  flow volumes create --size 100 --name dataset
  ```

## health

- Purpose: GPU fleet health checks
- Examples:
  ```bash
  flow health --gpu
  flow health --task my-task-name --history 24
  ```

---

Tip: Use `FLOW_DEBUG=1` to enable verbose CLI diagnostics during troubleshooting.


## update

- Purpose: Update Flow SDK/CLI
- Examples:
  ```bash
  flow update            # Update to latest
  flow update --check    # Check without installing
  flow update --json     # JSON output (no prompts)
  flow update --version 0.0.22  # Pin a specific version
  flow update --rollback ~/.flow/backups/backup_0.0.22_20250101T000000Z.json
  # See details: docs/cli/update.md
  ```


