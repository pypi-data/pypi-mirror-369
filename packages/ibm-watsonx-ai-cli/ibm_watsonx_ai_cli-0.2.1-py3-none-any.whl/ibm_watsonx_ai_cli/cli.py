#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import typer

from ibm_watsonx_ai_cli import __version__
from ibm_watsonx_ai_cli.commands import apps, services, templates

cli = typer.Typer(no_args_is_help=True, add_completion=False)
cli.add_typer(
    templates.cli, name="template", help="Explore, download and try-out the template."
)
cli.add_typer(services.cli, name="service", help="Work with deployed templates.")
cli.add_typer(apps.cli, name="app", help="Build & run an UI playground.")


@cli.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Print the current CLI version.",
        is_eager=True,
    ),
) -> None:
    """
    Entry point for the CLI.

    Args:
        version (bool): If set to True, prints the CLI version and exits.
    """
    if version:
        typer.echo(f"watsonx-cli {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    cli()
