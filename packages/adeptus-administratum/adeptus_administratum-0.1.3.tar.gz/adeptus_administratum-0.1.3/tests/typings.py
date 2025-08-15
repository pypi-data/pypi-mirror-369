"""Holds annotations for tests package."""

import functools

import click

type Runner = functools.partial[click.testing.Result]
