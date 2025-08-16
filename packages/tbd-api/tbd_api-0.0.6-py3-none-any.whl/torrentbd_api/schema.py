from typing import List

from pydantic import BaseModel


class Badge(BaseModel):
    title: str
    image_url: str


class User(BaseModel):
    user_id: int
    name: str
    profile_url: str
    rank: str
    badges: List[Badge] = []


class OnlineUsersResponse(BaseModel):
    count: int
    users: List[User]
