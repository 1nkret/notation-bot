import random

from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ParseMode

from db.mongo import get_user, get_inbox, get_categories, create_record
from utils.locales import t
from bot.records.keyboards import quick_capture_kb

router = Router()


@router.message()
async def quick_capture(message: Message):
    if not message.text:
        return

    user = await get_user(message.from_user.id)
    if not user:
        return

    lang = user["lang"]
    inbox = await get_inbox(message.from_user.id)
    if not inbox:
        return

    rec = await create_record(message.from_user.id, str(inbox["_id"]), message.text.strip())
    cats = await get_categories(message.from_user.id)

    key = f"quick_saved_{random.randint(1, 4)}"
    await message.answer(
        t(key, lang),
        reply_markup=quick_capture_kb(str(rec["_id"]), cats, inbox["_id"], lang),
        parse_mode=ParseMode.HTML,
    )
