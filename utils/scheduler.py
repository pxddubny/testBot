from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class ReminderService:
    def __init__(self, scheduler: AsyncIOScheduler, bot: Bot):
        self.scheduler = scheduler
        self.bot = bot

    async def send_reminder(self, user_id: int, slot_time: str):
        await self.bot.send_message(
            user_id,
            f"<b>Напоминаем, что вы записаны на наращивание ресниц завтра в {slot_time}.\nЖдём вас ❤️</b>",
            parse_mode="HTML",
        )

    def schedule_reminder(
        self,
        appointment_id: int,
        user_id: int,
        work_date: str,
        slot_time: str,
    ) -> str | None:
        visit_dt = datetime.fromisoformat(f"{work_date} {slot_time}:00")
        run_time = visit_dt - timedelta(hours=24)
        if run_time <= datetime.utcnow():
            return None
        job_id = f"reminder_{appointment_id}"
        self.scheduler.add_job(
            self.send_reminder,
            "date",
            id=job_id,
            run_date=run_time,
            kwargs={"user_id": user_id, "slot_time": slot_time},
            replace_existing=True,
        )
        return job_id

    def remove_reminder(self, job_id: str | None) -> None:
        if not job_id:
            return
        job = self.scheduler.get_job(job_id)
        if job:
            job.remove()
