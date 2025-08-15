"""Example greeting module."""

import typer

app = typer.Typer()


@app.command()
def hello(name: str) -> None:
    """Says hello to someone."""
    print(f"Hello {name}!")  # noqa: T201


@app.command()
def goodbye(
    name: str,
    formal: bool = False,  # noqa: FBT001,FBT002
) -> None:
    """Says goodbye to someone."""
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")  # noqa: T201
    else:
        print(f"Bye {name}!")  # noqa: T201
