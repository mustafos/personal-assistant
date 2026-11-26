"""Interactive command-line interface."""

import itertools
import shlex
import shutil
import textwrap
from collections.abc import Callable

from colorama import Fore, Style, init

from assistant.cli.commands import Command, CommandRegistry
from assistant.storage.storage import StorageError

_RAINBOW_COLORS = (
    Fore.RED,
    Fore.LIGHTRED_EX,
    Fore.YELLOW,
    Fore.GREEN,
    Fore.CYAN,
    Fore.BLUE,
    Fore.MAGENTA,
)

_BUILTIN_HELP: dict[str, tuple[str, str]] = {
    "help": ("Show available commands", "help [command]"),
    "exit": ("Exit the application", "exit"),
    "quit": ("Exit the application", "quit"),
}


def _rainbow_text(text: str) -> str:
    colors = itertools.cycle(_RAINBOW_COLORS)
    parts: list[str] = []
    for char in text:
        if char.isspace():
            parts.append(char)
        else:
            parts.append(f"{next(colors)}{char}")
    return "".join(parts) + Style.RESET_ALL


def _rainbow_lines(text: str) -> str:
    colors = itertools.cycle(_RAINBOW_COLORS)
    styled_lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            styled_lines.append(line)
        else:
            styled_lines.append(f"{next(colors)}{line}{Style.RESET_ALL}")
    return "\n".join(styled_lines)


def _colorize_row(plain_row: str, *, rainbow: bool = False, color: str = "") -> str:
    """Apply ANSI color after fixed-width alignment so padding stays exact."""
    if rainbow:
        return _rainbow_text(plain_row)
    if color:
        return f"{color}{plain_row}{Style.RESET_ALL}"
    return plain_row


def _resolve_page_width(*, preferred: int = 38, min_width: int = 26, max_width: int = 42) -> int:
    """Fit two pages + spine safely inside the current terminal width without wrapping."""
    term_cols = shutil.get_terminal_size(fallback=(80, 24)).columns
    available_per_page = max(12, (term_cols - 2) // 2)
    return max(min_width, min(preferred, max_width, available_per_page))


def _render_book_spread(
    left_plain_rows: list[tuple[str, bool, str]],
    right_plain_rows: list[tuple[str, bool, str]],
    *,
    page_width: int = 36,
    left_page_num: int = 1,
    right_page_num: int = 2,
) -> str:
    """Render a two-page book spread with a single center spine."""
    inner = max(12, page_width - 2)
    total_rows = max(len(left_plain_rows), len(right_plain_rows))

    padded_left = list(left_plain_rows) + [("", False, "")] * (
        total_rows - len(left_plain_rows)
    )
    padded_right = list(right_plain_rows) + [("", False, "")] * (
        total_rows - len(right_plain_rows)
    )

 # Each page with side walls `|` has a width of `inner + 2`, with 1 space between them:
 # Left wall `|` -> index 0
 # Right wall of the left page `|` -> index inner + 1
 # Left wall of the right page `|` -> index inner + 3
 # Right wall of the right page `|` -> index 2 * inner + 4
    top = f" {'_' * inner}   {'_' * inner}"
    arch = f"/{' ' * inner}\\ /{' ' * inner}\\"
    lines: list[str] = [top, arch]

    for (l_text, l_rain, l_col), (r_text, r_rain, r_col) in zip(
        padded_left, padded_right
    ):
        l_aligned = f"{l_text[:inner]:<{inner}}"
        r_aligned = f"{r_text[:inner]:<{inner}}"
        l_styled = _colorize_row(l_aligned, rainbow=l_rain, color=l_col)
        r_styled = _colorize_row(r_aligned, rainbow=r_rain, color=r_col)
        lines.append(f"|{l_styled}| |{r_styled}|")

    spacer = f"|{' ' * inner}| |{' ' * inner}|"
    lines.append(spacer)

    left_footer = f"{f'Page {left_page_num}':^{inner}}"
    right_footer = f"{f'Page {right_page_num}':^{inner}}"
    lines.append(f"|{left_footer}| |{right_footer}|")

    lines.append(f"\\{'_' * inner}/_\\{'_' * inner}/")


    return "\n".join(lines)


def _format_command_entry(
    name: str,
    description: str,
    inner_width: int,
    *,
    name_col_width: int = 16,
    gap: int = 2,
) -> list[str]:
    """Format a command and description with a clean column scale and hanging wrap."""
    desc_start = 1 + name_col_width + gap
    if desc_start >= inner_width - 4:
        rows = [f" {name[: inner_width - 2]}"]
        wrapped = textwrap.wrap(description, width=max(8, inner_width - 4)) or [""]
        for part in wrapped:
            rows.append(f"   {part}")
        return rows

    desc_width = max(8, inner_width - desc_start - 1)
    wrapped = textwrap.wrap(description, width=desc_width) or [""]

    if len(name) <= name_col_width:
        first_line = f" {name:<{name_col_width}}{' ' * gap}{wrapped[0]}"
        rows = [first_line]
        cont_indent = " " * desc_start
        for part in wrapped[1:]:
            rows.append(f"{cont_indent}{part}")
        return rows

    rows = [f" {name[: inner_width - 2]}"]
    cont_indent = " " * desc_start
    for part in wrapped:
        rows.append(f"{cont_indent}{part}")
    return rows


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
        init(autoreset=True)
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
        self._output(_rainbow_text("Personal Assistant"))
        self._output("Manage contacts, notes, and birthday reminders.")
        self._output("")
        self._output(self._render_book_catalog())
        self._output("")
        self._output("Type 'help' to show commands again, or 'exit' to quit.")

    def _command_catalog(self) -> str:
        lines = ["Commands:"]
        for command in self._commands.list_commands():
            lines.append(f"  {command.name:<18} {command.description}")
        lines.append(f"  {'help':<18} Show available commands")
        lines.append(f"  {'exit':<18} Exit the application (alias: quit)")
        return "\n".join(lines)

    def _render_book_catalog(self) -> str:
        """Render commands on the left page and assistant notes on the right page."""
        page_width = _resolve_page_width(preferred=38, min_width=26, max_width=40)
        inner = page_width - 2
        commands = self._commands.list_commands()
        cmd_count = len(commands) + 2  

        all_names = [cmd.name for cmd in commands] + ["help", "exit / quit"]
        longest_name = max((len(n) for n in all_names), default=12)
        name_col_width = min(max(longest_name + 1, 14), max(10, inner // 2 - 2))

        left_rows: list[tuple[str, bool, str]] = [
            (" COMMANDS", True, ""),
            (f" {'-' * (inner - 2)}", False, Fore.LIGHTBLACK_EX),
        ]
        for command in commands:
            for row_text in _format_command_entry(
                command.name,
                command.description,
                inner,
                name_col_width=name_col_width,
                gap=2,
            ):
                left_rows.append((row_text, True, ""))

        for row_text in _format_command_entry(
            "help",
            "Show available commands",
            inner,
            name_col_width=name_col_width,
            gap=2,
        ):
            left_rows.append((row_text, True, ""))
        for row_text in _format_command_entry(
            "exit / quit",
            "Exit the application",
            inner,
            name_col_width=name_col_width,
            gap=2,
        ):
            left_rows.append((row_text, True, ""))

        right_rows: list[tuple[str, bool, str]] = [
            (" ASSISTANT NOTES", False, Fore.CYAN),
            (f" {'-' * (inner - 2)}", False, Fore.LIGHTBLACK_EX),
        ]
        note_lines = [
            ("Contacts, notes & birthdays", Fore.WHITE),
            (f"Commands loaded: {cmd_count}", Fore.GREEN),
            ("Quotes supported via shlex", Fore.YELLOW),
            ("", ""),
            ("Quick tips:", Fore.MAGENTA),
            ("- 'help <cmd>' for usage", Fore.WHITE),
            ("- 'exit' or Ctrl+C to quit", Fore.WHITE),
        ]
        for text, col in note_lines:
            if not text:
                right_rows.append(("", False, ""))
                continue
            wrapped = textwrap.wrap(text, width=max(10, inner - 2)) or [""]
            for part in wrapped:
                right_rows.append((f" {part}", False, col))

        return _render_book_spread(
            left_rows,
            right_rows,
            page_width=page_width,
            left_page_num=1,
            right_page_num=2,
        )

    def _parse_line(self, line: str) -> list[str] | None:
        """Split a command line using shlex while keeping quoted strings intact."""
        try:
            return shlex.split(line.strip())
        except ValueError as exc:
            self._output(f"Invalid command syntax: {exc}. Check matching quotes.")
            return None

    def _dispatch(self, line: str) -> bool:
        """Handle one line.

        Returns:
            True when the session should end.
        """
        parts = self._parse_line(line)
        if parts is None:
            return False
        if not parts:
            return False
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
            self._output(self._render_book_catalog())
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
