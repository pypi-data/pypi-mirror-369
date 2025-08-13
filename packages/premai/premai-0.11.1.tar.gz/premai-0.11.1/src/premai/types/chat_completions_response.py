# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ChatCompletionsResponse", "Choice", "ChoiceMessage", "Usage"]


class ChoiceMessage(BaseModel):
    content: Optional[str] = None

    role: Literal["assistant"]


class Choice(BaseModel):
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"]

    index: int

    message: ChoiceMessage


class Usage(BaseModel):
    completion_tokens: int

    prompt_tokens: int

    total_tokens: int


class ChatCompletionsResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    model: str

    object: Literal["chat.completion"]

    system_fingerprint: Optional[str] = None

    usage: Optional[Usage] = None
