from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from pydantic import ConfigDict, EmailStr
from beanie import Document
from pymongo import IndexModel
from pymongo.collation import Collation


class AbstractUser(SQLModel):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    if TYPE_CHECKING:
        email: str
    else:
        email: EmailStr = Field(
            sa_column_kwargs={"unique": True, "index": True}, nullable=False
        )
    hashed_password: str

    is_active: bool = Field(True, nullable=False)
    is_superuser: bool = Field(False, nullable=False)
    is_verified: bool = Field(False, nullable=False)

    model_config = ConfigDict(from_attributes=True)


class User(AbstractUser, table=True):
    pass


class AbstractUserDocument(Document):
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Settings:
        name = "users"
        email_collation = Collation("en", strength=2)
        indexes = [
            IndexModel(
                "email",
                name="case_insensitive_email_index",
                collation=email_collation,
                unique=True,
            ),
        ]


class UserDocument(AbstractUserDocument):
    pass
