from . import AIReport, _ops

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "by_nfs"


async def save(report: AIReport) -> dict:
    return await _ops.save(COL_NAME, report)


async def get_latest(ticker: str) -> AIReport | None:
    return await _ops.get_latest(COL_NAME, ticker)


async def exist_today(ticker: str) -> bool:
    return await _ops.exists_today(COL_NAME, ticker)