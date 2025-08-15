from pathlib import Path
import shutil
from cli_cleaner.display import CleanerConsole

def matches_any_glob(path: Path, patterns: list[str]) -> bool:
    return any(path.match(pattern) for pattern in patterns)

def find_targets(root: Path, dirs: list[str], files: list[str], globs: list[str], ignored_dirs: list[str], ignored_files: list[str]) -> set[Path]:
    paths_to_delete = set()

    for current_root, current_dirs, current_files in root.walk(top_down=True):
        current_path = Path(current_root)

        current_dirs[:] = [d for d in current_dirs if d not in ignored_dirs]
        for name in current_dirs:
            filepath = current_path / name
            if (dirs or globs) and (name in dirs or matches_any_glob(filepath, globs)):
                paths_to_delete.add(filepath.resolve())

        if not files and not globs: current_files.clear()
        for name in current_files:
            if name in ignored_files:
                continue

            filepath = current_path / name
            if name in files or matches_any_glob(filepath, globs):
                paths_to_delete.add(filepath.resolve())

    return paths_to_delete

def process_targets(console: CleanerConsole, filepaths: set[Path], delete_mode: bool) -> tuple[int, int]:
    deleted = 0
    failed = 0
    for filepath in filepaths:
        deleted += 1
        console.show_action(filepath)
        if not delete_mode: continue

        try:
            if filepath.is_dir():
                shutil.rmtree(filepath)
            elif filepath.is_file():
                filepath.unlink()
            console.show_result(True)
        except Exception:
            deleted -= 1
            failed += 1
            console.show_result(False)

    return deleted, failed