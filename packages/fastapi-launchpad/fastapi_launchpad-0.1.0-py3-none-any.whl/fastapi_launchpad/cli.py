from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .templates import create_project_structure
from .utils import validate_project_name

console = Console()
cli = typer.Typer(
    name="fastapi-launch",
    help="FastAPI project scaffolding tool",
    add_completion=False,
)


@cli.command()
def project(
    project_name: str = typer.Argument(..., help="Name of the project or '.' for current directory"),
    path: Optional[str] = typer.Option(None, help="Custom path for project creation"),
    database: Optional[str] = typer.Option(
        None,
        help="Database to use",
        case_sensitive=False,
        rich_help_panel="Options",
    ),
):
    """Create a new FastAPI project with best practices."""
    try:
        if project_name == ".":
            project_name = None
            project_path = Path("./")
            console.print(Panel.fit(
                "🚀 [blue]The `path` option will be ignored when project name is set to `.`",
                title="Info",
                border_style="blue"
            ))
        else:
            project_name = validate_project_name(project_name)
            project_path = Path(path or ".") / project_name

            if project_path.exists():
                raise typer.BadParameter(f"Directory {project_path} already exists!")

            console.print(Panel.fit(
                f"🚀 Creating new FastAPI project: [bold green]{project_name}[/]",
                title="FastAPI Launchpad",
            ))

        valid_databases = ["postgres", "mysql", "mongodb"]
        if database and database.lower() not in valid_databases:
            raise typer.BadParameter(
                f"Invalid database choice. Must be one of: {', '.join(valid_databases)}"
            )

        create_project_structure(
            project_path,
            project_name,
            database=database.lower() if database else None,
        )

        console.print("\n✨ Project created successfully! Next steps:")
        console.print(f"  1. Navigate to project root directory containing main.py")
        console.print("  2. python -m venv venv")
        console.print("  3. source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate")
        console.print("  4. pip install -r requirements.txt")
        console.print("  5. Configure your database in .env (see README.md for instructions)")
        console.print("  6. uvicorn src.main:app --reload")
        console.print("\n📚 Documentation will be available at: http://127.0.0.1:8000/docs")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise typer.Exit(1)


@cli.command()
def version():
    """Show the version of fastapi-launchpad."""
    from . import __version__
    console.print(f"FastAPI Launchpad v{__version__}")


if __name__ == "__main__":
    cli() 