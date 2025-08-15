#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import shutil
import subprocess
from pathlib import Path

import tomli
import typer

from ibm_watsonx_ai_cli.utils.utils import check_poetry_cli, check_poetry_python_package


def get_package_name_and_version(pyproject_path: str) -> tuple[str, str]:
    """
    Extract the package name and version from a pyproject.toml file.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.

    Returns:
        tuple[str, str]: A tuple containing the package name and version.

    Raises:
        ValueError: If either the package name or version is missing in the file.
    """
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)
    tool_poetry = pyproject_data.get("tool", {}).get("poetry", {})
    package_name = tool_poetry.get("name")
    package_version = tool_poetry.get("version")
    if not package_name or not package_version:
        raise ValueError("Package name or version is missing in pyproject.toml.")
    return package_name, package_version


def build_zip_sc(sc_dir: Path) -> None:
    """
    Build and package a source distribution as a ZIP archive.

    This function performs the following steps:
    1. Builds a source distribution using Poetry.
    2. Extracts the built archive.
    3. Normalizes file timestamps to fix ZIP timestamp issues.
    4. Creates a ZIP archive of the source directory.

    Args:
        sc_dir (Path): The reference path used to locate and name the built source distribution.
                       The ZIP archive will be created based on this path (with its suffix removed).
    """

    poetry_cli_ok = check_poetry_cli()
    poetry_pkg_ok = check_poetry_python_package()

    if poetry_cli_ok or poetry_pkg_ok:
        subprocess.run(
            [
                "poetry",
                "build",
                f"--directory={sc_dir.parent.parent}",
                f"--output={sc_dir.parent}",
                "--format=sdist",
            ],
            check=True,
        )
        shutil.unpack_archive(sc_dir.with_suffix(".tar.gz"), sc_dir.parent)

        for file in sc_dir.parent.rglob("*"):
            if file.is_file():
                file.touch()

        zip_dir = str(sc_dir.with_suffix(""))
        shutil.make_archive(zip_dir, "zip", zip_dir)

    else:
        typer.echo(
            typer.style(
                "Poetry is not installed whereas it is essential for the AI service deployment process. To proceed please install the `poetry` package and rerun the `service new` command.",
                fg="bright_red",
                bold=True,
            )
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    pkg_name, pkg_version = get_package_name_and_version("../pyproject.toml")
    pkg_ext_sc = (
        Path(__file__).parent
        / ".."
        / "dist"
        / f"{pkg_name.replace('-', '_')}-{pkg_version}.zip"
    )
    build_zip_sc(pkg_ext_sc)
