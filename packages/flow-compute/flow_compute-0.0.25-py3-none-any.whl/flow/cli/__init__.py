"""Flow CLI package."""

import sys


def main():
    """Entry point for the CLI."""
    # Check Python version before importing anything that uses modern syntax
    if sys.version_info < (3, 10):
        print(
            f"Error: Flow SDK requires Python 3.10 or later. "
            f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.\n\n"
            f"Recommended: Install and use 'uv' for automatic Python version management:\n"
            f"  curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            f"  uv tool install flow-compute\n\n"
            f"Or install without uv:\n"
            f"  pipx install flow-compute\n"
            f"  # macOS/Linux one-liner: curl -fsSL https://raw.githubusercontent.com/mithrilcompute/flow/main/scripts/install.sh | sh\n\n"
            f"Alternative: Upgrade your Python installation to 3.10 or later.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # Import after version check
    from flow.cli.app import create_cli

    cli_group = create_cli()
    cli_group(prog_name="flow")


__all__ = ["main"]
