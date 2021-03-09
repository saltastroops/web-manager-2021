from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    email: str
    family_name: str
    given_name: str
    username: str


class UserInDB(User):
    hashed_password: str
