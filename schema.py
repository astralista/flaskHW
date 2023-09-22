from typing import Optional

from pydantic import BaseModel, validator


class CreateUser(BaseModel):
    name: str
    password: str

    @validator("password")
    def secure_password(cls, value):
        if len(value) <= 8:
            raise ValueError("Password is short")
        return value


class UpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]

    @validator("password")
    def secure_password(cls, value):
        if len(value) <= 8:
            raise ValueError("Password is short")
        return value


class CreateAd(BaseModel):
    headline: str
    description: str


class UpdateAd(BaseModel):
    headline: Optional[str]
    description: Optional[str]


class AdSchema(BaseModel):
    id: int
    headline: str
    description: str
    creation_time: str
    owner: int
