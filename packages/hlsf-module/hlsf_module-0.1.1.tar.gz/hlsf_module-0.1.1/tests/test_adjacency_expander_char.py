import asyncio
import logging
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio

from hlsf_module.adjacency_expander import expand, clear_cache
from hlsf_module.symbols.schema import SymbolToken
from hlsf_module.llm_client import StubLLMClient


class RecordingLLM(StubLLMClient):
    async def neighbors(self, text: str, *, count: int, prompt_template: str):
        self.last = text
        return await super().neighbors(text, count=count, prompt_template=prompt_template)


def test_expand_uses_char_field():
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={"char": ord("A")})
    llm = RecordingLLM(["foo"])
    asyncio.run(expand(token, llm))
    assert llm.last == "A"


def test_expand_without_llm_returns_empty(caplog):
    clear_cache()
    token = SymbolToken(t=0, id=1, mod="x", feat={})
    with caplog.at_level(logging.WARNING):
        assert asyncio.run(expand(token)) == []
        assert "No LLM client provided" in caplog.text

