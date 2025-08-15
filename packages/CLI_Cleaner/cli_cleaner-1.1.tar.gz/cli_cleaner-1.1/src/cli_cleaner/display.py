from rich.console import Console
from rich.markup import escape
from rich.theme import Theme
from pathlib import Path

class CleanerConsole:
    def __init__(self, delete_mode: bool) -> None:
        theme = Theme(
            {
                "dry": "yellow",
                "delete": "bold red",
                "path": "dim",
                "ok": "green",
                "err": "bold red",
            }
        )
        self.console = Console(theme=theme)
        self.delete_mode = delete_mode

    def show_header(self, root: Path) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        text = "DELETING" if self.delete_mode else "DRY RUN"
        style = "delete" if self.delete_mode else "dry"
        self.console.rule(f"{icon} [{style}]{text} in [bold]{escape(root.as_posix())}[/bold][/]")


    def show_action(self, path: Path) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        verb = "Deleting" if self.delete_mode else "Would delete"
        self.console.print(f"{icon} [{'delete' if self.delete_mode else 'dry'}]{verb}[/]: [path]{escape(path.as_posix())}[/]")


    def show_result(self, ok: bool) -> None:
        self.console.print(":white_check_mark: [ok]done[/]" if ok else ":x: [err]failed[/]")


    def show_footer(self, deleted: int, failed: int) -> None:
        icon = ":wastebasket:" if self.delete_mode else ":eyes:"
        text = (
            f"{deleted} files successfully deleted; {failed} could not be deleted"
            if self.delete_mode
            else f"{deleted} files will be deleted with --delete option"
        )
        style = "delete" if self.delete_mode else "dry"
        self.console.rule(f"{icon} [{style}]{text}[/]")