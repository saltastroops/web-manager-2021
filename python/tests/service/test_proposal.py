"""Tests for the proposal service."""
from datetime import date

import pytest
from aiomysql import Pool

from app.models.pydantic import Semester
from app.service.proposal import (
    get_block_visits,
    get_observed_time,
    get_time_allocations,
    get_requested_time,
    get_text_content, get_investigators,
)
from tests.markers import nodatabase


@nodatabase
@pytest.mark.asyncio
async def test_get_text_content_return_correct_text(db: Pool) -> None:
    """get_text_content return correct proposal text"""
    proposal_text = await get_text_content(
        "2020-1-MLT-005", Semester(semester=1, year=2020), db
    )
    assert "and Kinematics of Multi-phase Gas" in proposal_text.title
    assert (
        "providing an excellent tracer of dynamical mass" in proposal_text.abstract
    )
    assert "Specific notes and instructions to observer:" in proposal_text.read_me


@nodatabase
@pytest.mark.asyncio
async def test_get_proposal_allocations_return_correct_allocations(db: Pool) -> None:
    """get_time_allocations return correct allocations."""
    proposal_allocations = await get_time_allocations(
        "2020-1-MLT-005", Semester(semester=2, year=2020), db
    )
    for a in proposal_allocations:
        if a["partner"].code == "UW":
            assert a["priority_0"] == 0
            assert a["priority_1"] == 55781
            assert a["priority_2"] == 0
            assert a["priority_3"] == 0
            assert a["priority_4"] == 0
        if a["partner"].code == "RU":
            assert a["priority_0"] == 0
            assert a["priority_1"] == 0
            assert a["priority_2"] == 0
            assert a["priority_3"] == 0
            assert a["priority_4"] == 0
        if not a["partner"].code in ["UW", "RU"]:
            assert False


@nodatabase
@pytest.mark.asyncio
async def test_get_proposal_requested_time_return_correct_requested_time(
    db: Pool,
) -> None:
    """get_requested_time return correct requested time."""
    proposal_requested_time = await get_requested_time("2021-1-MLT-005", 10497, db)
    assert len(proposal_requested_time) == 4
    for r in proposal_requested_time:
        if (
            r.semester == Semester(year=2021, semester=1)
            or r.semester == Semester(year=2022, semester=1)
        ):
            assert r.total_requested_time == 127000
            assert r.minimum_useful_time == 20000
        if (
            r.semester == Semester(year=2021, semester=2)
            or r.semester == Semester(year=2022, semester=2)
        ):
            assert r.total_requested_time == 76000
            assert r.minimum_useful_time == 20000
        if not r.semester in [
            Semester(year=2021, semester=1),
            Semester(year=2021, semester=2),
            Semester(year=2022, semester=1),
            Semester(year=2022, semester=2),
            "2021-2", "2022-1", "2022-2"]:
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
    """get_block_visits return correct targets."""

    observed_targets = await get_block_visits("2017-1-SCI-005", db)
    assert len(observed_targets) == 12
    sot = sorted(observed_targets, key=lambda i: i.block_id)
    assert sot[0].block_id == 56305
    assert sot[0].block_name == "Block for SN2017cbv"
    assert sot[0].target_name == "SN2017cbv"
    assert sot[0].observation_date == date(2017, 5, 14)

    assert sot[9].block_id == 60479
    assert sot[9].block_name == "Block for SN2017cbv - Blue3"
    assert sot[9].target_name == "SN2017cbv"
    assert sot[9].observation_date == date(2017, 7, 26)

    assert sot[10].block_id == 62760
    assert sot[10].block_name == "Block for SN2017bzc - Blue4"
    assert sot[10].target_name == "SN2017bzc"
    assert sot[10].observation_date == date(2017, 8, 26)

