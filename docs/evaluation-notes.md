# Local evaluation, 2026-09-12

Model: `aisingapore/Llama-SEA-LION-v3.5-8B-R`, existing local weights on RTX 4090.
The improved branch was evaluated with thinking disabled, against the unchanged
deployment's vLLM endpoint. No LINE messages or production conversations were used.

- 9 of 13 strict literal checks passed in two prompt iterations.
- The conversation case recalled an appointment outside the former four-message window.
- Both official-referral cases included the expected hotline and source domain.
- Three translations changed date/time formatting while preserving the apparent
  meaning. These fail exact-format checks and need human review, not an automatic
  conclusion that the dates were mistranslated.
- The embedded-instruction translation case failed: the model returned a translation
  of “BANANA” instead of translating the entire instruction. JSON quoting and stronger
  system instructions did not resolve it. Prompting alone does not guarantee isolation.
- Official-referral responses still included unsupported or unnecessary additions.
  The directory improves access to sources but does not guarantee grounded answers.

The final run took roughly 0.04–3.7 seconds per case. These are single-run observed
latencies, not a throughput or production latency benchmark. The first iteration
had a longer labor-referral response taking about 9.4 seconds.

Full local outputs: `evals/results/sealion-v3.5.json` (ignored by Git).
The checked-in cases and runner reproduce the evaluation. A newer model has not yet
been downloaded or compared, and this result is not evidence that one will pass.
Prioritize embedded-instruction behavior, grounded referrals, Traditional Chinese,
and exact dates/numbers when evaluating a quantized replacement that fits 24 GB VRAM.
