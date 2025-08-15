# 🧹 cleaner

**cleaner** is a powerful and safe CLI tool for cleaning up unwanted files and directories in your project, with support for dry-run mode, glob patterns, and rich terminal output.

## ✨ Features

- Dry-run mode (`--delete` optional)
- Match by:
  - folder name (`--dirs`)
  - file name (`--files`)
  - glob patterns (`--globs`)
- Rich output with icons and colors
- Ignore specific files and folders
- Root directory control (`--root`)
- Works well with `pipx` or `uv tool install`

---

## 🚀 Installation

Install via [`pipx`](https://pypa.github.io/pipx/):

```bash
pipx install git+https://github.com/DasKaroWow/cli_cleaner.git
```

Or with [`uv`](https://github.com/astral-sh/uv):

```bash
uv tool install --from git+https://github.com/DasKaroWow/cli_cleaner
```

---

## 🛠 Usage

```bash
cleaner --dirs __pycache__ -g "*.pyc" -g "build/**" --delete
```

🔎 Dry-run (default):
```bash
cleaner --files project_dump.txt --globs "*.log"
```

🗑️ Real delete:
```bash
cleaner --dirs dist --delete
```

📁 Specify root directory:
```bash
cleaner --dirs .venv --root ./backend --delete
```

🙈 Ignore certain files/folders:
```bash
cleaner --dirs __pycache__ --ignore-dirs migrations --ignore-files keep.py
```

---

## 💻 Example Output

```
👀 DRY RUN in /home/user/project
👀 Would delete: src/__pycache__/utils.cpython-310.pyc
👀 Would delete: build/output.txt
────────────────────────────────────────────
👀 2 files will be deleted with --delete option
```

Or:

```
🗑️ DELETING in /home/user/project
🗑️ Deleting: dist/
✅ done
────────────────────────────────────────────
🗑️ 1 files successfully deleted; 0 could not be deleted
```

---

## 📦 Project layout

```
src/
└── cleaner/
    ├── cli.py
    ├── __init__.py
    └── __main__.py
```

---

## ✅ Requirements

- Python 3.10+
- [`typer`](https://typer.tiangolo.com/)
- [`rich`](https://rich.readthedocs.io/)

---

## 📄 License

MIT License
