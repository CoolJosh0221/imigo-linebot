"""Keep complete recent turns within a UTF-8 input budget."""


def build_messages(
    system_prompt: str, history: list[dict], message: str, max_bytes: int
) -> list[dict]:
    if not message.strip():
        raise ValueError("Please enter a message")
    remaining = (
        max_bytes - len(system_prompt.encode("utf-8")) - len(message.encode("utf-8"))
    )
    if remaining < 0:
        raise ValueError(
            "Your message is too long; please split it into smaller messages"
        )

    # Select whole user/assistant pairs, keeping the most recent exchanges intact.
    turns = []
    for previous, reply in zip(history, history[1:]):
        if previous.get("role") == "user" and reply.get("role") == "assistant":
            turns.append(
                [
                    {"role": "user", "content": previous["content"]},
                    {"role": "assistant", "content": reply["content"]},
                ]
            )
    selected = []
    for turn in reversed(turns):
        size = sum(len(item["content"].encode("utf-8")) for item in turn)
        if size > remaining:
            break
        selected.append(turn)
        remaining -= size
    return (
        [{"role": "system", "content": system_prompt}]
        + [item for turn in reversed(selected) for item in turn]
        + [{"role": "user", "content": message}]
    )
