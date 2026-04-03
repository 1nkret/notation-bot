from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def lang_select_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="set_lang:en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="Українська 🇺🇦", callback_data="set_lang:uk")],
    ])
