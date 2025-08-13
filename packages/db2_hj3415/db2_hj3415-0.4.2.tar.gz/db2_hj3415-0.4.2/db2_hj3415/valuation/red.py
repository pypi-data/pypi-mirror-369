from . import RedData, _ops

from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "red"


async def save(red_data: RedData) -> dict:
    return await _ops.save(COL_NAME, red_data)


async def save_many(many_data: dict[str, RedData]) -> dict:
    return await _ops.save_many(COL_NAME, many_data)

async def get_latest(code: str) -> RedData | None:
    return await _ops.get_latest(COL_NAME, code)


