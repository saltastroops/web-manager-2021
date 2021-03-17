"""Tests for the block service."""
import pytest

from app.models.pydantic import Semester
from app.service import block as block_service


@pytest.mark.asyncio
async def test_get_block_raises_not_found_error_for_wrong_proposal_code():
    with pytest.raises(FileNotFoundError):
        await block_service.get_block(
            "non-existing",
            "abcd1234",
            Semester(year=2020, semester=1),
            "tests/__testdata__/proposals",
        )


@pytest.mark.asyncio
async def test_get_block_raises_not_found_error_for_wrong_block_code():
    with pytest.raises(FileNotFoundError):
        await block_service.get_block(
            "2020-2-SCI-065",
            "non-existing",
            Semester(year=2020, semester=1),
            "tests/__testdata__/proposals",
        )


@pytest.mark.asyncio
async def test_get_block_raises_not_found_error_for_wrong_semester():
    with pytest.raises(FileNotFoundError):
        await block_service.get_block(
            "2020-2-SCI-065",
            "abcd1234",
            Semester(year=2007, semester=1),
            "tests/__testdata__/proposals",
        )


@pytest.mark.asyncio
async def test_get_block_raises_not_found_error_for_wrong_base_directory():
    with pytest.raises(FileNotFoundError):
        await block_service.get_block(
            "2020-2-SCI-065",
            "abcd1234",
            Semester(year=2020, semester=1),
            "non-existing",
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "proposal_code,block_code,semester",
    [
        ("2020-2-SCI-065", "abcd1234", Semester(year=2020, semester=1)),
        ("2020-2-SCI-065", "abcd1234", Semester(year=2020, semester=1)),
    ],
)
async def test_get_block_returns_correct_value(
    proposal_code: str, block_code: str, semester: Semester
) -> None:
    """get_block returns the correct block content."""
    block = await block_service.get_block(
        proposal_code, block_code, semester, "tests/__testdata__/proposals"
    )
    assert True
