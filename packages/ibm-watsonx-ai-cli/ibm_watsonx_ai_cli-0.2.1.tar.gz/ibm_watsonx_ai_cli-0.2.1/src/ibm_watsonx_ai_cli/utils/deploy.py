#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import json
import logging
from importlib.machinery import SourceFileLoader
from pathlib import Path

import typer
from ibm_watsonx_ai import APIClient  # type:ignore[import-untyped]
from ibm_watsonx_ai.wml_client_error import (  # type:ignore[import-untyped]
    ResourceIdByNameNotFound,
)

from ibm_watsonx_ai_cli.utils.build_package import (
    build_zip_sc,
    get_package_name_and_version,
)
from ibm_watsonx_ai_cli.utils.config import (
    get_base_sw_spec,
    get_custom_or_online_params,
    get_sw_spec_name,
    overwrite_sw_spec,
)
from ibm_watsonx_ai_cli.utils.utils import func_has_generate_stream

logging.basicConfig()
logger = logging.getLogger(__name__)

DEFAULT_AI_SERVICE_ASSET_NAME = "online ai_service"
DEFAULT_AI_SERVICE_DEPLOYMENT_NAME = "online ai_service deployment"


def deploy_ai_service(
    client: APIClient, agent_root_dir: Path, name: str | None
) -> dict:
    """
    Deploy an AI service from the specified agent root directory.

    Args:
        client (APIClient): Instance of APIClient.
        agent_root_dir (Path): The root directory of the agent from which the AI service is to be deployed.
        name (str | None): AI service assets name used in deploying process.

    Returns:
        dict: The deployment details returned by the API client after creating the deployment.
    """
    pyproject_path = agent_root_dir / "pyproject.toml"
    pkg_name, pkg_version = get_package_name_and_version(str(pyproject_path))
    pkg_name = pkg_name.split("/")[-1]

    # Create package extension
    pkg_ext_metadata = {
        client.package_extensions.ConfigurationMetaNames.NAME: pkg_name,
        client.package_extensions.ConfigurationMetaNames.TYPE: "pip_zip",
    }

    pkg_ext_sc = (
        agent_root_dir / "dist" / f"{pkg_name.replace('-', '_')}-{pkg_version}.zip"
    )

    if not pkg_ext_sc.exists():
        build_zip_sc(pkg_ext_sc)
    else:
        logger.warning(
            f"package extension was not built as path: '{pkg_ext_sc}' is not empty. Using the already existing path for deployment. "
            "In case of any problems you might want to delete it and rerun the `service new` command."
        )
    pkg_ext_asset_details = client.package_extensions.store(
        meta_props=pkg_ext_metadata, file_path=str(pkg_ext_sc)
    )
    pkg_ext_asset_id = client.package_extensions.get_id(pkg_ext_asset_details)

    # Select base software specification to extend
    base_sw_spec_name = get_base_sw_spec()
    base_sw_spec_id = client.software_specifications.get_id_by_name(base_sw_spec_name)

    # Define new software specification based on base one and custom library
    template_sw_spec_name = get_sw_spec_name()
    if not template_sw_spec_name:
        template_sw_spec_name = f"{pkg_name}-sw-spec"

    sw_spec_metadata = {
        client.software_specifications.ConfigurationMetaNames.NAME: template_sw_spec_name,
        client.software_specifications.ConfigurationMetaNames.BASE_SOFTWARE_SPECIFICATION: {
            "guid": base_sw_spec_id
        },
        client.software_specifications.ConfigurationMetaNames.PACKAGE_EXTENSIONS: [
            {"guid": pkg_ext_asset_id}
        ],
    }

    # Delete if sw_spec already exists
    try:
        sw_spec_id = client.software_specifications.get_id_by_name(
            template_sw_spec_name
        )
        # If the specification exists, decide based on the overwrite configuration.
        if not overwrite_sw_spec():
            typer.echo(
                typer.style(
                    f"Software specification '{template_sw_spec_name}' already exists. Please specify custom name 'deployment.software_specification.name' or set 'deployment.software_specification.overwrite' to True if you want to overwrite already existing one.",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)
        logger.warning(f"Deleting previously created sw_spec: {template_sw_spec_name}")
        client.software_specifications.delete(sw_spec_id)
    except ResourceIdByNameNotFound:
        pass

    # Store the software spec
    sw_spec_asset_details = client.software_specifications.store(
        meta_props=sw_spec_metadata
    )

    # Get the id of the new asset
    asset_id = client.software_specifications.get_id(sw_spec_asset_details)

    ai_service_asset_name = name if name else DEFAULT_AI_SERVICE_ASSET_NAME

    with (agent_root_dir / "schema" / "request.json").open(
        "r", encoding="utf-8"
    ) as file:
        request_schema = json.load(file)

    with (agent_root_dir / "schema" / "response.json").open(
        "r", encoding="utf-8"
    ) as file:
        response_schema = json.load(file)

    agent_ai_service_module = SourceFileLoader(
        "ai_service", str(agent_root_dir / "ai_service.py")
    ).load_module()
    agent_ai_service = agent_ai_service_module.deployable_ai_service

    meta_props = {
        client.repository.AIServiceMetaNames.SOFTWARE_SPEC_ID: asset_id,
        client.repository.AIServiceMetaNames.NAME: ai_service_asset_name,
        client.repository.AIServiceMetaNames.REQUEST_DOCUMENTATION: request_schema,
        client.repository.AIServiceMetaNames.RESPONSE_DOCUMENTATION: response_schema,
    }
    if func_has_generate_stream(func=agent_ai_service):
        meta_props[client.repository.AIServiceMetaNames.TAGS] = ["wx-agent"]

    stored_ai_service_details = client.repository.store_ai_service(
        agent_ai_service, meta_props
    )
    ai_deployment_id = stored_ai_service_details["metadata"].get("id")

    ai_service_deployment_name = (
        f"{name} deployment" if name else DEFAULT_AI_SERVICE_DEPLOYMENT_NAME
    )

    meta_props = {
        client.deployments.ConfigurationMetaNames.NAME: ai_service_deployment_name,
    }
    if func_has_generate_stream(func=agent_ai_service):
        meta_props[client.repository.AIServiceMetaNames.TAGS] = ["wx-agent"]

    custom_or_online_params = get_custom_or_online_params(with_source=True)
    source = custom_or_online_params.pop("source", None)

    if source == "online":
        if not custom_or_online_params:
            meta_props[client.deployments.ConfigurationMetaNames.ONLINE] = {}
        else:
            meta_props[client.deployments.ConfigurationMetaNames.ONLINE] = {
                "parameters": custom_or_online_params
            }
    elif source == "custom":
        meta_props[client.deployments.ConfigurationMetaNames.CUSTOM] = (
            custom_or_online_params
        )
        meta_props[client.deployments.ConfigurationMetaNames.ONLINE] = {}
    else:
        raise ValueError(f"Unknown configuration source: {source}")

    deployment_details = client.deployments.create(ai_deployment_id, meta_props)

    return deployment_details
