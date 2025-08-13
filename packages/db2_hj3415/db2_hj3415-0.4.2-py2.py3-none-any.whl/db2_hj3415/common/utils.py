# 자주 쓰는 간단한 유틸 함수
import pandas as pd
import numpy as np
import math

def df_to_dict_replace_nan(df: pd.DataFrame) -> list[dict]:
    # NaN → None으로 변환
    return df.replace({np.nan: None}).to_dict(orient="records")


def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(v) for v in obj]
    else:
        return obj