#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import json
from pathlib import Path

import typer
from ibm_watsonx_ai import APIClient  # type:ignore[import-untyped]
from ibm_watsonx_ai.wml_client_error import (  # type:ignore[import-untyped]
    WMLClientError,
)
from tabulate import tabulate  # type:ignore[import-untyped]
from typing_extensions import Annotated

from ibm_watsonx_ai_cli.utils.chat import ChatAgent
from ibm_watsonx_ai_cli.utils.config import update_config
from ibm_watsonx_ai_cli.utils.deploy import deploy_ai_service
from ibm_watsonx_ai_cli.utils.utils import (
    ensure_template_is_cli_compatible,
    get_ai_service_dashboard_url,
    get_dotenv_path,
    get_package_root,
    load_question_payload,
    prepare_client,
    prompt_and_get_deployment_id,
    prompt_choice,
    update_dotenv,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command(help="List all of AI services.")
def list() -> None:
    """
    List all available AI services.

    Usage:
        watsonx-ai service list
    """
    client: APIClient = prepare_client()
    df = client.deployments.list(artifact_type="ai_service")
    table = tabulate(df, headers="keys", tablefmt="psql", showindex=False)
    typer.echo(table)


@cli.command(help="Create & deploy a new AI service from a root template directory.")
def new(
    name: Annotated[str | None, typer.Argument(help="AI service assets name")] = None,
) -> None:
    """
    Create and deploy a new AI service from a root template directory.

    Args:
        name (str | None): AI service assets name used in deploying process.

    Usage:
        watsonx-ai service new
    """
    ensure_template_is_cli_compatible(
        project_directory=Path().cwd(), cli_method="watsonx-ai service new"
    )

    project_directory = get_package_root()

    typer.echo(
        typer.style(
            f"Starting to deploy AI service from directory {project_directory}",
            fg="bright_green",
            bold=True,
        )
    )
    client = prepare_client()
    deployed_agent = deploy_ai_service(
        client=client, agent_root_dir=project_directory, name=name
    )
    deployment_id = deployed_agent.get("metadata", {})["id"]
    dotenv_path = get_dotenv_path()
    if dotenv_path.is_file():
        update_dotenv(
            file_path=dotenv_path, param="WATSONX_DEPLOYMENT_ID", value=deployment_id
        )
    else:
        config_file_path = project_directory / "config.toml"
        update_config(
            file_path=config_file_path,
            section="deployment",
            param="deployment_id",
            value=deployment_id,
        )

    typer.echo(
        typer.style(
            f"The AI service has been successfully deployed from the directory '{project_directory}', and the corresponding deployment identifier is '{deployment_id}'.",
            fg="bright_green",
            bold=True,
        )
    )
    typer.echo(
        typer.style(
            "\nNote:\n",
            fg="bright_blue",
            bold=True,
        )
    )
    typer.echo(
        typer.style(
            "Try the deployed agent locally from your terminal:\n\n"
            "  watsonx-ai service invoke 'Hello, how can you help me?'\n\n"
        )
    )
    ai_service_dashboard_url = get_ai_service_dashboard_url(
        client=client, deployment_id=deployment_id
    )

    if ai_service_dashboard_url is not None:
        typer.echo(
            typer.style(
                f"View the deployed AI service in the dashboard: {ai_service_dashboard_url}\n\n"
            )
        )


@cli.command(help="Get service details.")
def get(
    deployment_id: Annotated[str, typer.Argument(help="Deployment id")],
) -> None:
    """
    Retrieve and display details for a specified service.

    Args:
        deployment_id (str): The unique identifier of the service whose details are to be retrieved.

    Usage:
        watsonx-ai service get <deployment_id>
    """
    typer.echo(
        typer.style(
            f"Displaying details for deployment_id: {deployment_id}",
            fg="bright_green",
            bold=True,
        )
    )
    client: APIClient = prepare_client()
    details = client.deployments.get_details(deployment_id=deployment_id)
    formatted_json = json.dumps(details, indent=4, ensure_ascii=False)
    typer.echo(formatted_json)


@cli.command(help="Delete an AI service.")
def delete(deployment_id: str) -> None:
    """
    Delete an AI service and optionally its associated asset.

    Args:
        deployment_id (str): The unique identifier of the AI service to delete.

    Usage:
        watsonx-ai service delete <deployment_id>
    """
    client: APIClient = prepare_client()

    typer.echo(
        typer.style(
            f"Preparing to delete service with ID: {deployment_id}",
            fg="bright_green",
            bold=True,
        )
    )

    remove_asset = prompt_choice(
        "Do you also want to remove the AI service asset from watsonx repository?",
        ["y", "n"],
    )

    if remove_asset == "y":
        try:
            deployment_details = client.deployments.get_details(
                deployment_id=deployment_id
            )
            ai_service_asset = (
                deployment_details.get("entity", {}).get("asset", {}).get("id")
            )

            client.deployments.delete(deployment_id=deployment_id)
            client.data_assets.delete(asset_id=ai_service_asset)

            message = (
                f"The service with ID '{deployment_id}' and its associated asset with ID "
                f"'{ai_service_asset}' have been successfully removed."
            )
        except WMLClientError as error:
            typer.echo(
                typer.style(f"Error: {error.error_msg}", fg="bright_red", bold=True)
            )
            return
    else:
        try:
            client.deployments.delete(deployment_id=deployment_id)
            message = (
                f"The service with ID '{deployment_id}' has been successfully removed."
            )
        except WMLClientError as error:
            typer.echo(
                typer.style(f"Error: {error.error_msg}", fg="bright_red", bold=True)
            )
            return

    typer.echo(typer.style(message, fg="bright_green", bold=True))


def validate_deployment_id(value: str | None) -> str:
    if not value:
        raise typer.BadParameter(
            "Please provide --deployment_id as an option or set `WATSONX_DEPLOYMENT_ID` in `.env` file or in config.toml file."
        )
    return value


@cli.command(help="Calls the service by providing the test record.")
def invoke(
    deployment_id: Annotated[
        str,
        typer.Option(
            "--deployment_id",
            default_factory=prompt_and_get_deployment_id,
            callback=validate_deployment_id,
            help="Deployment id",
        ),
    ],
    query: Annotated[str | None, typer.Argument(help="Content of User Message")] = None,
) -> None:
    """
    Invoke an AI service with a test record.

    Args:
        deployment_id (str): The unique identifier of the AI service to invoke.
        query (str | None): The test query to be sent to the AI service.

    Usage:
        watsonx-ai service invoke --deployment_id "<deployment_id>" "<question>"
    """

    typer.echo(
        typer.style(
            f"Preparing to invoke service with ID: {deployment_id}",
            fg="bright_green",
            bold=True,
        )
    )
    chat_agent = ChatAgent()

    if query is None:
        query = load_question_payload()

    chat_agent.chat_with_agent(deployment_id=deployment_id, agent_payload=query)


if __name__ == "__main__":
    cli()
