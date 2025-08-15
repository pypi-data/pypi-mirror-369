from __future__ import annotations

import rich_click as click

from hcli import __version__
from hcli.env import ENV
from hcli.lib.commands import async_command
from hcli.lib.console import console
from hcli.lib.util.version import (
    compare_versions,
    is_frozen,
    get_latest_version,
)


@click.command()
@click.option("-f", "--force", is_flag=True, help="Force update.")
@click.option("-m", "--mode", default="pypi", help="Update source.")
@click.option(
    "--check-only",
    is_flag=True,
    help="Only check for updates, do not suggest installation.",
)
@async_command
async def update(force: bool, mode: str, check_only: bool) -> None:
    """Check for updates to the CLI."""
    console.print(f"[bold]Checking for updates ({mode})...[/bold]")
    latest_version = await get_latest_version("ida-hcli", mode)
    current_version = __version__
    update_available = compare_versions(current_version, latest_version)

    if update_available:
        console.print("[green]Update available![/green]")
        console.print(f"Current version: [yellow]{current_version}[/yellow]")
        console.print(f"Latest version: [green]{latest_version}[/green]")

        if not check_only:
            if not is_frozen():
                console.print("\nTo update, run:")
                console.print("\nOn Mac or Linux, run:")
                console.print(f"[bold cyan]curl -LsSf {ENV.HCLI_RELEASE_URL}/install | sh[/bold cyan]")
                console.print("\nOr on Windows, run:")
                console.print(f"[bold cyan]iwr {ENV.HCLI_RELEASE_URL}/install.ps1 | iex[/bold cyan]")
                pass
            else:
                console.print("\nTo update, run:")
                console.print("[bold cyan]uv tool upgrade ida-hcli[/bold cyan]")
                console.print("or")
                console.print("[bold cyan]pipx upgrade ida-hcli[/bold cyan]")

    else:
        console.print(f"[green]You are using the latest version ({current_version})[/green]")
    pass
