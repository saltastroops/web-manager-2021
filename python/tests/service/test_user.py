from tests.markers import nodatabase


@nodatabase
def test_get_user_raises_an_exception_for_unknown_user() -> None:
    assert False
