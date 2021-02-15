from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str
