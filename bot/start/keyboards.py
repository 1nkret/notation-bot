from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.locales import t


def dashboard_kb(categories: list[dict], counts: dict, locale: str) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        count = counts.get(cat["_id"], 0)
        label = f"{cat['emoji']} {cat['name']} ({count})"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"recs_cat:{cat['_id']}")])

    buttons.append([
        InlineKeyboardButton(text=t("btn_add_record", locale), callback_data="rec_add_inbox"),
        InlineKeyboardButton(text=t("btn_settings", locale), callback_data="settings"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_kb(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_categories", locale), callback_data="categories")],
        [InlineKeyboardButton(text=t("btn_lang", locale), callback_data="change_lang")],
        [InlineKeyboardButton(text=t("btn_about", locale), callback_data="about")],
        [InlineKeyboardButton(text=t("btn_back_menu", locale), callback_data="menu")],
    ])
