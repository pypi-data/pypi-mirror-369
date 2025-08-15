from __future__ import annotations

import rich_click as click

from hcli.lib.console import console


@click.command(name="uninstall", help="Remove locally installed API key.")
def uninstall_key() -> None:
    """Deprecated: Remove locally installed API key."""
    console.print("[yellow]This command is deprecated.[/yellow]")
    console.print("Use '[bold]hcli logout[/bold]' to remove credentials (including API keys).")
    console.print()
    console.print("Examples:")
    console.print("  hcli logout                    # Interactive selection")
    console.print("  hcli logout --name <source>    # Remove specific source")
    console.print("  hcli logout --all              # Remove all sources")
