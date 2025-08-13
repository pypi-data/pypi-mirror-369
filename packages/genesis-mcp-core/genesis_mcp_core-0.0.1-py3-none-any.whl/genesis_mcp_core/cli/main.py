"""Main CLI entry point for Genesis MCP Core."""

import click
from pathlib import Path
from typing import Optional

from .create import create_server
from .templates import list_templates


@click.group()
@click.version_option(version="0.1.0", prog_name="genesis-mcp")
def cli():
    """Genesis MCP Core - Build powerful MCP servers with ease."""
    pass


@cli.command()
@click.argument("name")
@click.option(
    "--template", 
    "-t", 
    default="basic",
    help="Template to use (basic, healthcare, api, database)"
)
@click.option(
    "--output-dir",
    "-o", 
    type=click.Path(),
    help="Output directory (defaults to current directory)"
)
def create(name: str, template: str, output_dir: Optional[str]):
    """Create a new MCP server project."""
    output_path = Path(output_dir) if output_dir else Path.cwd()
    create_server(name, template, output_path)


@cli.group()
def templates():
    """Manage project templates."""
    pass


@templates.command("list")
def templates_list():
    """List available project templates."""
    list_templates()


if __name__ == "__main__":
    cli()