import random

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from db.mongo import (
    get_user, get_categories, get_category,
    get_records, count_records, get_record,
    create_record, update_record, toggle_done,
    move_record, delete_record, clear_done,
)
from utils.locales import t
from bot.records.keyboards import (
    records_list_kb, record_view_kb, record_move_kb,
    confirm_delete_kb, cancel_kb, quick_capture_kb,
)
from bot.records.states import RecordStates

router = Router()

PER_PAGE = 8


async def _lang(user_id: int) -> str:
    user = await get_user(user_id)
    return user["lang"] if user else "en"


def _done_phrase(lang: str) -> str:
    return t(f"todo_done_{random.randint(1, 5)}", lang)


# ── List records in category ──

@router.callback_query(F.data.startswith("recs_cat:"))
async def list_records(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    cat_id = cb.data.split(":")[1]
    await _show_page(cb, cat_id, 0)


@router.callback_query(F.data.startswith("recs_page:"))
async def paginate(cb: CallbackQuery):
    parts = cb.data.split(":")
    await _show_page(cb, parts[1], int(parts[2]))


async def _show_page(cb: CallbackQuery, cat_id: str, page: int):
    lang = await _lang(cb.from_user.id)
    cat = await get_category(cat_id)
    cat_name = f"{cat['emoji']} {cat['name']}" if cat else "?"

    total = await count_records(cb.from_user.id, cat_id)
    recs = await get_records(cb.from_user.id, cat_id, skip=page * PER_PAGE, limit=PER_PAGE)

    text = t("records_list", lang).format(category=cat_name) if recs else t("records_empty", lang)

    await cb.message.edit_text(
        text,
        reply_markup=records_list_kb(recs, cat_id, page, total, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


# ── Quick toggle from list ──

@router.callback_query(F.data.startswith("rec_toggle:"))
async def toggle_from_list(cb: CallbackQuery):
    parts = cb.data.split(":")
    rec_id, cat_id, page = parts[1], parts[2], int(parts[3])
    lang = await _lang(cb.from_user.id)

    new_done = await toggle_done(rec_id)
    phrase = _done_phrase(lang) if new_done else t("todo_undone", lang)
    await cb.answer(phrase, show_alert=False)
    await _show_page(cb, cat_id, page)


# ── View record ──

@router.callback_query(F.data.startswith("rec:"))
async def view_record(cb: CallbackQuery):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    rec = await get_record(rec_id)
    if not rec:
        await cb.answer()
        return

    icon = "✅" if rec["done"] else "⬜"
    text = f"{icon} <b>{rec['text']}</b>\n\n<i>{rec['created_at'][:10]}</i>"

    await cb.message.edit_text(
        text,
        reply_markup=record_view_kb(rec, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


# ── Toggle from view ──

@router.callback_query(F.data.startswith("rec_toggle_view:"))
async def toggle_from_view(cb: CallbackQuery):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    new_done = await toggle_done(rec_id)
    phrase = _done_phrase(lang) if new_done else t("todo_undone", lang)
    await cb.answer(phrase, show_alert=False)

    rec = await get_record(rec_id)
    if rec:
        icon = "✅" if rec["done"] else "⬜"
        text = f"{icon} <b>{rec['text']}</b>\n\n<i>{rec['created_at'][:10]}</i>"
        await cb.message.edit_text(
            text,
            reply_markup=record_view_kb(rec, lang),
            parse_mode=ParseMode.HTML,
        )


# ── Add record ──

@router.callback_query(F.data.startswith("rec_add:"))
async def start_add(cb: CallbackQuery, state: FSMContext):
    cat_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    await state.set_state(RecordStates.entering_text)
    await state.update_data(cat_id=cat_id, lang=lang)
    await cb.message.edit_text(
        t("rec_enter_text", lang),
        reply_markup=cancel_kb(f"recs_cat:{cat_id}", lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.message(RecordStates.entering_text)
async def finish_add(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    cat_id = data["cat_id"]
    await create_record(message.from_user.id, cat_id, message.text.strip())
    await state.clear()
    await message.answer(t("rec_created", lang), parse_mode=ParseMode.HTML)


# ── Edit record ──

@router.callback_query(F.data.startswith("rec_edit:"))
async def start_edit(cb: CallbackQuery, state: FSMContext):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    await state.set_state(RecordStates.editing_text)
    await state.update_data(rec_id=rec_id, lang=lang)
    await cb.message.edit_text(
        t("rec_enter_new_text", lang),
        reply_markup=cancel_kb(f"rec:{rec_id}", lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.message(RecordStates.editing_text)
async def finish_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    await update_record(data["rec_id"], text=message.text.strip())
    await state.clear()
    await message.answer(t("rec_updated", lang), parse_mode=ParseMode.HTML)


# ── Move record ──

@router.callback_query(F.data.startswith("rec_move:"))
async def pick_move_cat(cb: CallbackQuery):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    cats = await get_categories(cb.from_user.id)
    await cb.message.edit_text(
        t("rec_pick_category", lang),
        reply_markup=record_move_kb(cats, rec_id, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data.startswith("rec_move_to:"))
async def do_move(cb: CallbackQuery):
    parts = cb.data.split(":")
    rec_id, new_cat_id = parts[1], parts[2]
    lang = await _lang(cb.from_user.id)
    await move_record(rec_id, new_cat_id)
    await cb.answer(t("rec_moved", lang), show_alert=False)

    rec = await get_record(rec_id)
    if not rec:
        return

    cats = await get_categories(cb.from_user.id)
    await cb.message.edit_reply_markup(
        reply_markup=quick_capture_kb(rec_id, cats, rec["category_id"], lang),
    )


# ── Delete record ──

@router.callback_query(F.data.startswith("rec_del:"))
async def confirm_del(cb: CallbackQuery):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    await cb.message.edit_text(
        t("rec_confirm_delete", lang),
        reply_markup=confirm_delete_kb(rec_id, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data.startswith("rec_del_yes:"))
async def do_delete(cb: CallbackQuery):
    rec_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    await delete_record(rec_id)
    await cb.message.edit_text(t("rec_deleted", lang), parse_mode=ParseMode.HTML)
    await cb.answer()


# ── Clear done ──

@router.callback_query(F.data.startswith("rec_clear:"))
async def do_clear(cb: CallbackQuery):
    cat_id = cb.data.split(":")[1]
    lang = await _lang(cb.from_user.id)
    count = await clear_done(cb.from_user.id, cat_id)
    if count:
        await cb.answer(t("cleared_done", lang).format(count=count), show_alert=False)
    else:
        await cb.answer(t("nothing_to_clear", lang), show_alert=False)
    await _show_page(cb, cat_id, 0)


# ── Noop (page indicator) ──

@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery):
    await cb.answer()
