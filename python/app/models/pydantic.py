from pydantic import BaseModel, validator


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class Semester(BaseModel):
    """
    A SALT semester.

    A semester has a year and a semester. The year must be between 2006 and 2100 (both
    inclusive), the semester must be 1 or 2.

    Semester 1 runs from 1 May noon UTC to 1 November noon UTC, semester 2 from
    1 November noon UTC to 1 May noon UTC. So, for example, 2 June 2021 belongs to
    semester 2021-1, 5 December 2021 to semester 2021-2 and 16 February 2022 also to
    semester 2021-2.
    """

    semester: int
    year: int

    @validator("year")
    def year_must_in_valid_range(cls, v: int) -> int:
        if v < 2006 or v > 2100:
            raise ValueError("must be between 2005 and 2100")
        return v

    @validator("semester")
    def semester_must_be_one_or_two(cls, v: int) -> int:
        if v != 1 and v != 2:
            raise ValueError("must be 1 or 2")
        return v


class User(BaseModel):
    email: str
    family_name: str
    given_name: str
    username: str


class UserInDB(User):
    hashed_password: str
