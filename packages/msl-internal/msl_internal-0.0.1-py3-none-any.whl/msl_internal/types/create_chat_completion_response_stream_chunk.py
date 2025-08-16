# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "CreateChatCompletionResponseStreamChunk",
    "Event",
    "EventDelta",
    "EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseTextDelta",
    "EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDelta",
    "EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDeltaFunction",
    "EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseReasoningDelta",
    "EventMetric",
]


class EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseTextDelta(BaseModel):
    text: str

    type: str


class EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDeltaFunction(BaseModel):
    arguments: Optional[str] = None

    name: Optional[str] = None


class EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDelta(BaseModel):
    function: EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDeltaFunction

    type: str

    id: Optional[str] = None


class EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseReasoningDelta(BaseModel):
    reasoning: str

    type: str


EventDelta: TypeAlias = Union[
    EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseTextDelta,
    EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseToolCallDelta,
    EventDeltaLlmStefiLlamaAPIChatCompletionStreamingResponseReasoningDelta,
]


class EventMetric(BaseModel):
    metric: str

    value: float

    unit: Optional[str] = None


class Event(BaseModel):
    delta: EventDelta

    event_type: Literal["start", "complete", "progress", "metrics"]

    metrics: Optional[List[EventMetric]] = None

    stop_reason: Optional[str] = None


class CreateChatCompletionResponseStreamChunk(BaseModel):
    id: str

    event: Event
