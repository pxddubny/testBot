from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.inline import main_menu_kb

router = Router()


@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer(
        "<b>Добро пожаловать в бот записи мастера маникюра!</b>\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "to_menu")
async def to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Главное меню</b>", parse_mode="HTML", reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_prices")
async def show_prices(callback: CallbackQuery):
    await callback.message.answer(
        "<b>Прайс:</b>\n\n"
        "• <b>Френч</b> — 1000₽\n"
        "• <b>Квадрат</b> — 500₽",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "menu_portfolio")
async def show_portfolio(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Смотреть портфолио",
                    url="https://ru.pinterest.com/crystalwithluv/_created/",
                )
            ]
        ]
    )
    await callback.message.answer("<b>Портфолио мастера:</b>", parse_mode="HTML", reply_markup=kb)
    await callback.answer()
