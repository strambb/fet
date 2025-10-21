import pytest


def 


def test_can_get_user_role_from_repo(FakeUserRepository):
    assert FakeUserRepository.has_role("1", "a") == 