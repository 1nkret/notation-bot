from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.locales import t

EMOJI_OPTIONS = ["📁", "🏠", "💼", "🚗", "🛒", "📚", "🎮", "💡", "🍳", "🏋️", "✈️", "💰"]


def categories_list_kb(categories: list[dict], locale: str) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        label = f"{cat['emoji']} {cat['name']}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"cat:{cat['_id']}")])
    buttons.append([InlineKeyboardButton(text=t("btn_add_category", locale), callback_data="cat_add")])
    buttons.append([InlineKeyboardButton(text=t("btn_back", locale), callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def category_actions_kb(cat_id: str, is_inbox: bool, locale: str) -> InlineKeyboardMarkup:
    buttons = []
    if not is_inbox:
        buttons.append([
            InlineKeyboardButton(text=t("btn_rename", locale), callback_data=f"cat_rename:{cat_id}"),
            InlineKeyboardButton(text=t("btn_delete", locale), callback_data=f"cat_del:{cat_id}"),
        ])
    buttons.append([InlineKeyboardButton(text=t("btn_back", locale), callback_data="categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def emoji_picker_kb(locale: str) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(EMOJI_OPTIONS), 4):
        row = [InlineKeyboardButton(text=e, callback_data=f"cat_emoji:{e}") for e in EMOJI_OPTIONS[i:i+4]]
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t("btn_cancel", locale), callback_data="categories")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_delete_kb(cat_id: str, locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_confirm_yes", locale), callback_data=f"cat_del_yes:{cat_id}"),
            InlineKeyboardButton(text=t("btn_confirm_no", locale), callback_data="categories"),
        ],
    ])


def cancel_kb(locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", locale), callback_data="categories")],
    ])
