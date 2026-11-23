"""Command-line interface."""

from assistant.cli.commands import (
    Command,
    CommandHandler,
    CommandRegistry,
    build_registry,
)
from assistant.cli.interface import CLI

__all__ = [
    "CLI",
    "Command",
    "CommandHandler",
    "CommandRegistry",
    "build_registry",
]
