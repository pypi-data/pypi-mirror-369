from cli_cleaner import core
from pathlib import Path
from typing import Annotated

import typer
from cli_cleaner.display import CleanerConsole

import unicodedata as ud


APP_NAME = "cleaner"

app = typer.Typer(help="A tool for quickly cleaning files in the project directory", add_completion=False)

def normalize(s: str) -> str:
    return ud.normalize("NFC", s)

@app.command()
def main(
    dirs: Annotated[
        list[str],
        typer.Option("--dirs", "-d", help="Folder names to delete")
    ] = list(),
    files: Annotated[
        list[str],
        typer.Option("--files", "-f", help="File names to delete")
    ] = list(),
    globs: Annotated[
        list[str],
        typer.Option("--globs", "-g", help="Patterns to delete")
    ] = list(),
    ignored_dirs: Annotated[
        list[str],
        typer.Option("--ignore-dirs", "-id", help="Folders to ignore")
    ] = list(),
    ignored_files: Annotated[
        list[str],
        typer.Option("--ignore-files", "-if", help="Files to ignore")
    ] = list(),
    root: Annotated[
        Path | None,
        typer.Option("--root", "-r", help="Root dir where will be deletion", show_default="current working directory"),
    ] = None,
    delete_mode: Annotated[
        bool,
        typer.Option("--delete", help="Actually delete files instead of dry run")
    ] = False
) -> None:
    if not (dirs or files or globs):
        raise typer.BadParameter("You must provide at least one of --dirs, --files, or --globs")

    dirs = list(map(normalize, dirs))
    files = list(map(normalize, files))
    globs = list(map(normalize, globs))
    ignored_dirs = list(map(normalize, ignored_dirs))
    ignored_files = list(map(normalize, ignored_files))
    root = root or Path.cwd()
    console = CleanerConsole(delete_mode)

    console.show_header(root)

    filepaths = core.find_targets(root, dirs, files, globs, ignored_dirs, ignored_files)
    deleted, failed = core.process_targets(console, filepaths, delete_mode)

    console.show_footer(deleted, failed)
