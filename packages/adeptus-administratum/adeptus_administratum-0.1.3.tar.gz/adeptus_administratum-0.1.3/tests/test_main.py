"""Example test module."""

import pytest

from tests.typings import Runner


@pytest.mark.parametrize(
    "name",
    [
        "Thelma",
        "Louise",
    ],
)
def test_casual_goodbye(runner: Runner, name: str) -> None:
    """Test goodbye command casual properties."""
    result = runner(["goodbye", "--no-formal", name])
    assert "Bye" in result.output
    assert name in result.output


@pytest.mark.parametrize(
    "name",
    [
        "Thelma",
        "Louise",
    ],
)
def test_default_goodbye(runner: Runner, name: str) -> None:
    """Test goodbye command default properties."""
    result = runner(["goodbye", "--no-formal", name])
    assert "Bye" in result.output
    assert name in result.output


@pytest.mark.parametrize(
    "name",
    [
        "Thelma",
        "Louise",
    ],
)
def test_formal_goodbye(runner: Runner, name: str) -> None:
    """Test goodbye command formal properties."""
    result = runner(["goodbye", "--formal", name])
    assert "Goodbye" in result.output
    assert name in result.output


@pytest.mark.parametrize(
    "name",
    [
        "Thelma",
        "Louise",
    ],
)
def test_hello(runner: Runner, name: str) -> None:
    """Test hello command properties."""
    result = runner(["hello", name])
    assert result.exit_code == 0
    assert "Hello" in result.output
    assert name in result.output
