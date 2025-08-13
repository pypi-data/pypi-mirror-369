from .models import FavoriteItem
from ..common import connection
from ..common.db_ops import get_collection
from . import DB_NAME
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "favorite"

async def _upsert(favorite_data: FavoriteItem | None) -> dict:
    if not favorite_data:
        msg = "Favorite 데이터가 None입니다."
        mylogger.warning(msg)
        return {"item": None, "success": False, "message": msg}

    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, COL_NAME)
    await collection.create_index([("user_id", 1), ("code", 1)], unique=True)
    # upsert 필터: 동일한 user_id + 종목코드 조합 기준
    filter_ = {
        "user_id": favorite_data.user_id,
        "code": favorite_data.code,
    }

    # 날짜 업데이트
    data = favorite_data.model_dump(by_alias=True, exclude_unset=True, exclude={"_id"}) # ← 중요: _id는 immutable

    result = await collection.update_one(
        filter_,
        {
            "$set": data,
            "$currentDate": {"last_updated": True},  # UTC time을 몽고가 직접 적재
        },
        upsert=True,
    )

    if result.upserted_id or result.modified_count:
        doc = await collection.find_one(filter_)  # 방금 저장된 문서
        return {"success": True, "item": doc, "message": "저장됨"}
    return {"item": None, "success": False, "message": "변화없음"}

update = _upsert
save = _upsert

async def delete(user_id: str, code: str) -> dict:
    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, COL_NAME)
    res = await collection.delete_one({"user_id": user_id, "code": code})
    if res.deleted_count:
        return {"status": "deleted", "code": str(code)}
    return {"status": "삭제 대상이 없거나 권한이 없습니다."}


async def list_items(user_id: str) -> list[FavoriteItem]:
    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, COL_NAME)

    cursor = collection.find({"user_id": user_id}).sort("last_updated", -1)
    return [
        FavoriteItem.model_validate(d)
        async for d in cursor
    ]
