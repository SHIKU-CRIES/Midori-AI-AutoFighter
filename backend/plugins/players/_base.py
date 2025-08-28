from __future__ import annotations

import copy
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
import logging

from autofighter.character import CharacterType
from autofighter.stats import Stats
from plugins.damage_types import random_damage_type
from plugins.damage_types._base import DamageTypeBase

# Module-level cache to avoid repeatedly loading SentenceTransformer
_EMBEDDINGS: object | None = None

log = logging.getLogger(__name__)


class SimpleConversationMemory:
    """Lightweight, dependency-free memory used as a safe default.

    Provides the minimal interface expected by PlayerBase methods without
    bringing in external dependencies that can break deepcopy/pickling.
    """

    def __init__(self) -> None:
        self._history: list[tuple[str, str]] = []

    def save_context(self, inputs: dict[str, str], outputs: dict[str, str]) -> None:
        self._history.append((inputs.get("input", ""), outputs.get("output", "")))

    def load_memory_variables(self, _: dict[str, str]) -> dict[str, str]:
        lines: list[str] = []
        for human, ai in self._history:
            if human:
                lines.append(f"Human: {human}")
            if ai:
                lines.append(f"AI: {ai}")
        return {"history": "\n".join(lines)}


@dataclass
class PlayerBase(Stats):
    plugin_type = "player"

    # Override Stats defaults with PlayerBase-specific values
    hp: int = 1000
    char_type: CharacterType = CharacterType.C
    prompt: str = "Player prompt placeholder"
    about: str = "Player description placeholder"

    exp: int = 1
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    damage_type: DamageTypeBase = field(default_factory=random_damage_type)

    action_points: int = 1
    damage_taken: int = 1
    damage_dealt: int = 1
    kills: int = 1

    last_damage_taken: int = 1

    passives: list[str] = field(default_factory=list)
    dots: list[str] = field(default_factory=list)
    hots: list[str] = field(default_factory=list)

    stat_gain_map: dict[str, str] = field(default_factory=dict)
    stat_loss_map: dict[str, str] = field(default_factory=dict)
    lrm_memory: object | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        # Initialize base stats with PlayerBase defaults
        self._base_max_hp = 1000
        self._base_atk = 100
        self._base_defense = 50
        self._base_crit_rate = 0.05
        self._base_crit_damage = 2.0
        self._base_effect_hit_rate = 0.01
        self._base_mitigation = 1.0
        self._base_regain = 1
        self._base_dodge_odds = 0.0
        self._base_effect_resistance = 1.0
        self._base_vitality = 1.0

        # Call parent post_init
        super().__post_init__()

        # Use centralized torch checker instead of individual import attempts
        from llms.torch_checker import is_torch_available

        if not is_torch_available():
            # Fall back to simple in-process memory without dependencies
            self.lrm_memory = SimpleConversationMemory()
            return

        try:
            from langchain.memory import VectorStoreRetrieverMemory
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings
        except (ImportError, ModuleNotFoundError):
            # Fallback if imports still fail despite torch being available
            self.lrm_memory = SimpleConversationMemory()
            return

        run = getattr(self, "run_id", "run")
        ident = getattr(self, "id", type(self).__name__)
        collection = f"{run}-{ident}"
        global _EMBEDDINGS
        if _EMBEDDINGS is None:
            _EMBEDDINGS = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
            )
        embeddings = _EMBEDDINGS
        try:
            store = Chroma(
                collection_name=collection,
                embedding_function=embeddings,
            )
        except Exception:
            # If vector store init fails, use simple memory
            self.lrm_memory = SimpleConversationMemory()
            return

        self.lrm_memory = VectorStoreRetrieverMemory(
            retriever=store.as_retriever()
        )

    def __deepcopy__(self, memo):  # type: ignore[override]
        """Custom deepcopy that skips copying non-serializable memory bindings.

        - Deep-copies all dataclass fields except `lrm_memory`.
        - Replaces `lrm_memory` with a fresh SimpleConversationMemory instance.
        This avoids pydantic/langchain binding errors during deepcopy while
        ensuring lists/dicts are independently copied for battle simulation.
        """
        cls = type(self)
        result = cls.__new__(cls)  # Do not call __init__/__post_init__
        memo[id(self)] = result
        for f in fields(cls):
            name = f.name
            if name == "lrm_memory":
                setattr(result, name, SimpleConversationMemory())
                continue
            val = getattr(self, name)
            setattr(result, name, copy.deepcopy(val, memo))
        return result


    async def send_lrm_message(self, message: str) -> str:
        import asyncio

        from llms.torch_checker import is_torch_available

        if not is_torch_available():
            # Return empty response but still save context
            response = ""
            self.lrm_memory.save_context({"input": message}, {"output": response})
            return response

        try:
            from llms.loader import load_llm
            # Load LLM in thread pool to avoid blocking the event loop
            llm = await asyncio.to_thread(load_llm)
        except Exception:
            # Fallback to empty LLM if loading fails
            class _LLM:
                async def generate_stream(self, text: str):
                    yield ""
            llm = _LLM()

        context = self.lrm_memory.load_memory_variables({}).get("history", "")
        prompt = f"{context}\n{message}".strip()
        chunks: list[str] = []
        async for chunk in llm.generate_stream(prompt):
            chunks.append(chunk)
        response = "".join(chunks)
        self.lrm_memory.save_context({"input": message}, {"output": response})
        return response

    async def receive_lrm_message(self, message: str) -> None:
        self.lrm_memory.save_context({"input": ""}, {"output": message})
