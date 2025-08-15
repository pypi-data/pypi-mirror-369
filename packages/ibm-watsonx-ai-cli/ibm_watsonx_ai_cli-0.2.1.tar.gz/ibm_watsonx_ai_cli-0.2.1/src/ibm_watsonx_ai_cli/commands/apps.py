#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import re
import subprocess
from pathlib import Path
from typing import Annotated

import typer

from ibm_watsonx_ai_cli.utils.github import (
    download_and_extract_resource,
    get_available_resources,
)
from ibm_watsonx_ai_cli.utils.utils import (
    get_directory,
    get_package_name,
    get_package_root,
    get_resource_name,
    prepare_resources_prompt,
    prompt_choice,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command(help="List playground app samples.")
def list() -> None:
    """
    List all available app samples.

    Usage:
        watsonx-ai app list
    """
    apps = get_available_resources(resource_type="app")
    typer.echo(prepare_resources_prompt(apps, resource_type="app"))


@cli.command(help="Creates a demo playground app for the service.")
def new(
    name: Annotated[str | None, typer.Argument(help="App name")] = None,
    target_dir: Annotated[
        str | None, typer.Argument(help="The name of the folder to create")
    ] = None,
) -> None:
    """
    Download app sample into your working directory.

    Args:
        name (str | None): The name of the app to use. If not provided, the user will be prompted to choose one.
        target_dir (str | None): The target folder where the app will be downloaded. If not provided, the user will be prompted to enter one.

    Usage:
        watsonx-ai app new [TEMPLATE_NAME] [TARGET_FOLDER]
    """
    available_agents = get_available_resources(resource_type="app")
    selected_template = get_resource_name(
        available_agents, resource_name=name, resource_type="app"
    )
    target_directory = get_directory(selected_template, target_dir)

    typer.echo(
        typer.style(
            f"---> Downloading app '{selected_template}' into '{target_directory}'...",
            fg="bright_green",
            bold=True,
        )
    )
    target_directory = download_and_extract_resource(
        selected_template, target_directory, resource_type="app"
    )
    typer.echo(
        typer.style(
            f"---> App '{selected_template}' downloaded successfully into '{target_directory}'.",
            fg="bright_green",
            bold=True,
        )
    )
    typer.echo(
        typer.style(
            "\nNext steps\n",
            fg="bright_blue",
            bold=True,
        )
    )

    typer.echo(
        typer.style(
            "Configure your app:\n\n"
            "Before running or deploying the app, copy and update your environment variable file:\n\n"
            f"  cd {target_directory}\n"
            "  cp template.env .env\n\n"
            "Now the app can be deployed via 'watsonx-ai app run'\n"
        )
    )


@cli.command(help="Start the playground app.")
def run(
    target_dir: Annotated[
        str | None, typer.Argument(help="Target directory of app")
    ] = None,
    dev: bool = typer.Option(False, "--dev", "-d", help="Run app in developer mode"),
) -> None:
    """
    Deploy and run app in your local environment.

    Args:
        target_dir (str | None): The directory to the app.
        dev (Boolean): A flag indicating either app should be deployed in developer mode. Usage: (--dev | -d)
    Usage:
        watsonx-ai app run "<target_dir>" --dev | -d
    """
    try:
        subprocess.run(
            ["npm", "--v"],
            stdout=subprocess.PIPE,
        )
    except FileNotFoundError:
        typer.echo(
            typer.style(
                "Node.js is not currently installed in your environment, which is required to run 'npm'. Please install Node.js to proceed.\n",
                fg="bright_red",
                bold=True,
            )
        )
        typer.echo(
            typer.style(
                "To install:\n"
                "- on Windows & macOS:\n"
                "\t1. Go to  https://nodejs.org\n"
                "\t2. Download the installer.\n"
                "\t3. Run the installer\n"
                "- on Linux:\n"
                "\t1. run:\n"
                "\tsudo apt update\n"
                "\tsudo apt install nodejs npm.",
                fg="blue",
                bold=True,
            )
        )
        raise typer.Exit(code=1)

    project_directory = (
        get_package_root(agent_dir=Path(target_dir), config_file="package.json")
        if target_dir
        else get_package_root(config_file="package.json")
    )

    name = get_package_name(Path(project_directory, "package.json"))

    typer.echo(
        typer.style(
            f"Starting to deploy app locally from directory {project_directory}",
            fg="bright_green",
            bold=True,
        )
    )

    result = subprocess.run(
        ["npm", "list", "--depth=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_directory,
    )

    matches = re.findall(r"UNMET DEPENDENCY (\S+)@(\S+)", result.stdout)

    unique_packages = sorted(set(matches))
    if unique_packages:
        typer.echo(typer.style("Missing dependecies:", fg="bright_red", bold=True))
        for package_name, version in unique_packages:
            typer.echo(f"\t{package_name}: {version}")

        install_library = prompt_choice(
            question="Would you be willing to install the above packages from npm? These libraries are essential for the operation of the app.",
            options=["y", "n"],
        )

        if install_library == "y":
            typer.echo(
                typer.style(
                    f"---> Starting initialization of {name}",
                    fg="bright_green",
                    bold=True,
                )
            )
            subprocess.run(["npm", "install"], check=True, cwd=project_directory)
        else:
            typer.echo(
                typer.style(
                    "Installation aborted. The libraries are required to proceed.",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)
    if dev:
        subprocess.run(["npm", "run", "dev"], cwd=project_directory)
    else:
        try:
            subprocess.run(["npm", "run", "build"], check=True, cwd=project_directory)
            subprocess.run(["npm", "start"], cwd=project_directory)
        except subprocess.CalledProcessError:
            typer.echo(
                typer.style(
                    f"Build errored. Make sure environmental variables are set in '.env' file within {project_directory} directory",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
