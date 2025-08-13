Hier ist ein Vorschlag für eine prägnante, aber informative `README.md` für dein Projekt:

````markdown
# bookup-fuse

**Mount Bookup `.bdb` (SQLite) databases as a virtual FUSE filesystem** — browse and edit your Bookup pages and sections directly as Markdown files.

## Features

- Mount a Bookup `.bdb` file into a directory
- Exposes two top-level folders:
  - `Pages/` — all pages without section nesting
  - `Sections/` — hierarchical structure of sections containing pages
- Read and edit Markdown content directly via any text editor
- Changes are written back to the `.bdb` database in real time
- Works with standard FUSE mounts on Linux

## Requirements

- **Python** ≥ 3.9
- **libfuse** installed on your system
  Fedora / RHEL:
  ```bash
  sudo dnf install fuse fuse3 fuse3-libs
````

Debian / Ubuntu:

```bash
sudo apt install fuse
```

* Python package **fusepy** (installed automatically with this package)

## Installation

```bash
pip install bookup-fuse
```

Or from source:

```bash
git clone https://github.com/beimgraben/bookup-fuse.git
cd bookup-fuse
pip install .
```

## Usage

```bash
bookup-fuse <bookup_bdb_file> <mount_point>
```

Example:

```bash
bookup-fuse my-notes.bdb /mnt/bookup
```

This will create a directory structure like:

```
/mnt/bookup
├── Pages
│   ├── Page One.md
│   └── Another Note.md
├── Sections
│   ├── Work
│   │   └── Task List.md
│   └── Personal
│       ├── Recipes.md
│       └── Journal.md
└── .desktop.ini
```

## Unmounting

```bash
fusermount -u /mnt/bookup     # Linux (FUSE)
# or
umount /mnt/bookup
```

## Notes

* `.desktop.ini` is included for compatibility with Windows' folder tooltips but can be ignored.
* Page and section names containing `/` are automatically sanitized to `_` in file names.
* Timestamps are stored as UNIX epochs in the database.

## Development

```bash
# Install in editable mode
pip install -e ".[dev]"

# Run from source
python src/bookup_fuse.py my-notes.bdb /mnt/bookup
```
