# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = [
    "CompletionCreateResponse",
    "CompletionMessage",
    "CompletionMessageContent",
    "CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItem",
    "CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItemURL",
    "CompletionMessageToolCall",
    "CompletionMessageToolCallFunction",
    "Logprobs",
    "LogprobsContent",
    "LogprobsContentTopLogprob",
    "Metric",
]


class CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItemURL(BaseModel):
    uri: str


class CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItem(BaseModel):
    type: str

    data: Optional[str] = None

    text: Optional[str] = None

    transcript: Optional[str] = None

    url: Optional[CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItemURL] = None


CompletionMessageContent: TypeAlias = Union[
    str, CompletionMessageContentLlmStefiLlamaAPIChatCompletionResponseContentItem
]


class CompletionMessageToolCallFunction(BaseModel):
    arguments: str

    name: str


class CompletionMessageToolCall(BaseModel):
    id: str

    function: CompletionMessageToolCallFunction


class CompletionMessage(BaseModel):
    role: str

    stop_reason: str

    content: Optional[CompletionMessageContent] = None

    reasoning: Optional[str] = None

    tool_calls: Optional[List[CompletionMessageToolCall]] = None


class LogprobsContentTopLogprob(BaseModel):
    token: Optional[str] = None

    logprob: Optional[float] = None


class LogprobsContent(BaseModel):
    token: Optional[str] = None

    logprob: Optional[float] = None

    top_logprobs: Optional[List[LogprobsContentTopLogprob]] = None


class Logprobs(BaseModel):
    content: Optional[List[LogprobsContent]] = None


class Metric(BaseModel):
    metric: str

    value: float

    unit: Optional[str] = None


class CompletionCreateResponse(BaseModel):
    id: str

    completion_message: CompletionMessage

    logprobs: Optional[Logprobs] = None

    metrics: Optional[List[Metric]] = None
