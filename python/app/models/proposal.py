from datetime import date, datetime
from typing import List, Optional, Dict, Any

from astropy.coordinates import Angle
from astropy.units import Quantity
from pydantic import BaseModel, validator

from app.models.general import Semester


class TextContent(BaseModel):
    """
    The text content of a proposal.

    Fields
    ------
    title:
        Proposal title.
    abstract:
        Proposal abstract.
    read_me:
        Instructions for the observer.
    nightlog_summary:
        Brief (one-line) summary to include in the nightlog.
    """

    title: str
    abstract: str
    read_me: str
    nightlog_summary: str


class Partner(BaseModel):
    """
    A SALT partner.

    Fields
    ------
    code:
        Partner code, such as IUCAA or RSA.
    name:
        Partner name.
    """

    code: str
    name: str


class Institute(BaseModel):
    """
    An institute, optionally with a department.

    Fields
    ------
    partner:
        SALT Partner to which the institute belongs.
    name:
        Institute name.
    department:
        Department within the institute.
    home_page:
        URL of the institute's (or department's) home page.
    """

    partner: Partner
    name: str
    department: Optional[str]
    home_page: str


class PersonalDetails(BaseModel):
    """
    Personal details.

    Fields
    ------
    given_name:
        The given ("first") name(s).
    family_name:
        The family ("last") name.
    email:
        The preferred email address.
    """

    given_name: str
    family_name: str
    email: str


class Investigator(BaseModel):
    """
    An investigator on a proposal.

    Fields
    ------
    is_pc:
        Whether the investigator is the Principal Contact.
    is_pi:
        Whether the investigator is the Principal Investigator.
    personal_details:
        Personal details of the investigator, which may differ from the ones given in
        the proposal.
    affiliation:
        Affiliation of the investigator (for the proposal).
    """

    is_pc: bool
    is_pi: bool
    personal_details: PersonalDetails
    affiliation: Institute


class TimeAllocations(BaseModel):
    """
    A time allocation by a partner.

    Fields
    ------
    partner:
        SALT partner that allocated the time.
    tac_comment:
        An (optional) comment made by the TAC on the proposal for which this time
        allocation was made.
    priority_0:
        Allocated priority 0 time.
    priority_1:
        Allocated priority 1 time.
    priority_2:
        Allocated priority 2 time.
    priority_3:
        Allocated priority 3 time.
    priority_4:
        Allocated priority 4 time.
    """

    partner_code: str
    partner_name: str
    tac_comment: Optional[str]
    priority_0: Quantity
    priority_1: Quantity
    priority_2: Quantity
    priority_3: Quantity
    priority_4: Quantity


class BlockVisit(BaseModel):
    """
    A block visit, i.e. an observation made for a block.

    Fields
    ------
    block_id:
       Database id of the observed block.
    block_name:
       Name of the observed block.
    observed_time:
       The nominal time spent on making the observation. This is the time charged for,
       and may differ from the actual time spent.
    priority:
       Priority of the block.
    max_lunar_phase:
       The maximum lunar phase allowed for the observation. The lunar phase is the
       illuminated fraction of the Moon, as a percentage. It is taken to be 0 if the
       Moon is below the horizon.
    target_names:
       Names of the observed targets.
    observation_night:
       Date of the observation night. This is the date when the night starts, i.e. all
       observation done during the same night have the same observation night date.
    status:
       Status of the observation, such "Accepted" or "Rejected".
    rejection_reason:
       Reason why the observation has been rejected.
    """

    block_id: int
    block_name: str
    observed_time: str
    priority: str
    max_lunar_phase: str
    target_names: List[str]
    observation_night: date
    status: str
    rejection_reason: Optional[str]


class Phase1Target(BaseModel):
    """
    Target details in a Phase 1 proposal.

    Fields
    ------
    name:
        Target name.
    right_ascension:
        Right ascension.
    declination:
        Declination.
    equinox:
        Equinox for the target coordinates.
    horizons_identifier:
        Identifier in the Horizons database for solar system targets.
    minimum_magnitude:
        Minimum magnitude of the target.
    maximum_magnitude:
        Maximum magnitude.
    target_type:
        Target type (broad category).
    target_subtype:
        Target subtype.
    is_optional:
        Whether the target is optional. i.e. whether it is part of a pool of targets
        from which only a subset needs to be observed.
    n_visits:
        The number of observations requested for the target.
    max_lunar_phase:
        The maximum lunar phase allowed for an observation of the target. The lunar
        phase is the illuminated fraction of the Moon, as a percentage. It is taken to
        be 0 if the Moon is below the horizon.
    ranking:
        Importance attributed by the Principal Investigator to observations of this
        target relative to other observations for the same proposal.
    night_count:
        The number of nights when the target can be observed, given the requested
        observation time and observation constraints.
    TODO: Comment on probabilities
    """

    name: str
    right_ascension: Optional[Angle]
    declination: Optional[Angle]
    equinox: float
    horizons_identifier: Optional[str]
    minimum_magnitude: float
    maximum_magnitude: float
    target_type: str
    target_subtype: str
    is_optional: bool
    n_visits: int
    max_lunar_phase: float
    ranking: str
    night_count: int
    moon_probability: int
    competition_probability: int
    observability_probability: int
    seeing_probability: int


class RequestedTime(BaseModel):
    total_requested_time: int
    minimum_useful_time: int
    time_comment: Optional[str]
    semester: Semester
    distribution: List


class Proposal(BaseModel):
    text_content: TextContent
    investigators: List[Investigator]
    block_visits: List[BlockVisit]
    observed_time: Dict[str, Any]
    time_allocations: TimeAllocations


class Phase1Proposal(BaseModel):
    text_content: TextContent
    investigators: List[Investigator]
    block_visits: List[BlockVisit]
    observed_time: Dict[str, Any]
    time_allocations: TimeAllocations