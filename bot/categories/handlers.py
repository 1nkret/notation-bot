from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from db.mongo import (
    get_user, get_categories, get_category,
    create_category, rename_category, delete_category,
)
from utils.locales import t
from bot.categories.keyboards import (
    categories_list_kb, category_actions_kb,
    emoji_picker_kb, confirm_delete_kb, cancel_kb,
)
from bot.categories.states import CategoryStates

router = Router()


async def _get_lang(user_id: int) -> str:
    user = await get_user(user_id)
    return user["lang"] if user else "en"


@router.callback_query(F.data == "categories")
async def show_categories(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await _get_lang(cb.from_user.id)
    cats = await get_categories(cb.from_user.id)
    text = t("categories_list", lang) if cats else t("categories_empty", lang)
    await cb.message.edit_text(text, reply_markup=categories_list_kb(cats, lang), parse_mode=ParseMode.HTML)
    await cb.answer()


@router.callback_query(F.data.startswith("cat:"))
async def view_category(cb: CallbackQuery):
    cat_id = cb.data.split(":")[1]
    lang = await _get_lang(cb.from_user.id)
    cat = await get_category(cat_id)
    if not cat:
        await cb.answer()
        return
    is_inbox = cat.get("is_inbox", False)
    text = f"{cat['emoji']} <b>{cat['name']}</b>"
    await cb.message.edit_text(text, reply_markup=category_actions_kb(cat_id, is_inbox, lang), parse_mode=ParseMode.HTML)
    await cb.answer()


# ── Add category ──

@router.callback_query(F.data == "cat_add")
async def start_add_category(cb: CallbackQuery, state: FSMContext):
    lang = await _get_lang(cb.from_user.id)
    await state.set_state(CategoryStates.entering_name)
    await state.update_data(lang=lang)
    await cb.message.edit_text(t("cat_enter_name", lang), reply_markup=cancel_kb(lang), parse_mode=ParseMode.HTML)
    await cb.answer()


@router.message(CategoryStates.entering_name)
async def enter_cat_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    await state.update_data(cat_name=message.text.strip())
    await state.set_state(CategoryStates.entering_emoji)
    await message.answer(t("cat_pick_emoji", lang), reply_markup=emoji_picker_kb(lang), parse_mode=ParseMode.HTML)


@router.callback_query(CategoryStates.entering_emoji, F.data.startswith("cat_emoji:"))
async def pick_emoji_button(cb: CallbackQuery, state: FSMContext):
    emoji = cb.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "en")
    await create_category(cb.from_user.id, data["cat_name"], emoji)
    await state.clear()
    await cb.message.edit_text(t("cat_created", lang), parse_mode=ParseMode.HTML)

    cats = await get_categories(cb.from_user.id)
    await cb.message.answer(
        t("categories_list", lang),
        reply_markup=categories_list_kb(cats, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.message(CategoryStates.entering_emoji)
async def pick_emoji_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    emoji = message.text.strip()[:2]
    await create_category(message.from_user.id, data["cat_name"], emoji)
    await state.clear()

    cats = await get_categories(message.from_user.id)
    await message.answer(t("cat_created", lang), parse_mode=ParseMode.HTML)
    await message.answer(
        t("categories_list", lang),
        reply_markup=categories_list_kb(cats, lang),
        parse_mode=ParseMode.HTML,
    )


# ── Rename ──

@router.callback_query(F.data.startswith("cat_rename:"))
async def start_rename(cb: CallbackQuery, state: FSMContext):
    cat_id = cb.data.split(":")[1]
    lang = await _get_lang(cb.from_user.id)
    await state.set_state(CategoryStates.renaming)
    await state.update_data(cat_id=cat_id, lang=lang)
    await cb.message.edit_text(t("cat_enter_new_name", lang), reply_markup=cancel_kb(lang), parse_mode=ParseMode.HTML)
    await cb.answer()


@router.message(CategoryStates.renaming)
async def finish_rename(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    cat = await get_category(data["cat_id"])
    emoji = cat["emoji"] if cat else "📁"
    await rename_category(data["cat_id"], message.text.strip(), emoji)
    await state.clear()

    cats = await get_categories(message.from_user.id)
    await message.answer(t("cat_renamed", lang), parse_mode=ParseMode.HTML)
    await message.answer(
        t("categories_list", lang),
        reply_markup=categories_list_kb(cats, lang),
        parse_mode=ParseMode.HTML,
    )


# ── Delete ──

@router.callback_query(F.data.startswith("cat_del:"))
async def confirm_delete(cb: CallbackQuery):
    cat_id = cb.data.split(":")[1]
    lang = await _get_lang(cb.from_user.id)
    cat = await get_category(cat_id)
    name = cat["name"] if cat else "?"
    await cb.message.edit_text(
        t("cat_confirm_delete", lang).format(name=name),
        reply_markup=confirm_delete_kb(cat_id, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data.startswith("cat_del_yes:"))
async def do_delete(cb: CallbackQuery):
    cat_id = cb.data.split(":")[1]
    lang = await _get_lang(cb.from_user.id)
    await delete_category(cat_id, cb.from_user.id)

    cats = await get_categories(cb.from_user.id)
    await cb.message.edit_text(t("cat_deleted", lang), parse_mode=ParseMode.HTML)
    await cb.message.answer(
        t("categories_list", lang),
        reply_markup=categories_list_kb(cats, lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()
