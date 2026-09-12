"""Shared model client settings and response validation."""

import os

from openai import AsyncOpenAI

from config import BotConfig


def create_client(config: BotConfig) -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=config.llm_base_url or None,
        api_key=os.getenv("LLM_API_KEY") or "dummy-key",
        timeout=config.llm_timeout,
        max_retries=1,
    )


def generation_options(config: BotConfig) -> dict:
    if config.llm_base_url and config.chat_template_kwargs:
        return {"extra_body": {"chat_template_kwargs": config.chat_template_kwargs}}
    return {}


def completion_text(response) -> str:
    """Reject incomplete answers and remove a model's explicit thinking section."""
    if not response.choices:
        raise ValueError("The model returned no answer")
    choice = response.choices[0]
    if choice.finish_reason != "stop":
        raise ValueError(
            "The model did not finish its answer; please try a shorter request"
        )
    text = (choice.message.content or "").strip()
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1].strip()
    elif "<think>" in text:
        raise ValueError("The model returned unfinished reasoning")
    if not text:
        raise ValueError("The model returned an empty answer")
    return text
