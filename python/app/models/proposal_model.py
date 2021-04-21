from datetime import date, datetime
from astropy.coordinates import Angle
from typing import Optional, List

from pydantic import BaseModel, validator

from app.models.pydantic import Semester


class TextContent(BaseModel):
    """

    """
    title: str
    abstract: str
    read_me: str
    nightlog_summary: str


class Affiliation(BaseModel):
    """

    """
    partner_code: str
    partner_name: str
    institute: str
    department: str
    home_page: str


class Investigator(BaseModel):
    """

    """
    is_pc: bool
    is_pi: bool
    name: str
    affiliation: Affiliation


class TimeAllocations(BaseModel):
    """

    """
    partner_code: str
    partner_name: str
    tac_comment: Optional[str]
    priority_0: int
    priority_1: int
    priority_2: int
    priority_3: int
    priority_4: int


class BlockVisit(BaseModel):
    """

    """
    block_id: int
    block_name: str
    observed_time: str
    priority: str
    max_luner_phase: str
    target_name: str
    observation_date: date
    status: str
    rejection_reason: Optional[str]


class Partner(BaseModel):
    name: str
    code: str


class AstroAngle(BaseModel):
    v: Angle

    class Config:
        arbitrary_types_allowed = True


class Target(BaseModel):
    name: str
    ra: Optional[AstroAngle]
    dec_sign: Optional[AstroAngle]
    dec: str
    equinox: float
    minimum_magnitude: float
    maximum_magnitude: float
    target_type: str
    sub_type: str
    is_optional: bool
    n_visits: int
    max_luner_phase: float
    ranking: str
    night_count: int
    moon_probability: int
    competition_probability: int
    observability_probability: int
    seeing_probability: int
    identifier: Optional[str]
    output_interval: Optional[int]
    ra_dot: Optional[AstroAngle]
    dec_dot: Optional[AstroAngle]
    epoch: Optional[datetime]


class RequestedTime(BaseModel):
    total_requested_time: int
    minimum_useful_time: int
    time_comment: Optional[str]
    semester: Semester
    distribution: List
