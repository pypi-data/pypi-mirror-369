# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..user_message_param import UserMessageParam
from ..system_message_param import SystemMessageParam
from ..completion_message_param import CompletionMessageParam
from ..tool_response_message_param import ToolResponseMessageParam

__all__ = [
    "CompletionCreateParamsBase",
    "Message",
    "ResponseFormat",
    "ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchema",
    "ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchemaJsonSchema",
    "ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatText",
    "ToolChoice",
    "ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoice",
    "ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoiceFunction",
    "Tool",
    "ToolFunction",
    "CompletionCreateParamsNonStreaming",
    "CompletionCreateParamsStreaming",
]


class CompletionCreateParamsBase(TypedDict, total=False):
    messages: Required[Iterable[Message]]

    model: Required[str]

    logprobs: Optional[bool]

    max_completion_tokens: int

    repetition_penalty: float

    response_format: ResponseFormat

    store: bool

    temperature: float

    tool_choice: ToolChoice

    tools: Iterable[Tool]

    top_k: int

    top_logprobs: int

    top_p: float

    user: str


Message: TypeAlias = Union[UserMessageParam, SystemMessageParam, CompletionMessageParam, ToolResponseMessageParam]


class ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchemaJsonSchema(TypedDict, total=False):
    name: Required[str]

    description: str

    schema: Dict[str, object]

    strict: bool


class ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchema(TypedDict, total=False):
    json_schema: Required[ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchemaJsonSchema]

    type: Required[Literal["json_schema"]]


class ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatText(TypedDict, total=False):
    type: Required[Literal["text"]]


ResponseFormat: TypeAlias = Union[
    ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatJsonSchema,
    ResponseFormatLlmStefiLlamaStackOpenAIRequestResponseFormatText,
]


class ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoiceFunction(TypedDict, total=False):
    name: Required[str]


class ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoice(TypedDict, total=False):
    function: Required[ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoiceFunction]

    type: Required[Literal["function"]]


ToolChoice: TypeAlias = Union[
    Literal["auto", "required", "none"], ToolChoiceLlmStefiLlamaAPIChatCompletionNamedToolChoice
]


class ToolFunction(TypedDict, total=False):
    name: Required[str]

    description: str

    parameters: Dict[str, object]

    strict: bool


class Tool(TypedDict, total=False):
    function: Required[ToolFunction]

    type: Required[Literal["function"]]


class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase, total=False):
    stream: Literal[False]


class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Required[Literal[True]]


CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]
