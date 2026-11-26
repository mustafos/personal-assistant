"""Import and dependency-direction checks."""

import ast
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ASSISTANT = ROOT / "assistant"

MODULES = (
    "assistant",
    "assistant.main",
    "assistant.cli",
    "assistant.cli.commands",
    "assistant.cli.interface",
    "assistant.models",
    "assistant.models.contact",
    "assistant.models.fields",
    "assistant.models.note",
    "assistant.services",
    "assistant.services.birthday_service",
    "assistant.services.contact_service",
    "assistant.services.note_service",
    "assistant.storage",
    "assistant.storage.json_storage",
    "assistant.storage.storage",
    "assistant.utils",
    "assistant.utils.helpers",
    "assistant.utils.validators",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def _assert_allowed(path: Path, allowed_prefixes: tuple[str, ...]) -> None:
    for name in _imports(path):
        if name.startswith("assistant"):
            assert any(
                name == prefix or name.startswith(prefix + ".")
                for prefix in allowed_prefixes
            ), f"{path.relative_to(ROOT)} imports {name}"


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name: str) -> None:
    importlib.import_module(module_name)


def test_models_stay_inside_the_model_layer() -> None:
    for path in (ASSISTANT / "models").glob("*.py"):
        _assert_allowed(path, ("assistant.models",))
        assert "json" not in _imports(path)


def test_services_depend_on_models_and_storage_abstraction() -> None:
    allowed = (
        "assistant.models",
        "assistant.services",
        "assistant.storage.storage",
        "assistant.utils.validators",
    )
    service_files = (
        "contact_service.py",
        "note_service.py",
        "birthday_service.py",
    )
    for name in service_files:
        path = ASSISTANT / "services" / name
        imports = _imports(path)
        _assert_allowed(path, allowed)
        assert "json" not in imports
        assert "assistant.storage.json_storage" not in imports
        assert "assistant.cli" not in imports


def test_utils_do_not_depend_on_application_layers() -> None:
    for path in (ASSISTANT / "utils").glob("*.py"):
        assert not any(name.startswith("assistant") for name in _imports(path))


def test_cli_does_not_import_the_json_backend() -> None:
    for name in ("commands.py", "interface.py"):
        imports = _imports(ASSISTANT / "cli" / name)
        assert "json" not in imports
        assert "assistant.storage.json_storage" not in imports


def test_storage_abstraction_is_not_tied_to_json() -> None:
    imports = _imports(ASSISTANT / "storage" / "storage.py")
    assert "json" not in imports
    assert not any(name.startswith("assistant") for name in imports)
