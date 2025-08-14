# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Required, TypedDict

from .chat_completion_message_param import ChatCompletionMessageParam

__all__ = [
    "ChatCreateCompletionParams",
    "Function",
    "Prediction",
    "ResponseFormat",
    "ResponseFormatJsonSchema",
    "StreamOptions",
    "Tool",
    "ToolFunction",
]


class ChatCreateCompletionParams(TypedDict, total=False):
    messages: Required[Iterable[ChatCompletionMessageParam]]

    model: Required[str]

    chat_template_kwargs: object

    frequency_penalty: float

    function_call: object

    functions: Iterable[Function]

    logit_bias: Dict[str, int]

    logprobs: bool

    max_completion_tokens: int

    max_tokens: int

    metadata: Dict[str, str]

    n: int

    parallel_tool_calls: object

    prediction: Prediction

    presence_penalty: float

    reasoning_effort: str

    response_format: ResponseFormat

    seed: int

    stop: List[str]

    store: bool

    stream: bool

    stream_options: StreamOptions

    temperature: float

    tool_choice: object

    tools: Iterable[Tool]

    top_logprobs: int

    top_p: float

    user: str


class Function(TypedDict, total=False):
    name: Required[str]

    parameters: Required[object]

    description: str

    strict: bool


class Prediction(TypedDict, total=False):
    content: Required[str]

    type: Required[str]


class ResponseFormatJsonSchema(TypedDict, total=False):
    name: Required[str]

    strict: Required[bool]

    description: str


class ResponseFormat(TypedDict, total=False):
    json_schema: ResponseFormatJsonSchema

    type: str


class StreamOptions(TypedDict, total=False):
    include_usage: bool


class ToolFunction(TypedDict, total=False):
    name: Required[str]

    parameters: Required[object]

    description: str

    strict: bool


class Tool(TypedDict, total=False):
    type: Required[str]

    function: ToolFunction
