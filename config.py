import os
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str
    admin_id: int
    channel_id: int
    channel_link: str
    db_path: str = "bot.db"



def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_id=int(os.getenv("ADMIN_ID", "0")),
        channel_id=int(os.getenv("CHANNEL_ID", "0")),
        channel_link=os.getenv("CHANNEL_LINK", ""),
        db_path=os.getenv("DB_PATH", "bot.db"),
    )
