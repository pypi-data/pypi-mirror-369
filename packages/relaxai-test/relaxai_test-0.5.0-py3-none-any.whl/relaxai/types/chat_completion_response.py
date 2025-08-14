# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.openai_usage import OpenAIUsage
from .chat_completion_message import ChatCompletionMessage

__all__ = [
    "ChatCompletionResponse",
    "Choice",
    "ChoiceContentFilterResults",
    "ChoiceContentFilterResultsHate",
    "ChoiceContentFilterResultsJailbreak",
    "ChoiceContentFilterResultsProfanity",
    "ChoiceContentFilterResultsSelfHarm",
    "ChoiceContentFilterResultsSexual",
    "ChoiceContentFilterResultsViolence",
    "ChoiceLogprobs",
    "ChoiceLogprobsContent",
    "ChoiceLogprobsContentTopLogprob",
    "PromptFilterResult",
    "PromptFilterResultContentFilterResults",
    "PromptFilterResultContentFilterResultsHate",
    "PromptFilterResultContentFilterResultsJailbreak",
    "PromptFilterResultContentFilterResultsProfanity",
    "PromptFilterResultContentFilterResultsSelfHarm",
    "PromptFilterResultContentFilterResultsSexual",
    "PromptFilterResultContentFilterResultsViolence",
]


class ChoiceContentFilterResultsHate(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class ChoiceContentFilterResultsJailbreak(BaseModel):
    detected: bool

    filtered: bool


class ChoiceContentFilterResultsProfanity(BaseModel):
    detected: bool

    filtered: bool


class ChoiceContentFilterResultsSelfHarm(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class ChoiceContentFilterResultsSexual(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class ChoiceContentFilterResultsViolence(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class ChoiceContentFilterResults(BaseModel):
    hate: Optional[ChoiceContentFilterResultsHate] = None

    jailbreak: Optional[ChoiceContentFilterResultsJailbreak] = None

    profanity: Optional[ChoiceContentFilterResultsProfanity] = None

    self_harm: Optional[ChoiceContentFilterResultsSelfHarm] = None

    sexual: Optional[ChoiceContentFilterResultsSexual] = None

    violence: Optional[ChoiceContentFilterResultsViolence] = None


class ChoiceLogprobsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    bytes: Optional[str] = None


class ChoiceLogprobsContent(BaseModel):
    token: str

    logprob: float

    top_logprobs: List[ChoiceLogprobsContentTopLogprob]

    bytes: Optional[str] = None


class ChoiceLogprobs(BaseModel):
    content: List[ChoiceLogprobsContent]


class Choice(BaseModel):
    finish_reason: str

    index: int

    message: ChatCompletionMessage

    content_filter_results: Optional[ChoiceContentFilterResults] = None

    logprobs: Optional[ChoiceLogprobs] = None


class PromptFilterResultContentFilterResultsHate(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class PromptFilterResultContentFilterResultsJailbreak(BaseModel):
    detected: bool

    filtered: bool


class PromptFilterResultContentFilterResultsProfanity(BaseModel):
    detected: bool

    filtered: bool


class PromptFilterResultContentFilterResultsSelfHarm(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class PromptFilterResultContentFilterResultsSexual(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class PromptFilterResultContentFilterResultsViolence(BaseModel):
    filtered: bool

    severity: Optional[str] = None


class PromptFilterResultContentFilterResults(BaseModel):
    hate: Optional[PromptFilterResultContentFilterResultsHate] = None

    jailbreak: Optional[PromptFilterResultContentFilterResultsJailbreak] = None

    profanity: Optional[PromptFilterResultContentFilterResultsProfanity] = None

    self_harm: Optional[PromptFilterResultContentFilterResultsSelfHarm] = None

    sexual: Optional[PromptFilterResultContentFilterResultsSexual] = None

    violence: Optional[PromptFilterResultContentFilterResultsViolence] = None


class PromptFilterResult(BaseModel):
    index: int

    content_filter_results: Optional[PromptFilterResultContentFilterResults] = None


class ChatCompletionResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    model: str

    object: str

    system_fingerprint: str

    usage: OpenAIUsage

    prompt_filter_results: Optional[List[PromptFilterResult]] = None
