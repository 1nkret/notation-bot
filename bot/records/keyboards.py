import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.locales import t


def records_list_kb(records: list[dict], cat_id: str, page: int, total: int, locale: str) -> InlineKeyboardMarkup:
    buttons = []
    for rec in records:
        text_short = rec["text"][:30]
        icon = "✅" if rec["done"] else "⬜"
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {text_short}",
                callback_data=f"rec_toggle:{rec['_id']}:{cat_id}:{page}",
            ),
            InlineKeyboardButton(text="⚙️", callback_data=f"rec:{rec['_id']}"),
        ])

    total_pages = max(1, math.ceil(total / 8))
    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text=t("btn_prev", locale), callback_data=f"recs_page:{cat_id}:{page - 1}"))
        nav.append(InlineKeyboardButton(
            text=t("page_info", locale).format(current=page + 1, total=total_pages),
            callback_data="noop",
        ))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(text=t("btn_next", locale), callback_data=f"recs_page:{cat_id}:{page + 1}"))
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton(text=t("btn_add_record", locale), callback_data=f"rec_add:{cat_id}"),
        InlineKeyboardButton(text=t("btn_clear_done", locale), callback_data=f"rec_clear:{cat_id}"),
    ])
    buttons.append([InlineKeyboardButton(text=t("btn_back_menu", locale), callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def record_view_kb(rec: dict, locale: str) -> InlineKeyboardMarkup:
    rec_id = str(rec["_id"])
    cat_id = str(rec["category_id"])

    if rec["done"]:
        toggle_btn = InlineKeyboardButton(text=t("btn_undone", locale), callback_data=f"rec_toggle_view:{rec_id}")
    else:
        toggle_btn = InlineKeyboardButton(text=t("btn_done", locale), callback_data=f"rec_toggle_view:{rec_id}")

    return InlineKeyboardMarkup(inline_keyboard=[
        [toggle_btn],
        [
            InlineKeyboardButton(text=t("btn_move", locale), callback_data=f"rec_move:{rec_id}"),
            InlineKeyboardButton(text=t("btn_edit", locale), callback_data=f"rec_edit:{rec_id}"),
            InlineKeyboardButton(text=t("btn_delete", locale), callback_data=f"rec_del:{rec_id}"),
        ],
        [InlineKeyboardButton(text=t("btn_back", locale), callback_data=f"recs_cat:{cat_id}")],
    ])


def record_move_kb(categories: list[dict], rec_id: str, locale: str) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"rec_move_to:{rec_id}:{cat['_id']}",
        )])
    buttons.append([InlineKeyboardButton(text=t("btn_cancel", locale), callback_data=f"rec:{rec_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_delete_kb(rec_id: str, locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_confirm_yes", locale), callback_data=f"rec_del_yes:{rec_id}"),
            InlineKeyboardButton(text=t("btn_confirm_no", locale), callback_data=f"rec:{rec_id}"),
        ],
    ])


def quick_capture_kb(rec_id: str, categories: list[dict], current_cat_id, locale: str) -> InlineKeyboardMarkup:
    buttons = []

    # Categories in rows of 2, current marked with ✓
    row = []
    for cat in categories:
        if cat["_id"] == current_cat_id:
            label = f"✓ {cat['emoji']} {cat['name']}"
            row.append(InlineKeyboardButton(text=label, callback_data="noop"))
        else:
            label = f"{cat['emoji']} {cat['name']}"
            row.append(InlineKeyboardButton(text=label, callback_data=f"rec_move_to:{rec_id}:{cat['_id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text=t("btn_menu", locale), callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_kb(callback: str, locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", locale), callback_data=callback)],
    ])
