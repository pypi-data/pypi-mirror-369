from . import BlueData, _ops

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "blue"


async def save(blue_data: BlueData) -> dict:
    return await _ops.save(COL_NAME, blue_data)


async def save_many(many_data: dict[str, BlueData]) -> dict:
    return await _ops.save_many(COL_NAME, many_data)


async def get_latest(code: str) -> BlueData | None:
    return await _ops.get_latest(COL_NAME, code)

