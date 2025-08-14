## hello-cli

A tiny example CLI built with Python’s `argparse`. It exposes a `hello` command that greets one or more names with a couple of optional flags.

### Install (development)

```bash
poetry install
```

### Usage

Run via Poetry:

```bash
poetry run hello Alice Bob
poetry run hello -s -f Alice
```

Options:

- `-s, --shout`: Upper‑case the greeting
- `-f, --flirty`: Add a friendly compliment

### Install with pipx (optional)

```bash
pipx install .
hello --help
```

Reinstall after changes:

```bash
pipx reinstall .
```

### Project details

- Entry point: `hello` (configured in `pyproject.toml` under `[tool.poetry.scripts]`)
- Source: `src/hello/main.py`
