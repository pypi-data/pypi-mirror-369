from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, field_serializer


class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    username: str
    nickname: str | None
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = False
    roles: list[str] = Field(default_factory=lambda: ["user"])

    model_config = ConfigDict(populate_by_name=True)

class Portfolio(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str  # MongoDB의 ObjectId를 str로 저장
    코드: str
    종목명: str | None = None
    purchase_date: datetime | None
    purchase_price: float | None
    quantity: int | None

    target_price: float | None = None
    stop_loss_price: float | None = None
    memo: str | None = None
    tags: list[str] | None = []
    is_favorite: bool = False
    last_updated: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)





class FavoriteItem(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str = Field(...)
    code: str = Field(...)
    memo: str | None = Field(default='')
    last_updated: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("id", mode="before")
    @classmethod
    def cast_objectid(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    @field_serializer("last_updated", when_used="json")
    def serialize_date(self, v: datetime) -> str:
        return v.isoformat()
