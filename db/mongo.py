from datetime import datetime, timezone

from bson import ObjectId

from db.client import Database


def _db():
    return Database.get_db()


async def setup_indexes():
    await _db().users.create_index("user_id", unique=True)
    await _db().categories.create_index("user_id")
    await _db().records.create_index([("user_id", 1), ("category_id", 1)])


# ── Users ──

async def upsert_user(user_id: int, username: str, first_name: str, lang: str = "en") -> dict:
    user = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "lang": lang,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await _db().users.update_one(
        {"user_id": user_id},
        {"$setOnInsert": user},
        upsert=True,
    )
    return user


async def get_user(user_id: int) -> dict | None:
    return await _db().users.find_one({"user_id": user_id})


async def update_user_lang(user_id: int, lang: str):
    await _db().users.update_one(
        {"user_id": user_id},
        {"$set": {"lang": lang}},
    )


# ── Categories ──

async def create_category(user_id: int, name: str, emoji: str = "📁", is_inbox: bool = False) -> dict:
    count = await _db().categories.count_documents({"user_id": user_id})
    cat = {
        "user_id": user_id,
        "name": name,
        "emoji": emoji,
        "is_inbox": is_inbox,
        "order": 0 if is_inbox else count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await _db().categories.insert_one(cat)
    cat["_id"] = result.inserted_id
    return cat


async def get_categories(user_id: int) -> list[dict]:
    cursor = _db().categories.find({"user_id": user_id}).sort("order", 1)
    return await cursor.to_list(length=50)


async def get_category(category_id: str) -> dict | None:
    return await _db().categories.find_one({"_id": ObjectId(category_id)})


async def get_inbox(user_id: int) -> dict | None:
    return await _db().categories.find_one({"user_id": user_id, "is_inbox": True})


async def rename_category(category_id: str, name: str, emoji: str):
    await _db().categories.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": {"name": name, "emoji": emoji}},
    )


async def delete_category(category_id: str, user_id: int):
    inbox = await get_inbox(user_id)
    if inbox:
        await _db().records.update_many(
            {"category_id": ObjectId(category_id)},
            {"$set": {"category_id": inbox["_id"]}},
        )
    await _db().categories.delete_one({"_id": ObjectId(category_id)})


# ── Records ──

async def create_record(user_id: int, category_id: str, text: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    rec = {
        "user_id": user_id,
        "category_id": ObjectId(category_id),
        "text": text,
        "done": False,
        "created_at": now,
        "updated_at": now,
    }
    result = await _db().records.insert_one(rec)
    rec["_id"] = result.inserted_id
    return rec


async def get_records(user_id: int, category_id: str, skip: int = 0, limit: int = 8) -> list[dict]:
    cursor = (
        _db().records
        .find({"user_id": user_id, "category_id": ObjectId(category_id)})
        .sort([("done", 1), ("created_at", -1)])
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def count_records(user_id: int, category_id: str) -> int:
    return await _db().records.count_documents(
        {"user_id": user_id, "category_id": ObjectId(category_id)},
    )


async def count_by_category(user_id: int) -> dict:
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$category_id", "count": {"$sum": 1}}},
    ]
    result = {}
    async for doc in _db().records.aggregate(pipeline):
        result[doc["_id"]] = doc["count"]
    return result


async def get_record(record_id: str) -> dict | None:
    return await _db().records.find_one({"_id": ObjectId(record_id)})


async def update_record(record_id: str, **fields):
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    await _db().records.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": fields},
    )


async def toggle_done(record_id: str) -> bool:
    rec = await _db().records.find_one({"_id": ObjectId(record_id)})
    if not rec:
        return False
    new_done = not rec["done"]
    await _db().records.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {"done": new_done}},
    )
    return new_done


async def move_record(record_id: str, new_category_id: str):
    await update_record(record_id, category_id=ObjectId(new_category_id))


async def delete_record(record_id: str):
    await _db().records.delete_one({"_id": ObjectId(record_id)})


async def clear_done(user_id: int, category_id: str) -> int:
    result = await _db().records.delete_many({
        "user_id": user_id,
        "category_id": ObjectId(category_id),
        "done": True,
    })
    return result.deleted_count
