# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .message_text_content_item_param import MessageTextContentItemParam

__all__ = ["CompletionMessageParam", "Content", "ToolCall", "ToolCallFunction"]

Content: TypeAlias = Union[str, MessageTextContentItemParam]


class ToolCallFunction(TypedDict, total=False):
    arguments: Required[str]

    name: Required[str]


class ToolCall(TypedDict, total=False):
    id: Required[str]

    function: Required[ToolCallFunction]


class CompletionMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]

    content: Optional[Content]

    reasoning: str

    stop_reason: Literal["stop", "tool_calls", "length"]

    tool_calls: Iterable[ToolCall]
