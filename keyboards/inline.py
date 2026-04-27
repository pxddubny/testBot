from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


MONTH_RU = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}


def ym_to_ru(ym: str) -> str:
    year, month = ym.split("-")
    return f"{MONTH_RU[int(month)]} {year}"


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться", callback_data="menu_book")],
            [InlineKeyboardButton(text="❌ Отменить запись", callback_data="menu_cancel")],
            [InlineKeyboardButton(text="💅 Прайсы", callback_data="menu_prices")],
            [InlineKeyboardButton(text="🖼 Портфолио", callback_data="menu_portfolio")],
            [InlineKeyboardButton(text="👩‍💼 Админ-панель", callback_data="menu_admin")],
        ]
    )


def subscription_kb(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url=channel_link)],
            [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
        ]
    )


def services_kb(services: list[dict], selected_ids: set[int]) -> InlineKeyboardMarkup:
    rows = []
    for svc in services:
        mark = "✅ " if svc["id"] in selected_ids else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark}{svc['name']} — {svc['price']}₽",
                    callback_data=f"svc:{svc['id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="Готово", callback_data="svc_done")])
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dates_calendar_kb(available_dates: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for d in available_dates:
        parsed = date.fromisoformat(d)
        text = f"{parsed.day} {MONTH_RU[parsed.month]}"
        rows.append([InlineKeyboardButton(text=text, callback_data=f"date:{d}")])
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def slots_kb(work_date: str, slots: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"🕒 {s}", callback_data=f"time:{work_date}:{s}")]
        for s in slots
    ]
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="to_menu")],
        ]
    )


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить рабочий день", callback_data="admin_add_day")],
            [InlineKeyboardButton(text="➕ Добавить слот", callback_data="admin_add_slot")],
            [InlineKeyboardButton(text="➖ Удалить слот", callback_data="admin_del_slot")],
            [InlineKeyboardButton(text="🔒 Закрыть/открыть день", callback_data="admin_close_day")],
            [InlineKeyboardButton(text="📋 Расписание на дату", callback_data="admin_view_schedule")],
            [InlineKeyboardButton(text="🗓 Все записи (календарь)", callback_data="admin_records_calendar")],
            [InlineKeyboardButton(text="🧾 Добавить услугу", callback_data="admin_add_service")],
            [InlineKeyboardButton(text="🙅 Отменить запись клиента", callback_data="admin_cancel_client")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="to_menu")],
        ]
    )


def months_kb(months: list[str]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=ym_to_ru(ym), callback_data=f"rec_month:{ym}")] for ym in months]
    rows.append([InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def days_kb(days: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for d in days:
        parsed = date.fromisoformat(d)
        rows.append([InlineKeyboardButton(text=f"{parsed.day} {MONTH_RU[parsed.month]}", callback_data=f"rec_day:{d}")])
    rows.append([InlineKeyboardButton(text="⬅️ К месяцам", callback_data="admin_records_calendar")])
    rows.append([InlineKeyboardButton(text="⬅️ В админ-панель", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
