import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    bot_token: str
    admin_id: int
    channel_id: int
    channel_link: str
    db_path: str = "bot.db"



def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения."""
    # Автоматически подхватываем переменные из .env (если файл существует).
    load_dotenv(".env")

    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_id=int(os.getenv("ADMIN_ID", "0")),
        channel_id=int(os.getenv("CHANNEL_ID", "0")),
        channel_link=os.getenv("CHANNEL_LINK", ""),
        db_path=os.getenv("DB_PATH", "bot.db"),
    )
