# Progress

- 15:40 UTC: Started a 20-minute implementation window. Read planning skill and checked clean Git status.
- Created improve/linebot-quality from main using approved Git escalation.
- User additionally requested deployment of unchanged old code. Deployment is prioritized before branch edits.
- 15:43 UTC: Started isolated main e8d54f6 deployment at /tmp/imigo-linebot-live-e8d54f6 with cached Docker images and local Llama-SEA-LION-v3.5-8B-R weights. Backend health, model discovery, and public health pass.
- Webhook URL change rejected by automatic review; explicit approval requested for https://44c6-111-249-71-250.ngrok-free.app/webhook. Existing webhook remains unchanged.
- Baseline pytest run stalled after configuration tests inside the sandbox; investigating async database execution while implementing quick improvements.
- 15:48 UTC: Existing 37 tests pass outside sandbox. Shared client config, complete-turn context selection, atomic conversation writes, and translation validation implemented.
- 15:52 UTC: Expanded 58-case regression suite passes. Both compose configurations validate with overridden MODEL_NAME and MODEL_PATH. Added 13 synthetic quality cases and an evaluation CLI; actual local model evaluation started.
- Added keyword-selected official labor and immigration referrals from primary sources reviewed 2026-09-12. Full document retrieval and persistent summaries are outside this time box.
- 15:55 UTC: Final 62 tests pass; Ruff and Black checks pass. Local model evaluation passed 9/13 strict literal checks, with date/time normalization and embedded-instruction failures documented in docs/evaluation-notes.md. No newer weights downloaded or selected.
- Old application chat route returned an Indonesian reply; synthetic conversation was cleared afterward. No LINE messages sent.
- 15:57 UTC: Persistent deployment checkout created at .runtime/live-e8d54f6; old backend source mount switched successfully. vLLM and ngrok stayed running. Temporary checkout could not be moved across filesystems, so a second detached checkout was created instead.
- Earlier sandbox-stalled pytest/Black processes were terminated after replacement checks passed.
