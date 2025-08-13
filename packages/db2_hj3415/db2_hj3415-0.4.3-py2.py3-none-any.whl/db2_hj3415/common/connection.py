import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__)

# ─────────────────────────────
# 공통 환경변수
# ─────────────────────────────
MONGO_URI = os.getenv("MONGO_ADDR", "mongodb://localhost:27017")

# ─────────────────────────────
# 비동기 클라이언트 (motor)
# ─────────────────────────────
client_async: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    global client_async
    if client_async is None:
        mylogger.info(f"[MongoDB] Connecting to async MongoDB: {MONGO_URI}")
        client_async = AsyncIOMotorClient(MONGO_URI)
    return client_async

def close_mongo_client():
    if client_async:
        mylogger.info("[MongoDB] Closing async MongoDB connection")
        client_async.close()

# ─────────────────────────────
# 동기 클라이언트 (pymongo)
# ─────────────────────────────
client_sync: MongoClient | None = None

def get_mongo_client_sync() -> MongoClient:
    global client_sync
    if client_sync is None:
        mylogger.info(f"[MongoDB] Connecting to sync MongoDB: {MONGO_URI}")
        client_sync = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        try:
            client_sync.admin.command("ping")
            mylogger.info("[MongoDB] Sync MongoDB connection successful")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            mylogger.error(f"[MongoDB] Sync connection failed: {e}")
            raise
    return client_sync

def close_mongo_client_sync():
    if client_sync:
        mylogger.info("[MongoDB] Closing sync MongoDB connection")
        client_sync.close()