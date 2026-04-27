import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config
from database.db import Database
from handlers import admin, common, user
from utils.scheduler import ReminderService


async def restore_reminders(db: Database, reminder_service: ReminderService):
    """Восстанавливает задачи напоминаний после перезапуска бота."""
    for appt in db.get_active_appointments():
        job_id = reminder_service.schedule_reminder(
            appointment_id=appt["id"],
            user_id=appt["user_id"],
            work_date=appt["work_date"],
            slot_time=appt["slot_time"],
        )
        db.update_reminder_job(appt["id"], job_id)


async def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    if not config.bot_token or not config.admin_id:
        raise RuntimeError("Заполните BOT_TOKEN и ADMIN_ID в переменных окружения")

    db = Database(config.db_path)
    db.init()

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.start()
    reminder_service = ReminderService(scheduler, bot)

    await restore_reminders(db, reminder_service)

    dp["db"] = db
    dp["config"] = config
    dp["reminder_service"] = reminder_service

    dp.include_router(common.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
