# Development workflow

`develop` and `main` currently point at the same architecture commit. Feature
work starts from `develop` and returns there by pull request. `main` is updated
from `develop` only when a milestone is integrated.

```text
feature/<area>  -->  pull request  -->  develop  -->  main
```

## Day to day

```bash
git switch develop
git pull origin develop
git switch -c feature/contacts
```

Commit with a Conventional Commits subject, for example
`feat: store a new contact by id`. Push the feature branch and open a pull
request whose base is `develop`.

One other developer reviews the pull request. CI must pass:

```bash
pytest
ruff check .
ruff format --check .
```

Squash-merge. Delete the feature branch after it is merged. Update local
`develop` before starting the next task.

## What not to do

- Do not commit on `main` or `develop`.
- Do not force-push `main` or `develop`.
- Do not open a pull request against `main` for feature work.
- Do not implement another issue's module in your branch.

## Order

Validators and storage reliability (#4) and contact CRUD (#2) can start
together. Note CRUD (#3) can start with them because it uses a different
service file. Birthday queries are part of #2 and need `list_contacts()`.
Tag work (#6) starts after note CRUD is on `develop`. The CLI (#5) connects
commands after the service methods it calls exist.

Ownership and branch names are in [../CONTRIBUTING.md](../CONTRIBUTING.md).
Issue boundaries are in [issue-scope.md](issue-scope.md).
