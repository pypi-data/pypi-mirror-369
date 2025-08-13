from datetime import datetime, time, timezone, timedelta
from pymongo import ASCENDING, DESCENDING
from pydantic import ValidationError
from bson import ObjectId

from .models import AIReport
from . import DB_NAME
from db2_hj3415.common.db_ops import get_collection
from db2_hj3415.common import connection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

from typing import Optional, Tuple
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

def _day_range_as_utc(dt: datetime, day_tz=timezone.utc) -> tuple[datetime, datetime]:
    """
    dt가 속한 '하루'를 day_tz 기준으로 계산한 뒤,
    MongoDB 쿼리에 쓰기 좋게 UTC 경계시간 [start, next_day)로 변환해서 반환.
    """
    # naive이면 UTC로 간주(정책에 맞게 조정 가능)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    local_dt = dt.astimezone(day_tz)
    start_local = datetime.combine(local_dt.date(), time(0, 0, 0, tzinfo=day_tz))
    next_local = start_local + timedelta(days=1)

    start_utc = start_local.astimezone(timezone.utc)
    next_utc = next_local.astimezone(timezone.utc)
    return start_utc, next_utc

async def find_today_doc(collection, ticker: str, 기준시각: datetime, day_tz=timezone.utc) -> Optional[dict]:
    """
    주어진 기준시각이 속한 '오늘'(day_tz 기준)에 해당하는 문서를 찾아 반환.
    없으면 None.
    """
    start_utc, next_utc = _day_range_as_utc(기준시각, day_tz)
    return await collection.find_one({
        "ticker": ticker,
        "날짜": {"$gte": start_utc, "$lt": next_utc}
    })

async def exists_today(col:str, ticker: str) -> bool:
    """
    존재 여부만 필요할 때: True/False
    """
    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, col)
    now = datetime.now(timezone.utc)
    return (await find_today_doc(collection, ticker, now, KST)) is not None


async def save(col: str, data: AIReport) -> dict:
    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, col)
    await collection.create_index([("날짜", ASCENDING), ("ticker", ASCENDING)], unique=True)

    if not data.날짜:
        data.날짜 = datetime.now(timezone.utc)

    # 오늘 기준 중복 확인 (기본 UTC 기준; KST 기준으로 바꾸려면 day_tz=KST)
    existing = await find_today_doc(collection, data.ticker, data.날짜, day_tz=timezone.utc)
    mylogger.debug(f"이미 저장된 오늘 날짜 데이터가 있나?: {existing}")

    if existing:
        return {"status": "skipped", "reason": "already_saved_today"}

    doc = data.model_dump(by_alias=True, mode='python', exclude_none=False)

    if '_id' in doc:
        if doc['_id'] is None:
            doc.pop('_id')
        else:
            doc['_id'] = ObjectId(doc['_id']) if isinstance(doc['_id'], str) else doc['_id']
            await collection.replace_one({'_id': doc['_id']}, doc, upsert=True)
            return {"status": "updated", "_id": str(doc['_id'])}

    result = await collection.insert_one(doc)
    data.id = str(result.inserted_id)
    return {"status": "inserted", "_id": data.id}


async def get_latest(col: str, ticker: str) -> AIReport | None:
    if col not in ['by_nfs', 'by_price']:
        raise ValueError(f"지원되지 않는 컬렉션: {col}")

    client = connection.get_mongo_client()
    collection = get_collection(client, DB_NAME, col)
    doc = await collection.find_one(
        {"ticker": ticker},
        sort=[("날짜", DESCENDING)]
    )

    if not doc:
        mylogger.warning("데이터 없음: %s (%s)", col, ticker)
        return None

    doc["_id"] = str(doc["_id"])  # 필요 시만

    try:
        return AIReport(**doc)  # type: ignore[arg-type]
    except ValidationError as e:
        mylogger.error("Pydantic 검증 실패 (%s, %s): %s", col, ticker, e)
        return None