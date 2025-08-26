from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import logging

from autofighter.character import CharacterType
from autofighter.stats import Stats
from plugins.damage_types import random_damage_type
from plugins.damage_types._base import DamageTypeBase

log = logging.getLogger(__name__)


@dataclass
class PlayerBase(Stats):
    plugin_type = "player"

    hp: int = 1000
    max_hp: int = 1000
    atk: int = 100
    defense: int = 50
    char_type: CharacterType = CharacterType.C
    prompt: str = "Player prompt placeholder"
    about: str = "Player description placeholder"

    exp: int = 1
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    crit_rate: float = 0.05
    crit_damage: float = 2
    effect_hit_rate: float = 0.01
    damage_type: DamageTypeBase = field(default_factory=random_damage_type)

    mitigation: float = 1.0
    regain: int = 1
    dodge_odds: float = 0
    effect_resistance: float = 1.0

    vitality: float = 1.0
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
        try:
            from langchain.memory import VectorStoreRetrieverMemory
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
        except (ImportError, ModuleNotFoundError):
            try:
                from langchain.memory import ConversationBufferMemory
            except (ImportError, ModuleNotFoundError):
                class ConversationBufferMemory:  # type: ignore[override]
                    def __init__(self) -> None:
                        self._history: list[tuple[str, str]] = []

                    def save_context(
                        self,
                        inputs: dict[str, str],
                        outputs: dict[str, str],
                    ) -> None:
                        self._history.append(
                            (inputs.get("input", ""), outputs.get("output", ""))
                        )

                    def load_memory_variables(self, _: dict[str, str]) -> dict[str, str]:
                        lines: list[str] = []
                        for human, ai in self._history:
                            if human:
                                lines.append(f"Human: {human}")
                            if ai:
                                lines.append(f"AI: {ai}")
                        return {"history": "\n".join(lines)}

            self.lrm_memory = ConversationBufferMemory()
            return

        run = getattr(self, "run_id", "run")
        ident = getattr(self, "id", type(self).__name__)
        collection = f"{run}-{ident}"
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
        try:
            store = Chroma(
                collection_name=collection,
                embedding_function=embeddings,
            )
        except Exception:
            from langchain.memory import ConversationBufferMemory

            self.lrm_memory = ConversationBufferMemory()
            return

        self.lrm_memory = VectorStoreRetrieverMemory(
            retriever=store.as_retriever()
        )

    def adjust_stat_on_gain(self, stat_name: str, amount: int) -> None:
        target = self.stat_gain_map.get(stat_name, stat_name)
        log.debug(
            "%s gaining %s: %s",
            getattr(self, "id", type(self).__name__),
            target,
            amount,
        )
        super().adjust_stat_on_gain(target, amount)

    def adjust_stat_on_loss(self, stat_name: str, amount: int) -> None:
        target = self.stat_loss_map.get(stat_name, stat_name)
        log.debug(
            "%s losing %s: %s",
            getattr(self, "id", type(self).__name__),
            target,
            amount,
        )
        super().adjust_stat_on_loss(target, amount)

    async def send_lrm_message(self, message: str) -> str:
        try:
            from llms.loader import load_llm
        except Exception:
            class _LLM:
                async def generate_stream(self, text: str):
                    yield ""

            llm = _LLM()
        else:
            llm = load_llm()
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
