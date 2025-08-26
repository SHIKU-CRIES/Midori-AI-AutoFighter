# Implement LangChain-based LLM loader

## Summary
Build a new loader in `backend/llms/` that uses LangChain to interface with multiple local or remote models. The loader should support `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`, `google/gemma-3-4b-it`, and a shardable GGUF reasoning model. Expose a unified API for inference and allow model selection via configuration.

## Why
LLM interactions currently require manual model setup. A standardized loader enables consistent inference across hardware profiles and simplifies adding or switching models.

## Requirements
- [ ] Create a LangChain-based loader module under `backend/llms/` with a single public interface for loading and running models.
- [ ] Support the following model backends using the existing LangChain HuggingFace local interface:
  - `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`.
  - `google/gemma-3-4b-it`.
  - A shardable GGUF reasoning model (use `llama.cpp` or equivalent with optional shard configuration).
- [ ] Provide configuration options (env vars or settings module) to select the model. Hardware acceleration is determined by the backend setup.
- [ ] Ensure each backend implements a common asynchronous, streaming prediction method (e.g., `async generate_stream(text: str) -> AsyncIterator[str]`).
- [ ] Add unit tests verifying loader selection and basic inference for each model.
- [ ] Update `backend/README.md` and add an `.codex/implementation` document explaining the loader and configuration.
- [ ] Ensure new files follow repository import style, file size guidance, and are referenced in the PR template checklist.

## Acceptance Criteria
- Loader can instantiate each target model and return text for a prompt.
- Selecting a model via configuration switches behavior without code changes.
- Tests pass and demonstrate the loader choosing different backends.
- Documentation covers setup steps and usage for all supported models.
