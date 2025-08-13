from . import MilData, _ops

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "mil"


async def save(mil_data: MilData) -> dict:
    return await _ops.save(COL_NAME, mil_data)


async def save_many(many_data: dict[str, MilData]) -> dict:
    return await _ops.save_many(COL_NAME, many_data)


async def get_latest(code: str) -> MilData | None:
    return await _ops.get_latest(COL_NAME, code)
