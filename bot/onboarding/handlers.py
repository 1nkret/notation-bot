from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode

from db.mongo import upsert_user, get_user, create_category, update_user_lang
from utils.locales import t
from bot.onboarding.keyboards import lang_select_kb
from bot.start.handlers import show_dashboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user(message.from_user.id)

    if user:
        lang = user["lang"]
        await show_dashboard(message.from_user.id, lang, send_message=message.answer)
        return

    await message.answer(
        t("onboarding_hello", "en"),
        reply_markup=lang_select_kb(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def on_lang_select(cb: CallbackQuery):
    lang = cb.data.split(":")[1]

    user = await get_user(cb.from_user.id)
    if user:
        await update_user_lang(cb.from_user.id, lang)
        await cb.message.edit_text(t("lang_changed", lang), parse_mode=ParseMode.HTML)
        await show_dashboard(cb.from_user.id, lang, send_message=cb.message.answer)
        await cb.answer()
        return

    await upsert_user(
        user_id=cb.from_user.id,
        username=cb.from_user.username or "",
        first_name=cb.from_user.first_name or "",
        lang=lang,
    )

    inbox_name = {"en": "Inbox", "ru": "Входящие", "uk": "Вхідні"}.get(lang, "Inbox")
    await create_category(cb.from_user.id, inbox_name, "📥", is_inbox=True)

    await cb.message.edit_text(t("onboarding_welcome", lang), parse_mode=ParseMode.HTML)
    await show_dashboard(cb.from_user.id, lang, send_message=cb.message.answer)
    await cb.answer()
