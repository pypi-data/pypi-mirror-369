#!/usr/bin/env python3
"""
FUSE FS to mount a Bookup SQLite (".bdb") file as a directory tree.

Usage:
    python src/bookup_fuse.py <bookup_bdb_file> <mount_point>

Directory structure exposed:
    .
    ├── Pages
    │   └── <page-name>.md
    ├── Sections
    │   └── <section-name>
    │       └── <page-name>.md
    └── Images
        └── <id>.bin

Notes
-----
* Bookup ".bdb" files are SQLite databases.
* This implementation handles `page`, `section`, and `image` tables.
* Timestamps are stored as integer UNIX epochs to match the schema's
  `INTEGER` type for date fields.
"""

from __future__ import annotations

import errno
import logging
import os
import sqlite3
import stat
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Union
from argparse import ArgumentParser

try:
    import _find_fuse_parts  # noqa: F401 - optional helper in some envs
except ImportError:
    pass

import fuse
from fuse import Fuse


AUTORUN_INF = lambda label: f"""[.ShellClassInfo]
InfoTip={label}""".encode()

# ---------------------------------------------------------------------------
# FUSE setup
# ---------------------------------------------------------------------------
if not hasattr(fuse, "__version__"):
    raise RuntimeError(
        "Your fuse-py doesn't know fuse.__version__; the library may be too old."
    )

fuse.fuse_python_api = (0, 2)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("BOOKUP_FUSE_LOG", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SQLite helpers and models
# ---------------------------------------------------------------------------

def log(msg: str):
    with open("log.txt", "a") as f:
        f.write(f"{msg}\n")

def _dict_factory(cursor: sqlite3.Cursor, row: Sequence[object]):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _now_epoch() -> int:
    return int(datetime.now().timestamp())


class BookupMeta:
    name: str

    @classmethod
    def from_row(cls, env: dict):
        """Construct dataclass from row dict, ignoring extra columns."""
        return cls(**{k: v for k, v in env.items() if k in cls.__dataclass_fields__})  # type: ignore[attr-defined]

    # -------- filesystem helpers --------
    def sanitize_name(self) -> str:
        if getattr(self, "name", None) in {".", ".."}:
            return ""
        n = getattr(self, "name", None)
        return n.replace("/", "_") if isinstance(n, str) else ""

    @property
    def file_name(self) -> str:
        if isinstance(self, BookupPage):
            return f"{self.sanitize_name()}.md"
        if isinstance(self, BookupImage):
            return f"{self.id}.bin"
        return f"{self.sanitize_name()}"


class BookupConnection:
    """with BookupConnection(path) as (conn, cur): ..."""

    def __init__(self, file: str):
        self._conn = sqlite3.connect(file)
        self._conn.row_factory = _dict_factory
        self._cur = self._conn.cursor()

    def __enter__(self):
        return self._conn, self._cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()


@dataclass
class BookupPage(BookupMeta):
    id: int
    section_id: Optional[int]
    name: str
    data: str
    creation_date: Optional[int] = None
    modification_date: Optional[int] = None
    trash: int = 0

    # Update in DB
    def update(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute(
                "UPDATE page SET name=?, data=?, modification_date=? WHERE id=?",
                (self.name, self.data, _now_epoch(), self.id),
            )
            conn.commit()

    @classmethod
    def create(cls, bdb_file: str, section_id: Optional[int], name: str, data: str):
        now = _now_epoch()
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute(
                "INSERT INTO page (section_id, name, data, creation_date, modification_date, trash) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (section_id, name, data, now, now, 0),
            )
            conn.commit()
            last_id = cur.lastrowid
        return cls(id=last_id, section_id=section_id, name=name, data=data, creation_date=now, modification_date=now, trash=0)

    @classmethod
    def get(cls, bdb_file: str, id: int) -> Optional["BookupPage"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM page WHERE id=?", (id,))
            row = cur.fetchone()
        return cls.from_row(row) if row else None

    def delete(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("DELETE FROM page WHERE id=?", (self.id,))
            conn.commit()

    @classmethod
    def all(cls, bdb_file: str) -> List["BookupPage"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM page WHERE trash=0")
            rows = cur.fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_name(cls, bdb_file: str, name: str) -> Optional["BookupPage"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM page WHERE name=? AND trash=0", (name,))
            row = cur.fetchone()
        return cls.from_row(row) if row else None


@dataclass
class BookupSection(BookupMeta):
    id: int
    name: str
    parent_id: Optional[int] = None

    def update(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("UPDATE section SET name=?, parent_id=? WHERE id=?", (self.name, self.parent_id, self.id))
            conn.commit()

    @classmethod
    def from_id(cls, bdb_file: str, section_id: int) -> Optional["BookupSection"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM section WHERE id=?", (section_id,))
            row = cur.fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def create(cls, bdb_file: str, name: str, parent_id: Optional[int] = None):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("INSERT INTO section (name, parent_id) VALUES (?, ?)", (name, parent_id))
            conn.commit()
            last_id = cur.lastrowid
        return cls(id=last_id, name=name, parent_id=parent_id)

    def pages(self, bdb_file: str) -> List[BookupPage]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM page WHERE section_id=? AND trash=0", (self.id,))
            rows = cur.fetchall()
        return [BookupPage.from_row(row) for row in rows]

    def delete(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("DELETE FROM section WHERE id=?", (self.id,))
            conn.commit()

    @classmethod
    def all(cls, bdb_file: str) -> List["BookupSection"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM section ORDER BY order_num, name")
            rows = cur.fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def all_root(cls, bdb_file: str) -> List["BookupSection"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM section WHERE parent_id = 0 ORDER BY order_num, name")
            rows = cur.fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def all_children(cls, parent: "BookupSection", bdb_file: str) -> List[Union["BookupSection", BookupPage]]:
        children: List[Union[BookupSection, BookupPage]] = []
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM section WHERE parent_id=? ORDER BY order_num, name", (parent.id,))
            rows = cur.fetchall()
            children.extend([cls.from_row(row) for row in rows])
            cur.execute("SELECT * FROM page WHERE section_id=? AND trash=0", (parent.id,))
            rows = cur.fetchall()
            children.extend([BookupPage.from_row(row) for row in rows])
        return children

    @classmethod
    def get_child(
        cls, parent: "BookupSection", name: str, bdb_file: str
    ) -> Optional[Union["BookupSection", BookupPage]]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT * FROM section WHERE parent_id=? AND name=?", (parent.id, name))
            row = cur.fetchone()
            if row:
                return BookupSection.from_row(row)
            cur.execute("SELECT * FROM page WHERE section_id=? AND name=? AND trash=0", (parent.id, name))
            row = cur.fetchone()
            return BookupPage.from_row(row) if row else None

    @classmethod
    def resolve_path(
        cls, bdb_file: str, path: Sequence[str], parent: Optional["BookupSection"] = None
    ) -> Optional[Union["BookupSection", BookupPage]]:
        if not path:
            return None

        current_item_name = _name_from_pages_path(path[0])
        current_item: Optional[Union[BookupSection, BookupPage]]

        current_item = cls.get_child(parent, current_item_name, bdb_file) if parent else cls.from_name(bdb_file, current_item_name)

        if isinstance(current_item, BookupPage):
            return current_item

        if current_item is None:
            return BookupPage.from_name(bdb_file, current_item_name)

        return cls.resolve_path(bdb_file, path[1:], current_item) if len(path) != 1 else current_item


# NEW: Image model ------------------------------------------------------------

@dataclass
class BookupImage:
    id: int
    data: bytes

    @classmethod
    def from_row(cls, env: dict) -> "BookupImage":
        return cls(id=env["id"], data=env["data"])

    @property
    def file_name(self) -> str:
        return f"{self.id}.bin"

    def update(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("UPDATE image SET data=? WHERE id=?", (self.data, self.id))
            conn.commit()

    @classmethod
    def create(cls, bdb_file: str, data: bytes) -> "BookupImage":
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("INSERT INTO image (data) VALUES (?)", (data,))
            conn.commit()
            last_id = cur.lastrowid
        return cls(id=last_id, data=data)

    @classmethod
    def get(cls, bdb_file: str, id_: int) -> Optional["BookupImage"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT id, data FROM image WHERE id=?", (id_,))
            row = cur.fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def all(cls, bdb_file: str) -> List["BookupImage"]:
        with BookupConnection(bdb_file) as (_, cur):
            cur.execute("SELECT id, data FROM image")
            rows = cur.fetchall()
        return [cls.from_row(r) for r in rows]

    def delete(self, bdb_file: str):
        with BookupConnection(bdb_file) as (conn, cur):
            cur.execute("DELETE FROM image WHERE id=?", (self.id,))
            conn.commit()


# ---------------------------------------------------------------------------
# FUSE stat wrappers
# ---------------------------------------------------------------------------
class BookupStat(fuse.Stat):
    def __init__(self):
        self.st_mode = stat.S_IFDIR | 0o755
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 4096
        self.st_atime = _now_epoch()
        self.st_mtime = _now_epoch()
        self.st_ctime = _now_epoch()


# ---------------------------------------------------------------------------
# FUSE FS implementation
# ---------------------------------------------------------------------------
class BookupFuse(Fuse):
    file: str

    def __init__(self, bdb_file: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = os.path.abspath(bdb_file)

    def getattr(self, path):
        st = BookupStat()

        if path == "/" or path in {"/Pages", "/Sections", "/Images"}:
            return st  # directory

        if path == "/.desktop.ini":
            st.st_mode = stat.S_IFREG | 0o644
            st.st_nlink = 1
            st.st_size = len(AUTORUN_INF(os.path.basename(self.file)))
            return st

        if path.startswith("/Sections"):
            parts = [p for p in _split_path(_unsuffix_md(path)) if p][1:]
            item = BookupSection.resolve_path(self.file, parts)
            if isinstance(item, BookupSection):
                st.st_mode = stat.S_IFDIR | 0o755
                st.st_nlink = 2
            elif isinstance(item, BookupPage):
                st.st_mode = stat.S_IFREG | 0o644
                st.st_nlink = 1
                st.st_size = len(item.data.encode("utf-8"))
            else:
                raise fuse.FuseError(errno.ENOENT)
            return st

        if path.startswith("/Pages"):
            name = _name_from_pages_path(path)
            item = BookupPage.from_name(self.file, name)
            if not item:
                raise fuse.FuseError(errno.ENOENT)
            st.st_mode = stat.S_IFREG | 0o644
            st.st_nlink = 1
            st.st_size = len(item.data.encode("utf-8"))
            return st

        if path.startswith("/Images"):
            img_id = _image_id_from_path(path)
            if img_id is None:
                raise fuse.FuseError(errno.ENOENT)
            img = BookupImage.get(self.file, img_id)
            if not img:
                raise fuse.FuseError(errno.ENOENT)
            st.st_mode = stat.S_IFREG | 0o644
            st.st_nlink = 1
            st.st_size = len(img.data or b"")
            return st

        raise fuse.FuseError(errno.ENOENT)

    def readdir(self, path: str, fh):  # noqa: ARG002 - signature dictated by fuse
        dirents: List[str] = [".", ".."]

        if path == "/":
            dirents.extend(["Pages", "Sections", "Images", ".desktop.ini"])
        elif path == "/Pages":
            pages = BookupPage.all(self.file)
            dirents.extend([f"{i+1} : {section.name if (section := BookupSection.from_id(self.file, p.section_id)) else '#'} – {p.file_name}" for i, p in enumerate(pages)])
        elif path.startswith("/Sections"):
            if path == "/Sections":
                sections = BookupSection.all_root(self.file)
                dirents.extend([f"{i+1} – {s.file_name}" for i, s in enumerate(sections)])
            else:
                parts = [p for p in _split_path(path) if p][1:]
                element = BookupSection.resolve_path(self.file, parts)
                if isinstance(element, BookupSection):
                    dirents.extend([f"{i+1} – {child.file_name}" for i, child in enumerate(BookupSection.get_children(element, self.file))])
                else:
                    raise fuse.FuseError(errno.ENOTDIR)
        elif path == "/Images":
            images = BookupImage.all(self.file)
            dirents.extend([f"{i+1} – {img.file_name}" for i, img in enumerate(images)])
        else:
            raise fuse.FuseError(errno.ENOENT)

        for d in dirents:
            yield fuse.Direntry(d)

    def open(self, path, flags):  # noqa: D401 - FUSE signature
        if path in {"/", "/Pages", "/Sections", "/Images"}:
            raise fuse.FuseError(errno.EISDIR)
        return 0

    def read(self, path, size, offset):
        if path.startswith("/Pages") and path != "/Pages":
            name = _name_from_pages_path(path)
            page = BookupPage.from_name(self.file, name)
            if not page:
                raise fuse.FuseError(errno.ENOENT)
            return page.data.encode("utf-8")[offset : offset + size]

        if path.startswith("/Sections") and path != "/Sections":
            parts = [p for p in _split_path(_unsuffix_md(path)) if p][1:]
            item = BookupSection.resolve_path(self.file, parts)
            if isinstance(item, BookupSection):
                raise fuse.FuseError(errno.EISDIR)
            if isinstance(item, BookupPage):
                return item.data.encode("utf-8")[offset : offset + size]
            raise fuse.FuseError(errno.ENOENT)

        if path.startswith("/Images") and path != "/Images":
            img_id = _image_id_from_path(path)
            if img_id is None:
                raise fuse.FuseError(errno.ENOENT)
            img = BookupImage.get(self.file, img_id)
            if not img:
                raise fuse.FuseError(errno.ENOENT)
            return (img.data or b"")[offset : offset + size]

        if path == "/.desktop.ini":
            return AUTORUN_INF(os.path.basename(self.file))

        raise fuse.FuseError(errno.EISDIR)

    def write(self, path, data, offset):
        text = data.decode("utf-8", errors="ignore")

        if path.startswith("/Pages") and path != "/Pages":
            name = _name_from_pages_path(path)
            page = BookupPage.from_name(self.file, name)
            if not page:
                raise fuse.FuseError(errno.ENOENT)
            page.data = _splice(page.data, text, offset)
            page.update(self.file)
            return len(data)

        if path.startswith("/Sections") and path != "/Sections":
            parts = [p for p in _split_path(_unsuffix_md(path)) if p][1:]
            item = BookupSection.resolve_path(self.file, parts)
            if isinstance(item, BookupSection):
                raise fuse.FuseError(errno.EISDIR)
            if isinstance(item, BookupPage):
                item.data = _splice(item.data, text, offset)
                item.update(self.file)
                return len(data)
            raise fuse.FuseError(errno.ENOENT)

        if path.startswith("/Images") and path != "/Images":
            img_id = _image_id_from_path(path)
            if img_id is None:
                raise fuse.FuseError(errno.ENOENT)
            img = BookupImage.get(self.file, img_id)
            if not img:
                raise fuse.FuseError(errno.ENOENT)
            img.data = _splice_bytes(img.data or b"", data, offset)
            img.update(self.file)
            return len(data)

        if path == "/.desktop.ini":
            raise fuse.FuseError(errno.EPERM)

        raise fuse.FuseError(errno.EISDIR)

    def release(self, path, fh):  # noqa: D401 - FUSE signature
        return 0

    def truncate(self, path, length):
        if path.startswith("/Pages") and path != "/Pages":
            name = _name_from_pages_path(path)
            item = BookupPage.from_name(self.file, name)
            if not item:
                return -errno.ENOENT
            item.data = item.data[:length]
            item.update(self.file)
            return 0

        if path.startswith("/Sections") and path != "/Sections":
            parts = [p for p in _split_path(_unsuffix_md(path)) if p][1:]
            item = BookupSection.resolve_path(self.file, parts)
            if isinstance(item, BookupSection):
                raise fuse.FuseError(errno.EISDIR)
            if isinstance(item, BookupPage):
                item.data = item.data[:length]
                item.update(self.file)
                return 0
            raise fuse.FuseError(errno.ENOENT)

        if path.startswith("/Images") and path != "/Images":
            img_id = _image_id_from_path(path)
            if img_id is None:
                raise fuse.FuseError(errno.ENOENT)
            img = BookupImage.get(self.file, img_id)
            if not img:
                raise fuse.FuseError(errno.ENOENT)
            img.data = (img.data or b"")[:length]
            img.update(self.file)
            return 0

        if path == "/.desktop.ini":
            raise fuse.FuseError(errno.EPERM)

        raise fuse.FuseError(errno.ENOENT)

    def utimens(self, path, times):
        # Only pages persist mtime; images are binary blobs without timestamp fields.
        if path.startswith("/Pages") and path != "/Pages":
            name = _name_from_pages_path(path)
            item = BookupPage.from_name(self.file, name)
            if not item:
                return -errno.ENOENT
            item.modification_date = int(times[1]) if times and times[1] else _now_epoch()
            item.update(self.file)
            return 0

        if path.startswith("/Sections") and path != "/Sections":
            parts = [p for p in _split_path(_unsuffix_md(path)) if p][1:]
            item = BookupSection.resolve_path(self.file, parts)
            if isinstance(item, BookupSection):
                raise fuse.FuseError(errno.EISDIR)
            if isinstance(item, BookupPage):
                item.modification_date = int(times[1]) if times and times[1] else _now_epoch()
                item.update(self.file)
                return 0
            raise fuse.FuseError(errno.ENOENT)

        if path == "/.desktop.ini":
            raise fuse.FuseError(errno.EPERM)

        return 0  # noop for Images and others

    def chown(self, path, uid, gid):
        return -errno.ENOSYS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_path(path: str) -> List[str]:
    return [p for p in path.split("/") if p]


def _unsuffix_md(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path


def _name_from_pages_path(path: str) -> str:
    name = os.path.basename(path)
    name = name[:-3] if name.endswith(".md") else name
    name = ' – '.join(name.split(' – ')[1:])
    return name


def _splice(original: str, new_chunk: str, offset: int) -> str:
    """Insert/overwrite new_chunk into original at `offset` (byte offset on UTF-8 text)."""
    b = original.encode("utf-8")
    left = b[:offset]
    right = b[offset + len(new_chunk.encode("utf-8")) :]
    merged = left + new_chunk.encode("utf-8") + right
    return merged.decode("utf-8", errors="ignore")


def _splice_bytes(original: bytes, new_chunk: bytes, offset: int) -> bytes:
    """Insert/overwrite bytes at byte offset (for BLOBs)."""
    left = original[:offset]
    right = original[offset + len(new_chunk) :]
    return left + new_chunk + right


def _image_id_from_path(path: str) -> Optional[int]:
    """
    Accept /Images/<id> or /Images/<id>.bin; returns int id or None.
    """
    base = os.path.basename(path)
    base = ' – '.join(base.split(' – ')[1:])
    if base.endswith(".bin"):
        base = base[:-4]
    try:
        return int(base)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = ArgumentParser(description="Mount a Bookup .bdb file using FUSE")
    parser.add_argument("bdb_file", help="Path to the .bdb SQLite file")
    parser.add_argument("mount_point", help="Mount point directory")
    args = parser.parse_args()

    usage = "\nMount a bookup-DB file to a directory\n\n" + Fuse.fusage

    server = BookupFuse(
        bdb_file=args.bdb_file,
        version="%prog " + fuse.__version__,
        usage=usage,
        dash_s_do="setsingle",
    )
    # Pass the mount point to FUSE's parser
    server.parse(errex=1, args=[f'-ofsname={os.path.basename(args.bdb_file)}', args.mount_point, '-df'])
    server.main()


if __name__ == "__main__":
    main()
