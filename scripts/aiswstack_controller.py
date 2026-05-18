#!/usr/bin/env python3
"""AISW-stack MVC Controller —— 类层级 API + 结构化定位（slug / num / (L,B)）。

架构：
  Model       chat/AISW-stack/index.sqlite3
  View        chat/AISW-stack/README.md
  Controller  scripts/aiswstack_controller.py（本文件）

## 数据模型

  sections      key PK, position, section_type, heading, body, layer_code, branch_code
                  body 是 markdown 原貌（**source of truth**）。
  entries       slug PK, name, url, notes, section_key, vendor, category, position
                  作为查询索引 + 定位锚（slug 唯一）。可由 `refresh-index` 重建。
  entry_refs    entry_id, ref_num, position
  refs          num PK, citation, url（source of truth）
  cells         layer_code, branch_code, text, marker（source of truth）
  layers        code PK, position, name
  branches      code PK, parent_code, position, name

## 类层级（公开 API；定位全部走 key / slug / num / (L,B)，不用字符串搜索）

  Document
    section(key)                          → Section
    entry(slug)                           → Entry
    ref(num)                              → Ref

  Section（抽象）
    set_heading(text)
    render() → str
    + 各子类：

  DocTop / MainOverview / BranchIntro / Branch / Crosscut / Other
    get_body() / set_body(text)

  Layer / SubBranch
    get_body() / set_body(text)
    add_entry(vb_label, name, url, ref_num, notes=None, separator=None)
                                          → Entry（按 vendor 标签插入 body）
    remove_entry(slug)                    在 body 里精确剔除该 entry token
    set_entry_url(slug, url)              `[[N]](old)` → `[[N]](new)`
    set_entry_name(slug, name)            `OldName[[N]]` → `NewName[[N]]`
    set_entry_notes(slug, notes)          替换 `[[N]](url)（…）` 后的注解

  SummaryTable
    get_intro() / set_intro(text)
    get_cell(L, B) / set_cell(L, B, text)
    rendered table 从 cells 表重建。

  Refs
    next_num() → int
    add(citation, url=None) → int         自动 max+1；按 url 去重
    get(num) / set(num, …) / remove(num)

## CLI 一览

  init                          建表
  migrate-from-blocks           一次性把旧 blocks 表搬到 sections
  render                        重建 README.md
  refresh-index                 从 sections.body 重建 entries / refs / cells 索引
  stats                         表行数
  query SQL                     只读 SELECT

  section list
  section show KEY
  section set-heading KEY --heading TEXT
  section set-body KEY (--body TEXT | --file F)        prose-only 与 layer/sub
                                                       都可整段替换

  entry list [--section K] [--layer L] [--branch B] [--vendor V]
  entry show SLUG
  entry add KEY --vb-label LBL --name N --url U --ref R [--notes T]
              [--separator SEP]
  entry remove SLUG
  entry set-url SLUG --url U
  entry set-name SLUG --name N
  entry set-notes SLUG --notes T

  ref list [--orphan]
  ref show NUM
  ref add --citation TXT [--url URL]    去重，返回 num
  ref set NUM [--citation T] [--url U]
  ref remove NUM
  ref next-num

  cell get LAYER BRANCH
  cell set LAYER BRANCH --text TEXT

## 设计要点

1. `section.body` 是 markdown 原貌。render 对绝大多数 section 直接吐出 body；
   只有 summary_table 与 refs 走"按结构表重建"的渲染路径。
2. entries 是 derived 索引：每次 mutation 通过 `refresh-index` 重建；slug 在
   重建后稳定（slug 由 layer/branch code + 名字归一）。
3. mutation 不接受 `--old/--new` 字符串。set-url 之类内部用 `[[N]](current_url)`
   token 在 body 里做唯一替换——(ref_num, url) 全局唯一，不会误匹配。
4. add-entry 时按 vb 标签（如 `**NVIDIA**：`）定位插入点；标签在一个 section
   内本就唯一。layout 由现状推断（bullets 行 vs inline 列表）。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "chat/AISW-stack/README.md"
DB_PATH = ROOT / "chat/AISW-stack/index.sqlite3"
TEMPLATES_DIR = ROOT / "chat/AISW-stack/templates"

# ---------------------------------------------------------------------------
# constants

MAIN_BRANCHES = [
    ("A", "LLM / Agent"), ("B", "科学计算"), ("C", "机器人"),
    ("D", "自动驾驶"), ("E", "世界模型 / 3D"), ("F", "经典 CV"),
    ("G", "量化金融"), ("H", "游戏"), ("I", "影视娱乐"),
    ("J", "学习 / 教育"),
]

KNOWN_VENDORS = {
    "NVIDIA", "AMD", "Intel", "Apple", "AWS", "Google", "Microsoft", "Meta",
    "Anthropic", "OpenAI", "xAI", "DeepSeek", "Mistral", "Cohere",
    "Databricks", "Snowflake", "Cloudflare", "HuggingFace", "Hugging Face",
    "IBM", "Oracle", "SAP", "Salesforce", "ServiceNow", "Workday",
    "华为", "华为昇腾", "阿里", "百度", "腾讯", "字节",
    "高通", "Qualcomm", "联发科", "MediaTek", "瑞芯微", "Rockchip",
}

VENDOR_ALIASES = {
    "华为昇腾": "华为",
    "华为昇腾（Ascend）": "华为",
    "Hugging Face": "HuggingFace",
    "Qualcomm": "高通",
    "MediaTek": "联发科",
    "Rockchip": "瑞芯微",
}

PROSE_ONLY_TYPES = {"doc_top", "main_overview", "branch_intro", "branch",
                    "crosscut", "other"}
LAYER_LIKE_TYPES = {"layer", "subbranch"}

# ---------------------------------------------------------------------------
# schema

SCHEMA = """
CREATE TABLE IF NOT EXISTS sections (
    key           TEXT PRIMARY KEY,
    position      INTEGER NOT NULL,
    section_type  TEXT NOT NULL,
    heading       TEXT,
    body          TEXT NOT NULL DEFAULT '',
    layer_code    TEXT,
    branch_code   TEXT
);

CREATE TABLE IF NOT EXISTS entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    url          TEXT,
    notes        TEXT,
    section_key  TEXT NOT NULL,
    layer_code   TEXT,
    branch_code  TEXT,
    vendor       TEXT,
    category     TEXT,
    position     INTEGER NOT NULL,
    FOREIGN KEY (section_key) REFERENCES sections(key) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS entry_refs (
    entry_id  INTEGER NOT NULL,
    ref_num   INTEGER NOT NULL,
    position  INTEGER NOT NULL,
    PRIMARY KEY (entry_id, ref_num),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (ref_num)  REFERENCES refs(num)
);

CREATE TABLE IF NOT EXISTS refs (
    num      INTEGER PRIMARY KEY,
    citation TEXT NOT NULL,
    url      TEXT
);

CREATE TABLE IF NOT EXISTS cells (
    layer_code   TEXT NOT NULL,
    branch_code  TEXT NOT NULL,
    text         TEXT,
    marker       TEXT,
    PRIMARY KEY (layer_code, branch_code)
);

CREATE TABLE IF NOT EXISTS layers (
    code     TEXT PRIMARY KEY,
    position INTEGER NOT NULL,
    name     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    code        TEXT PRIMARY KEY,
    parent_code TEXT,
    position    INTEGER NOT NULL,
    name        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_section ON entries(section_key);
CREATE INDEX IF NOT EXISTS idx_entries_layer   ON entries(layer_code);
CREATE INDEX IF NOT EXISTS idx_entries_branch  ON entries(branch_code);
CREATE INDEX IF NOT EXISTS idx_entries_vendor  ON entries(vendor);
CREATE INDEX IF NOT EXISTS idx_entry_refs_ref  ON entry_refs(ref_num);
CREATE INDEX IF NOT EXISTS idx_sections_position ON sections(position);
"""

# ---------------------------------------------------------------------------
# regex helpers

_PUNCT_RE = re.compile(r"[\s/（）()，,、；;:：&+]+")
_SLUG_DECO_RE = re.compile(r"[*_`\"'·]")
SEP_CHARS = "、，,；;|。：:"
NAME_SPLIT_RE = re.compile(r"[" + re.escape(SEP_CHARS) + r"]|(?<=[）)\s])\+\s")
REF_LINK_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^\s)]+)\)")
REF_ENTRY_RE = re.compile(
    r"^\[(\d+)\]\s+(.+?)(?:\s*\[Online\]\.\s+Available:\s*<([^>]+)>)?\s*$"
)
LAYER_TITLE_RE = re.compile(r"^(L\d{2})\s+(.+)$")
BRANCH_TITLE_RE = re.compile(r"^([A-Z](?:\d+)?)\s+(.+)$")
VENDOR_BLOCK_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*$")
VENDOR_INLINE_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*(\S.*)$")
GROUP_LABEL_RE = re.compile(r"^([-*])\s+\*\*([^*]+)\*\*[:：]\s*(.*)$")
BARE_VENDOR_RE = re.compile(r"^[-*]\s+([^*：:\[]{1,24}?)[：:]\s*(.+)$")


def canonical_vendor(label: str | None) -> str | None:
    if not label:
        return None
    plain = label.strip()
    bare = re.sub(r"（[^）]*）|\([^)]*\)", "", plain).strip()
    for cand in (plain, bare):
        if cand in VENDOR_ALIASES:
            return VENDOR_ALIASES[cand]
        if cand in KNOWN_VENDORS:
            return cand
    return None


def slugify(prefix: str, name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = _SLUG_DECO_RE.sub("", s)
    s = _PUNCT_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    if not s:
        s = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return f"{prefix.lower()}-{s}"


def clean_display_name(raw: str) -> str:
    """Strip leading bullet decorations and trailing separators but preserve
    backticks, underscores, asterisks (bold), and other intra-name characters."""
    s = raw
    s = re.sub(r"^[\s\-+]+|[\s\-+:：]+$", "", s)
    return s.strip()


def is_valid_name(name: str) -> bool:
    if not name:
        return False
    plain = re.sub(r"[*_`]", "", name).strip()
    if not plain:
        return False
    if plain.startswith(("//", ")", "）", "/")):
        return False
    if "://" in plain:
        return False
    if re.fullmatch(r"[（(].*[）)]", plain):
        return False
    return True


def extract_trailing_notes(text: str, pos: int) -> str | None:
    rest = text[pos:].lstrip()
    if rest.startswith(("（", "(")):
        opener = rest[0]
        closer = "）" if opener == "（" else ")"
        depth = 0
        for i, ch in enumerate(rest):
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return rest[1:i]
    return None


def classify_cell_marker(text: str) -> str:
    t = (text or "").strip()
    if not t or t in ("—", "-", "–"):
        return "none"
    if t.startswith("同 A"):
        return "same_a"
    if t.startswith("与 ") and "共用" in t:
        return "shared"
    return "normal"


# ---------------------------------------------------------------------------
# dataclasses

@dataclass
class Ref:
    num: int
    citation: str
    url: str | None

    def render(self) -> str:
        if self.url:
            return f"[{self.num}] {self.citation} [Online]. Available: <{self.url}>"
        return f"[{self.num}] {self.citation}"


@dataclass
class Entry:
    id: int
    slug: str
    name: str
    url: str | None
    notes: str | None
    section_key: str
    layer_code: str | None
    branch_code: str | None
    vendor: str | None
    category: str | None
    position: int
    ref_nums: list[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# index: extract entries / refs / cells from sections.body

def extract_entries_from_text(text: str):
    out = []
    for m in REF_LINK_RE.finditer(text):
        ref_num = int(m.group(1))
        url = m.group(2)
        before = text[:m.start()]
        parts = NAME_SPLIT_RE.split(before)
        raw_name = parts[-1] if parts else ""
        name = clean_display_name(raw_name)
        if not is_valid_name(name):
            continue
        notes = extract_trailing_notes(text, m.end())
        out.append({"name": name, "url": url, "ref": ref_num, "notes": notes})
    return out


def index_section_body(conn: sqlite3.Connection, section_key: str,
                       section_type: str, body: str,
                       layer_code: str | None, branch_code: str | None,
                       slug_seen: set[str]):
    """Walk a layer/subbranch body and write derived entries + entry_refs."""
    if section_type not in LAYER_LIKE_TYPES:
        return
    slug_prefix = layer_code or branch_code or section_key
    if not slug_prefix:
        return
    state_vendor: str | None = None
    state_category: str | None = None
    position = 0
    cur = conn.cursor()
    for line in body.split("\n"):
        m = VENDOR_BLOCK_RE.match(line.strip())
        if m:
            label = m.group(1).strip()
            cv = canonical_vendor(label)
            if cv:
                state_vendor, state_category = cv, None
            else:
                state_category, state_vendor = label, None
            continue
        m_inline = VENDOR_INLINE_RE.match(line.strip())
        if m_inline:
            label = m_inline.group(1).strip()
            cv = canonical_vendor(label)
            local_vendor = cv
            local_category = label if not cv else None
            rest = m_inline.group(2)
            state_vendor = cv if cv else None
            state_category = label if not cv else None
            for e in extract_entries_from_text(rest):
                position = _emit_entry(
                    cur, e, section_key, slug_prefix,
                    layer_code, branch_code,
                    local_vendor, local_category, position, slug_seen)
            continue
        if not REF_LINK_RE.search(line):
            continue
        local_vendor = state_vendor
        local_category = state_category
        rest = line
        if line.lstrip().startswith(("-", "*")):
            rest = line.lstrip()[1:].strip()
            g = GROUP_LABEL_RE.match(line)
            if g:
                label = g.group(2).strip()
                cv = canonical_vendor(label)
                if cv:
                    local_vendor = cv
                local_category = label
                rest = g.group(3)
            else:
                b = BARE_VENDOR_RE.match(line)
                if b and (cv := canonical_vendor(b.group(1).strip())):
                    local_vendor = cv
                    rest = b.group(2)
        for e in extract_entries_from_text(rest):
            position = _emit_entry(
                cur, e, section_key, slug_prefix,
                layer_code, branch_code,
                local_vendor, local_category, position, slug_seen)


def _emit_entry(cur, e: dict, section_key: str, slug_prefix: str,
                layer_code: str | None, branch_code: str | None,
                vendor: str | None, category: str | None,
                position: int, slug_seen: set[str]) -> int:
    base = slugify(slug_prefix, e["name"])
    slug = base
    n = 2
    while slug in slug_seen:
        slug = f"{base}-{n}"; n += 1
    slug_seen.add(slug)
    cur.execute(
        "INSERT INTO entries(slug, name, url, notes, section_key, "
        "layer_code, branch_code, vendor, category, position) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (slug, e["name"], e["url"], e["notes"], section_key,
         layer_code, branch_code, vendor, category, position),
    )
    entry_id = cur.lastrowid
    cur.execute(
        "INSERT OR IGNORE INTO entry_refs(entry_id, ref_num, position) "
        "VALUES (?, ?, 0)",
        (entry_id, e["ref"]),
    )
    return position + 1


def index_summary_table(conn: sqlite3.Connection, body: str):
    """Walk the summary-table body, populate `cells` + `layers`."""
    cur = conn.cursor()
    for line in body.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not re.match(r"^L\d{2}\b", cells[0]):
            continue
        m = re.match(r"^(L\d{2})\s+(.+)$", cells[0])
        if not m:
            continue
        lc = m.group(1); lname = m.group(2).strip()
        cur.execute(
            "INSERT OR REPLACE INTO layers(code, position, name) VALUES (?, ?, ?)",
            (lc, int(lc[1:]), lname),
        )
        for i, raw_cell in enumerate(cells[1:]):
            if i >= len(MAIN_BRANCHES):
                break
            bcode = MAIN_BRANCHES[i][0]
            cur.execute(
                "INSERT OR REPLACE INTO cells(layer_code, branch_code, "
                "text, marker) VALUES (?, ?, ?, ?)",
                (lc, bcode, raw_cell, classify_cell_marker(raw_cell)),
            )


def index_refs(conn: sqlite3.Connection, body: str):
    cur = conn.cursor()
    for line in body.split("\n"):
        m = REF_ENTRY_RE.match(line)
        if not m:
            continue
        num = int(m.group(1))
        cit = m.group(2).strip()
        url = m.group(3)
        try:
            cur.execute(
                "INSERT INTO refs(num, citation, url) VALUES (?, ?, ?)",
                (num, cit, url),
            )
        except sqlite3.IntegrityError:
            cur.execute(
                "UPDATE refs SET citation=?, url=? WHERE num=?",
                (cit, url, num),
            )


def refresh_all_indexes(conn: sqlite3.Connection):
    """Rebuild entries / entry_refs / refs / cells / layers / branches from
    sections.body. Idempotent; safe to call after any body mutation."""
    cur = conn.cursor()
    cur.executescript("""
        DELETE FROM entry_refs;
        DELETE FROM entries;
        DELETE FROM cells;
        DELETE FROM refs;
        DELETE FROM layers;
        DELETE FROM branches;
    """)
    # branches: seed main + populate sub from sections of type branch/subbranch
    for i, (code, name) in enumerate(MAIN_BRANCHES, start=1):
        cur.execute(
            "INSERT OR REPLACE INTO branches(code, parent_code, position, "
            "name) VALUES (?, NULL, ?, ?)",
            (code, i, name),
        )
    rows = cur.execute(
        "SELECT key, section_type, heading, body, layer_code, branch_code "
        "FROM sections ORDER BY position"
    ).fetchall()
    # refs first, so FK targets exist
    for key, stype, heading, body, lc, bc in rows:
        if stype == "refs":
            index_refs(conn, body)
    for key, stype, heading, body, lc, bc in rows:
        if stype == "summary_table":
            index_summary_table(conn, body)
        if stype in ("branch", "subbranch") and heading:
            m = BRANCH_TITLE_RE.match(heading)
            if m:
                bc = m.group(1)
                parent = bc[0] if len(bc) > 1 else None
                pos = 100 + sum(1 for _ in cur.execute(
                    "SELECT 1 FROM branches WHERE parent_code IS NOT NULL"
                ).fetchall())
                cur.execute(
                    "INSERT OR REPLACE INTO branches(code, parent_code, "
                    "position, name) VALUES (?, ?, ?, ?)",
                    (bc, parent, pos, m.group(2).strip()),
                )
    slug_seen: set[str] = set()
    for key, stype, heading, body, lc, bc in rows:
        if stype in LAYER_LIKE_TYPES:
            index_section_body(conn, key, stype, body, lc, bc, slug_seen)
    cur.execute(
        "INSERT OR REPLACE INTO sync_meta(key, value) VALUES (?, ?)",
        ("last_refresh_ts", str(int(time.time()))),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# repo helpers

def get_section_row(conn, key: str):
    return conn.execute(
        "SELECT key, position, section_type, heading, body, layer_code, "
        "branch_code FROM sections WHERE key=?", (key,)
    ).fetchone()


def load_entry(conn, slug: str = None, entry_id: int = None) -> Entry | None:
    if slug is not None:
        row = conn.execute(
            "SELECT id, slug, name, url, notes, section_key, layer_code, "
            "branch_code, vendor, category, position FROM entries WHERE slug=?",
            (slug,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, slug, name, url, notes, section_key, layer_code, "
            "branch_code, vendor, category, position FROM entries WHERE id=?",
            (entry_id,),
        ).fetchone()
    if not row:
        return None
    e = Entry(
        id=row[0], slug=row[1], name=row[2], url=row[3], notes=row[4],
        section_key=row[5], layer_code=row[6], branch_code=row[7],
        vendor=row[8], category=row[9], position=row[10],
    )
    e.ref_nums = [
        r[0] for r in conn.execute(
            "SELECT ref_num FROM entry_refs WHERE entry_id=? ORDER BY position",
            (e.id,),
        ).fetchall()
    ]
    return e


def load_ref(conn, num: int) -> Ref | None:
    row = conn.execute(
        "SELECT num, citation, url FROM refs WHERE num=?", (num,)
    ).fetchone()
    return Ref(num=row[0], citation=row[1], url=row[2]) if row else None


# ---------------------------------------------------------------------------
# Document + Section class hierarchy

class Section:
    section_type: str = "other"

    def __init__(self, doc: "Document", key: str, position: int,
                 heading: str | None, body: str,
                 layer_code: str | None, branch_code: str | None):
        self.doc = doc
        self.conn = doc.conn
        self.key = key
        self.position = position
        self.heading = heading
        self.body = body
        self.layer_code = layer_code
        self.branch_code = branch_code

    def get_body(self) -> str:
        return self.body

    def set_body(self, body: str):
        self.body = body
        self.conn.execute("UPDATE sections SET body=? WHERE key=?",
                          (body, self.key))

    def set_heading(self, heading: str):
        self.heading = heading
        self.conn.execute("UPDATE sections SET heading=? WHERE key=?",
                          (heading, self.key))

    def render(self) -> str:
        body = self._render_body()
        if self.section_type == "doc_top":
            return body
        prefix = "###" if self.section_type in ("branch", "subbranch") else "##"
        return f"\n\n{prefix} {self.heading}\n\n{body}"

    def _render_body(self) -> str:
        return self.body


class DocTop(Section):       section_type = "doc_top"
class MainOverview(Section): section_type = "main_overview"
class BranchIntro(Section):  section_type = "branch_intro"
class Branch(Section):       section_type = "branch"
class Crosscut(Section):     section_type = "crosscut"
class Other(Section):        section_type = "other"


class _LayerLike(Section):
    """Layer / SubBranch: body is markdown, but offers entry-level methods
    that locate by slug and patch body via stable [[N]](url) tokens."""

    # --- entry mutations (operate on section.body) ----------------------

    def _entry_or_die(self, slug: str) -> Entry:
        e = load_entry(self.conn, slug=slug)
        if not e:
            raise KeyError(f"entry slug='{slug}' not found")
        if e.section_key != self.key:
            raise ValueError(
                f"entry '{slug}' belongs to section '{e.section_key}', "
                f"not '{self.key}'")
        return e

    def _patch_body_unique(self, old: str, new: str):
        count = self.body.count(old)
        if count == 0:
            raise ValueError(
                f"internal: token {old!r} not found in section '{self.key}'. "
                f"index out of sync — run `refresh-index`.")
        if count > 1:
            raise ValueError(
                f"internal: token {old!r} appears {count} times in "
                f"section '{self.key}' — ambiguous patch.")
        self.set_body(self.body.replace(old, new, 1))

    def set_entry_url(self, slug: str, url: str):
        e = self._entry_or_die(slug)
        if not e.ref_nums:
            raise ValueError(f"entry '{slug}' has no refs — can't locate token")
        n = e.ref_nums[0]
        old_tok = f"[[{n}]]({e.url})"
        new_tok = f"[[{n}]]({url})"
        # apply to ALL occurrences of this exact (N, url) token (some entries
        # appear in multiple cells; for layer/sub body it's typically 1 hit)
        if old_tok not in self.body:
            raise ValueError(
                f"entry '{slug}' token {old_tok!r} not in body — "
                f"run refresh-index.")
        self.set_body(self.body.replace(old_tok, new_tok))
        self.conn.execute("UPDATE entries SET url=? WHERE id=?", (url, e.id))

    def set_entry_name(self, slug: str, name: str):
        e = self._entry_or_die(slug)
        if not e.ref_nums:
            raise ValueError(f"entry '{slug}' has no refs")
        n = e.ref_nums[0]
        # token in body: <name>[[N]](url) — match name + immediate `[[N]]`
        old_pat = re.compile(
            r"(?P<name>[^\s|，,、；;（(\[\]]+(?:\s[^\s|，,、；;（(\[\]]+)*)"
            + re.escape(f"[[{n}]]"))
        # we expect exactly one match where group('name') equals e.name (after
        # stripping bold wrap). Find candidates whose name token == e.name.
        target = None
        for m in old_pat.finditer(self.body):
            cand = m.group("name").lstrip("*").rstrip("*").strip()
            if cand == e.name or cand.endswith(e.name):
                target = m; break
        if not target:
            raise ValueError(
                f"could not locate name token for entry '{slug}'. "
                f"Use `section set-body` to edit manually.")
        old_full = target.group(0)
        # preserve bold wrap if present
        prefix = ""
        suffix = ""
        body_name = target.group("name")
        if body_name.startswith("**") and body_name.endswith("**"):
            prefix = "**"; suffix = "**"
            inner = body_name[2:-2]
            old_full = f"{prefix}{inner}[[{n}]]"
            new_full = f"{prefix}{name}{suffix}[[{n}]]"
        else:
            new_full = old_full.replace(e.name, name, 1)
        self._patch_body_unique(old_full, new_full)
        self.conn.execute("UPDATE entries SET name=? WHERE id=?", (name, e.id))

    def set_entry_notes(self, slug: str, notes: str | None):
        e = self._entry_or_die(slug)
        if not e.ref_nums:
            raise ValueError(f"entry '{slug}' has no refs")
        n = e.ref_nums[0]
        anchor = f"[[{n}]]({e.url})" if e.url else f"[[{n}]]"
        idx = self.body.find(anchor)
        if idx < 0:
            raise ValueError(f"anchor {anchor!r} not in body")
        end = idx + len(anchor)
        tail = self.body[end:]
        # Existing parenthetical immediately after?
        m_open = re.match(r"^\s*[（(]", tail)
        if m_open:
            # find matching close
            opener = tail.lstrip()[0]
            closer = "）" if opener == "（" else ")"
            depth = 0; close_idx = None
            scan_start = end + (len(tail) - len(tail.lstrip()))
            for i in range(scan_start, len(self.body)):
                ch = self.body[i]
                if ch == opener:
                    depth += 1
                elif ch == closer:
                    depth -= 1
                    if depth == 0:
                        close_idx = i; break
            if close_idx is None:
                raise ValueError(f"unbalanced parens after {anchor}")
            old_segment = self.body[end:close_idx + 1]
            new_segment = f"（{notes}）" if notes else ""
            self.set_body(self.body[:end] + new_segment +
                          self.body[close_idx + 1:])
        else:
            if not notes:
                pass  # nothing to remove
            else:
                self.set_body(self.body[:end] + f"（{notes}）" + self.body[end:])
        self.conn.execute("UPDATE entries SET notes=? WHERE id=?",
                          (notes, e.id))

    def add_entry(self, vb_label: str | None, name: str, url: str,
                  ref_num: int, notes: str | None = None,
                  separator: str | None = None) -> Entry:
        """Insert a new entry into the body under the given vendor-block
        label. Layout (bullets vs inline) is auto-detected. Returns the
        freshly-indexed Entry."""
        # render the new token
        note_part = f"（{notes}）" if notes else ""
        tok = f"{name}[[{ref_num}]]({url}){note_part}"

        if vb_label is None:
            # append as new bullet at end of body
            new_body = self.body.rstrip() + f"\n- {tok}"
        else:
            new_body = self._insert_in_vendor_block(vb_label, tok, separator)
        self.set_body(new_body)
        # update derived index for just this section
        refresh_section_index(self.conn, self.key)
        # locate the new entry
        slug = slugify(self.layer_code or self.branch_code or self.key, name)
        e = load_entry(self.conn, slug=slug)
        if e is None:
            # slug may have collided; pick most recent matching name in section
            row = self.conn.execute(
                "SELECT slug FROM entries WHERE section_key=? AND name=? "
                "ORDER BY id DESC LIMIT 1", (self.key, name)
            ).fetchone()
            if row:
                e = load_entry(self.conn, slug=row[0])
        return e

    def remove_entry(self, slug: str):
        e = self._entry_or_die(slug)
        if not e.ref_nums:
            raise ValueError(f"entry '{slug}' has no refs")
        n = e.ref_nums[0]
        anchor = f"[[{n}]]({e.url})" if e.url else f"[[{n}]]"
        # find the line containing the anchor
        lines = self.body.split("\n")
        target_idx = None
        for i, ln in enumerate(lines):
            if anchor in ln:
                target_idx = i; break
        if target_idx is None:
            raise ValueError(f"could not locate entry '{slug}' for removal")
        line = lines[target_idx]
        if line.lstrip().startswith(("-", "*")) and line.count("[[") == 1:
            # whole bullet is this single entry → drop the line
            del lines[target_idx]
        else:
            # remove just this entry token + adjacent separator
            new_line = _remove_entry_token(line, e.name, n, e.url, e.notes)
            lines[target_idx] = new_line
        self.set_body("\n".join(lines))
        # delete from index
        self.conn.execute("DELETE FROM entries WHERE id=?", (e.id,))

    # --- internal: insert into vendor block -----------------------------

    def _insert_in_vendor_block(self, vb_label: str, tok: str,
                                separator: str | None) -> str:
        """Locate `**vb_label**：` header in body and append tok. Layout is
        auto-detected: bullets vs inline."""
        # standalone header: `**LBL**：\n - ...` (bullets)
        header_full = f"**{vb_label}**："
        # try halfwidth colon too
        header_alt = f"**{vb_label}**:"
        lines = self.body.split("\n")
        # find header line
        header_idx = None
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s == header_full or s == header_alt:
                header_idx = i; break
            # inline form: header at start of line
            if s.startswith(header_full) or s.startswith(header_alt):
                header_idx = i; break
        if header_idx is None:
            raise KeyError(
                f"vendor-block label '{vb_label}' not found in section "
                f"'{self.key}'. Edit body manually via `section set-body`.")

        header_line = lines[header_idx]
        s = header_line.strip()
        if s == header_full or s == header_alt:
            # bullets layout — find last bullet line in this group
            end = header_idx + 1
            while end < len(lines) and lines[end].lstrip().startswith(("-", "*")):
                end += 1
            insert_at = end
            indent = "- "
            lines.insert(insert_at, f"{indent}{tok}")
            return "\n".join(lines)
        # inline layout — append to header line
        sep = separator or _infer_inline_separator(header_line)
        lines[header_idx] = header_line.rstrip() + sep + tok
        return "\n".join(lines)


def _infer_inline_separator(line: str) -> str:
    # try to detect from existing entry separators
    if "、" in line:
        return "、"
    if " + " in line:
        return " + "
    if ", " in line:
        return ", "
    return "、"


def _remove_entry_token(line: str, name: str, ref_num: int,
                        url: str | None, notes: str | None) -> str:
    """Strip the entry token + an adjoining separator from a single line."""
    note_part = f"（{notes}）" if notes else ""
    suffix = f"[[{ref_num}]]" + (f"({url})" if url else "") + note_part
    # build target substring: name + suffix
    target = name + suffix
    idx = line.find(target)
    if idx < 0:
        # try without notes (notes may have escaped chars)
        target = name + f"[[{ref_num}]]" + (f"({url})" if url else "")
        idx = line.find(target)
        if idx < 0:
            return line  # silent no-op; caller can refresh-index
    # absorb adjoining separator on left (preferred) or right
    seps = ["、", " + ", ", ", "；", "; "]
    before = line[:idx]; after = line[idx + len(target):]
    for sep in seps:
        if before.endswith(sep):
            before = before[:-len(sep)]; break
        if after.startswith(sep):
            after = after[len(sep):]; break
    return before + after


class Layer(_LayerLike):    section_type = "layer"
class SubBranch(_LayerLike): section_type = "subbranch"


class SummaryTable(Section):
    section_type = "summary_table"

    def get_intro(self) -> str:
        """The prose paragraph before the markdown table."""
        for i, line in enumerate(self.body.split("\n")):
            if line.startswith("|"):
                return "\n".join(self.body.split("\n")[:i]).rstrip()
        return self.body.rstrip()

    def set_intro(self, text: str):
        lines = self.body.split("\n")
        table_start = None
        for i, line in enumerate(lines):
            if line.startswith("|"):
                table_start = i; break
        new_body = text.rstrip() + ("\n\n" + "\n".join(lines[table_start:])
                                    if table_start is not None else "")
        self.set_body(new_body)

    def get_cell(self, layer_code: str, branch_code: str) -> str | None:
        row = self.conn.execute(
            "SELECT text FROM cells WHERE layer_code=? AND branch_code=?",
            (layer_code, branch_code)
        ).fetchone()
        return row[0] if row else None

    def set_cell(self, layer_code: str, branch_code: str, text: str | None):
        marker = classify_cell_marker(text or "")
        self.conn.execute(
            "INSERT OR REPLACE INTO cells(layer_code, branch_code, text, marker) "
            "VALUES (?, ?, ?, ?)",
            (layer_code, branch_code, text, marker),
        )
        # rebuild body so render is byte-faithful even if we never re-render
        self._rebuild_table_body()

    def _rebuild_table_body(self):
        """Rebuild the markdown table from cells. Preserve any prose
        before / after the table (intro / outro) from the current body."""
        lines = self.body.split("\n")
        first_tbl = last_tbl = None
        for i, ln in enumerate(lines):
            if ln.startswith("|"):
                if first_tbl is None:
                    first_tbl = i
                last_tbl = i
        intro = "\n".join(lines[:first_tbl]).rstrip() if first_tbl else ""
        outro = "\n".join(lines[last_tbl + 1:]) if last_tbl is not None else ""

        header = "| L | " + " | ".join(f"{c}. {n}" for c, n in MAIN_BRANCHES) + " |"
        sep = "|---|" + "---|" * len(MAIN_BRANCHES)
        rows = [header, sep]
        layers = self.conn.execute(
            "SELECT code, name FROM layers ORDER BY position"
        ).fetchall()
        for code, name in layers:
            cells = {b: "" for b, _ in MAIN_BRANCHES}
            for br, txt in self.conn.execute(
                "SELECT branch_code, text FROM cells WHERE layer_code=?",
                (code,),
            ).fetchall():
                cells[br] = txt or ""
            row_cells = " | ".join(cells[b] for b, _ in MAIN_BRANCHES)
            rows.append(f"| {code} {name} | {row_cells} |")
        new_body = intro + "\n\n" + "\n".join(rows)
        # outro starts at lines[last_tbl+1] — the "\n" between the table row
        # and lines[last_tbl+1] is implicit, so we always add it back here
        if outro:
            new_body += "\n" + outro
        self.set_body(new_body)


class Refs(Section):
    section_type = "refs"

    def next_num(self) -> int:
        row = self.conn.execute(
            "SELECT COALESCE(MAX(num), 0) FROM refs"
        ).fetchone()
        return row[0] + 1

    def add(self, citation: str, url: str | None = None) -> int:
        # Strip the trailing "[Online]. Available: <...>" if user pasted a
        # full IEEE-style citation AND also supplied --url; Ref.render adds
        # this suffix from the url field on its own.
        citation = re.sub(
            r"\s*\[Online\]\.\s+Available:\s*<[^>]+>\s*$", "", citation
        ).strip()
        if url:
            row = self.conn.execute(
                "SELECT num FROM refs WHERE url=?", (url,)
            ).fetchone()
            if row:
                return row[0]
        num = self.next_num()
        self.conn.execute(
            "INSERT INTO refs(num, citation, url) VALUES (?, ?, ?)",
            (num, citation, url),
        )
        self._rebuild_body()
        return num

    def get(self, num: int) -> Ref | None:
        return load_ref(self.conn, num)

    def set(self, num: int, citation: str | None = None, url: str | None = None):
        fields, vals = [], []
        if citation is not None:
            citation = re.sub(
                r"\s*\[Online\]\.\s+Available:\s*<[^>]+>\s*$", "", citation
            ).strip()
            fields.append("citation=?"); vals.append(citation)
        if url is not None:
            fields.append("url=?"); vals.append(url)
        if fields:
            vals.append(num)
            self.conn.execute(
                f"UPDATE refs SET {', '.join(fields)} WHERE num=?", vals)
            self._rebuild_body()

    def remove(self, num: int):
        self.conn.execute("DELETE FROM refs WHERE num=?", (num,))
        self._rebuild_body()

    def _rebuild_body(self):
        rows = self.conn.execute(
            "SELECT num, citation, url FROM refs ORDER BY num"
        ).fetchall()
        rendered = "\n\n".join(
            Ref(num=r[0], citation=r[1], url=r[2]).render() for r in rows
        )
        self.set_body(rendered)


SECTION_CLASSES = {
    "doc_top": DocTop,
    "summary_table": SummaryTable,
    "main_overview": MainOverview,
    "layer": Layer,
    "branch_intro": BranchIntro,
    "branch": Branch,
    "subbranch": SubBranch,
    "crosscut": Crosscut,
    "refs": Refs,
    "other": Other,
}


class Document:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def section(self, key: str) -> Section:
        row = get_section_row(self.conn, key)
        if not row:
            raise KeyError(f"section '{key}' not found")
        return self._instantiate(row)

    def sections(self) -> Iterable[Section]:
        rows = self.conn.execute(
            "SELECT key, position, section_type, heading, body, layer_code, "
            "branch_code FROM sections ORDER BY position"
        ).fetchall()
        for row in rows:
            yield self._instantiate(row)

    def _instantiate(self, row) -> Section:
        key, position, stype, heading, body, lc, bc = row
        cls = SECTION_CLASSES.get(stype, Other)
        return cls(self, key=key, position=position, heading=heading,
                   body=body or "", layer_code=lc, branch_code=bc)

    def entry(self, slug: str) -> Entry | None:
        return load_entry(self.conn, slug=slug)

    def ref(self, num: int) -> Ref | None:
        return load_ref(self.conn, num)

    def render(self) -> str:
        out: list[str] = []
        for s in self.sections():
            out.append(s.render())
        return "".join(out).rstrip() + "\n"

    def commit(self):
        self.conn.commit()


def refresh_section_index(conn: sqlite3.Connection, section_key: str):
    """Rebuild entries for a single section after a body mutation."""
    row = get_section_row(conn, section_key)
    if not row:
        return
    _, _, stype, _, body, lc, bc = row
    if stype not in LAYER_LIKE_TYPES:
        return
    # delete this section's entries (cascade drops entry_refs)
    conn.execute("DELETE FROM entries WHERE section_key=?", (section_key,))
    # rebuild slug_seen by collecting globally-existing slugs
    slug_seen = {r[0] for r in conn.execute(
        "SELECT slug FROM entries").fetchall()}
    index_section_body(conn, section_key, stype, body, lc, bc, slug_seen)


# ---------------------------------------------------------------------------
# migration from legacy `blocks` table

def migrate_from_blocks(conn: sqlite3.Connection):
    cur = conn.cursor()
    has_blocks = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='blocks'"
    ).fetchone()
    if not has_blocks:
        sys.exit("legacy `blocks` table not found — nothing to migrate.")
    conn.execute("PRAGMA foreign_keys = OFF")
    # wipe new tables
    cur.executescript("""
        DELETE FROM entry_refs;
        DELETE FROM entries;
        DELETE FROM cells;
        DELETE FROM refs;
        DELETE FROM layers;
        DELETE FROM branches;
        DELETE FROM sections;
    """)
    rows = cur.execute(
        "SELECT key, order_idx, block_type, title, body, layer_code, "
        "branch_code FROM blocks ORDER BY order_idx"
    ).fetchall()
    for key, order_idx, btype, title, body, lc, bc in rows:
        cur.execute(
            "INSERT INTO sections(key, position, section_type, heading, "
            "body, layer_code, branch_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, order_idx, btype, title, body or "", lc, bc),
        )
    refresh_all_indexes(conn)
    conn.execute("PRAGMA foreign_keys = ON")


# ---------------------------------------------------------------------------
# db lifecycle

def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        sys.exit(f"db not found: {DB_PATH}; run `init`.")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# CLI

def cmd_init(args):
    init_db()
    print(f"initialized {DB_PATH}")


def cmd_migrate(args):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    # drop any leftover v1/v2 tables
    conn.executescript("""
        DROP TABLE IF EXISTS section_parts;
        DROP TABLE IF EXISTS vendor_blocks;
        DROP TABLE IF EXISTS entry_refs;
        DROP TABLE IF EXISTS entries;
        DROP TABLE IF EXISTS refs;
        DROP TABLE IF EXISTS cells;
        DROP TABLE IF EXISTS branch_cells;
        DROP TABLE IF EXISTS layers;
        DROP TABLE IF EXISTS branches;
        DROP TABLE IF EXISTS sections;
        DROP TABLE IF EXISTS sync_meta;
    """)
    conn.executescript(SCHEMA)
    migrate_from_blocks(conn)
    for table in ("sections", "entries", "entry_refs", "refs", "cells",
                  "layers", "branches"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:14s} {n}")
    conn.close()


def cmd_render(args):
    """Render README.md from templates/ + db data via Jinja2.

    Inputs:
      - chat/AISW-stack/templates/readme.md.j2   主模版
      - chat/AISW-stack/templates/_macros.j2      渲染宏
      - chat/AISW-stack/templates/prose/<key>.md  各 section 散文（source of truth）
      - index.sqlite3                              layers / branches / refs / cells /
                                                   sections.body（entries 部分）

    After migration sections.body for layer/subbranch holds ONLY the entries
    markdown (intro prose moved to templates/prose/<key>.md). prose-only
    section types have empty body.
    """
    try:
        import jinja2
    except ModuleNotFoundError:
        sys.exit("jinja2 not installed. Run: .venv/bin/pip install jinja2")
    conn = connect()

    # ---- load data ----------------------------------------------------
    layers = [{"code": r[0], "position": r[1], "name": r[2]}
              for r in conn.execute(
                  "SELECT code, position, name FROM layers ORDER BY position"
              ).fetchall()]
    short_map = {code: name for code, name in MAIN_BRANCHES}
    branches_all = [{"code": r[0], "parent_code": r[1], "position": r[2],
                     "name": r[3], "name_short": short_map.get(r[0], r[3])}
                    for r in conn.execute(
                        "SELECT code, parent_code, position, name FROM branches "
                        "ORDER BY position"
                    ).fetchall()]
    branches = [b for b in branches_all if b["parent_code"] is None]
    sub_branches = [b for b in branches_all if b["parent_code"] is not None]
    refs = [{"num": r[0], "citation": r[1], "url": r[2]}
            for r in conn.execute(
                "SELECT num, citation, url FROM refs ORDER BY num"
            ).fetchall()]
    cells = {(r[0], r[1]): r[2] or "" for r in conn.execute(
        "SELECT layer_code, branch_code, text FROM cells").fetchall()}
    section_body = {r[0]: r[1] or "" for r in conn.execute(
        "SELECT key, body FROM sections").fetchall()}
    section_heading = {r[0]: r[1] or "" for r in conn.execute(
        "SELECT key, heading FROM sections").fetchall()}

    # prose from templates/prose/*.md
    prose = {}
    prose_dir = TEMPLATES_DIR / "prose"
    if prose_dir.exists():
        for p in prose_dir.glob("*.md"):
            prose[p.stem] = p.read_text(encoding="utf-8").rstrip("\n")

    # ---- render -------------------------------------------------------
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=False,
    )
    env.globals["cells"] = cells
    tpl = env.get_template("readme.md.j2")
    md = tpl.render(
        layers=layers,
        branches=branches,
        sub_branches=sub_branches,
        section_body=section_body,
        section_heading=section_heading,
        prose=prose,
        refs=refs,
        cells=cells,
    )
    md = md.rstrip() + "\n"
    MD_PATH.write_text(md, encoding="utf-8")
    print(f"rendered → {MD_PATH}  ({len(md):,} chars)")


def cmd_refresh_index(args):
    conn = connect()
    refresh_all_indexes(conn)
    print("rebuilt entries / refs / cells / layers / branches from sections.body")


def cmd_stats(args):
    conn = connect()
    for table in ("sections", "entries", "entry_refs", "refs", "cells",
                  "layers", "branches"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:14s} {n}")


def cmd_query(args):
    conn = connect()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(args.sql).fetchall()
    except sqlite3.Error as e:
        print(f"sql error: {e}", file=sys.stderr); sys.exit(1)
    if not rows:
        print("(no rows)"); return
    cols = rows[0].keys()
    print("\t".join(cols))
    for r in rows:
        print("\t".join("" if r[c] is None else str(r[c]) for c in cols))


# ---- section subcommands --------------------------------------------------

def cmd_section_list(args):
    conn = connect()
    rows = conn.execute(
        "SELECT position, key, section_type, heading FROM sections "
        "ORDER BY position"
    ).fetchall()
    for r in rows:
        print(f"{r[0]:3d}  {r[1]:18s}  {r[2]:14s}  {r[3] or ''}")


def cmd_section_show(args):
    conn = connect()
    row = get_section_row(conn, args.key)
    if not row:
        sys.exit(f"section '{args.key}' not found")
    key, position, stype, heading, body, lc, bc = row
    print(f"key={key}  type={stype}  position={position}")
    print(f"heading={heading!r}")
    print(f"layer_code={lc}  branch_code={bc}")
    print(f"body ({len(body)} chars):")
    print("-" * 60)
    print(body)


def cmd_section_set_heading(args):
    conn = connect()
    doc = Document(conn)
    s = doc.section(args.key)
    s.set_heading(args.heading)
    doc.commit()
    print(f"set heading of '{args.key}' → {args.heading!r}")


def cmd_section_set_body(args):
    conn = connect()
    doc = Document(conn)
    s = doc.section(args.key)
    if s.section_type in PROSE_ONLY_TYPES or s.section_type == "summary_table":
        sys.exit(
            f"section '{args.key}' is prose-only — its body lives in "
            f"chat/AISW-stack/templates/prose/{args.key}.md. "
            f"Edit that file directly, then `render`."
        )
    if s.section_type == "refs":
        sys.exit("refs body is rebuilt from the refs table — use `ref add` / "
                 "`ref set` / `ref remove`.")
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8").rstrip()
    elif args.body is not None:
        body = args.body
    else:
        body = sys.stdin.read().rstrip()
    s.set_body(body)
    if s.section_type in LAYER_LIKE_TYPES:
        refresh_section_index(conn, args.key)
    doc.commit()
    print(f"set body of '{args.key}' ({len(body)} chars)")


# ---- prose subcommands ----------------------------------------------------

def cmd_prose_list(args):
    """List prose templates that exist on disk."""
    prose_dir = TEMPLATES_DIR / "prose"
    if not prose_dir.exists():
        sys.exit(f"prose dir not found: {prose_dir}")
    for p in sorted(prose_dir.glob("*.md")):
        size = p.stat().st_size
        first = p.read_text(encoding="utf-8").splitlines()[:1]
        snippet = first[0][:60] if first else ""
        print(f"{p.stem:18s} {size:5d}  {snippet}")


def cmd_prose_path(args):
    """Print the absolute path of a prose file for a given section key."""
    p = TEMPLATES_DIR / "prose" / f"{args.key}.md"
    print(p)


def cmd_prose_show(args):
    """Dump the contents of a prose template file."""
    p = TEMPLATES_DIR / "prose" / f"{args.key}.md"
    if not p.exists():
        sys.exit(f"prose file not found: {p}")
    sys.stdout.write(p.read_text(encoding="utf-8"))


# ---- entry subcommands ----------------------------------------------------

def cmd_entry_list(args):
    conn = connect()
    sql = ("SELECT slug, name, vendor, layer_code, branch_code, url "
           "FROM entries WHERE 1=1")
    params = []
    if args.section: sql += " AND section_key=?"; params.append(args.section)
    if args.layer:   sql += " AND layer_code=?";  params.append(args.layer)
    if args.branch:  sql += " AND branch_code=?"; params.append(args.branch)
    if args.vendor:  sql += " AND vendor=?";      params.append(args.vendor)
    sql += " ORDER BY layer_code, branch_code, position"
    for slug, name, vendor, lc, bc, url in conn.execute(sql, params).fetchall():
        print(f"{slug:40s}  {(lc or bc or ''):4s}  {vendor or '':12s}  {name}  {url or ''}")


def cmd_entry_show(args):
    conn = connect()
    doc = Document(conn)
    e = doc.entry(args.slug)
    if not e:
        sys.exit(f"entry slug='{args.slug}' not found")
    print(f"slug={e.slug}")
    print(f"name={e.name!r}")
    print(f"url={e.url}")
    print(f"section={e.section_key}  layer={e.layer_code}  branch={e.branch_code}")
    print(f"vendor={e.vendor}  category={e.category}")
    print(f"notes={e.notes!r}")
    print(f"refs={e.ref_nums}")


def cmd_entry_set_url(args):
    conn = connect()
    doc = Document(conn)
    e = doc.entry(args.slug)
    if not e:
        sys.exit(f"entry '{args.slug}' not found")
    s = doc.section(e.section_key)
    if not isinstance(s, _LayerLike):
        sys.exit(f"entry's section is not Layer/SubBranch — can't patch body")
    s.set_entry_url(args.slug, args.url)
    doc.commit()
    print(f"set url of '{args.slug}' → {args.url}")


def cmd_entry_set_name(args):
    conn = connect()
    doc = Document(conn)
    e = doc.entry(args.slug)
    if not e:
        sys.exit(f"entry '{args.slug}' not found")
    s = doc.section(e.section_key)
    if not isinstance(s, _LayerLike):
        sys.exit("entry's section is not Layer/SubBranch")
    s.set_entry_name(args.slug, args.name)
    refresh_section_index(conn, e.section_key)
    doc.commit()
    print(f"set name of '{args.slug}' → {args.name!r}")


def cmd_entry_set_notes(args):
    conn = connect()
    doc = Document(conn)
    e = doc.entry(args.slug)
    if not e:
        sys.exit(f"entry '{args.slug}' not found")
    s = doc.section(e.section_key)
    if not isinstance(s, _LayerLike):
        sys.exit("entry's section is not Layer/SubBranch")
    s.set_entry_notes(args.slug, args.notes)
    doc.commit()
    print(f"set notes of '{args.slug}' → {args.notes!r}")


def cmd_entry_add(args):
    conn = connect()
    doc = Document(conn)
    s = doc.section(args.section_key)
    if not isinstance(s, _LayerLike):
        sys.exit(f"section '{args.section_key}' is not Layer/SubBranch")
    e = s.add_entry(args.vb_label, args.name, args.url, args.ref,
                    notes=args.notes, separator=args.separator)
    doc.commit()
    if e:
        print(f"added entry slug={e.slug} → {e.name}[[{args.ref}]]({args.url})")
    else:
        print("entry inserted but index lookup didn't find it; run refresh-index")


def cmd_entry_remove(args):
    conn = connect()
    doc = Document(conn)
    e = doc.entry(args.slug)
    if not e:
        sys.exit(f"entry '{args.slug}' not found")
    s = doc.section(e.section_key)
    if not isinstance(s, _LayerLike):
        sys.exit("entry's section is not Layer/SubBranch")
    s.remove_entry(args.slug)
    doc.commit()
    print(f"removed entry '{args.slug}'")


# ---- ref subcommands ------------------------------------------------------

def cmd_ref_list(args):
    conn = connect()
    if args.orphan:
        rows = conn.execute("""
            SELECT r.num, r.url FROM refs r
            LEFT JOIN entry_refs er ON r.num = er.ref_num
            WHERE er.entry_id IS NULL ORDER BY r.num
        """).fetchall()
    else:
        rows = conn.execute(
            "SELECT num, url, citation FROM refs ORDER BY num"
        ).fetchall()
    for r in rows:
        print("\t".join("" if v is None else str(v) for v in r))


def cmd_ref_show(args):
    conn = connect()
    doc = Document(conn)
    r = doc.ref(args.num)
    if not r:
        sys.exit(f"ref [{args.num}] not found")
    print(r.render())


def cmd_ref_add(args):
    conn = connect()
    doc = Document(conn)
    refs = doc.section("refs")
    num = refs.add(args.citation, args.url)
    doc.commit()
    print(num)


def cmd_ref_set(args):
    conn = connect()
    doc = Document(conn)
    refs = doc.section("refs")
    refs.set(args.num, args.citation, args.url)
    doc.commit()
    print(f"updated ref [{args.num}]")


def cmd_ref_remove(args):
    conn = connect()
    doc = Document(conn)
    refs = doc.section("refs")
    refs.remove(args.num)
    doc.commit()
    print(f"removed ref [{args.num}]")


def cmd_ref_next(args):
    conn = connect()
    doc = Document(conn)
    refs = doc.section("refs")
    print(refs.next_num())


# ---- cell subcommands -----------------------------------------------------

def cmd_cell_get(args):
    conn = connect()
    doc = Document(conn)
    summary = doc.section("summary-table")
    text = summary.get_cell(args.layer, args.branch)
    print(text if text is not None else "(empty)")


def cmd_cell_set(args):
    conn = connect()
    doc = Document(conn)
    summary = doc.section("summary-table")
    summary.set_cell(args.layer, args.branch, args.text)
    doc.commit()
    print(f"set cell ({args.layer}, {args.branch}) → {args.text!r}")


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("migrate-from-blocks").set_defaults(func=cmd_migrate)
    sub.add_parser("render").set_defaults(func=cmd_render)
    sub.add_parser("refresh-index").set_defaults(func=cmd_refresh_index)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    pq = sub.add_parser("query"); pq.add_argument("sql")
    pq.set_defaults(func=cmd_query)

    # section
    ps = sub.add_parser("section")
    pss = ps.add_subparsers(dest="section_cmd", required=True)
    pss.add_parser("list").set_defaults(func=cmd_section_list)
    psh = pss.add_parser("show"); psh.add_argument("key")
    psh.set_defaults(func=cmd_section_show)
    pH = pss.add_parser("set-heading"); pH.add_argument("key")
    pH.add_argument("--heading", required=True)
    pH.set_defaults(func=cmd_section_set_heading)
    pB = pss.add_parser("set-body"); pB.add_argument("key")
    pB.add_argument("--body"); pB.add_argument("--file")
    pB.set_defaults(func=cmd_section_set_body)

    # prose
    pp = sub.add_parser("prose")
    pps = pp.add_subparsers(dest="prose_cmd", required=True)
    pps.add_parser("list").set_defaults(func=cmd_prose_list)
    ppp = pps.add_parser("path"); ppp.add_argument("key")
    ppp.set_defaults(func=cmd_prose_path)
    ppsh = pps.add_parser("show"); ppsh.add_argument("key")
    ppsh.set_defaults(func=cmd_prose_show)

    # entry
    pe = sub.add_parser("entry")
    pes = pe.add_subparsers(dest="entry_cmd", required=True)
    pel = pes.add_parser("list")
    pel.add_argument("--section"); pel.add_argument("--layer")
    pel.add_argument("--branch");  pel.add_argument("--vendor")
    pel.set_defaults(func=cmd_entry_list)
    peshow = pes.add_parser("show"); peshow.add_argument("slug")
    peshow.set_defaults(func=cmd_entry_show)
    pea = pes.add_parser("add"); pea.add_argument("section_key")
    pea.add_argument("--vb-label", dest="vb_label")
    pea.add_argument("--name", required=True)
    pea.add_argument("--url", required=True)
    pea.add_argument("--ref", type=int, required=True)
    pea.add_argument("--notes")
    pea.add_argument("--separator")
    pea.set_defaults(func=cmd_entry_add)
    per = pes.add_parser("remove"); per.add_argument("slug")
    per.set_defaults(func=cmd_entry_remove)
    peu = pes.add_parser("set-url"); peu.add_argument("slug")
    peu.add_argument("--url", required=True)
    peu.set_defaults(func=cmd_entry_set_url)
    pen = pes.add_parser("set-name"); pen.add_argument("slug")
    pen.add_argument("--name", required=True)
    pen.set_defaults(func=cmd_entry_set_name)
    pet = pes.add_parser("set-notes"); pet.add_argument("slug")
    pet.add_argument("--notes")
    pet.set_defaults(func=cmd_entry_set_notes)

    # ref
    pr = sub.add_parser("ref")
    prs = pr.add_subparsers(dest="ref_cmd", required=True)
    prl = prs.add_parser("list"); prl.add_argument("--orphan", action="store_true")
    prl.set_defaults(func=cmd_ref_list)
    prsh = prs.add_parser("show"); prsh.add_argument("num", type=int)
    prsh.set_defaults(func=cmd_ref_show)
    pra = prs.add_parser("add"); pra.add_argument("--citation", required=True)
    pra.add_argument("--url"); pra.set_defaults(func=cmd_ref_add)
    prset = prs.add_parser("set"); prset.add_argument("num", type=int)
    prset.add_argument("--citation"); prset.add_argument("--url")
    prset.set_defaults(func=cmd_ref_set)
    prrm = prs.add_parser("remove"); prrm.add_argument("num", type=int)
    prrm.set_defaults(func=cmd_ref_remove)
    prs.add_parser("next-num").set_defaults(func=cmd_ref_next)

    # cell
    pc = sub.add_parser("cell")
    pcs = pc.add_subparsers(dest="cell_cmd", required=True)
    pcg = pcs.add_parser("get"); pcg.add_argument("layer")
    pcg.add_argument("branch"); pcg.set_defaults(func=cmd_cell_get)
    pcset = pcs.add_parser("set"); pcset.add_argument("layer")
    pcset.add_argument("branch"); pcset.add_argument("--text", required=True)
    pcset.set_defaults(func=cmd_cell_set)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
