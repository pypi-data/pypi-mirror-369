# Adeptus Administratum

CLI game in 40k setting.

## Testing

### Installation

```bash
pip install -e .[ALL]
pre-commit install
```

Run pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

This will run the following hooks:

- `ruff`

### Running tests

```bash
pytest
```

# Generating distribution archives

```bash
pip install --upgrade build
python -m build
```