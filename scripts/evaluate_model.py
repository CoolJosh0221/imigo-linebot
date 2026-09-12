"""Run synthetic bot cases against an already running model; never sends LINE messages."""

import argparse
import asyncio
import json
import time
from pathlib import Path

from config import BotConfig
from services.ai_service import AIService
from services.translation_service import TranslationService


class EvaluationHistory:
    def __init__(self, case):
        self.case = case

    async def get_user_language(self, user_id):
        return self.case.get("language", "en")

    async def get_conversation_history(self, user_id, limit):
        return self.case.get("history", [])[-limit:]

    async def save_exchange(self, *args):
        pass


async def evaluate(args):
    config = BotConfig()
    if args.base_url:
        config.llm_base_url = args.base_url
    if args.model:
        config.model_name = args.model
    cases = json.loads(args.cases.read_text())
    if args.limit:
        cases = cases[: args.limit]
    results = []
    translation = TranslationService(config)
    try:
        for case in cases:
            started = time.perf_counter()
            service = None
            try:
                if case["type"] == "translation":
                    answer = await translation.translate_message(
                        case["text"], case["target"], case["source"]
                    )
                else:
                    service = AIService(EvaluationHistory(case), config)
                    answer = await service.generate_response(
                        "synthetic-evaluation", case["text"]
                    )
                missing = [
                    value
                    for value in case.get("must_include", [])
                    if value not in answer
                ]
                result = {
                    "id": case["id"],
                    "answer": answer,
                    "missing_literals": missing,
                    "automatic_pass": not missing,
                    "human_review": case["review"],
                }
            except Exception as error:
                # Avoid serializing provider exceptions that may contain request metadata.
                result = {
                    "id": case["id"],
                    "automatic_pass": False,
                    "error_type": type(error).__name__,
                }
            finally:
                if service:
                    await service.aclose()
            result["seconds"] = round(time.perf_counter() - started, 3)
            results.append(result)
            print(
                case["id"],
                "PASS" if result["automatic_pass"] else "REVIEW",
                result["seconds"],
                "s",
                flush=True,
            )
    finally:
        await translation.aclose()
    report = {
        "model": config.model_name,
        "chat_template_kwargs": config.chat_template_kwargs,
        "automatic_passes": sum(r["automatic_pass"] for r in results),
        "total": len(results),
        "results": results,
        "note": "Literal checks are not a translation quality score. Review each answer with a fluent speaker.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("Report:", args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model")
    parser.add_argument(
        "--base-url", help="Endpoint of an already running model server"
    )
    parser.add_argument("--cases", type=Path, default=Path("evals/linebot_cases.json"))
    parser.add_argument("--output", type=Path, default=Path("evals/results/local.json"))
    parser.add_argument("--limit", type=int)
    asyncio.run(evaluate(parser.parse_args()))
