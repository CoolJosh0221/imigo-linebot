# Evaluating LINE bot quality and model upgrades

The configured Qwen-SEA-LION-v4-32B-IT-4BIT remains available. AI Singapore links
[Qwen-SEA-LION-v4.5-27B-IT](https://huggingface.co/aisingapore/Qwen-SEA-LION-v4.5-27B-IT)
as a newer model. The default stays on v4 until a replacement has been tested.
The v4.5 full-precision model is not an equivalent memory replacement for a
4-bit model; choose an appropriate quantization and check runtime support and
GPU memory before loading it. Never relabel old weights as a newer model.

## Run the synthetic evaluation

Start the desired model server separately. This command does not download or
switch models, initialize a database, contact LINE, or send messages to users:

```bash
LLM_CHAT_TEMPLATE_KWARGS='{"enable_thinking":false,"thinking_mode":"off"}' \
  .venv/bin/python -m scripts.evaluate_model \
  --base-url http://localhost:8001/v1 \
  --model aisingapore/Llama-SEA-LION-v3.5-8B-R \
  --output evals/results/sealion-v3.5.json
```

The command uses the existing `.env` for configuration. Repeat against each
candidate server/model and save separate reports. Check `/v1/models` first:
the requested model must match a served model ID. Results contain synthetic
answers, timings, literal preservation checks, and a human review rubric.
Use `--limit 3` for a quick translation smoke test.

The cases cover all six supported output languages, amounts, negation, dates,
workplace terms, embedded instructions, context recall, and official referrals.
Fluent speakers should score accuracy, naturalness, Traditional Chinese usage,
and unsupported additions from 1 to 5. Record GPU memory and repeat cases to
measure variability. Automatic literal checks alone cannot establish quality.

## Configuration and conversation context

- Both chat and translation use `MODEL_NAME`, `LLM_BASE_URL`, and `LLM_API_KEY`.
- Both compose files use `MODEL_NAME` as the served ID. `MODEL_PATH` optionally
  selects local weights, e.g. `/models/sealion-model`, mounted from `./models`.
- `LLM_CHAT_TEMPLATE_KWARGS` is a JSON object passed only to custom endpoints.
  SEA-LION v3.5 uses `thinking_mode: off`; Qwen SEA-LION uses `enable_thinking: false`.
  Use `{}` for providers without vLLM template support.
- `CHAT_HISTORY_MESSAGES=12` retrieves up to six recent exchanges. Whole turns
  fit into `CHAT_INPUT_MAX_BYTES=6000`, including system prompt and current input.
  Current messages are never silently truncated. This uses UTF-8 bytes, not an
  exact tokenizer count; the default reserves room under the compose server's
  8192-token context for up to 1000 output tokens and template overhead. With
  a 4096-token server, use a smaller input budget such as 3000 bytes.
- No long-term summaries are stored. `/clear` removes conversation history.
- Incomplete, empty, and explicit unfinished-thinking responses are rejected.

## Official referrals

`services/official_resources.py` supplies a small keyword-selected directory
for labor and immigration inquiries. Its source URLs and reviewed date are
stored with the facts. It does not fetch websites during a conversation and
does not establish legal eligibility, fees, or deadlines. Review the official
pages before updating the facts; expand the directory with source-backed entries.
Full document retrieval and persistent conversation summaries remain future work.
