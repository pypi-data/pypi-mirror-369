# dirflex/core.py
from __future__ import annotations
import os
import re
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Iterable, Optional

# ---- helpers for parsing (robust) ----

BOX_DRAWING_RE = re.compile(r'[\u2500-\u257F]')
TREE_CHARS_RE = re.compile(r'(^\s*[\|│\s]*)(?:[├└┐┬┤╰╭╮╯]\s*[-–—─]+\s*)?')

def normalize_line_for_parsing(line: str, tab_size: int = 4) -> str:
    line = line.replace("\t", " " * tab_size)
    cleaned = BOX_DRAWING_RE.sub(" ", line)
    cleaned = re.sub(r'[–—\-]{2,}', ' ', cleaned)
    m = TREE_CHARS_RE.match(cleaned)
    if m:
        prefix = m.group(1)
        rest = cleaned[len(prefix):]
        rest = re.sub(r'^[\s\-\└\├\─\┬\╰\╭\╮\╯\|]+', ' ', rest)
        return prefix + rest.lstrip()
    return cleaned

def detect_spaces_per_level(lines: Iterable[str]) -> int:
    indents = []
    for raw in lines:
        normalized = normalize_line_for_parsing(raw)
        if not normalized.strip():
            continue
        leading = len(normalized) - len(normalized.lstrip(" "))
        if leading > 0:
            indents.append(leading)
    if not indents:
        return 4
    base = min(indents)
    if base >= 8:
        for d in (4, 2):
            if all((x % d == 0) for x in indents):
                return d
    return base or 4

def guess_is_file(name: str) -> bool:
    if not name:
        return False
    if name.endswith("/"):
        return False
    simple = name.rstrip("/").strip()
    if simple.startswith(".") and simple.count(".") == 1:
        return False
    if re.search(r'\.[A-Za-z0-9][A-Za-z0-9_\-]*(?:$|\b|\))', simple):
        return True
    return False

def parse_lines_to_depth_name(lines: Iterable[str], spaces_per_level: int, tab_size:int=4) -> List[Tuple[int, str]]:
    entries: List[Tuple[int,str]] = []
    for raw in lines:
        if not raw.strip():
            continue
        # Remove inline comments (anything after '#')
        raw = raw.split('#', 1)[0].rstrip()
        if not raw.strip():
            continue

        normalized = normalize_line_for_parsing(raw, tab_size)
        leading = len(normalized) - len(normalized.lstrip(" "))
        depth = 0 if spaces_per_level == 0 else leading // spaces_per_level
        name = normalized.strip()
        if name == ".":
            continue
        entries.append((depth, name))
    return entries

def path_components_from_structure(entries: List[Tuple[int, str]]) -> List[Tuple[List[str], bool]]:
    stack: List[str] = []
    out = []
    for depth, name in entries:
        stack = stack[:depth]
        stack.append(name)
        comps = [c for c in stack if c and c != "."]
        is_file = guess_is_file(name)
        out.append((comps, is_file))
    return out

# ---- create on disk ----

def create_from_components(
    comps_and_fileflags: List[Tuple[List[str], bool]],
    output_root: Path,
    mode: str = "skip",
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    no_color: bool = False
) -> Tuple[int,int]:
    created = 0
    skipped = 0
    for comps, is_file in comps_and_fileflags:
        if not comps:
            continue
        target = output_root.joinpath(*comps)
        parent = target.parent

        if is_file:
            if dry_run:
                if verbose: print(f"[DRY] File: {target}")
                continue
            if parent.exists() and parent.is_file():
                if force:
                    parent.unlink()
                    parent.mkdir(parents=True, exist_ok=True)
                else:
                    if verbose: print(f"Conflict: parent is file: {parent}")
                    skipped += 1
                    continue
            else:
                parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.is_dir():
                    if force:
                        shutil.rmtree(target)
                    else:
                        if verbose: print(f"Conflict: directory exists where file expected: {target}")
                        skipped += 1
                        continue
                if mode == "skip":
                    skipped += 1
                    if verbose: print(f"Skipped existing file: {target}")
                    continue
                elif mode == "merge":
                    if verbose: print(f"Kept existing file (merge): {target}")
                    continue
                elif mode == "overwrite":
                    target.write_text("", encoding="utf-8")
                    created += 1
                    if verbose: print(f"Overwrote file: {target}")
                    continue
            else:
                target.touch(exist_ok=True)
                created += 1
                if verbose: print(f"Created file: {target}")
        else:
            if dry_run:
                if verbose: print(f"[DRY] Dir: {target}")
                continue
            if target.exists():
                if target.is_file():
                    if force:
                        target.unlink()
                        target.mkdir(parents=True, exist_ok=True)
                        created += 1
                    else:
                        if verbose: print(f"Conflict: file exists where dir expected: {target}")
                        skipped += 1
                        continue
                else:
                    if mode == "overwrite" and force:
                        shutil.rmtree(target)
                        target.mkdir(parents=True, exist_ok=True)
                        created += 1
                        if verbose: print(f"Recreated directory: {target}")
                    else:
                        if verbose: print(f"Directory exists: {target}")
                        skipped += 1
                        continue
            else:
                target.mkdir(parents=True, exist_ok=True)
                created += 1
                if verbose: print(f"Created directory: {target}")
    return created, skipped

# ---- scan directory -> hierarchical tree, then render consistently ----

@dataclass
class Node:
    name: str
    is_file: bool
    children: list["Node"] = field(default_factory=list)

def _safe_is_file(p: Path) -> bool:
    try:
        return p.is_file()
    except OSError:
        return True

def build_tree(root: Path, follow_symlinks: bool=False, max_depth: Optional[int]=None) -> Node:
    """
    Build a directory tree as nested Node objects.
    Directories are listed before files; items are sorted case-insensitively.
    Symlinks are treated as files unless follow_symlinks=True. Cycles are avoided.
    """
    root = root.resolve()
    visited: set[Tuple[int, int]] = set()

    def _mark_visited(p: Path):
        try:
            st = p.stat()
            visited.add((st.st_dev, st.st_ino))
        except OSError:
            pass

    def _is_visited(p: Path) -> bool:
        try:
            st = p.stat()
            return (st.st_dev, st.st_ino) in visited
        except OSError:
            return True

    _mark_visited(root)

    def _build(path: Path, depth: int) -> Node:
        node = Node(path.name, _safe_is_file(path))
        if node.is_file:
            return node
        if max_depth is not None and depth >= max_depth:
            return node
        try:
            entries = sorted(
                list(path.iterdir()),
                key=lambda x: (_safe_is_file(x), x.name.lower())
            )
        except (PermissionError, OSError):
            return node

        for entry in entries:
            if entry.is_symlink():
                if not follow_symlinks:
                    node.children.append(Node(entry.name, True))
                    continue
                if _is_visited(entry):
                    node.children.append(Node(entry.name, True))
                    continue
                _mark_visited(entry)

            child = _build(entry, depth + 1)
            node.children.append(child)
        return node

    return _build(root, 0)

def _flatten(node: Node, depth: int = 0, out: Optional[List[Tuple[int, str, bool]]] = None) -> List[Tuple[int,str,bool]]:
    if out is None:
        out = []
    out.append((depth, node.name, node.is_file))
    if not node.is_file:
        for child in node.children:
            _flatten(child, depth+1, out)
    return out

def _render_ascii_from_node(root: Node) -> List[str]:
    lines: List[str] = [root.name]

    def rec(children: List[Node], prefix: str) -> None:
        for i, child in enumerate(children):
            last = (i == len(children) - 1)
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + child.name)
            if not child.is_file and child.children:
                extension = "    " if last else "│   "
                rec(child.children, prefix + extension)

    if not root.is_file and root.children:
        rec(root.children, "")
    return lines

# Public API (kept names but now Node-powered under the hood)

def scan_dir_to_entries(root: Path, follow_symlinks: bool=False, max_depth: Optional[int]=None):
    """
    Backwards-compatible name, but returns a Node tree now.
    """
    return build_tree(root, follow_symlinks=follow_symlinks, max_depth=max_depth)

def render_entries_as_indented(root_node, spaces:int=4, use_tabs:bool=False, emoji:Optional[Tuple[str,str]]=None) -> List[str]:
    """
    Render from Node into an indented list (tabs/spaces, optional emojis).
    """
    flat = _flatten(root_node)
    out: List[str] = []
    for depth, name, is_file in flat:
        indent = ("\t" * depth) if use_tabs else (" " * (spaces * depth))
        if emoji:
            folder_emoji, file_emoji = emoji
            symbol = file_emoji if is_file else folder_emoji
            out.append(f"{indent}{symbol} {name}")
        else:
            out.append(f"{indent}{name}")
    return out

def render_entries_as_ascii(root_node) -> List[str]:
    """
    Render from Node into ASCII tree (├──, │, └──), perfectly aligned.
    """
    return _render_ascii_from_node(root_node)

def entries_to_json(root_node) -> str:
    """
    JSON dump (depth + name + is_file) derived from the same Node tree
    used by all other renderers.
    """
    flat = _flatten(root_node)
    arr = [{"depth": d, "path": n, "is_file": is_f} for d, n, is_f in flat]
    return json.dumps(arr, indent=2, ensure_ascii=False)
