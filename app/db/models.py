from sqlmodel import SQLModel, Field
import datetime


class users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field( unique=True, max_length=50, nullable=False)
    email: str= Field(unique=True, max_length=100,nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.datetime.utcnow)
  