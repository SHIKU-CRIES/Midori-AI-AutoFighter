import os
import asyncio

from enum import Enum
from typing import Protocol
from collections.abc import AsyncIterator

from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_community.llms import LlamaCpp


class SupportsStream(Protocol):
    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        ...


class ModelName(str, Enum):
    DEEPSEEK = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    GEMMA = "google/gemma-3-4b-it"
    GGUF = "gguf"


class _LangChainWrapper:
    def __init__(self, llm) -> None:
        self._llm = llm

    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        result = await asyncio.to_thread(self._llm.invoke, text)
        yield result


def load_llm(model: str | None = None, *, gguf_path: str | None = None) -> SupportsStream:
    name = model or os.getenv("AF_LLM_MODEL", ModelName.DEEPSEEK.value)
    if name == ModelName.DEEPSEEK.value:
        pipe = pipeline("text-generation", model=ModelName.DEEPSEEK.value)
        return _LangChainWrapper(HuggingFacePipeline(pipeline=pipe))
    if name == ModelName.GEMMA.value:
        pipe = pipeline("text-generation", model=ModelName.GEMMA.value)
        return _LangChainWrapper(HuggingFacePipeline(pipeline=pipe))
    if name == ModelName.GGUF.value:
        path = gguf_path or os.getenv("AF_GGUF_PATH")
        if path is None:
            msg = "GGUF model path must be provided via argument or AF_GGUF_PATH"
            raise ValueError(msg)
        return _LangChainWrapper(LlamaCpp(model_path=path))
    msg = f"Unsupported model: {name}"
    raise ValueError(msg)


__all__ = ["ModelName", "load_llm", "SupportsStream"]
