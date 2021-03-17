"""Unit tests for pydantic models."""
import pytest

from app.models.pydantic import Semester


@pytest.mark.parametrize(
    "year,semester",
    [(-5, 1), (1900, 2), (2005, 2), (2101, 1), (34567, 2), (2021, 0), (2022, 3)],
)
def test_semester_rejects_invalid_values(year: int, semester: int) -> None:
    "The Semester raises an error for invalid argument values."
    with pytest.raises(ValueError):
        Semester(year=year, semester=semester)
