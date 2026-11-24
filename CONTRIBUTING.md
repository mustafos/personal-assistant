# Contributing

Work branches off `develop`. `main` receives only integrated, checked code.
Do not push directly to `develop` or `main`.

## Branch names

Start from an up-to-date `develop`:

```bash
git switch develop
git pull origin develop
git switch -c feature/<area>
```

Use one branch per issue:

| Branch | Issue |
| --- | --- |
| `feature/contacts` | #2 Contacts CRUD and birthday queries |
| `feature/notes` | #3 Notes CRUD |
| `feature/storage-validation` | #4 JSON storage reliability and validators |
| `feature/cli` | #5 CLI and integration |
| `feature/note-tags` | #6 Bonus tags, filtering, and sorting |

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add contact search by phone number
fix: reject a negative birthday window
test: cover loading a missing contacts file
docs: describe the contact edit prompts
refactor: share contact record loading
```

The subject is imperative, lowercase, and has no trailing period.

## Pull requests

1. Open the pull request against `develop`.
2. Describe what changed and how you tested it.
3. Ask one teammate to review.
4. Do not merge your own pull request.
5. Squash-merge when the review and CI checks are green.

`develop` is merged into `main` only by the integrator, after the milestone
works from the CLI.

## Checks

From the project root, with the dev tools installed:

```bash
pytest
ruff check .
ruff format --check .
```

Format the files you touched with `ruff format .` before pushing. CI runs the
same three commands on pull requests to `develop` and `main`.

## Stay out of each other's files

| Owner | May edit | Leave for someone else |
| --- | --- | --- |
| #2 | `contact_service.py`, `birthday_service.py` | `note_service.py`, `validators.py`, `cli/` |
| #3 | CRUD methods in `note_service.py` | Tag methods, `birthday_service.py`, `cli/` |
| #4 | `json_storage.py`, `validators.py`, `helpers.py` | Service CRUD, `cli/` |
| #5 | `assistant/cli/` | Service implementations |
| #6 | Tag methods in `note_service.py`, after #3 has merged | Contact and birthday code |

`assistant/main.py`, `assistant/models/contact.py`, and `assistant/models/note.py`
are shared. Change them only when a service signature cannot be implemented
as it stands, and say so in the pull request.

Add new tests under `tests/`. Do not rewrite another person's tests to make
yours pass.

## More detail

- [docs/onboarding.md](docs/onboarding.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/development-workflow.md](docs/development-workflow.md)
- [docs/cli-contracts.md](docs/cli-contracts.md)
- [docs/issue-scope.md](docs/issue-scope.md)
