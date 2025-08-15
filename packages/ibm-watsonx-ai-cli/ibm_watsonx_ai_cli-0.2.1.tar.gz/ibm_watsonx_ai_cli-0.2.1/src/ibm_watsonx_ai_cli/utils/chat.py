#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Iterable, Iterator, cast

import typer
from ibm_watsonx_ai import APIClient  # type:ignore[import-untyped]
from ibm_watsonx_ai.deployments import RuntimeContext  # type:ignore[import-untyped]

from ibm_watsonx_ai_cli.utils.config import (
    get_custom_or_online_params,
    is_streaming_enabled,
)
from ibm_watsonx_ai_cli.utils.utils import prepare_client


class ChatAgent:
    def __init__(self, agent_root_directory: Path | None = None):
        """
        Initialize the ChatAgent instance.

        Args:
            agent_root_directory (Path): The directory containing the agent's AI service module.
        """
        self.agent_root_directory = agent_root_directory
        self.stream = is_streaming_enabled()
        self.delta_start = False

    def _print_message(self, choice: dict) -> None:
        """
        Print the message with a header. If the message includes a delta, print the delta message.

        Args:
            choice (dict): The message dictionary containing the role and content/delta.
        """
        if delta := choice.get("delta"):
            if not self.delta_start:
                header = f" {delta['role'].capitalize()} Message ".center(80, "=")
                print("\n", header)
                self.delta_start = (
                    True
                    and (choice.get("finish_reason") is None)
                    and delta["role"] != "tool"
                )
            print(delta.get("content") or delta.get("tool_calls"), flush=True, end="")
        else:
            header = f" {choice['message']['role'].capitalize()} Message ".center(
                80, "="
            )
            print("\n", header)
            print(f"{choice['message'].get('content', choice['message'])}\n")

    def chat_with_agent(
        self, deployment_id: str, agent_payload: str | dict[str, list[dict[str, str]]]
    ) -> None:
        """
        Chat with the deployed AI agent using the provided question.

        Args:
            deployment_id (str): Used deployment id.
            agent_payload (str | dict[str, list[dict[str, str]]]): The user's question to send to the agent.
        """
        client: APIClient = prepare_client()

        if self.stream:

            def ai_service_invoke(payload: dict[Any, Any]) -> Any:
                return client.deployments.run_ai_service_stream(deployment_id, payload)
        else:

            def ai_service_invoke(payload: dict[Any, Any]) -> Any:
                return client.deployments.run_ai_service(deployment_id, payload)

        if isinstance(agent_payload, str):
            request_payload_json = {
                "messages": [{"role": "user", "content": agent_payload}]
            }
        else:
            request_payload_json = agent_payload

        resp = ai_service_invoke(payload=request_payload_json)

        if self.stream:
            for r in resp:
                if isinstance(r, str):
                    r = json.loads(r)
                for c in r["choices"]:
                    self._print_message(c)
            self.delta_start = False
            print("\n")
        else:
            choices = resp.get("body", resp)["choices"]
            for c in choices:
                self._print_message(c)

    def chat_with_agent_locally(
        self, agent_payload: str | dict[str, list[dict[str, str]]]
    ) -> None:
        """
        Chat with the AI agent locally using the provided question.

        Args:
            agent_payload (str | dict[str, list[dict[str, str]]]): The user's question to send to the agent.
        """
        client: APIClient = prepare_client()

        self.agent_root_directory = cast(Path, self.agent_root_directory)

        ai_service = SourceFileLoader(
            "ai_service.py",
            str(self.agent_root_directory / "ai_service.py"),
        ).load_module()

        context = RuntimeContext(api_client=client)

        online_params = get_custom_or_online_params(with_source=False)

        ai_service_resp_func = ai_service.deployable_ai_service(
            context=context, **online_params
        )
        if self.stream:
            function_name = "generate_stream"
        else:
            function_name = "generate"

        inference_service_generate = next(
            filter(
                lambda func: func.__name__.endswith(function_name),
                (
                    ai_service_resp_func
                    if isinstance(ai_service_resp_func, Iterable)
                    else [ai_service_resp_func]
                ),
            ),
            None,
        )

        if inference_service_generate is None:
            typer.echo(
                typer.style(
                    f"Unable to execute the '{function_name}' function. Please verify that the file 'ai_service.py' contains definition of the '{function_name}' function, or ensure that `cli.options.stream` is set to the correct value in your config.toml file.",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)

        def ai_service_invoke(
            payload: dict[str, Any],
        ) -> Iterator[Any] | dict[str, Any]:
            context.request_payload_json = payload
            return inference_service_generate(context)

        if isinstance(agent_payload, str):
            request_payload_json = {
                "messages": [{"role": "user", "content": agent_payload}]
            }
        else:
            request_payload_json = agent_payload

        resp = ai_service_invoke(payload=request_payload_json)

        if self.stream:
            stream_resp = cast(Iterator[Any], resp)
            for r in stream_resp:
                if isinstance(r, str):
                    r = json.loads(r)
                for c in r["choices"]:
                    self._print_message(c)
            self.delta_start = False
            print("\n")
        else:
            no_stream_resp = cast(dict[str, Any], resp)
            choices = no_stream_resp.get("body", resp)["choices"]
            for c in choices:
                self._print_message(c)
