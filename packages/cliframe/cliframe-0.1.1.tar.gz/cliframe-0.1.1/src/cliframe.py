import os
import re
import sys
import importlib
import importlib.util
import inspect
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle, print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from pathlib import Path
from typing import List, Tuple

# Default CLI root is the directory of this file
CLI_ROOT = Path(__file__).parent


# Utility functions to eliminate duplicate code
def load_module_from_path(file_path: Path, module_name: str = "cli_module"):
    """Load a Python module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception:
        pass
    return None


def get_handler_class(module):
    """Extract handler class from a module."""
    if module:
        # First try the standard names
        handler = getattr(module, "StartCommand", None) or getattr(module, "Command", None)
        if handler:
            return handler

        # 2nd option: If not found, look for any class ending with 'Command'
        for name in dir(module):
            if name.endswith('Command'):
                attr = getattr(module, name)
                if isinstance(attr, type):
                    return attr

        # Third option: return the first defined class in the module
        for name in dir(module):
            attr = getattr(module, name)
            if isinstance(attr, type):
                return attr
    return None


def get_handler_doc(handler, module=None) -> str:
    """Extract documentation from a handler class or module-level help() function."""
    # Prefer module-level help() if present
    if module and hasattr(module, 'help') and callable(getattr(module, 'help')):
        try:
            return module.help()
        except Exception:
            pass
    if not handler:
        return "no docs available"
    doc = getattr(handler, "__docs__", None) or getattr(handler, "__doc__", "")
    if doc is None:
        return "no docs available"
    return doc.strip()


def parse_color_markers(line):
    """Parse color markers in text and convert to prompt_toolkit format."""
    fragments = []
    pos = 0
    # Regex to match [style]...[/style] for any style name
    pattern = re.compile(r'\[([a-zA-Z0-9 :;#.,\-]+)\](.*?)\[/\1\]', re.DOTALL)
    for match in pattern.finditer(line):
        start, end = match.span()
        style_name = match.group(1)
        text = match.group(2)
        if start > pos:
            fragments.append(('class:output', line[pos:start]))
        fragments.append((f'class:{style_name.strip()}', text))
        pos = end
    if pos < len(line):
        fragments.append(('class:output', line[pos:]))
    return fragments


class RecursiveCompleter(Completer):
    def __init__(self, cli_service):
        self.cli_service = cli_service

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        parts = text.strip().split()
        if text.endswith(' ') or not parts:
            current_token = None
            base_parts = parts
        else:
            current_token = parts[-1]
            base_parts = parts[:-1]
        completions, _ = self._recursive_completions(base_parts)
        # Remove trailing spaces for menu display
        plain_completions = [c.rstrip() for c in completions]
        # If only one match, add trailing space for shell-like completion
        matches = [c for c in plain_completions if current_token is None or c.startswith(current_token)]
        for comp in plain_completions:
            if current_token is None or comp.startswith(current_token):
                display_comp = comp
                # Add trailing space if unique match
                if len(matches) == 1:
                    display_comp = comp + ' '
                yield Completion(display_comp, start_position=-(len(current_token) if current_token else 0))

    def _recursive_completions(self, parts: List[str]) -> Tuple[List[str], Path]:
        cwd = self.cli_service.cli_root
        idx = 0
        while idx < len(parts):
            next_dir = cwd / parts[idx]
            next_file = cwd / (parts[idx] + ".py")
            if next_dir.is_dir():
                cwd = next_dir
                idx += 1
            elif next_file.exists():
                # If a module-level completions function exists, use it for argument completions
                module = load_module_from_path(next_file)
                if module and hasattr(module, 'completions') and callable(getattr(module, 'completions')):

                    # Pass remaining arguments (parts[idx+1:]) to completions
                    completions_func = module.completions
                    sig = inspect.signature(completions_func)
                    if len(sig.parameters) == 1:
                        completions = completions_func(parts[idx + 1:])
                    else:
                        completions = completions_func(None, parts[idx + 1:])
                    return (completions, cwd)
                return ([], cwd)
            else:
                break
        init_py = cwd / "__init__.py"
        if init_py.exists():
            # For filesystem-based resolution, we don't need to import modules
            # Just check if there's a handler class in the __init__.py file
            module = load_module_from_path(init_py)
            handler = get_handler_class(module)
            if handler and hasattr(handler, "get_completions"):
                completions = handler().get_completions(parts[idx:])
                return (completions, cwd)
        completions = []
        for item in os.listdir(cwd):
            if item == self.cli_service._configure_folder:
                continue
            if item.startswith("__"):
                continue
            full_item = cwd / item
            if full_item.is_dir():
                completions.append(item)
            elif full_item.suffix == ".py":
                completions.append(item[:-3])
        # At root, if _configure exists and not in config mode, add 'configure' as a special completion
        if (
            cwd == self.cli_service.cli_root and
            self.cli_service._configure_path is not None and
            self.cli_service.cli_root == self.cli_service._initial_cli_root
        ):
            completions.append("configure")

        # Always add 'exit' in config mode if not present
        if self.cli_service._configure_path is not None and "exit" not in completions:
            completions.append("exit")
        return (completions, cwd)


class CliFrame:
    def __init__(self, core=None, cli_root=None):
        self.core = core
        # Use provided cli_root or default to 'cli' directory in project root
        if cli_root:
            self.cli_root = Path(cli_root)
        else:
            # Default to 'cli' directory next to this script
            self.cli_root = (Path(__file__).parent.parent / 'cli').resolve()

        # Update the global CLI_ROOT to use the instance's cli_root
        global CLI_ROOT
        CLI_ROOT = self.cli_root
        self._motd = None
        self._motd_rich = False
        self._console = Console()
        self._prompt_text = "cli"
        self._prompt_mode_sign = ">"
        self._configure_folder = "_configure"
        # Check if _configure folder exists
        self._initial_cli_root = self.cli_root  # Store initial root for config mode logic
        self._configure_path = self.cli_root / self._configure_folder
        if not self._configure_path.exists():
            self._configure_path = None

    def prompt(self, prompt_text: str = "cli"):
        """Set the prompt text (before the mode sign)."""
        if prompt_text is not None:
            self._prompt_text = prompt_text
        return self

    def prompt_mode_sign(self, sign: str = ">"):
        """Set the prompt mode sign (e.g., '>', '#')."""
        if sign is not None:
            self._prompt_mode_sign = sign
        return self

    def motd(self, message: str, rich: bool = True):
        """Set the Message of the Day (motd) to display on CLI start."""
        self._motd = message
        self._motd_rich = rich
        return self

    def folder(self, path):
        """Set the CLI root directory for command resolution.

        Args:
            path (str): Path to the CLI root directory

        Returns:
            CliService: Returns self for method chaining
        """
        self.cli_root = Path(path).resolve()
        # Update the global CLI_ROOT to use the instance's cli_root
        global CLI_ROOT
        CLI_ROOT = self.cli_root
        return self

    def _execute_handler(self, handler_class, args, style):
        """Execute a command handler directly.

        Args:
            handler_class: The handler class to instantiate
            args: Arguments to pass to the handler's run method
            style: Style object for formatting output

        Returns:
            str: Empty string (output is printed directly)
        """
        if not handler_class:
            return f"Unknown command: {' '.join(args)}\n"

        try:
            handler = handler_class(self.core)
            # Run handler directly without stdout redirection
            handler.run(args)
        except Exception as e:
            # Print error message but don't crash the CLI
            print(f"Error executing command: {e}", file=sys.stderr)
        return ""

    def _display_text(self, text, style):
        """Display text with proper formatting.

        Args:
            text: Text to display, possibly with color markers
            style: Style object for formatting
        """
        print_formatted_text(FormattedText(parse_color_markers(text)), style=style)

    def _display_output(self, output, style):
        """Display command output with proper formatting.

        Args:
            output: Command output text
            style: Style object for formatting
        """
        if output:
            lines = output.rstrip().splitlines()
            for line in lines:
                self._display_text(line, style)
            print()

    def run(self):
        bindings = KeyBindings()

        # Display MOTD if set
        if self._motd:
            if self._motd_rich:
                self._console.print(self._motd)
            else:
                print(self._motd)
        style = Style.from_dict({
            'prompt': 'bold fg:green',
            'input': 'bold fg:white',
            'output': 'fg:#888888',
            'red': 'fg:red bold',
            'green': 'fg:green bold',
            'yellow': 'fg:yellow bold',
            'blue': 'fg:blue bold',
            'magenta': 'fg:magenta bold',
            'cyan': 'fg:cyan bold',
            # You can use any valid prompt_toolkit style string as a marker
        })

        history = InMemoryHistory()
        session = PromptSession(history=history,
                                completer=RecursiveCompleter(self),
                                complete_style=CompleteStyle.READLINE_LIKE,
                                complete_while_typing=True,
                                key_bindings=bindings,
                                style=style,
                                )

        @bindings.add('?')
        def _(event):
            buf = event.app.current_buffer
            text = buf.text
            cursor = buf.cursor_position
            if cursor == len(text):
                parts = text.strip().split()
                if parts and parts[-1] == '?':
                    # Print the prompt line as if user typed 'cli> start ?'
                    helptext = self._show_help(parts[:-1])
                    prompt_display = f"{self._prompt_text}{self._prompt_mode_sign} "
                    print_formatted_text(FormattedText([
                        ('class:prompt', prompt_display),
                        ('class:input', text)
                    ]), style=style)
                    if helptext:
                        self._display_text(helptext, style)
                    # Restore buffer to previous state with a trailing space
                    if not text[:-1].endswith(' '):
                        buf.text = text[:-1].rstrip() + ' '
                    event.prevent_insert = True
                elif text.endswith(' '):
                    helptext = self._show_help(parts)
                    prompt_display = f"{self._prompt_text}{self._prompt_mode_sign} "
                    print_formatted_text(FormattedText([
                        ('class:prompt', prompt_display),
                        ('class:input', text + '?')
                    ]), style=style)
                    if helptext:
                        self._display_text(helptext, style)
                    event.prevent_insert = True

        text = ""
        while True:
            try:
                prompt_display = f"{self._prompt_text}{self._prompt_mode_sign} "
                text = session.prompt([
                    ('class:prompt', prompt_display)
                ])
                parts = text.strip().split()
                if not parts:
                    continue

                # Handle help command
                if parts[-1] == "?":
                    helptext = self._show_help(parts[:-1])
                    if helptext:
                        self._display_text(helptext, style)
                    continue

                # Handle exit command
                if parts[0] == "exit":
                    # If in config mode, exit config mode instead of quitting CLI
                    if self.cli_root == self._configure_path:
                        self.cli_root = self._initial_cli_root
                        self.prompt_mode_sign(">")
                        self._display_text('Exited configuration mode\n', style)
                        continue
                    self._display_text('Exiting...\n', style)
                    break

                # Special handling for 'configure' command at root
                if parts[0] == "configure" and self._configure_path is not None and self.cli_root == self._initial_cli_root:
                    # Enter configuration mode: switch cli_root and prompt sign
                    self.cli_root = self._configure_path
                    self.prompt_mode_sign("(config)#")
                    self._display_text("Entered configuration mode\n", style)
                    continue

                # Handle regular commands
                handler_class, args = self._resolve_handler(parts)
                output = self._execute_handler(handler_class, args, style)
                self._display_output(output, style)

            except (EOFError, KeyboardInterrupt):
                prompt_line = f"cli> {text}"
                self._display_text(prompt_line, style)
                break

    def _resolve_path(self, parts: List[str]) -> Tuple[Path, int]:
        """Resolve a path from command parts.

        Args:
            parts (List[str]): Command parts to resolve

        Returns:
            Tuple[Path, int]: The resolved path and index of the next unprocessed part
        """
        cwd = self.cli_root
        idx = 0
        while idx < len(parts):
            next_dir = cwd / parts[idx]
            next_file = cwd / (parts[idx] + ".py")
            if next_dir.is_dir():
                cwd = next_dir
                idx += 1
            elif next_file.exists():
                cwd = next_file
                idx += 1
                if cwd.is_file():
                    break
            else:
                break
        return cwd, idx

    def _show_help(self, parts: List[str]):
        # Special case: if asking for help on 'configure', show nothing
        if parts and parts[0] == "configure":
            return ""
        # Show subcommands and their docs for the current command path
        cwd = self.cli_root
        idx = 0

        # Resolve the path for the help command
        while idx < len(parts):
            next_dir = cwd / parts[idx]
            next_file = cwd / (parts[idx] + ".py")
            if next_dir.is_dir():
                cwd = next_dir
                idx += 1
            elif next_file.exists():
                cwd = next_file
                idx += 1
                break
            else:
                break

        # If the resolved path is a file, show its help docstring instead of listing contents
        if cwd.is_file():
            # For filesystem-based resolution, directly load the Python file
            module = load_module_from_path(cwd)
            handler = get_handler_class(module)
            if handler:
                return get_handler_doc(handler, module=module)
            return "No help available."

        # List subcommands (dirs and .py files)
        entries = []
        # Hide _configure from help listing
        for entry in os.listdir(cwd):
            if entry == self._configure_folder:
                continue
            entry_path = cwd / entry
            if entry_path.is_dir() and (entry_path / "__init__.py").exists():
                # For directories with __init__.py, try to load the __init__.py file
                module = load_module_from_path(entry_path / "__init__.py")
                handler = get_handler_class(module)
                doc = get_handler_doc(handler)
                entries.append((entry, doc))
            elif entry_path.is_dir():
                # For directories without __init__.py, show them with a generic message
                entries.append((entry, ""))
            elif entry.endswith(".py") and entry != "__init__.py":
                # For .py files, try to load them directly
                module = load_module_from_path(entry_path)
                handler = get_handler_class(module)
                doc = get_handler_doc(handler)
                entries.append((entry[:-3], doc))
        # At root, if _configure exists and not in config mode, add 'configure' as a special help entry
        if cwd == self.cli_root and self._configure_path is not None and self.cli_root == self._initial_cli_root:
            entries.append(("configure", "Enter configuration mode"))
        if not entries:
            return "No subcommands available."
        else:
            lines = [f"{name} - {doc}" for name, doc in sorted(entries)]
            return "\n".join(lines)

    def _resolve_handler(self, parts: List[str]):
        """Recursively resolve the command handler class and remaining arguments.

        Args:
            parts (List[str]): Command parts to resolve

        Returns:
            Tuple: (handler_class, args) where handler_class is the resolved handler 
                   class and args are the remaining unprocessed command parts
        """
        cwd, idx = self._resolve_path(parts)
        handler_class = None

        # For directory paths, check for __init__.py
        if cwd.is_dir():
            init_py = cwd / "__init__.py"
            if init_py.exists():
                module = load_module_from_path(init_py)
                handler_class = get_handler_class(module)
        # For file paths (from _resolve_path for non-help commands)
        elif cwd.is_file() and cwd.suffix == ".py":
            module = load_module_from_path(cwd)
            handler_class = get_handler_class(module)

        args = parts[idx:]
        return handler_class, args


def main():
    """Main entry point for the CLI application."""


if __name__ == "__main__":
    main()
