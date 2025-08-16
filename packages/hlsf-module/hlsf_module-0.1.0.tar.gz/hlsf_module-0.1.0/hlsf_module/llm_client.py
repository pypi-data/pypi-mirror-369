"""Client helpers for retrieving semantic neighbours via LLM providers.

This module now defines a small pluggable architecture where the public
``LLMClient`` delegates neighbour lookups to provider specific classes.  The
``LLMClient`` itself adds a tiny in-memory cache and exposes a uniform
asynchronous interface used throughout the project.  Provider implementations
only need to implement :class:`RetrievalClient` which consists of a single
``neighbors`` coroutine.

Two concrete providers are supplied:

``OpenAIProvider``
    Uses the OpenAI chat completion API (identical behaviour to the previous
    implementation).
``EmbeddingLLMClient``
    Loads local embeddings and performs cosine similarity search without any
    network traffic.

The active provider can be chosen via the ``provider`` constructor argument or
by setting the ``LLM_PROVIDER`` environment variable.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Protocol, Sequence, Tuple
import asyncio
import logging
import os
import time
import json
import math

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------


class RetrievalClient(Protocol):
    """Common interface implemented by all LLM neighbour providers."""

    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:
        """Return semantic neighbours for ``text``."""


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


class OpenAIProvider:
    """Provider querying the OpenAI API for neighbouring words."""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
        backoff: float = 1.0,
    ) -> None:
        self.model = model or os.getenv("ADJ_MODEL", "gpt-3.5-turbo")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.max_retries = max_retries
        self.backoff = backoff

    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:
        return await asyncio.to_thread(
            self._neighbors_sync, text, count, prompt_template
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _neighbors_sync(
        self, text: str, count: int, prompt_template: str
    ) -> List[str]:
        try:  # pragma: no cover - optional dependency
            import openai  # type: ignore
            from openai.error import OpenAIError  # type: ignore
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("OpenAI package not available: %s", exc)
            return []

        if self.api_key:
            openai.api_key = self.api_key

        prompt = prompt_template.format(text=text, count=count)

        for attempt in range(1, self.max_retries + 1):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You suggest semantic neighbors for tokens.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    n=1,
                )
                content = response["choices"][0]["message"]["content"]
                return [
                    n.strip()
                    for n in content.replace("\n", ",").split(",")
                    if n.strip()
                ]
            except OpenAIError as exc:  # pragma: no cover - network failures
                if attempt == self.max_retries:
                    logger.error("OpenAI request failed: %s", exc)
                    break
                wait = self.backoff * (2 ** (attempt - 1))
                logger.warning(
                    "OpenAI request failed (%s). Retrying in %.1f s", exc, wait
                )
                time.sleep(wait)
            except Exception as exc:  # pragma: no cover - unexpected errors
                logger.error("OpenAI request failed: %s", exc)
                break
        return []


class EmbeddingLLMClient:
    """Provider retrieving neighbours from local embeddings.

    Parameters
    ----------
    embeddings:
        Either a mapping ``word -> vector`` or a path to a JSON file containing
        such a mapping.  Vectors are expected to be sequences of floats.
    """

    def __init__(self, embeddings: Mapping[str, Sequence[float]] | str) -> None:
        if isinstance(embeddings, str):
            with open(embeddings, "r", encoding="utf8") as f:
                embeddings = json.load(f)
        self.embeddings = {
            word: [float(v) for v in vec] for word, vec in embeddings.items()
        }

    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:  # pragma: no cover - simple math
        if text not in self.embeddings:
            return []
        query = self.embeddings[text]
        sims: List[Tuple[float, str]] = []
        norm_q = math.sqrt(sum(v * v for v in query))
        for word, vec in self.embeddings.items():
            if word == text:
                continue
            norm_v = math.sqrt(sum(v * v for v in vec))
            denom = norm_q * norm_v
            if denom == 0.0:
                continue
            dot = sum(a * b for a, b in zip(query, vec))
            sims.append((dot / denom, word))

        sims.sort(reverse=True)
        return [w for _, w in sims[:count]]


# ---------------------------------------------------------------------------
# Public delegating client
# ---------------------------------------------------------------------------


class LLMClient:
    """Wrapper adding caching on top of a provider implementation."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
        backoff: float = 1.0,
        *,
        provider: RetrievalClient | None = None,
        provider_name: str | None = None,
        **provider_kwargs,
    ) -> None:
        if provider is None:
            name = provider_name or os.getenv("LLM_PROVIDER", "openai")
            provider = self._create_provider(
                name,
                model=model,
                api_key=api_key,
                max_retries=max_retries,
                backoff=backoff,
                **provider_kwargs,
            )
        self.provider = provider
        self._cache: Dict[Tuple[str, int, str], List[str]] = {}

    # ------------------------------------------------------------------
    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:
        """Return ``count`` semantic neighbours for ``text``."""

        key = (text, count, prompt_template)
        if key in self._cache:
            return list(self._cache[key])

        result = await self.provider.neighbors(
            text, count=count, prompt_template=prompt_template
        )
        self._cache[key] = list(result)
        return list(result)

    # ------------------------------------------------------------------
    @staticmethod
    def _create_provider(
        name: str,
        *,
        model: str | None,
        api_key: str | None,
        max_retries: int,
        backoff: float,
        **kwargs,
    ) -> RetrievalClient:
        name = name.lower()
        if name == "openai":
            return OpenAIProvider(
                model=model, api_key=api_key, max_retries=max_retries, backoff=backoff
            )
        if name == "embedding":
            return EmbeddingLLMClient(**kwargs)
        raise ValueError(f"Unknown LLM provider: {name}")


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class StubLLMClient:
    """Deterministic implementation used for tests and examples."""

    def __init__(
        self, responses: Sequence[str], delay: float = 0.0, fail: bool = False
    ) -> None:
        self.responses = list(responses)
        self.delay = delay
        self.fail = fail
        self.calls = 0

    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:  # noqa: D401 - short delegate
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.fail:
            raise RuntimeError("stub failure")
        return list(self.responses)[:count]


class StubEmbeddingClient:
    """Simple mapping based embedding retriever for tests."""

    def __init__(self, mapping: Mapping[str, Sequence[str]], delay: float = 0.0):
        self.mapping = {k: list(v) for k, v in mapping.items()}
        self.delay = delay
        self.calls = 0

    async def neighbors(
        self, text: str, *, count: int, prompt_template: str
    ) -> List[str]:
        self.calls += 1
        if self.delay:
            await asyncio.sleep(self.delay)
        return self.mapping.get(text, [])[:count]


# Backwards compatibility alias; previously code imported ``OpenAIClient``
# directly.  ``LLMClient`` now provides the required functionality so we expose
# a compatible name.
OpenAIClient = LLMClient

