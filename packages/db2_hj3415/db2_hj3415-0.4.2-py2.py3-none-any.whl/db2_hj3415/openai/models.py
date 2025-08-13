from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from . import DATE_FORMAT


class AIReport(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    ticker: str
    날짜: datetime | None = None
    message: str

    @field_validator("id", mode="before")
    @classmethod
    def cast_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    @field_validator("날짜", mode="before")
    @classmethod
    def parse_date(cls, v):
        # ① 이미 datetime 이면 그대로 통과
        if isinstance(v, datetime):
            return v
        # ② YYYY.MM.DD 형태의 순수 문자열
        if isinstance(v, str) and len(v) == 10:
            return datetime.strptime(v, DATE_FORMAT)
        # ③ ISO-8601 문자열도 허용하고 싶다면
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                pass
        raise TypeError("잘못된 날짜 형식")

    # 날짜 필드 ISO 직렬화
    @field_serializer("날짜", when_used="json")
    def serialize_date(self, v: datetime) -> str:
        return v.isoformat()

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )