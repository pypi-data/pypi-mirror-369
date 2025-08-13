"""Docs command for Flow CLI.

Provides quick access to documentation links sourced from centralized
link definitions in `flow.links`. Keeps URLs consistent across the
codebase and allows terminals with hyperlink support to render
clickable links.
"""

from __future__ import annotations

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.hyperlink_support import hyperlink_support
from flow.cli.utils.theme_manager import theme_manager


class DocsCommand(BaseCommand):
    """Show documentation links."""

    @property
    def name(self) -> str:
        return "docs"

    @property
    def help(self) -> str:
        return "Show links to the Flow/Mithril documentation"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option(
            "--verbose",
            "verbose",
            is_flag=True,
            help="Show additional popular documentation links",
        )
        def docs(verbose: bool) -> None:
            """Print documentation links from the centralized link module."""
            from flow.links import DocsLinks  # Local import to avoid early import cycles

            def link(label: str, url: str) -> str:
                try:
                    if hyperlink_support.is_supported():
                        return hyperlink_support.create_link(label, url)
                except Exception:
                    pass
                return f"{label}: {url}"

            accent = theme_manager.get_color("accent")
            console.print(f"[bold {accent}]Flow Documentation[/bold {accent}]")

            # Root docs
            console.print(link("Docs", DocsLinks.root()))

            # Common starting points
            try:
                console.print(link("Quickstart", DocsLinks.quickstart()))
            except Exception:
                pass

            if verbose:
                # Popular deep links when requested
                try:
                    console.print(link("Compute quickstart", DocsLinks.compute_quickstart()))
                except Exception:
                    pass
                try:
                    console.print(link("Compute API overview", DocsLinks.compute_api_overview()))
                except Exception:
                    pass
                try:
                    console.print(link("Compute API reference", DocsLinks.compute_api_reference()))
                except Exception:
                    pass
                try:
                    console.print(link("Startup scripts", DocsLinks.startup_scripts()))
                except Exception:
                    pass
                try:
                    console.print(link("Regions", DocsLinks.regions()))
                except Exception:
                    pass

        return docs


# Export command instance
command = DocsCommand()


