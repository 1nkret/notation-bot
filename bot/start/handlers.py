from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from db.mongo import get_user, get_categories, count_by_category, get_inbox
from utils.locales import t
from bot.start.keyboards import dashboard_kb, settings_kb
from bot.onboarding.keyboards import lang_select_kb
from bot.records.states import RecordStates

router = Router()


async def show_dashboard(user_id: int, lang: str, edit_message=None, send_message=None):
    cats = await get_categories(user_id)
    counts = await count_by_category(user_id)
    text = t("dashboard_title", lang)
    kb = dashboard_kb(cats, counts, lang)
    if edit_message:
        await edit_message(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    elif send_message:
        await send_message(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "menu")
async def menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await get_user(cb.from_user.id)
    lang = user["lang"] if user else "en"
    await show_dashboard(cb.from_user.id, lang, edit_message=cb.message.edit_text)
    await cb.answer()


# ── Settings ──

@router.callback_query(F.data == "settings")
async def settings(cb: CallbackQuery):
    user = await get_user(cb.from_user.id)
    lang = user["lang"] if user else "en"
    await cb.message.edit_text(
        t("settings_title", lang),
        reply_markup=settings_kb(lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data == "about")
async def about(cb: CallbackQuery):
    user = await get_user(cb.from_user.id)
    lang = user["lang"] if user else "en"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="settings")],
    ])
    await cb.message.edit_text(t("about_text", lang), reply_markup=kb, parse_mode=ParseMode.HTML)
    await cb.answer()


@router.callback_query(F.data == "change_lang")
async def change_lang(cb: CallbackQuery):
    user = await get_user(cb.from_user.id)
    lang = user["lang"] if user else "en"
    await cb.message.edit_text(t("lang_prompt", lang), reply_markup=lang_select_kb(), parse_mode=ParseMode.HTML)
    await cb.answer()


# ── Quick add from dashboard (into Inbox) ──

@router.callback_query(F.data == "rec_add_inbox")
async def add_to_inbox(cb: CallbackQuery, state: FSMContext):
    user = await get_user(cb.from_user.id)
    lang = user["lang"] if user else "en"
    inbox = await get_inbox(cb.from_user.id)
    if not inbox:
        await cb.answer()
        return
    await state.set_state(RecordStates.entering_text)
    await state.update_data(cat_id=str(inbox["_id"]), lang=lang)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="menu")],
    ])
    await cb.message.edit_text(t("rec_enter_text", lang), reply_markup=cancel_kb, parse_mode=ParseMode.HTML)
    await cb.answer()
