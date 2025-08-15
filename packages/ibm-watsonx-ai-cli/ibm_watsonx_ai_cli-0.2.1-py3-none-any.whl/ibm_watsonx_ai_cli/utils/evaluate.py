from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, cast

import typer
from ibm_watsonx_ai import APIClient  # type:ignore[import-untyped]
from ibm_watsonx_ai.deployments import RuntimeContext  # type:ignore[import-untyped]
from ibm_watsonx_gov.entities.credentials import (  # type:ignore[import-untyped]
    WxAICredentials,
)
from ibm_watsonx_gov.entities.enums import (  # type:ignore[import-untyped]
    ModelProviderType,
)
from ibm_watsonx_gov.entities.foundation_model import (  # type:ignore[import-untyped]
    WxAIFoundationModel,
)
from ibm_watsonx_gov.entities.llm_judge import LLMJudge  # type:ignore[import-untyped]
from ibm_watsonx_gov.entities.metric import GenAIMetric  # type:ignore[import-untyped]
from ibm_watsonx_gov.entities.model_provider import (  # type:ignore[import-untyped]
    WxAIModelProvider,
)
from ibm_watsonx_gov.metrics.answer_relevance.answer_relevance_metric import (  # type:ignore[import-untyped]
    AnswerRelevanceMetric,
)
from ibm_watsonx_gov.metrics.answer_similarity.answer_similarity_metric import (  # type:ignore[import-untyped]
    AnswerSimilarityMetric,
)
from ibm_watsonx_gov.metrics.text_grade_level.text_grade_level_metric import (  # type:ignore[import-untyped]
    TextGradeLevelMetric,
)
from ibm_watsonx_gov.metrics.text_reading_ease.text_reading_ease_metric import (  # type:ignore[import-untyped]
    TextReadingEaseMetric,
)
from ibm_watsonx_gov.metrics.unsuccessful_requests.unsuccessful_requests_metric import (  # type:ignore[import-untyped]
    UnsuccessfulRequestsMetric,
)

from ibm_watsonx_ai_cli.utils.config import get_custom_or_online_params


def generate_metrics(
    metrics: str, client: APIClient | None = None
) -> list[GenAIMetric]:
    if client is None:
        method = "token_recall"
        metrics_mapping = {
            "answer_similarity": AnswerSimilarityMetric(method=method),
            "answer_relevance": AnswerRelevanceMetric(method=method),
            "text_reading_ease": TextReadingEaseMetric(),
            "unsuccessful_request_metric": UnsuccessfulRequestsMetric(),
            "text_grade_level": TextGradeLevelMetric(),
        }
    else:
        metrics_mapping = {
            "answer_similarity": AnswerSimilarityMetric(
                llm_judge=create_llm_judge(client=client)
            ),
            "answer_relevance": AnswerRelevanceMetric(
                llm_judge=create_llm_judge(client=client)
            ),
            "text_reading_ease": TextReadingEaseMetric(),
            "unsuccessful_request_metric": UnsuccessfulRequestsMetric(),
            "text_grade_level": TextGradeLevelMetric(),
        }

    metrics_classes = []
    for metric in metrics.split(","):
        metric_class = metrics_mapping.get(metric.lower(), None)
        if metric_class is None:
            typer.echo(
                typer.style(
                    "Incorrect metric '{}', please choose from {}".format(
                        metric, ", ".join(metrics_mapping.keys())
                    ),
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)
        else:
            metrics_classes.append(metric_class)

    return metrics_classes


def create_llm_judge(client: APIClient) -> LLMJudge:
    wx_ai_foundation_model = WxAIFoundationModel(
        model_id="meta-llama/llama-3-3-70b-instruct",
        space_id=client.default_space_id,
        provider=WxAIModelProvider(
            credentials=WxAICredentials(
                api_key=client.credentials.api_key,
                url=client.credentials.url,
            ),
            type=ModelProviderType.IBM_WATSONX_AI,
        ),
    )
    llm_judge = LLMJudge(model=wx_ai_foundation_model)
    return llm_judge


def initialize_ai_service(agent_root_directory: Path, client: APIClient) -> Callable:
    agent_root_directory = cast(Path, agent_root_directory)

    ai_service = SourceFileLoader(
        "ai_service.py",
        str(agent_root_directory / "ai_service.py"),
    ).load_module()

    context = RuntimeContext(api_client=client)
    online_params = get_custom_or_online_params(with_source=False)
    ai_service_resp_func = ai_service.deployable_ai_service(
        context=context, **online_params
    )
    inference_service_generate = next(
        filter(
            lambda func: func.__name__.endswith("generate"),
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
                "Unable to execute the 'generate' function. Please verify that the file 'ai_service.py' contains definition of AI service function with the internal 'generate' function, or ensure that `cli.options.stream` is set to the correct value in your config.toml file.",
                fg="bright_red",
                bold=True,
            )
        )
        raise typer.Exit(code=1)
    return inference_service_generate


def run_agent(
    inference_service_generate: Callable, agent_payload: str, client: APIClient
) -> str:
    context = RuntimeContext(api_client=client)

    def ai_service_invoke(
        payload: dict[str, Any],
    ) -> Iterator[Any] | dict[str, Any]:
        context.request_payload_json = payload
        return inference_service_generate(context)

    request_payload_json = {"messages": [{"role": "user", "content": agent_payload}]}

    resp = ai_service_invoke(payload=request_payload_json)

    no_stream_resp = cast(dict[str, Any], resp)
    choices = no_stream_resp.get("body", resp).get("choices", [])
    return choices[-1].get("message", {}).get("content", "")
