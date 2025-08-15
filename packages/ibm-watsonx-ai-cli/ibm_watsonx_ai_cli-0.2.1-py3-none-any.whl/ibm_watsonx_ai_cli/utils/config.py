#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from pathlib import Path
from typing import Any

import tomli
import tomlkit

DEFAULT_BASE_SW_SPEC = "runtime-24.1-py3.11"


def load_config(section: str | None = None) -> dict:
    """
    Load the configuration from a TOML file.

    Args:
        section (str | None): Optional. The name of the configuration section to retrieve.
                              If provided, the function returns the dictionary corresponding
                              to that section. Otherwise, the entire configuration is returned.

    Returns:
        dict: The full configuration dictionary if no section is specified, or the dictionary
              for the specified section.

    Raises:
        KeyError: If the specified section does not exist in the configuration.
        FileNotFoundError: If the "config.toml" file is not found in the current working directory.
        tomli.TOMLDecodeError: If the configuration file cannot be parsed.
    """
    package_root = Path.cwd()
    config_path = package_root / "config.toml"

    config_text = config_path.read_text()
    config = tomli.loads(config_text)

    if section is not None:
        return config[section]
    return config


def update_config(file_path: Path, section: str, param: str, value: str) -> None:
    """
    Updates or adds a parameter in a specified section of a TOML configuration file, preserving formatting and comments.

    Args:
        file_path (Path): Path to the TOML configuration file.
        section (str): Dot-separated string indicating the section to update (e.g., "deployment.custom.a").
        param (str): The name of the parameter to update or add.
        value (str): The value to assign to the parameter.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        Exception: If there is an error parsing or writing the TOML file.
    """
    content = file_path.read_text(encoding="utf-8")
    doc = tomlkit.parse(content)

    current: Any = doc
    for key in section.split("."):
        if key not in current:
            new_table = tomlkit.table()
            new_table.trivia.trail = "\n"
            current.add(key, new_table)
        current = current[key]

    item = tomlkit.item(value)
    item.trivia.indent = "  "
    current[param] = item

    lines = tomlkit.dumps(doc).splitlines()
    new_lines = []
    for i, line in enumerate(lines):
        if line.startswith("[") and i > 0 and lines[i - 1].strip():
            new_lines.append("")
        new_lines.append(line)
    result = "\n".join(new_lines) + "\n"

    file_path.write_text(result, encoding="utf-8")


def get_custom_or_online_params(with_source: bool = False) -> dict:
    """
    Loads the deployment configuration and returns a dictionary of merged parameters.

    If with_source is True, the returned dictionary will include a 'source' key indicating
    whether the parameters were taken from 'custom' or 'online' settings.

    Returns:
        dict: A dictionary containing the merged deployment parameters. Optionally includes a
              'source' key if with_source is True.

    Raises:
        KeyError: If the required keys ('watsonx_url' or 'space_id') are missing in the deployment configuration.
        ValueError: If either both 'deployment.custom' and 'deployment.online.parameters' are set.
    """
    config = load_config()
    deployment_config = config.get("deployment", {})

    custom_params = deployment_config.get("custom", {})
    online_params = deployment_config.get("online", {}).get("parameters", {})

    if custom_params and online_params:
        raise ValueError(
            "Please ensure that only one of the following parameters is configured: "
            "'deployment.custom' or 'deployment.online.parameters'. Do not set both simultaneously."
        )

    source = "custom" if custom_params else "online"
    merged_params = custom_params if custom_params else online_params

    if with_source:
        merged_params = merged_params.copy()
        merged_params["source"] = source

    return merged_params


def is_streaming_enabled() -> bool:
    """
    Determines whether streaming is enabled based on configuration.

    Returns:
        bool: True if streaming is enabled, otherwise False.
    """
    config = load_config()
    return config.get("cli", {}).get("options", {}).get("stream", True)


def get_sw_spec_name() -> str | None:
    """
    Retrieve the software specification name from the configuration.

    Returns:
        str: The software specification name as a string if it exists; otherwise, None.
    """
    config = load_config()
    return (
        config.get("deployment", {}).get("software_specification", {}).get("name", None)
    )


def overwrite_sw_spec() -> bool:
    """
    Determine whether the software specification should be overwritten based on configuration settings.

    Returns:
        bool: True if the configuration specifies that the software specification should be overwritten; otherwise, False.
    """
    config = load_config()
    return (
        config.get("deployment", {})
        .get("software_specification", {})
        .get("overwrite", False)
    )


def get_base_sw_spec() -> str:
    """
    Retrieve the base software specification from the configuration.

    Returns:
        str: The base software specification string from the configuration, or the default
             value if not specified.
    """
    config = load_config()
    return (
        config.get("deployment", {})
        .get("software_specification", {})
        .get("base_sw_spec", DEFAULT_BASE_SW_SPEC)
    )


def get_payload_path() -> str | None:
    """
    Retrieve the payload path from the software specifications in the configuration.

    Returns:
        str | None: The payload path if present in the configuration; otherwise, None.
    """
    config = load_config()
    return config.get("cli", {}).get("options", {}).get("payload_path", None)
