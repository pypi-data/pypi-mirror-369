from motor.motor_asyncio import AsyncIOMotorClient

def get_collection(client: AsyncIOMotorClient, db_name: str, col_name: str):
    return client[db_name][col_name]