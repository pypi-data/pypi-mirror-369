from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
from janito.cli.console import shared_console
import os


class HelpShellHandler(ShellCmdHandler):
    help_text = "Show this help message"

    def run(self):
        from . import COMMAND_HANDLERS
        from ._priv_check import user_has_any_privileges

        shared_console.print("[bold magenta]Available commands:[/bold magenta]")
        for cmd, handler_cls in sorted(COMMAND_HANDLERS.items()):
            help_text = getattr(handler_cls, "help_text", "")
            shared_console.print(f"[cyan]{cmd}[/cyan]: {help_text}")

        # After help, print privilege info if user has no privileges
        if not user_has_any_privileges():
            shared_console.print(
                "[yellow]Note: You currently have no privileges enabled. If you need to interact with files or the system, enable permissions using /read on, /write on, or /execute on.[/yellow]"
            )
