# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ChatCompletionMessage",
    "FunctionCall",
    "MultiContent",
    "MultiContentImageURL",
    "ToolCall",
    "ToolCallFunction",
]


class FunctionCall(BaseModel):
    arguments: Optional[str] = None

    name: Optional[str] = None


class MultiContentImageURL(BaseModel):
    detail: Optional[str] = None

    url: Optional[str] = None


class MultiContent(BaseModel):
    image_url: Optional[MultiContentImageURL] = None

    text: Optional[str] = None

    type: Optional[str] = None


class ToolCallFunction(BaseModel):
    arguments: Optional[str] = None

    name: Optional[str] = None


class ToolCall(BaseModel):
    function: ToolCallFunction

    type: str

    id: Optional[str] = None

    index: Optional[int] = None


class ChatCompletionMessage(BaseModel):
    content: str

    role: str

    function_call: Optional[FunctionCall] = None

    multi_content: Optional[List[MultiContent]] = FieldInfo(alias="MultiContent", default=None)

    name: Optional[str] = None

    reasoning_content: Optional[str] = None

    refusal: Optional[str] = None

    tool_call_id: Optional[str] = None

    tool_calls: Optional[List[ToolCall]] = None
