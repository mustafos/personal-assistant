# Issue scope

This page is the working scope for issues #2–#6. It does not replace the
GitHub issues until those descriptions are updated. Birthday behavior belongs
only to #2. Tag behavior belongs only to #6.

The architecture and these boundaries are issue #1, which is already underway.

## #2 Contacts CRUD and birthday queries

Own `assistant/services/contact_service.py` and
`assistant/services/birthday_service.py`.

In scope:

- `add_contact`, `get_contact`, `list_contacts`, `search_contacts`,
  `update_contact`, `delete_contact`.
- Persist through the injected `Storage` and `Contact.to_dict` /
  `Contact.from_dict`.
- Case-insensitive search over name, address, phones, and email, with partial
  matches, as already written in the issue.
- `upcoming_birthdays`, using `list_contacts()`. Include year wraparound.
- Tests for those methods.

Out of scope: note methods, tag methods, `validators.py`, `assistant/cli/`,
and a second birthday implementation.

Call `is_valid_phone` and `is_valid_email` before storing those fields. If #4
has not merged yet, depend on the functions that already exist and are still
`NotImplementedError`.

29 February is still undefined. Do not pick a rule silently. Record the chosen
rule in the pull request.

## #3 Notes CRUD only

Own the CRUD methods in `assistant/services/note_service.py`:

- `add_note`, `get_note`, `list_notes`, `search_notes`, `update_note`,
  `delete_note`.

Search title and content with partial, case-insensitive matches. Do not
implement `add_tag`, `remove_tag`, or `find_by_tag`. Do not add filtering or
sorting by tag. Leave those methods raising `NotImplementedError`.

Tests cover note CRUD only.

## #4 JSON storage reliability and input validators

Own `assistant/storage/json_storage.py`, `assistant/utils/validators.py`, and
`assistant/utils/helpers.py`.

In scope:

- Keep the `Storage` methods `save(records)` and `load()`.
- Make `save` leave the previous file intact when encoding or writing fails.
- Keep missing and blank files loading as `[]`, and corrupt JSON raising
  `StorageError`.
- Keep files in the project `data/` directory. `PERSONAL_ASSISTANT_DATA_DIR`
  remains the override. Do not switch the default to the user's home directory.
- Implement `is_valid_phone` and `is_valid_email`.
- Tests for the storage failure case and for the validators.

Out of scope: contact or note CRUD, birthdays, tags, and CLI prompts.

The phone and email patterns are not specified in the repository. State the
pattern you implement in the pull request.

## #5 CLI and integration

Own `assistant/cli/`. Follow [cli-contracts.md](cli-contracts.md).

In scope:

- Prompt for contact and note fields on add and update.
- Wire the registered commands to the service methods.
- Keep unknown commands and bad arguments from ending the process.
- Integration tests that run a command, restart is not required inside one
  test, but a second `JSONStorage.load()` must see saved records.
- Usage examples in the README after the commands work.

Out of scope: reimplementing services, validators, or tag filtering. Tag
commands may call the #6 methods after that work has merged. Until then they
stay "not implemented yet."

## #6 Bonus: note tags, filtering, and sorting

Own only `add_tag`, `remove_tag`, and `find_by_tag`, plus whatever private
helpers those three need. Start after #3 is on `develop`.

In scope, from the existing bonus issue:

- Several tags on one note.
- No duplicate tag on the same note. Comparison is case-insensitive.
- Search or filter by tag.
- Tags survive `to_dict` / `from_dict` and a later `load()`.
- Sorting by tag.
- Tests for those cases.

Out of scope: note CRUD, contacts, and birthdays. Do not rewrite
`add_note` or `search_notes` except to stop them from breaking tags.

There is no separate command name yet for "filter" versus `notes-by-tag`, or
for sort. Add the command in `commands.py` only together with the CLI owner,
or describe the command in the #6 pull request before editing `assistant/cli/`.
