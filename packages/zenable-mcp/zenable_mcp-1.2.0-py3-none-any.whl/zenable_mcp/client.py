import os

import click

from zenable_mcp.commands import check, version


@click.group()
@click.pass_context
def cli(ctx):
    """Zenable MCP Client - Conformance checking for your code"""
    # Ensure that ctx.obj exists
    ctx.ensure_object(dict)

    # Store API key in context for subcommands to use
    ctx.obj["api_key"] = os.environ.get("ZENABLE_API_KEY")


# Add commands to the CLI group
cli.add_command(version)
cli.add_command(check)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
