# file_organizer/cli.py
import typer
from pathlib import Path
from rich.console import Console

app = typer.Typer()
console = Console()

def organize_by_extension(path: Path):
    """Organizes files in the given path by their extension."""
    console.print(
        f"\n[bold cyan]Organizing {path} by file extension...[/bold cyan]"
    )

    for item in path.iterdir():
        if not item.is_file() or item.name.startswith('.'):
            continue

        extension = item.suffix.lower()
        if not extension:
            console.print(
                f"[yellow]Skipping '{item.name}' (no extension)[/yellow]"
            )
            continue

        dest_dir = path / extension[1:]
        dest_dir.mkdir(exist_ok=True)

        try:
            dest_path = dest_dir / item.name
            item.rename(dest_path)
            console.print(
                f"[green]Moved '{item.name}' to '{dest_dir.name}/'[/green]"
            )
        except Exception as e:
            console.print(f"[bold red]Error moving '{item.name}': {e}[/bold red]")

@app.command()
def main(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
        help="The directory path to organize.",
    ),
    by_extension: bool = typer.Option(
        False, "--by-extension", "-e", help="Organize files by extension."
    ),
):
    """
    A powerful and configurable CLI tool to organize your files effortlessly.
    """
    if not any([by_extension]):
        console.print(
            "[bold yellow]No organization mode selected. "
            "Please specify an option like --by-extension.[/bold yellow]"
        )
        raise typer.Exit()

    if by_extension:
        organize_by_extension(path)

    console.print("\n[bold green]✨ Organization complete! ✨[/bold green]")

if __name__ == "__main__":
    app()