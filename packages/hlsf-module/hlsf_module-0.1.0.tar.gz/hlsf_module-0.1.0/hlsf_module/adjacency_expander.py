"""Expansion helper retrieving semantic neighbours via an LLM."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Dict, List, Tuple, Sequence
import asyncio
import json
import logging
import os
import time

from .llm_client import RetrievalClient, LLMClient
from .llm_weights import TrainingDB
from .symbols.schema import SymbolToken

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

# Cache structure: (modality, token_id, count, prompt_template) -> List[JSON]
_CACHE: Dict[Tuple[str, int, int, str], List[str]] = {}
# Frequency counter for simple weight calibration
_FREQ: Counter[str] = Counter()

logger = logging.getLogger(__name__)


def clear_cache() -> None:
    """Reset internal caches used by the expander."""

    _CACHE.clear()
    _FREQ.clear()

async def expand(
    token: SymbolToken,
    llm: LLMClient | None = None,
    *,
    training_db: TrainingDB | None = None,
    update: bool = False,
    neighbor_count: int | None = None,
    banned_words: Sequence[str] | None = None,
) -> List[str]:
    """Expand ``token`` into a list of JSON encoded neighbour tokens.

    Parameters
    ----------
    token:
        Seed token.
    llm:
        Client capable of providing semantic neighbours.  When ``None`` the
        function returns an empty list.
    training_db:
        Optional database receiving adjacency edges when ``update`` is ``True``.
    update:
        When set, store the discovered edges in ``training_db``.
    neighbor_count:
        Optional override for the number of neighbours to request.  Falls back
        to the ``ADJ_NEIGHBOR_COUNT`` environment variable which defaults to 2.
    banned_words:
        Optional collection of words to filter from the returned neighbours.
        When omitted the value of ``ADJ_BANNED_WORDS`` environment variable is
        used (default: ``"badword"``).
    """

    count = neighbor_count or int(os.getenv("ADJ_NEIGHBOR_COUNT", "2"))
    logger.info(
        "expanding token",
        extra={"token_id": token.id, "mod": token.mod, "count": count},
    )
    prompt_template = os.getenv(
        "ADJ_PROMPT_TEMPLATE",
        "Provide {count} distinct words that are semantic neighbors of '{text}'. Return them separated by commas.",
    )

    if llm is None:
        if training_db is None:
            logger.warning("No LLM client provided; returning empty list")
            return []
        key = (token.mod, token.id, count, "__embed__")
        if key in _CACHE:
            return list(_CACHE[key])
        neighbors: List[Tuple[int, float]] = []
        for (a, b), w in training_db.connections.items():
            if a == token.id:
                neighbors.append((b, w))
            elif b == token.id:
                neighbors.append((a, w))
        neighbors.sort(key=lambda x: x[1], reverse=True)
        out: List[str] = []
        now = time.time()
        for nid, w in neighbors[:count]:
            new_token = SymbolToken(t=token.t, id=nid, mod=token.mod, feat={}, w=w)
            out.append(json.dumps(asdict(new_token)))
            if update:
                training_db.add_edge(token, new_token, w, timestamp=now)
        _CACHE[key] = list(out)
        return out


    key = (token.mod, token.id, count, prompt_template)
    if key in _CACHE:
        return list(_CACHE[key])

    # Determine textual representation for prompts
    if "char" in token.feat:
        token_text = chr(int(token.feat["char"]))
    else:
        token_text = token.feat.get("text", str(token.id))

    raw = await llm.neighbors(
        token_text, count=count, prompt_template=prompt_template
    )

    banned = {
        w.strip().lower()
        for w in (
            banned_words
            if banned_words is not None
            else os.getenv("ADJ_BANNED_WORDS", "badword").split(",")
        )
        if w.strip()
    }
    neighbors = [n for n in raw if n.lower() not in banned]

    out: List[str] = []
    now = time.time()
    for word in neighbors[:count]:
        weight = 1.0 / (_FREQ[word.lower()] + 1.0)
        new_token = SymbolToken(
            t=token.t,
            id=hash((token.mod, word)) & 0x7FFFFFFF,
            mod=token.mod,
            feat={"text": word},
            w=weight,
        )
        out.append(json.dumps(asdict(new_token)))
        _FREQ[word.lower()] += 1
        if update and training_db is not None:
            training_db.add_edge(token, new_token, weight, timestamp=now)

    _CACHE[key] = list(out)
    logger.info(
        "adjacency expansion complete",
        extra={"token_id": token.id, "neighbors": len(out)},
    )
    return out

