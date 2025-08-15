#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Callable, Literal, cast

import dotenv
import tomli
import typer
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials  # type: ignore[import-untyped]

from ibm_watsonx_ai_cli.utils.config import (
    get_payload_path,
    load_config,
)


def get_from_env(
    key: str, env_key: str, default: str | None = None, allow_empty: bool = False
) -> str | None:
    """
    Retrieve the value of an environment variable, ensuring it is non-empty.

    Parameters:
        key (str): A descriptive name for the variable (used in error messages).
        env_key (str): The name of the environment variable to retrieve.
        default (str | None): The default value to return if the environment variable
            is not set or is empty. Defaults to None.
        allow_empty (bool): Skip raise error, Default to False.

    Returns:
        str: The non-empty value of the environment variable, or the default value if provided.

    Raises:
        ValueError: If the environment variable is not set or is empty and no default is provided.
    """
    value = os.environ.get(env_key, "").strip()
    if value:
        return value
    elif default is not None:
        return default
    else:
        if not allow_empty:
            raise ValueError(
                f"Did not find {key}. Please set environment variable `{env_key}` with a valid value."
            )
        return None


def get_project_or_space_from_env(allow_empty: bool = False) -> dict:
    """
    Get project_id or space_id from environment variable.

    Raises:
        ValueError: If not exactly one of `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID` is set.
    """
    space_id = os.environ.get("WATSONX_SPACE_ID", "").strip() or None
    project_id = os.environ.get("WATSONX_PROJECT_ID", "").strip() or None

    if bool(space_id) and bool(project_id):
        raise ValueError(
            "Please ensure that only one of the environment variables, `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID`, is set. Do not set both simultaneously."
        )
    if not allow_empty and (not space_id and not project_id):
        raise ValueError(
            "Please ensure that either `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID` environment variable, is set."
        )
    return {"space_id": space_id, "project_id": project_id}


def get_dotenv_path() -> Path:
    """
    Get the filesystem path to the `.env` file in the current working directory.
    Returns:
        Path: A `Path` object representing the `.env` file in the current working directory.
    """
    package_root = Path.cwd()
    dotenv_path = package_root / ".env"

    return dotenv_path


def load_dotenv_with_current_path() -> None:
    """
    Load environment variables from a `.env` file in the current working directory.

    Raises:
        typer.Exit: Exits with code 1 if the `.env` file is not found or fails to load.
    """
    dotenv_path = get_dotenv_path()

    if not dotenv_path.is_file():
        raise FileNotFoundError(".env was not found or is a directory")

    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)


def prepare_client() -> APIClient:
    """
    Prepares and returns an initialized IBM watsonx.ai APIClient.

    Returns:
        APIClient: An initialized API client created using the retrieved configuration.
    """
    dotenv_exists = True
    try:
        load_dotenv_with_current_path()
    except FileNotFoundError:
        dotenv_exists = False

    url = get_from_env("watsonx_url", "WATSONX_URL", allow_empty=True)
    api_key = get_from_env("watsonx_apikey", "WATSONX_APIKEY", allow_empty=True)
    token = get_from_env("watsonx_token", "WATSONX_TOKEN", allow_empty=True)
    password = get_from_env("watsonx_password", "WATSONX_PASSWORD", allow_empty=True)
    username = get_from_env("watsonx_username", "WATSONX_USERNAME", allow_empty=True)
    instance_id = get_from_env(
        "watsonx_instance_id", "WATSONX_INSTANCE_ID", allow_empty=True
    )
    url = cast(str, url)  # value of url will be always a str
    project_space_dict = {
        "space_id": get_from_env(
            "watsonx_space_id", "WATSONX_SPACE_ID", allow_empty=True
        ),
        "project_id": get_from_env(
            "watsonx_project_id", "WATSONX_PROJECT_ID", allow_empty=True
        ),
    }

    if not dotenv_exists:
        # Backward compatibility: in case when user has only config.toml file
        # Use creds from config toml [deployment] section
        # if some entity is empty or missing, fallback to env variables
        try:
            config = load_config()
            typer.echo(
                typer.style(
                    "Credentials have been loaded from config.toml, though this method is now deprecated. We recommend migrating all credential variables to a .env file for continued support",
                    fg="yellow",
                    bold=True,
                )
            )
        except FileNotFoundError:
            config = {"deployment": {}}

        dep_config = config["deployment"]
        url = dep_config.get("watsonx_url") or url
        api_key = dep_config.get("watsonx_apikey") or api_key
        token = dep_config.get("watsonx_token") or token
        password = dep_config.get("watsonx_password") or password
        username = dep_config.get("watsonx_username") or username
        instance_id = dep_config.get("watsonx_instance_id") or instance_id

        project_space_dict = {
            "space_id": dep_config.get("space_id") or project_space_dict["space_id"],
            "project_id": dep_config.get("project_id")
            or project_space_dict["project_id"],
        }

    hostname = urllib.parse.urlparse(url).hostname or ""
    if not hostname:
        raise ValueError(
            "Did not find url. Please set environment variable `WATSONX_URL` with a valid value."
        )
    is_cloud_url = hostname.lower().endswith("cloud.ibm.com")
    if is_cloud_url:
        if api_key is None and token is None:
            raise ValueError(
                "Did not find `WATSONX_APIKEY` or `WATSONX_TOKEN`. Please set environment variable `WATSONX_APIKEY` or `WATSONX_TOKEN` with a valid value."
            )
    else:
        if api_key is None and token is None and password is None:
            raise ValueError(
                "Did not find `WATSONX_APIKEY`, `WATSONX_TOKEN` or `WATSONX_PASSWORD`. Please set environment variable `WATSONX_APIKEY`, `WATSONX_TOKEN` or `WATSONX_PASSWORD` with a valid value."
            )
        if (api_key or password) is not None and username is None:
            raise ValueError(
                "Did not find `WATSONX_USERNAME`. Please set environment variable `WATSONX_USERNAME` with a valid value."
            )
        if instance_id is None:
            raise ValueError(
                "Did not find `WATSONX_INSTANCE_ID`. Please set environment variable `WATSONX_INSTANCE_ID` with a valid value."
            )

    if (
        project_space_dict["space_id"] is None
        and project_space_dict["project_id"] is None
    ):
        raise ValueError(
            "Did not find `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID`. Please set environment variable `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID` with a valid value."
        )

    return APIClient(
        credentials=Credentials(
            url=url,
            api_key=api_key,
            token=token,
            password=password,
            username=username,
            instance_id=instance_id,
        ),
        space_id=project_space_dict["space_id"],
        project_id=project_space_dict["project_id"],
    )


def prepare_resources_prompt(
    resources: list, resource_type: Literal["template", "app"], ask: bool = False
) -> str:
    """
    Construct a formatted prompt listing available resources.

    Args:
        resources (list): A list of available template names.
        ask (bool): If True, append a question prompting the user to choose a template. Defaults to False.
        resource_type: (Literal["template", "app"]): Type of resources to formatted into a prompt. Supported:
            - template (default)
            - app
    Returns:
        str: The formatted prompt string.
    """
    prompt = typer.style(
        f"\nList of available {resource_type}s:\n\n", fg="bright_blue", bold=True
    )
    for i, resource in enumerate(resources):
        prompt += typer.style(f"{i + 1}. {resource}\n")
    if ask:
        prompt += typer.style(
            f"\nWhich {resource_type} do you want to start with?",
            fg="bright_blue",
            bold=True,
        )

    return prompt


def get_package_root(
    agent_dir: Path | None = None, config_file: str = "pyproject.toml"
) -> Path:
    """
    Determine whether a given directory (or the current working directory) contains
    a specified configuration file and return that directory.

    Args:
        agent_dir (Path | None): Optional subdirectory under cwd to inspect.
            If None, uses cwd directly. Defaults to None.
        config_file (str): Name of the configuration file to look for in the target directory.
            Defaults to "pyproject.toml".

    Returns:
        Path: The directory in which `config_file` was found.

    Raises:
        FileNotFoundError: If `config_file` is not present in the target directory.
    """
    base_dir = Path.cwd()
    if agent_dir:
        base_dir = base_dir / agent_dir

    config_file_path = base_dir / config_file

    if config_file_path.is_file():
        return base_dir

    raise FileNotFoundError(f"No '{config_file}' found in directory {base_dir}.")


def is_cli_compatible(project_directory: Path) -> bool:
    """
    Check if the given project directory contains a CLI-compatible config file.

    Args:
        project_directory (Path): The path to the project directory.

    Returns:
        bool: True if a CLI-compatible config file is found, False otherwise.
    """
    config_files = ["config.toml", "config.toml.example"]

    for config_file in config_files:
        if (project_directory / config_file).is_file():
            return True

    return False


def ensure_template_is_cli_compatible(project_directory: Path, cli_method: str) -> None:
    """
    Validates whether the project template in the given directory is compatible with the CLI.

    Args:
        project_directory (Path): The root directory of the project to validate.
        cli_method (str): The CLI method being used, included in the error message if incompatible.

    Raises:
        typer.Exit: If the template is not compatible, exits the CLI with error code 1.
    """
    cli_compatible = is_cli_compatible(project_directory=project_directory)

    if not cli_compatible:
        error_msg = (
            f"The template located in the directory {project_directory} is "
            f"incompatible with the CLI `{cli_method}` method. "
        )

        readme_file = project_directory / "README.md"
        if readme_file.is_file():
            error_msg += f"Please refer to the {readme_file} file for further details."

        typer.echo(typer.style(error_msg, fg="bright_red", bold=True))
        raise typer.Exit(code=1)


def resource_exists(resource: str, available_resources: list) -> bool:
    """
    Check if a given resource exists within the available resources list.

    The function treats the input as a full resource path if it contains a "/".
    Otherwise, it checks if any available resource ends with "/{resource}".

    Args:
        resource (str): The resource name or full path to check.
        available_resources (list): List of available resource paths.

    Returns:
        bool: True if the resource exists, False otherwise.
    """
    if "/" in resource:
        return resource in available_resources
    else:
        return any(item.endswith(f"/{resource}") for item in available_resources)


def prompt_choice(question: str, options: list[str]) -> str:
    """
    Displays a question along with a list of allowed options and continues to prompt
    until the user provides a valid answer.

    Args:
        question (str): The question to display.
        options (list[str]): A list of allowed answers.

    Returns:
        str: The user's answer from the list of allowed options.
    """
    options_str = "/".join(options)
    while True:
        answer = (
            typer.prompt(typer.style(f"{question} ({options_str})", fg="bright_blue"))
            .strip()
            .lower()
        )
        if answer in options:
            return answer
        typer.echo(
            typer.style(
                f"Invalid option. Please choose one of: {options_str}.", fg="bright_red"
            )
        )


def select_resource_by_index(value: str, available_resources: list[str]) -> str | None:
    """
    Attempts to select and return a resource from the available_resources list
    based on the provided index (as a string).

    The index is expected to be a 1-based string (e.g., "1" selects the first element).
    If the value is not a valid integer, is out of range, or less than 1, None is returned.

    Args:
        value (str): The index of the desired resource as a string (1-based index).
        available_resources (list[str]): The list of available resource names.

    Returns:
        str | None: The selected resource if the index is valid, otherwise None.
    """
    try:
        index = int(value) - 1
        if index < 0:
            return None
        return available_resources[index]
    except (ValueError, IndexError):
        return None


def get_resource_name(
    available_resources: list[str],
    resource_type: Literal["template", "app"],
    resource_name: str | None = None,
) -> str:
    """
    Validate the provided resource name or prompt the user to select one.

    Args:
        available_resources (list[str]): A list of valid resource names.
        resource_name (str | None): The resource name provided by the user. If None,
            the user will be prompted to select a resource.
        resource_type: (Literal["template", "app"]): Type of resources to be validated. Supported:
            - template (default)
            - app

    Returns:
        str: The validated resource name selected or provided by the user.

    Raises:
        typer.Exit: If the provided or selected resource name is not found in the available_resources list.
    """
    if resource_name is None:
        resource_name = typer.prompt(
            prepare_resources_prompt(
                available_resources, ask=True, resource_type=resource_type
            )
        )

    selected = select_resource_by_index(resource_name, available_resources)
    if selected is not None:
        return selected

    if resource_name.isnumeric():
        typer.echo(
            typer.style(
                f"!!! Cannot find {resource_type} numbered {resource_name}",
                fg="bright_red",
                bold=True,
            )
        )
        raise typer.Exit(code=1)

    if not resource_exists(resource_name, available_resources):
        typer.echo(
            typer.style(
                f"!!! Cannot find {resource_type} '{resource_name}'. Available {resource_type}s: {available_resources}",
                fg="bright_red",
                bold=True,
            )
        )
        raise typer.Exit(code=1)
    return resource_name


def get_directory(selected_resource: str, directory: str | None) -> str:
    """
    Retrieve the target directory for resource creation.

    Args:
        selected_resource (str): The full path or name of the selected resource. Used to suggest a default folder name.
        directory (str | None): The target directory name. If None, the user will be prompted.

    Returns:
        str: The directory name to be used as the target folder.
    """
    shorted_selected_resource = selected_resource.split("/")[-1]
    if directory is None:
        directory = typer.prompt(
            typer.style(
                f"The name of the folder to create (press Enter to use default name: '{shorted_selected_resource}')",
                fg="bright_blue",
            ),
            default=shorted_selected_resource,
            show_default=False,
        )
    return directory


def load_question_payload() -> Any:
    """
    Load the question payload from the file specified in the configuration.

    Returns:
        Any: The JSON-decoded payload from the file.

    Raises:
        typer.Exit: If the payload path is not defined or if loading the JSON fails.
    """
    payload_path = get_payload_path()
    if payload_path:
        try:
            with open(payload_path, "r") as f:
                return json.load(f)
        except Exception as e:
            typer.echo(
                typer.style(
                    f"Failed to load payload from {payload_path}: {e}",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)
    else:
        typer.echo(
            typer.style(
                "Payload not provided. Please specify the `question` parameter or define the `payload_path` in the `[cli.options]` section of `config.toml` file.",
                fg="bright_red",
                bold=True,
            )
        )
        raise typer.Exit(code=1)


def get_ai_service_dashboard_url(client: APIClient, deployment_id: str) -> str | None:
    """
    Generate the AI service dashboard URL for a given deployment.

    Args:
        client (APIClient): The APIClient instance.
        deployment_id (str): The unique identifier for the deployment.

    Returns:
        str | None: The formatted AI service dashboard URL. If any component is
                    missing, it returns None.
    """
    space_id = get_deployment_space_id()
    deployment_url = get_deployment_url()

    if deployment_url is None:
        return None

    platform_url = (
        client.PLATFORM_URLS_MAP[deployment_url]
        if is_cloud_environment(deployment_url)
        else deployment_url
    )

    return f"{platform_url}/ml-runtime/deployments/{deployment_id}?space_id={space_id}".replace(
        "api.", ""
    )


def prompt_and_get_deployment_id() -> str | None:
    typer.echo(
        typer.style(
            "The `deployment_id` is sourced from the `WATSONX_DEPLOYMENT_ID` environment variable defined in your `.env` file or in the `deployment` section of your config.toml file.",
            fg="bright_green",
            bold=True,
        )
    )

    return get_deployment_id()


def get_package_name(project_path: Path) -> str:
    """
    Extract the package name from a pyproject.toml or package.json file.

    Args:
        project_path (Path): Path to the pyproject.toml or package.json file.

    Returns:
        str: A str containing the package name.

    Raises:
        ValueError: If either the package name is missing in the file.
    """
    if str(project_path).endswith("pyproject.toml"):
        with open(project_path, "rb") as f:
            pyproject_data = tomli.load(f)
        tool_poetry = pyproject_data.get("tool", {}).get("poetry", {})
        package_name = tool_poetry.get("name")
        if not package_name:
            raise ValueError("Package name is missing in pyproject.toml.")
        return package_name
    elif str(project_path).endswith("package.json"):
        folder_path = Path(str(project_path).split("/package.json")[0])
        result = subprocess.run(
            ["npm", "pkg", "get", "name"],
            capture_output=True,
            text=True,
            cwd=folder_path,
        )
        if result.returncode == 0:
            package_name = result.stdout.strip().replace('"', "").replace("name: ", "")
            print(package_name)
            if package_name != "{}":
                return package_name
            else:
                raise ValueError("Package name is missing in project.json.")
        else:
            raise ValueError("Failed to retrieve package name")
    else:
        raise Exception


def check_poetry_cli() -> bool:
    """Checks if the 'poetry' command-line tool is available (e.g., installed via Homebrew)."""
    try:
        subprocess.check_output(["poetry", "--version"], stderr=subprocess.STDOUT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_poetry_python_package() -> bool:
    """Checks if Poetry is installed as a Python package."""
    try:
        import poetry  # type: ignore[import]  # noqa: F401

        return True
    except ImportError:
        return False


def is_cloud_environment(url: str) -> bool:
    """Returns True if the given URL points to an IBM Cloud environment, else False"""
    if "://" not in url:
        url = "https://" + url
    hostname = urllib.parse.urlparse(url).hostname or ""
    return hostname.lower().endswith("cloud.ibm.com")


def get_deployment_space_id() -> str | None:
    """
    Retrieve the deployment space ID from env variable.

    Returns:
        str | None: The deployment space ID if available; otherwise, None.
    """
    try:
        load_dotenv_with_current_path()
        space_id = get_from_env(
            "watsonx_space_id", "WATSONX_SPACE_ID", allow_empty=True
        )
        return space_id

    except FileNotFoundError:
        config = load_config()
        return config.get("deployment", {}).get("space_id", None)


def get_deployment_url() -> str | None:
    """
    Retrieve the deployment URL from env variable.

    Returns:
        str | None: The deployment URL if available; otherwise, None.
    """
    try:
        load_dotenv_with_current_path()
        url = get_from_env("watsonx_url", "WATSONX_URL", allow_empty=True)
        return url
    except FileNotFoundError:
        config = load_config()
        return config.get("deployment", {}).get("watsonx_url", None)


def get_deployment_id() -> str | None:
    """
    Retrieve the deployment ID from env variable.

    Returns:
        str | None: The deployment ID if available; otherwise, None.
    """
    try:
        load_dotenv_with_current_path()
        deployment_id = get_from_env(
            "deployment_id", "WATSONX_DEPLOYMENT_ID", allow_empty=True
        )

        return deployment_id
    except FileNotFoundError:
        config = load_config()
        return config.get("deployment", {}).get("deployment_id", None)


def update_dotenv(file_path: Path, param: str, value: str) -> None:
    """
    Update or add a key/value pair in the specified `.env` file.

    Args:
        file_path (Path): The path to the `.env` file to update.
        param (str): The name of the environment variable to set.
        value (str): The value to assign to the environment variable.

    Raises:
        IOError: If the `.env` file cannot be read or written.
    """
    dotenv.set_key(dotenv_path=file_path, key_to_set=param, value_to_set=value)


def install_agent_library(project_directory: Path) -> None:
    template_name = project_directory.name
    pyproject_path = project_directory / "pyproject.toml"
    package_name = get_package_name(pyproject_path)
    package_spec = importlib.util.find_spec(package_name.replace("-", "_"))

    if package_spec is None:
        install_library = prompt_choice(
            question=f"Would you be willing to install the '{package_name}' library? This library is essential for the operation of your AI service.",
            options=["y", "n"],
        )

        if install_library == "y":
            typer.echo(
                typer.style(
                    f"---> Starting installation of `{template_name}` template ...",
                    fg="bright_green",
                    bold=True,
                )
            )
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-qe", "."],
                check=True,
                cwd=project_directory,
            )
            typer.echo(
                typer.style(
                    f"---> Successfully installed `{template_name}` template ...",
                    fg="bright_green",
                    bold=True,
                )
            )
            # Restart the process to pick up the newly installed library.
            if not os.environ.get("RESTARTED"):
                os.environ["RESTARTED"] = "1"
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            typer.echo(
                typer.style(
                    "Installation aborted. The library is required to proceed.",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)


def validate_evaluator(value: str) -> str:
    if value == "" or value == "llm_as_judge":
        return value
    raise typer.BadParameter("Only 'llm_as_judge' is allowed as evaluator.")


def func_has_generate_stream(func: Callable) -> bool:
    """
    Checks whether the last line of the source code of `func` contains the word 'generate_stream'.

    Args:
        func (Callable): Function to check if contain 'generate_stream'.

    Returns:
        bool: True if the pattern is found, otherwise False.
    """

    source = inspect.getsource(func)
    last_line = source.rstrip().split("\n")[-1].strip()

    pattern = r"\bgenerate_stream\b"
    return bool(re.search(pattern, last_line))
