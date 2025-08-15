"""
Advanced CLI example for integration tests.
"""

import os
import sys

# Add parent directory to path so we can import click_mcp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import click

from click_mcp import click_mcp


@click_mcp(command_name="start-mcp", server_name="advanced-cli")
@click.group()
def cli():
    """Advanced CLI application with custom MCP command name."""
    pass


@cli.command()
@click.option("--name", required=True, help="Name to greet")
@click.option("--formal", is_flag=True, help="Use formal greeting")
def greet(name, formal):
    """Greet someone with a formal or casual greeting."""
    if formal:
        click.echo(f"Good day, {name}.")
    else:
        click.echo(f"Hey {name}!")


@cli.group()
def config():
    """Configuration commands."""
    pass


@config.command()
@click.option("--key", required=True, help="Configuration key")
@click.option("--value", required=True, help="Configuration value")
def set(key, value):
    """Set a configuration value."""
    click.echo(f"Setting {key}={value}")


@config.command()
@click.argument("key")
def get(key):
    """Get a configuration value."""
    click.echo(f"Value for {key}: example_value")


@config.command()
@click.argument("key")
def get_value(key):
    """Get a configuration value with underscore in command name."""
    click.echo(f"Value for {key} (from get_value): example_value")


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "text"]),
    default="text",
    help="Output format",
)
@click.argument("filename")
def process(format, filename):
    """Process a file in the specified format."""
    click.echo(f"Processing {filename} in {format} format")


@cli.command()
@click.argument("source")
@click.argument("destination")
@click.option("--overwrite", is_flag=True, help="Overwrite destination if it exists")
def copy(source, destination, overwrite):
    """Copy a file from source to destination.

    SOURCE is the path to the source file.
    DESTINATION is the path where the file will be copied.
    """
    action = "Overwriting" if overwrite else "Copying"
    click.echo(f"{action} {source} to {destination}")


if __name__ == "__main__":
    cli()
