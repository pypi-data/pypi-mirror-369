"""Example test file to demonstrate pytest usage."""

import pytest


def test_example() -> None:
    """A simple example test that will always pass."""
    assert True


def test_example_with_fixture(example_fixture: str) -> None:
    """Example test using a fixture."""
    assert example_fixture == "example_value"


@pytest.fixture()
def example_fixture() -> str:
    """Example fixture that returns a string."""
    return "example_value"
