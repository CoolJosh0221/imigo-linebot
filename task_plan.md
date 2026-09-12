# LINE bot quality improvements

## Current task: custom-domain webhook and PR (2026-09-13)
1. [complete] Add an optional Cloudflare Tunnel deployment for webhook.imigo.tw.
2. [complete] Validate tunnel routing, LINE signature handling, and existing regression tests.
3. [in_progress] Publish improve/linebot-quality and create a PR against main.
4. [pending] Review CI and merge through the PR if repository rules permit.

Cloudflare account credentials are absent. Implementation and PR can complete;
activating the public hostname requires domain onboarding and tunnel credentials.
The existing live checkout remains at e8d54f6 until a separate rollout.

Started 2026-09-12 15:40 UTC. Deadline: 16:00 UTC (20 minutes).

## Scope and phases
1. [awaiting_approval] Old app deployed and health verified; final webhook URL change awaits explicit destination approval.
2. [complete] Align model configuration and document a benchmark-based upgrade path.
3. [complete] Improve bounded conversation context and translation behavior.
4. [complete] Add a small multilingual evaluation set and targeted regression checks.
5. [complete] Add verified official Taiwan resource references.
6. [complete] Run local model evaluation, review changes, and report results and deployment status.

## Constraints
- Branch: improve/linebot-quality.
- Quicker tasks first. No large model downloads or unmeasured default model replacement.
- User authorized deployment of the old code while improvements proceed separately.
- Do not expose credentials in command output.

## Errors
- Initial branch creation failed because Git metadata is read-only in the sandbox. Retried with escalation and succeeded.
- Active LINE webhook URL change rejected by automatic review due to new ngrok destination; user approval pending. Public health check passes.
- Async SQLite tests hang within the sandbox; the suite passes when run with approved escalation.
- Moving the temporary live checkout to persistent storage failed across filesystems. Created a second detached main checkout in .runtime/live-e8d54f6 and switched the backend mount successfully.

## Remaining work
- The ngrok webhook change was not approved; the user selected a custom-domain approach instead.
- Download/evaluate a compatible newer quantized model before changing the default.
- Full document retrieval and long-term conversation summaries were not implemented in the 20-minute window.
