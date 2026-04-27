import re
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import Config
from database.db import Database
from keyboards.inline import (
    confirm_kb,
    dates_calendar_kb,
    main_menu_kb,
    services_kb,
    slots_kb,
    subscription_kb,
)
from states import BookingStates
from utils.scheduler import ReminderService

router = Router()
PHONE_RE = re.compile(r"^\+?[0-9\-()\s]{7,20}$")


async def check_subscription(callback: CallbackQuery, config: Config) -> bool:
    try:
        member = await callback.bot.get_chat_member(config.channel_id, callback.from_user.id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False


@router.callback_query(F.data == "menu_book")
async def menu_book(
    callback: CallbackQuery, state: FSMContext, db: Database, config: Config
):
    subscribed = await check_subscription(callback, config)
    if not subscribed:
        await callback.message.answer(
            "<b>Для записи необходимо подписаться на канал</b>",
            parse_mode="HTML",
            reply_markup=subscription_kb(config.channel_link),
        )
        await callback.answer()
        return

    active = db.get_user_active_appointment(callback.from_user.id)
    if active:
        await callback.message.answer(
            f"<b>У вас уже есть запись:</b> {active['work_date']} {active['slot_time']}\n"
            f"Сначала отмените её.",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    services = [dict(r) for r in db.get_services()]
    if not services:
        await callback.message.answer("Пока нет доступных услуг. Попробуйте позже.")
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_services)
    await state.update_data(selected_services=[])
    await callback.message.answer(
        "<b>Выберите услугу(и):</b>",
        parse_mode="HTML",
        reply_markup=services_kb(services, set()),
    )
    await callback.answer()


@router.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery, config: Config):
    if await check_subscription(callback, config):
        await callback.message.answer("✅ Подписка подтверждена. Теперь можно записываться.")
    else:
        await callback.message.answer("❌ Подписка не найдена. Подпишитесь и попробуйте снова.")
    await callback.answer()


@router.callback_query(BookingStates.choosing_services, F.data.startswith("svc:"))
async def toggle_service(callback: CallbackQuery, state: FSMContext, db: Database):
    service_id = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    selected = set(data.get("selected_services", []))
    if service_id in selected:
        selected.remove(service_id)
    else:
        selected.add(service_id)
    await state.update_data(selected_services=list(selected))

    services = [dict(r) for r in db.get_services()]
    await callback.message.edit_reply_markup(reply_markup=services_kb(services, selected))
    await callback.answer("Обновлено")


@router.callback_query(BookingStates.choosing_services, F.data == "svc_done")
async def finish_services(callback: CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    selected = data.get("selected_services", [])
    if not selected:
        await callback.answer("Выберите хотя бы одну услугу", show_alert=True)
        return

    start = date.today()
    end = start + timedelta(days=31)
    available_dates = db.get_available_dates(start.isoformat(), end.isoformat())

    if not available_dates:
        await callback.message.answer("Свободных дат пока нет 😔")
        await callback.answer()
        return

    await state.set_state(BookingStates.choosing_date)
    await callback.message.answer(
        "<b>Выберите дату записи:</b>",
        parse_mode="HTML",
        reply_markup=dates_calendar_kb(available_dates),
    )
    await callback.answer()


@router.callback_query(BookingStates.choosing_date, F.data.startswith("date:"))
async def pick_date(callback: CallbackQuery, state: FSMContext, db: Database):
    work_date = callback.data.split(":", 1)[1]
    slots = db.get_available_slots(work_date)
    if not slots:
        await callback.message.answer("На эту дату нет доступных слотов.")
        await callback.answer()
        return
    await state.update_data(work_date=work_date)
    await state.set_state(BookingStates.choosing_time)
    await callback.message.answer(
        f"<b>Дата:</b> {work_date}\n<b>Выберите время:</b>",
        parse_mode="HTML",
        reply_markup=slots_kb(work_date, slots),
    )
    await callback.answer()


@router.callback_query(BookingStates.choosing_time, F.data.startswith("time:"))
async def pick_time(callback: CallbackQuery, state: FSMContext):
    _, work_date, slot_time = callback.data.split(":", 2)
    await state.update_data(work_date=work_date, slot_time=slot_time)
    await state.set_state(BookingStates.waiting_name)
    await callback.message.answer("Введите ваше <b>имя</b>:", parse_mode="HTML")
    await callback.answer()


@router.message(BookingStates.waiting_name)
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text.strip())
    await state.set_state(BookingStates.waiting_phone)
    await message.answer("Введите <b>номер телефона</b> (только цифры и символы + - ( )):", parse_mode="HTML")


@router.message(BookingStates.waiting_phone)
async def confirm_booking(message: Message, state: FSMContext, db: Database):
    phone = message.text.strip()
    if not PHONE_RE.fullmatch(phone):
        await message.answer(
            "❌ Номер выглядит неверно. Введите телефон еще раз (без букв).\n"
            "Пример: <code>+7 999 123-45-67</code>",
            parse_mode="HTML",
        )
        return

    await state.update_data(phone=phone)
    data = await state.get_data()
    services = db.get_services_by_ids(data.get("selected_services", []))
    services_text = "\n".join([f"• {s['name']} — {s['price']}₽" for s in services])

    await state.set_state(BookingStates.confirming)
    await message.answer(
        "<b>Подтвердите запись:</b>\n"
        f"Услуги:\n{services_text}\n\n"
        f"Дата: {data['work_date']}\n"
        f"Время: {data['slot_time']}\n"
        f"Имя: {data['user_name']}\n"
        f"Телефон: {data['phone']}",
        parse_mode="HTML",
        reply_markup=confirm_kb(),
    )


@router.callback_query(BookingStates.confirming, F.data == "confirm_yes")
async def save_booking(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    config: Config,
    reminder_service: ReminderService,
):
    data = await state.get_data()
    active = db.get_user_active_appointment(callback.from_user.id)
    if active:
        await callback.message.answer("У вас уже есть активная запись.")
        await state.clear()
        await callback.answer()
        return

    slots = db.get_available_slots(data["work_date"])
    if data["slot_time"] not in slots:
        await callback.message.answer("Этот слот уже недоступен. Выберите другой.")
        await state.clear()
        await callback.message.answer("<b>Главное меню</b>", parse_mode="HTML", reply_markup=main_menu_kb())
        await callback.answer()
        return

    appointment_id = db.create_appointment(
        user_id=callback.from_user.id,
        user_name=data["user_name"],
        phone=data["phone"],
        work_date=data["work_date"],
        slot_time=data["slot_time"],
        reminder_job_id=None,
    )
    db.link_appointment_services(appointment_id, data.get("selected_services", []))
    services = db.get_appointment_services(appointment_id)
    services_text = "\n".join([f"• {s['name']} — {s['price']}₽" for s in services])

    job_id = reminder_service.schedule_reminder(
        appointment_id=appointment_id,
        user_id=callback.from_user.id,
        work_date=data["work_date"],
        slot_time=data["slot_time"],
    )
    db.update_reminder_job(appointment_id, job_id)

    text = (
        "<b>Новая запись</b>\n"
        f"Клиент: {data['user_name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Услуги:\n{services_text}\n"
        f"Дата: {data['work_date']}\n"
        f"Время: {data['slot_time']}\n"
        f"User ID: <code>{callback.from_user.id}</code>"
    )
    await callback.bot.send_message(config.admin_id, text, parse_mode="HTML")
    await callback.bot.send_message(config.channel_id, f"📌 {text}", parse_mode="HTML")

    await callback.message.answer("✅ Запись успешно создана!")
    await state.clear()
    await callback.message.answer("<b>Главное меню</b>", parse_mode="HTML", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "menu_cancel")
async def cancel_own(callback: CallbackQuery, db: Database, reminder_service: ReminderService):
    appt = db.get_user_active_appointment(callback.from_user.id)
    if not appt:
        await callback.message.answer("У вас нет активной записи.")
        await callback.answer()
        return

    reminder_service.remove_reminder(appt["reminder_job_id"])
    db.cancel_appointment(appt["id"])
    await callback.message.answer("✅ Ваша запись отменена. Слот снова доступен.")
    await callback.answer()
