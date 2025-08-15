# Who is concerned by this file

[//]: # (For a guide to create CONTRIBUTING.md, see http://mozillascience.github.io/working-open-workshop/contributing/)

This file is for:

- Project owners - creators and maintainers of the project
- Project contributors - users of the project who want to know items they're welcome to tackle, and
  tact they need in navigating the project/respecting those involved with the project
- Project consumers - users who want to build off the project to create their own project

## Testing

### Installation

```bash
pip install --upgrade pip
pip install -e .[ALL]
pre-commit install
```

Run pre-commit hooks on all files:

```bash
pre-commit autoupdate
pre-commit run --all-files
```

This will run the following hooks:

- `black`
- `flake8`
- `isort`
- `mypy`
- `ruff`
- `pymarkdown`

### Running tests

```bash
pytest
```

## Generating distribution archives

```bash
pip install --upgrade pip
pip install --upgrade build
python -m build
```

## Pypi share

```bash
pip install --upgrade pip
pip install --upgrade twine
python -m twine upload --repository pypi dist/*
```

You will be prompted for a username and password. For the username, use __token__. For the password, use the token value, including the pypi- prefix.
