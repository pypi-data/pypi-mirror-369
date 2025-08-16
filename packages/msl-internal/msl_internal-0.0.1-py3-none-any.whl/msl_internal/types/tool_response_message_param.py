# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .message_text_content_item_param import MessageTextContentItemParam

__all__ = ["ToolResponseMessageParam"]


class ToolResponseMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[MessageTextContentItemParam]]]

    role: Required[Literal["tool"]]

    tool_call_id: Required[str]
