import os
import yaml
from typing import Dict, List, Optional
from attrs import define
from dotenv import load_dotenv


@define
class BotIdentity:
    name: str
    language: str
    country: str


@define
class QuickReplyItem:
    label: str
    text: str


@define
class BotConfig:
    bot: BotIdentity
    messages: Dict[str, str]
    emergency: Dict[str, str]
    quick_replies: List[QuickReplyItem]
    line_secret: str
    line_token: str
    llm_base_url: str
    model_name: str
    db_url: str
    google_maps_api_key: Optional[str] = None

    @classmethod
    def load(cls, config_file: str = None) -> "BotConfig":
        load_dotenv()

        if not config_file:
            default_lang = os.getenv("DEFAULT_LANGUAGE", "en")
            config_file = f"config/{default_lang}.yaml"

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            bot=BotIdentity(**data["bot"]),
            messages=data["messages"],
            emergency=data["emergency"],
            quick_replies=[
                QuickReplyItem(**item) for item in data.get("quick_replies", [])
            ],
            line_secret=os.getenv("LINE_CHANNEL_SECRET"),
            line_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),
            llm_base_url=os.getenv("LLM_BASE_URL", "http://localhost:8000/v1"),
            model_name=os.getenv("MODEL_NAME", "Qwen/Qwen2.5-9B-Instruct"),
            db_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db"),
            google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
        )

    def get_message(self, key: str) -> str:
        return self.messages.get(key, key)

    def get_emergency_info(self) -> str:
        lines = ["🚨 EMERGENCY CONTACTS:"]
        for label, value in self.emergency.items():
            lines.append(f"- {label.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)


_config: Optional[BotConfig] = None


def load_config(config_file: str = None) -> BotConfig:
    global _config
    _config = BotConfig.load(config_file)
    return _config


def get_config() -> BotConfig:
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config
