# Onboarding

## Prerequisites

- Python 3.12 or newer.
- Git.
- A GitHub account with access to `mustafos/personal-assistant`.

## Clone and install

```bash
git clone git@github.com:mustafos/personal-assistant.git
cd personal-assistant
git switch develop
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows, activate with `.venv\Scripts\activate`.

## Run the application

```bash
personal-assistant
```

Or, without relying on the console script:

```bash
python -m assistant.main
```

Type `help`, then `exit`. Data commands answer that they are not implemented
yet. Nothing is written under `data/` until a service saves.

## Test and lint

```bash
pytest
ruff check .
ruff format --check .
```

## Feature branch and pull request

```bash
git switch develop
git pull origin develop
git switch -c feature/contacts
```

Commit, push `feature/contacts`, and open a pull request whose base is
`develop`. The pull request title uses the same Conventional Commit style as
the commits. CI runs the three commands above.

Branch names, file ownership, and review rules are in
[../CONTRIBUTING.md](../CONTRIBUTING.md).
