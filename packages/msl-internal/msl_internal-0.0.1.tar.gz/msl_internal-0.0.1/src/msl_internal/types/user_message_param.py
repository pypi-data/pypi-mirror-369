# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .message_text_content_item_param import MessageTextContentItemParam
from .message_image_content_item_param import MessageImageContentItemParam

__all__ = [
    "UserMessageParam",
    "ContentUnionMember1",
    "ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItem",
    "ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItemVideoURL",
    "ContentUnionMember1LlmStefiLlamaStackRequestFileContentItem",
    "ContentUnionMember1LlmStefiLlamaStackRequestFileContentItemFile",
]


class ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItemVideoURL(TypedDict, total=False):
    url: str


class ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItem(TypedDict, total=False):
    type: Required[Literal["video_url"]]

    video_url: Required[ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItemVideoURL]


class ContentUnionMember1LlmStefiLlamaStackRequestFileContentItemFile(TypedDict, total=False):
    file_data: str

    file_id: str

    filename: str


class ContentUnionMember1LlmStefiLlamaStackRequestFileContentItem(TypedDict, total=False):
    file: Required[ContentUnionMember1LlmStefiLlamaStackRequestFileContentItemFile]

    type: Required[Literal["file"]]


ContentUnionMember1: TypeAlias = Union[
    MessageImageContentItemParam,
    MessageTextContentItemParam,
    ContentUnionMember1LlmStefiLlamaStackRequestVideoContentItem,
    ContentUnionMember1LlmStefiLlamaStackRequestFileContentItem,
]


class UserMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ContentUnionMember1]]]

    role: Required[Literal["user"]]
