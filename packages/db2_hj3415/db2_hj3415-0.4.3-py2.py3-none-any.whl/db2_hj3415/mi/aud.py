import pandas as pd
from . import _ops
from .models import Aud

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "aud"

async def save(data: Aud):
    return await _ops._save_one_collection(COL_NAME, data)

async def find(date_str: str):
    return await _ops.find(COL_NAME, date_str)

async def delete(date_str: str):
    return await _ops.delete(COL_NAME, date_str)

async def save_history(df: pd.DataFrame):
    numeric_columns = ["종가", "전일대비"]
    await _ops._save_market_history_type1(df, COL_NAME, numeric_columns)

