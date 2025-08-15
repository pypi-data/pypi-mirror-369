import os
import shutil
from fnmatch import fnmatch
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.theme import Theme

APP_NAME = "cleaner"

app = typer.Typer(help="A tool for quickly cleaning files in the project directory", add_completion=False)

theme = Theme(
    {
        "dry": "yellow",
        "delete": "bold red",
        "path": "dim",
        "ok": "green",
        "err": "bold red",
    }
)
console = Console(theme=theme)


def show_header(root: str, delete_mode: bool) -> None:
    icon = ":wastebasket:" if delete_mode else ":eyes:"
    text = "DELETING" if delete_mode else "DRY RUN"
    style = "delete" if delete_mode else "dry"
    console.rule(f"{icon} [{style}]{text} in [bold]{root}[/bold][/]")


def show_action(path: Path, delete_mode: bool) -> None:
    icon = ":wastebasket:" if delete_mode else ":eyes:"
    verb = "Deleting" if delete_mode else "Would delete"
    console.print(f"{icon} [{'delete' if delete_mode else 'dry'}]{verb}[/]: [path]{path}[/]")


def show_result(ok: bool) -> None:
    console.print(":white_check_mark: [ok]done[/]" if ok else ":x: [err]failed[/]")


def show_footer(deleted: int, failed: int, delete_mode: bool) -> None:
    icon = ":wastebasket:" if delete_mode else ":eyes:"
    text = (
        f"{deleted} files successfully deleted; {failed} could not be deleted"
        if delete_mode
        else f"{deleted} files will be deleted with --delete option"
    )
    style = "delete" if delete_mode else "dry"
    console.rule(f"{icon} [{style}]{text}[/]")


def matches_any_glob(path: Path, patterns: list[str]) -> bool:
    str_path = str(path.as_posix())
    return any(fnmatch(str_path, pattern) for pattern in patterns)


@app.command()
def main(
    dirs: Annotated[list[str], typer.Option("--dirs", "-d", help="Folder names to delete")] = [],  # noqa: B006
    files: Annotated[list[str], typer.Option("--files", "-f", help="File names to delete")] = [],  # noqa: B006
    globs: Annotated[list[str], typer.Option("--globs", "-g", help="Patterns to delete")] = [],  # noqa: B006
    ignored_dirs: Annotated[list[str], typer.Option("--ignore-dirs", "-id", help="Folders to ignore")] = [],  # noqa: B006
    ignored_files: Annotated[list[str], typer.Option("--ignore-files", "-if", help="Files to ignore")] = [],  # noqa: B006
    root: Annotated[
        Path | None,
        typer.Option("--root", "-r", help="Root dir where will be deletion", show_default="current working directory"),
    ] = None,
    delete_mode: Annotated[bool, typer.Option("--delete", help="Actually delete files instead of dry run")] = False,
) -> None:
    root = root or Path.cwd()
    if not (dirs or files or globs):
        raise typer.BadParameter("You must provide at least one of --dirs, --files, or --globs")

    show_header(str(root), delete_mode)
    deleted = 0
    failed = 0

    for current_root, current_dirs, current_files in os.walk(top=root):
        current_path = Path(current_root)

        for name in current_files:
            if name in ignored_files:
                continue
            filepath = current_path / name
            if name in files or matches_any_glob(filepath, globs):
                show_action(filepath, delete_mode)
                deleted += 1
                if delete_mode:
                    try:
                        filepath.unlink()
                        show_result(True)
                    except Exception:
                        deleted -= 1
                        failed += 1
                        show_result(False)

        for name in current_dirs:
            if name in ignored_dirs:
                current_dirs.remove(name)
                continue
            folderpath = current_path / name
            if name in dirs or matches_any_glob(folderpath, globs):
                show_action(folderpath, delete_mode)
                deleted += 1
                if delete_mode:
                    try:
                        shutil.rmtree(folderpath)
                        show_result(True)
                    except Exception:
                        deleted -= 1
                        failed += 1
                        show_result(False)

    show_footer(deleted, failed, delete_mode)
