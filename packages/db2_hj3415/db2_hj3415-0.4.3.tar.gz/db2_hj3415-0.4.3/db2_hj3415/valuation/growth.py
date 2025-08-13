from . import GrowthData, _ops
from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "growth"


async def save(growth_data: GrowthData) -> dict:
    return await _ops.save(COL_NAME, growth_data)


async def save_many(many_data: dict[str, GrowthData]) -> dict:
    return await _ops.save_many(COL_NAME, many_data)


async def get_latest(code: str) -> GrowthData | None:
    return await _ops.get_latest(COL_NAME, code)

