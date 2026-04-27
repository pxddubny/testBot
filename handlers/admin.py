from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import Config
from database.db import Database
from keyboards.inline import admin_menu_kb
from states import AdminStates
from utils.scheduler import ReminderService

router = Router()


def is_admin(user_id: int, config: Config) -> bool:
    return user_id == config.admin_id


@router.callback_query(F.data == "menu_admin")
async def admin_menu(callback: CallbackQuery, config: Config, state: FSMContext):
    if not is_admin(callback.from_user.id, config):
        await callback.message.answer("⛔ Доступ запрещен")
        await callback.answer()
        return
    await state.clear()
    await callback.message.answer("<b>Админ-панель</b>", parse_mode="HTML", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_add_day")
async def admin_add_day(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.add_day)
    await callback.message.answer("Введите дату в формате YYYY-MM-DD")
    await callback.answer()


@router.message(AdminStates.add_day)
async def admin_add_day_save(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user.id, config):
        return
    db.add_work_day(message.text.strip())
    await message.answer("✅ Рабочий день добавлен")
    await state.clear()


@router.callback_query(F.data == "admin_add_slot")
async def admin_add_slot_start(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.add_slot_date)
    await callback.message.answer("Введите дату слота YYYY-MM-DD")
    await callback.answer()


@router.message(AdminStates.add_slot_date)
async def admin_add_slot_date(message: Message, state: FSMContext):
    await state.update_data(work_date=message.text.strip())
    await state.set_state(AdminStates.add_slot_time)
    await message.answer("Введите время слота HH:MM")


@router.message(AdminStates.add_slot_time)
async def admin_add_slot_time(
    message: Message, state: FSMContext, db: Database, config: Config
):
    if not is_admin(message.from_user.id, config):
        return
    data = await state.get_data()
    db.add_slot(data["work_date"], message.text.strip())
    await message.answer("✅ Слот добавлен")
    await state.clear()


@router.callback_query(F.data == "admin_del_slot")
async def admin_del_slot_start(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.delete_slot_date)
    await callback.message.answer("Введите дату слота YYYY-MM-DD")
    await callback.answer()


@router.message(AdminStates.delete_slot_date)
async def admin_del_slot_date(message: Message, state: FSMContext):
    await state.update_data(work_date=message.text.strip())
    await state.set_state(AdminStates.delete_slot_time)
    await message.answer("Введите время слота HH:MM")


@router.message(AdminStates.delete_slot_time)
async def admin_del_slot_time(
    message: Message, state: FSMContext, db: Database, config: Config
):
    if not is_admin(message.from_user.id, config):
        return
    data = await state.get_data()
    db.delete_slot(data["work_date"], message.text.strip())
    await message.answer("✅ Слот удален")
    await state.clear()


@router.callback_query(F.data == "admin_close_day")
async def admin_close_day_start(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.close_day)
    await callback.message.answer("Введите дату YYYY-MM-DD и статус close/open (пример: 2026-05-03 close)")
    await callback.answer()


@router.message(AdminStates.close_day)
async def admin_close_day_save(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user.id, config):
        return
    work_date, status = message.text.strip().split()
    db.set_day_closed(work_date, status.lower() == "close")
    await message.answer("✅ Статус дня обновлен")
    await state.clear()


@router.callback_query(F.data == "admin_view_schedule")
async def admin_view_schedule_start(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.view_schedule_date)
    await callback.message.answer("Введите дату YYYY-MM-DD")
    await callback.answer()


@router.message(AdminStates.view_schedule_date)
async def admin_view_schedule_show(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user.id, config):
        return
    work_date = message.text.strip()
    rows = db.get_schedule_for_date(work_date)
    if not rows:
        await message.answer("Слотов на эту дату нет")
        await state.clear()
        return
    lines = [f"<b>Расписание на {work_date}</b>"]
    for r in rows:
        if r["user_name"]:
            lines.append(f"• {r['slot_time']} — занято ({r['user_name']}, {r['phone']})")
        else:
            lines.append(f"• {r['slot_time']} — свободно")
    await message.answer("\n".join(lines), parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data == "admin_cancel_client")
async def admin_cancel_client_start(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user.id, config):
        await callback.answer()
        return
    await state.set_state(AdminStates.cancel_client_date)
    await callback.message.answer("Введите дату записи YYYY-MM-DD")
    await callback.answer()


@router.message(AdminStates.cancel_client_date)
async def admin_cancel_client_date(message: Message, state: FSMContext):
    await state.update_data(work_date=message.text.strip())
    await state.set_state(AdminStates.cancel_client_time)
    await message.answer("Введите время записи HH:MM")


@router.message(AdminStates.cancel_client_time)
async def admin_cancel_client_time(
    message: Message,
    state: FSMContext,
    db: Database,
    config: Config,
    reminder_service: ReminderService,
):
    if not is_admin(message.from_user.id, config):
        return
    data = await state.get_data()
    appt = db.cancel_client_by_slot(data["work_date"], message.text.strip())
    if not appt:
        await message.answer("Активная запись не найдена")
        await state.clear()
        return
    reminder_service.remove_reminder(appt["reminder_job_id"])
    await message.answer("✅ Запись клиента отменена")
    await state.clear()
