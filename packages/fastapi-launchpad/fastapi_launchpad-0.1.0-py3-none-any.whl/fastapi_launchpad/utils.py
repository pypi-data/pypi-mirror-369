import typer


def validate_project_name(name: str) -> str:
    """Validate and normalize project name."""
    if not name.isidentifier():
        normalized = "".join(c if c.isalnum() or c == "_" else "_" for c in name).lower()
        if normalized[0].isdigit():
            raise typer.BadParameter("Project name cannot start with a number")
        return normalized
    return name