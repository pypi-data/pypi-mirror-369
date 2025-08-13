# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionsParams", "Message", "ResponseFormat"]


class ChatCompletionsParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]

    model: Required[str]

    frequency_penalty: float

    max_completion_tokens: Optional[int]

    presence_penalty: float

    response_format: ResponseFormat

    seed: int

    stop: Union[str, List[str]]

    stream: bool

    temperature: Optional[float]

    tool_choice: Union[Literal["none", "auto"], object]

    tools: Iterable[object]

    top_p: Optional[float]


class Message(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["system", "user", "assistant"]]


class ResponseFormat(TypedDict, total=False):
    json_schema: Required[Dict[str, object]]

    type: Required[Literal["text", "json_schema"]]
