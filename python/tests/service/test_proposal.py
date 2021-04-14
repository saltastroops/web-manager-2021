"""Tests for the proposal service."""
from datetime import date

import pytest
from aiomysql import Pool

from app.models.pydantic import Semester
from app.service.proposal import (
    get_observed_targets,
    get_observed_time,
    get_proposal_allocations,
    get_proposal_requested_time,
    get_proposal_text,
)
from tests.markers import nodatabase


@nodatabase
@pytest.mark.asyncio
async def test_get_proposal_text_return_correct_text(db: Pool) -> None:
    """get_proposal_text return correct proposal text"""
    proposal_text = await get_proposal_text(
        "2020-1-MLT-005", Semester(semester=1, year=2020), db
    )
    assert "and Kinematics of Multi-phase Gas" in proposal_text["title"]
    assert (
        "providing an excellent tracer of dynamical mass" in proposal_text["abstract"]
    )
    assert "Specific notes and instructions to observer:" in proposal_text["read_me"]


@nodatabase
@pytest.mark.asyncio
async def test_get_proposal_allocations_return_correct_allocations(db: Pool) -> None:
    """get_proposal_allocations return correct allocations."""
    proposal_allocations = await get_proposal_allocations(
        "2020-1-MLT-005", Semester(semester=2, year=2020), db
    )
    for a in proposal_allocations:
        if a["partner_code"] == "UW":
            assert a["priority_0"] == 0
            assert a["priority_1"] == 55781
            assert a["priority_2"] == 0
            assert a["priority_3"] == 0
            assert a["priority_4"] == 0
        if a["partner_code"] == "RU":
            assert a["priority_0"] == 0
            assert a["priority_1"] == 0
            assert a["priority_2"] == 0
            assert a["priority_3"] == 0
            assert a["priority_4"] == 0
        if not a["partner_code"] in ["UW", "RU"]:
            assert False


@nodatabase
@pytest.mark.asyncio
async def test_get_proposal_requested_time_return_correct_requested_time(
    db: Pool,
) -> None:
    """get_proposal_requested_time return correct requested time."""
    proposal_requested_time = await get_proposal_requested_time("2021-1-MLT-005", db)
    assert len(proposal_requested_time) == 4
    for r in proposal_requested_time:
        if r["semester"] == "2021-1":
            assert r["total_requested_time"] == 127000
            assert r["minimum_useful_time"] == 20000
            assert r["time_comment"].startswith("Minimum useful time is based")
        if (
            r["semester"] == "2022-1"
            or r["semester"] == "2021-2"
            or r["semester"] == "2022-2"
        ):
            assert r["total_requested_time"] == 127000
            assert r["minimum_useful_time"] == 20000
        if not r["semester"] in ["2021-1", "2021-2", "2022-1", "2022-2"]:
            assert False


@nodatabase
@pytest.mark.asyncio
async def test_get_observed_time_return_correct_time(db: Pool) -> None:
    """get_observed_time return correct charged time."""
    observed_time = await get_observed_time(
        "2017-1-SCI-003", Semester(semester=1, year=2017), db
    )
    assert observed_time["priority_0"] == 0
    assert observed_time["priority_1"] == 0
    assert observed_time["priority_2"] == 4614
    assert observed_time["priority_3"] == 2307
    assert observed_time["priority_4"] == 0


@nodatabase
@pytest.mark.asyncio
async def test_get_observed_targets_return_correct_targets(db: Pool) -> None:
    """get_observed_targets return correct targets."""

    observed_targets = await get_observed_targets("2020-1-MLT-005", db)
    assert len(observed_targets) == 29
    sot = sorted(observed_targets, key=lambda i: i["block_id"])
    assert sot[0]["block_id"] == 82583
    assert sot[0]["block_name"] == "730224776306_Med_Res"
    assert sot[0]["target_name"] == "730224776306 Medium Res"
    assert sot[0]["observation_date"] == date(year=2020, month=7, day=18)

    assert sot[9]["block_id"] == 85981
    assert sot[9]["block_name"] == "730226139133_Med_Res"
    assert sot[9]["target_name"] == "730226139133 Medium Res"
    assert sot[9]["observation_date"] == date(year=2020, month=12, day=19)

    assert sot[20]["block_id"] == 85999
    assert sot[20]["block_name"] == "730161469909_Med_Res"
    assert sot[20]["target_name"] == "730161469909 Medium Res"
    assert sot[20]["observation_date"] == date(year=2021, month=1, day=13)
