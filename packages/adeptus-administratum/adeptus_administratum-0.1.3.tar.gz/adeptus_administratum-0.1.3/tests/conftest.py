"""Holds main fixture for the entire tests package."""

import functools

import click
import pytest
import typer.testing

import adeptus_administratum


@pytest.fixture(scope="session")
def runner() -> functools.partial[click.testing.Result]:
    """Configure a pre-configured CLI runner with the main app."""
    runner = typer.testing.CliRunner()
    return functools.partial(runner.invoke, adeptus_administratum.app)
