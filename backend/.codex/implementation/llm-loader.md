# LLM Loader

The loader in `backend/llms/loader.py` wraps several LangChain-compatible backends behind a single streaming interface.

## Supported Models
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- `google/gemma-3-4b-it`
- `gguf` models via `llama.cpp`

## Configuration
- `AF_LLM_MODEL` selects the backend. It defaults to the DeepSeek model.
- `AF_GGUF_PATH` provides the path to the GGUF file when using `gguf`.

`load_llm()` returns an object exposing `async generate_stream(text: str) -> AsyncIterator[str]`.
