from typing import Literal
from . import DB_NAME
from .models import CodeName
from ..common import connection


async def get_all_codes() -> list[str]:
    """
    c103, c104, c106 컬렉션에 모두 존재하는 코드의 리스트를 반환함.

    Returns:
        list[str]: c103, c104, c106 컬렉션에 공통으로 존재하는 종목 코드 리스트
    """
    client = connection.get_mongo_client()
    db = client[DB_NAME]

    collections = ['c103', 'c104', 'c106']

    # 첫 컬렉션으로 초기화
    s = set(await db[collections[0]].distinct("코드"))

    for col in collections[1:]:
        codes = await db[col].distinct("코드")
        s &= set(codes)

    return list(s)

async def get_all_tickers() -> list[str]:
    all_codes = await get_all_codes()
    tickers = [code.strip() + ".KS" for code in all_codes if code]
    return tickers

def get_all_codes_sync() -> list[str]:
    """
    c103, c104, c106 컬렉션에 모두 존재하는 코드의 리스트를 반환함.
    """
    client = connection.get_mongo_client_sync()
    try:
        db = client[DB_NAME]
        collections = ['c103', 'c104', 'c106']

        # 첫 컬렉션 코드 셋팅
        common_codes = set(db[collections[0]].distinct("코드"))

        for col in collections[1:]:
            codes = db[col].distinct("코드")
            common_codes &= set(codes)

        return sorted(common_codes)  # 필요에 따라 정렬
    finally:
        connection.close_mongo_client_sync()


async def get_all_codes_names(sort_by:Literal['종목명', '코드']='종목명') -> list[CodeName]:
    client = connection.get_mongo_client()
    collection = client[DB_NAME]['c101']
    pipeline = [
        # ① 먼저 원하는 필드 기준으로 정렬
        #    → 이후 $group에서 같은 코드 중 '첫 번째' 문서를 취하기 위해
        {"$sort": {sort_by: 1}},

        # ② 코드별로 그룹핑, 중복 제거
        {
            "$group": {
                "_id": "$코드",  # 그룹 키
                "코드": {"$first": "$코드"},
                "종목명": {"$first": "$종목명"}
            }
        },

        # ③ _id 제거, 필드만 남김
        {"$project": {"_id": 0, "코드": 1, "종목명": 1}},

        # ④ (선택) 최종 정렬
        {"$sort": {sort_by: 1}}
    ]

    cursor = collection.aggregate(pipeline)
    return [CodeName(**doc) async for doc in cursor]


def get_all_codes_names_sync(sort_by:Literal['종목명', '코드']='종목명') -> list[CodeName] | None:
    client = connection.get_mongo_client_sync()
    try:
        collection = client[DB_NAME]['c101']

        pipeline = [
            {"$sort": {sort_by: 1}},  # ① 정렬
            {"$group": {  # ② 코드별 첫 문서
                "_id": "$코드",
                "코드": {"$first": "$코드"},
                "종목명": {"$first": "$종목명"},
            }},
            {"$project": {"_id": 0, "코드": 1, "종목명": 1}},  # ③ 필드 정제
            {"$sort": {sort_by: 1}},  # ④ 최종 정렬(선택)
        ]

        cursor = collection.aggregate(pipeline)
        return [CodeName(**doc) for doc in cursor]  # ← 동기 for

    finally:
        connection.close_mongo_client_sync()  # ← client 인자 전달


async def delete_code_from_all_collections(code: str) -> dict[str, int]:
    client = connection.get_mongo_client()
    db = client[DB_NAME]

    collections = ['c101', 'c103', 'c104', 'c106', 'c108']

    deleted_counts = {}

    for col in collections:
        result = await db[col].delete_many({"코드": code})
        deleted_counts[col] = result.deleted_count

    print(f"삭제된 도큐먼트 갯수: {deleted_counts}")
    return deleted_counts

