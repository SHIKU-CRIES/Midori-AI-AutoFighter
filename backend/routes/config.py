from __future__ import annotations

from llms.loader import ModelName
from options import get_option
from options import set_option
from quart import Blueprint
from quart import jsonify
from quart import request

bp = Blueprint("config", __name__, url_prefix="/config")

_OPTION_KEY = "lrm_model"


@bp.get("/lrm")
async def get_lrm_config() -> tuple[str, int, dict[str, object]]:
    current = get_option(_OPTION_KEY, ModelName.DEEPSEEK.value)
    models = [m.value for m in ModelName]
    return jsonify({"current_model": current, "available_models": models})


@bp.post("/lrm")
async def set_lrm_model() -> tuple[str, int, dict[str, str]]:
    data = await request.get_json()
    model = data.get("model", "")
    if model not in [m.value for m in ModelName]:
        return jsonify({"error": "invalid model"}), 400
    set_option(_OPTION_KEY, model)
    return jsonify({"current_model": model})


@bp.post("/lrm/test")
async def test_lrm_model() -> tuple[str, int, dict[str, str]]:
    import asyncio

    from llms.loader import load_llm

    data = await request.get_json()
    prompt = data.get("prompt", "")
    model = get_option(_OPTION_KEY, ModelName.DEEPSEEK.value)

    # Load LLM in thread pool to avoid blocking the event loop
    llm = await asyncio.to_thread(load_llm, model)
    reply = ""
    async for chunk in llm.generate_stream(prompt):
        reply += chunk
    return jsonify({"response": reply})
