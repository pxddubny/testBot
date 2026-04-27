from datetime import date, timedelta

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
            [InlineKeyboardButton(text="🙅 Отменить запись клиента", callback_data="admin_cancel_client")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="to_menu")],
        ]
    )
