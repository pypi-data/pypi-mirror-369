#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import os
import re
import shutil
import tempfile
import urllib.parse
import zipfile
from typing import Any, Literal

import httpx

# ibm_watsonx_ai requre requests package
import requests  # type:ignore[import-untyped]
import typer
from dotenv import load_dotenv

from ibm_watsonx_ai_cli.utils.utils import get_dotenv_path, prompt_choice

AGENTS_SUBDIR = "agents"
APPS_SUBDIR = "apps"
SUPPORTED_GIT_PROVIDERS = ("GitHub", "GitLab")


def get_repository_tree_items() -> list:
    """
    Retrieve the list of file/tree items from a GitHub or GitLab repository.

    Returns:
        A list of dictionaries representing the repository’s tree items (files and folders).

    Raises:
        ValueError: If TEMPLATE_REPO_URL does not point to GitHub or GitLab,
                    or if any underlying API request fails.
    """
    dotenv_path = get_dotenv_path()
    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

    repo_url = os.getenv(
        "TEMPLATE_REPO_URL", "https://github.com/IBM/watsonx-developer-hub"
    )
    repo_branch = os.getenv("TEMPLATE_REPO_BRANCH", "main")
    repo_token = os.getenv("TEMPLATE_REPO_TOKEN", None)

    parsed_url = urllib.parse.urlparse(repo_url)
    domain = parsed_url.netloc.lower()

    if "github.com" in domain:
        return _fetch_github_tree(parsed_url, repo_branch, repo_token)
    elif "gitlab.com" in domain:
        return _fetch_gitlab_tree(parsed_url, repo_branch, repo_token)
    else:
        raise ValueError(
            f"Unsupported 'TEMPLATE_REPO_URL': '{repo_url}'. "
            f"Please verify that your repository URL is correct. "
            f"Supported Git providers are: {', '.join(SUPPORTED_GIT_PROVIDERS)}."
        )


def _fetch_github_tree(
    parsed_url: urllib.parse.ParseResult, branch: str, token: str | None = None
) -> list[dict[str, Any]]:
    """
    Helper to fetch a GitHub repository tree via the GitHub REST API.
    """
    api_url = f"https://api.github.com/repos{parsed_url.path}/git/trees/{branch}"
    headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    params = {"recursive": "true"}

    response = httpx.get(api_url, params=params, headers=headers)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"GitHub request error: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Invalid JSON received from GitHub API") from exc

    return data.get("tree", [])


def _fetch_gitlab_tree(
    parsed_url: urllib.parse.ParseResult, branch: str, token: str | None = None
) -> list[dict[str, Any]]:
    """
    Helper to fetch a GitLab repository tree via the GitLab REST API.
    Paginates through all pages until no more items are returned.
    """
    project_path = parsed_url.path.lstrip("/")
    project = urllib.parse.quote_plus(project_path)

    api_url = f"https://gitlab.com/api/v4/projects/{project}/repository/tree"
    headers: dict[str, str] = {}
    if token:
        headers["Private-Token"] = token

    all_items: list[dict[str, Any]] = []
    page = 1
    per_page = 100

    while True:
        params = {
            "ref": branch,
            "recursive": "true",
            "per_page": str(per_page),
            "page": str(page),
        }
        response = httpx.get(api_url, params=params, headers=headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ValueError(f"GitLab request error: {exc}") from exc

        items = response.json()
        if not items:
            break

        all_items.extend(items)
        page += 1

    return all_items


def get_available_resources(
    resource_type: Literal["template", "app"], raw: bool = False
) -> list:
    """
    Retrieve a list of available agent templates (default) or app samples from the IBM/watsonx-developer-hub repository.

    Args:
        resource_type: (Literal["template", "app"]): Type of resources to be retrieved. Supported:
                             - template (default)
                             - app
        raw (bool): If True, return the raw list of tree items from the GitHub API.
                    If False, return a formatted list of resource identifiers.
                    Defaults to False.

    Returns:
        list: A list of available resources. The list will contain formatted strings
              (e.g., "base/template-name", "community/template-name" or "app-name") unless 'raw' is True,
              in which case it returns the raw dictionary items from the API response.

    Note:
        In case of HTTP errors or JSON decoding errors, the function prints an error message
        and returns an empty list.
    """
    tree_items = get_repository_tree_items()

    if resource_type == "template":
        agent_regex = r"^agents/(?:base|community)/[A-Za-z0-9_-]+$"
    elif resource_type == "app":
        agent_regex = r"^apps/(?:base|community)/[A-Za-z0-9_-]+$"
    else:
        raise ValueError("Unsupported resource_type")

    formatted_agents = []
    for tree in tree_items:
        if tree.get("type") == "tree" and re.match(agent_regex, tree.get("path", "")):
            parts = tree["path"].split("/")
            if len(parts) >= 3:
                formatted_agents.append(f"{parts[1]}/{parts[2]}")

    if raw:
        return [
            tree
            for tree in tree_items
            if tree.get("type") == "tree"
            and re.match(agent_regex, tree.get("path", ""))
        ]
    else:
        return formatted_agents


def send_repo_zip_url_request() -> requests.Response:
    dotenv_path = get_dotenv_path()
    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

    repo_url = os.getenv(
        "TEMPLATE_REPO_URL", "https://github.com/IBM/watsonx-developer-hub"
    )
    repo_branch = os.getenv("TEMPLATE_REPO_BRANCH", "main")
    repo_token = os.getenv("TEMPLATE_REPO_TOKEN", None)

    parsed_url = urllib.parse.urlparse(repo_url)
    path_full = parsed_url.path.rstrip("/")
    path_str = path_full.lstrip("/")
    domain = parsed_url.netloc.lower()

    headers: dict = {}

    if "github" in domain:
        repo_zip_url = (
            f"https://github.com/{path_str}/archive/refs/heads/{repo_branch}.zip"
        )
        headers["Authorization"] = f"token {repo_token}"

        response = requests.get(repo_zip_url, headers=headers)

        return response

    elif "gitlab" in domain:
        project_name = path_str.split("/")[-1]
        safe_branch = github_sanitized_branch(repo_branch)
        api_url = f"https://gitlab.com/{path_str}/-/archive/{repo_branch}/{project_name}-{safe_branch}.zip"

        headers["Private-Token"] = repo_token

        response = requests.get(api_url, headers=headers)

        return response

    else:
        raise ValueError(
            f"Unsupported 'TEMPLATE_REPO_URL': '{repo_url}'. "
            f"Please verify that your repository URL is correct. "
            f"Supported Git providers are: {', '.join(SUPPORTED_GIT_PROVIDERS)}."
        )


def download_and_extract_resource(
    resource_name: str, target_dir: str, resource_type: Literal["template", "app"]
) -> str:
    """
    Download the repository ZIP, extract the specified resource folder, and copy it to the target directory.

    Args:
        resource_name (str): The name of the resource to download and extract.
        target_dir (str): The local directory where the resource should be copied.
        resource_type: (Literal["template", "app"]): Type of resources to download and extract. Supported:
                        - template (default)
                        - app

    Raises:
        typer.Exit: If the repository ZIP cannot be downloaded successfully, if the expected resource folder is not
                    found in the extracted contents, or if any error occurs during the extraction/copy process.
    """
    dotenv_path = get_dotenv_path()
    load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

    repo_branch = os.getenv("TEMPLATE_REPO_BRANCH", "main")
    safe_branch = github_sanitized_branch(repo_branch)
    extracted_repo_dir = f"watsonx-developer-hub-{safe_branch}"

    if resource_type == "template":
        subdir = AGENTS_SUBDIR
    elif resource_type == "app":
        subdir = APPS_SUBDIR
    else:
        raise ValueError("Unsupported resource_type")

    folder_to_extract = os.path.join(extracted_repo_dir, subdir, resource_name)

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_path = os.path.join(tmpdirname, "repo.zip")
            response = send_repo_zip_url_request()
            if response.status_code != 200:
                raise Exception(
                    f"Failed to download repository ZIP (status code {response.status_code})"
                )
            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdirname)

            source_folder = os.path.join(tmpdirname, folder_to_extract)
            if not os.path.exists(source_folder):
                raise Exception(
                    f"{resource_type.capitalize()} folder '{resource_name}' not found in repository."
                )

            if os.path.exists(target_dir) and os.listdir(target_dir):
                overwrite = prompt_choice(
                    question=f"Folder '{target_dir}' already exists. Do you want to overwrite it?",
                    options=["y", "n"],
                )
                if overwrite == "y":
                    shutil.rmtree(target_dir)
                else:
                    target_dir = typer.prompt(
                        typer.style(
                            text=f"Please specify a new name for the {resource_type} folder",
                            fg="bright_blue",
                        )
                    )
                    while os.path.exists(target_dir):
                        target_dir = typer.prompt(
                            typer.style(
                                text=f"Folder '{target_dir}' already exists. Please specify a different name",
                                fg="bright_red",
                            )
                        )

            os.makedirs(target_dir, exist_ok=True)

            for item in os.listdir(source_folder):
                src_item_path = os.path.join(source_folder, item)
                dst_item_path = os.path.join(target_dir, item)
                if os.path.isdir(src_item_path):
                    shutil.copytree(src_item_path, dst_item_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_item_path, dst_item_path)

            return target_dir

    except Exception as e:
        typer.echo(
            typer.style(
                f"!!! Error downloading the resource: {e}", fg="bright_red", bold=True
            )
        )
        raise typer.Exit(code=1)


def github_sanitized_branch(branch_name: str) -> str:
    """
    Given a raw GitHub branch name (e.g. "feat/-123%24%25abc"), return the
    sanitized branch string that GitHub uses when naming the top‐level
    folder inside a ZIP download (e.g. "feat-123-abc").

    Args:
        branch_name (str): The original branch name, possibly containing
            slashes, percent-escapes, or other non-alphanumeric characters.

    Returns:
        str: The sanitized branch name.
    """
    # 1) URL-decode percent-escapes
    decoded = urllib.parse.unquote(branch_name)
    # 2) Replace slashes with dashes
    replaced_slash = decoded.replace("/", "-")
    # 3) Replace any character not alphanumeric or dot with a dash
    replace_non_alphanumeric = re.sub(r"[^0-9A-Za-z\.]", "-", replaced_slash)
    # 4) Collapse multiple dashes into a single dash
    collapsed = re.sub(r"-+", "-", replace_non_alphanumeric)
    # 5) Strip any leading/trailing dash
    clean = collapsed.strip("-")
    return clean
