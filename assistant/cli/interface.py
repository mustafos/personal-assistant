"""Interactive command-line interface."""

from collections.abc import Callable

from assistant.cli.commands import Command, CommandRegistry
from assistant.storage.storage import StorageError

_BUILTIN_HELP: dict[str, tuple[str, str]] = {
    "help": ("Show available commands", "help [command]"),
    "exit": ("Exit the application", "exit"),
    "quit": ("Exit the application", "quit"),
}


class CLI:
    """Read commands from input and print service results.

    ``help``, ``exit``, and ``quit`` are handled here. Every other command
    comes from the injected :class:`CommandRegistry`.
    """

    def __init__(
        self,
        commands: CommandRegistry,
        *,
        input_func: Callable[[str], str] | None = None,
        output_func: Callable[[str], None] | None = None,
    ) -> None:
        """Prepare the interaction loop.

        Args:
            commands: Commands this session can run.
            input_func: Reads one line. Defaults to :func:`input`.
            output_func: Writes one message. Defaults to :func:`print`.
        """
        self._commands = commands
        self._input = input if input_func is None else input_func
        self._output = print if output_func is None else output_func

    def run(self) -> None:
        """Show the welcome text and read commands until the user exits."""
        self._print_banner()
        while True:
            try:
                line = self._input("> ")
            except (EOFError, StopIteration):
                self._output("")
                self._output("Goodbye.")
                return
            except KeyboardInterrupt:
                self._output("\nGoodbye.")
                return
            if not line.strip():
                continue
            if self._dispatch(line):
                return

    def _print_banner(self) -> None:
        self._output("Personal Assistant")
        self._output("Manage contacts, notes, and birthday reminders.")
        self._output("")
        self._output(self._command_catalog())
        self._output("")
        self._output("Type 'help' to show commands again, or 'exit' to quit.")

    def _command_catalog(self) -> str:
        lines = ["Commands:"]
        for command in self._commands.list_commands():
            lines.append(f"  {command.name:<18} {command.description}")
        lines.append(f"  {'help':<18} Show available commands")
        lines.append(f"  {'exit':<18} Exit the application (alias: quit)")
        return "\n".join(lines)

    def _dispatch(self, line: str) -> bool:
        """Handle one line.

        Returns:
            True when the session should end.
        """
        parts = line.strip().split()
        name = parts[0].casefold()
        args = parts[1:]
        if name in {"exit", "quit"}:
            self._output("Goodbye.")
            return True
        if name == "help":
            self._show_help(args)
            return False
        command = self._commands.get(name)
        if command is None:
            self._output(
                f"Unknown command: '{parts[0]}'. Type 'help' for available commands."
            )
            return False
        self._run_command(command, args)
        return False

    def _show_help(self, args: list[str]) -> None:
        if not args:
            self._output(self._command_catalog())
            return
        if len(args) != 1:
            self._output("Usage: help [command]")
            return
        name = args[0].casefold()
        command = self._commands.get(name)
        if command is not None:
            self._output(f"{command.name}: {command.description}")
            self._output(f"Usage: {command.usage}")
            return
        builtin = _BUILTIN_HELP.get(name)
        if builtin is not None:
            description, usage = builtin
            self._output(f"{name}: {description}")
            self._output(f"Usage: {usage}")
            return
        self._output(
            f"Unknown command: '{args[0]}'. Type 'help' for available commands."
        )

    def _run_command(self, command: Command, args: list[str]) -> None:
        try:
            result = command.handler(args)
        except NotImplementedError:
            self._output("This command is not implemented yet.")
        except LookupError as exc:
            self._output(str(exc) or "The requested item was not found.")
        except ValueError as exc:
            self._output(str(exc) or "Invalid value.")
        except StorageError as exc:
            self._output(f"Storage error: {exc}")
        else:
            if result:
                self._output(result)


__all__ = ["CLI"]
