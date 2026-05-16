#!/usr/bin/env python3
"""AISW-stack MVC Controller。

架构：
  Model       chat/AISW-stack/index.sqlite3   （source of truth）
  View        chat/AISW-stack/README.md        （由 Model 单向渲染）
  Controller  scripts/aiswstack_controller.py （本文件）

单向流：所有内容修改都通过本 Controller 进入 db。README.md 是只读
渲染产物——不要手工编辑它，因为没有任何反向同步路径，下次 render
就会把人工改动覆盖掉。

Model 的核心是 `blocks` 表——存按 ## / ### 拆段后的 markdown 切片。
其他表（layers / branches / entries / refs / branch_cells / entry_refs）
是 render 时从 `blocks` 自动派生的查询索引，**不要直接 UPDATE / INSERT
它们**，会在下次 render 时被覆盖。

子命令：
  init                          新建空 schema
  render                        派生索引 + 写 README.md（每次改完都跑）
  stats                         表行数
  next-ref                      返回下一个可用引用号（max + 1）
  query SQL                     执行任意 SQL（推荐只读 SELECT）

  add-block KEY [..]            新建 block（自动 shift order_idx）
  delete-block KEY              删除 block（自动 shift）
  replace KEY --old X --new Y   在 block.body 中替换字符串
  append KEY --text "..."       追加到 block.body 末尾
  add-ref --citation "..."      追加引用到 refs block；输出新 ref 号

需要改本 Controller 代码的场景（结构性调整）：
  - 新增主分支（A–I 之外的顶级列）：MAIN_BRANCHES 与主表渲染逻辑
  - 改变 block 切分粒度或新 block_type：derive_indexes / render
  - 新增 vendor 白名单：KNOWN_VENDORS / VENDOR_ALIASES
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "chat/AISW-stack/README.md"
DB_PATH = ROOT / "chat/AISW-stack/index.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS blocks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT NOT NULL UNIQUE,
    order_idx   INTEGER NOT NULL,
    block_type  TEXT NOT NULL,
    title       TEXT,
    body        TEXT NOT NULL,
    layer_code  TEXT,
    branch_code TEXT
);

CREATE TABLE IF NOT EXISTS layers (
    code        TEXT PRIMARY KEY,
    position    INTEGER NOT NULL,
    name        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    code         TEXT PRIMARY KEY,
    parent_code  TEXT,
    position     INTEGER NOT NULL,
    name         TEXT NOT NULL,
    FOREIGN KEY (parent_code) REFERENCES branches(code)
);

CREATE TABLE IF NOT EXISTS refs (
    num      INTEGER PRIMARY KEY,
    citation TEXT NOT NULL,
    url      TEXT
);

CREATE TABLE IF NOT EXISTS entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    url          TEXT,
    layer_code   TEXT,
    branch_code  TEXT,
    vendor       TEXT,
    category     TEXT,
    notes        TEXT,
    block_key    TEXT,
    source_line  INTEGER,
    FOREIGN KEY (layer_code)  REFERENCES layers(code),
    FOREIGN KEY (branch_code) REFERENCES branches(code),
    FOREIGN KEY (block_key)   REFERENCES blocks(key)
);

CREATE TABLE IF NOT EXISTS entry_refs (
    entry_id  INTEGER NOT NULL,
    ref_num   INTEGER NOT NULL,
    PRIMARY KEY (entry_id, ref_num),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (ref_num)  REFERENCES refs(num)
);

CREATE TABLE IF NOT EXISTS branch_cells (
    layer_code   TEXT NOT NULL,
    branch_code  TEXT NOT NULL,
    raw_text     TEXT,
    marker       TEXT,
    PRIMARY KEY (layer_code, branch_code),
    FOREIGN KEY (layer_code)  REFERENCES layers(code),
    FOREIGN KEY (branch_code) REFERENCES branches(code)
);

CREATE TABLE IF NOT EXISTS sync_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_layer  ON entries(layer_code);
CREATE INDEX IF NOT EXISTS idx_entries_branch ON entries(branch_code);
CREATE INDEX IF NOT EXISTS idx_entries_vendor ON entries(vendor);
CREATE INDEX IF NOT EXISTS idx_entries_block  ON entries(block_key);
CREATE INDEX IF NOT EXISTS idx_entry_refs_ref ON entry_refs(ref_num);
CREATE INDEX IF NOT EXISTS idx_blocks_order   ON blocks(order_idx);
"""


# ---------------------------------------------------------------------------
# constants & helpers

_PUNCT_RE = re.compile(r"[\s/（）()，,、；;:：&+]+")
_DECO_RE = re.compile(r"[*_`\"'·]")
SEP_CHARS = "、，,；;|。：:"
NAME_SPLIT_RE = re.compile(r"[" + re.escape(SEP_CHARS) + r"]|(?<=[）)\s])\+\s")
REF_LINK_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^\s)]+)\)")
REF_ENTRY_RE = re.compile(
    r"^\[(\d+)\]\s+(.+?)(?:\s*\[Online\]\.\s+Available:\s*<([^>]+)>)?\s*$"
)
LAYER_TITLE_RE = re.compile(r"^(L\d{2})\s+(.+)$")
BRANCH_TITLE_RE = re.compile(r"^([A-I](?:\d+)?)\s+(.+)$")
VENDOR_BLOCK_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*$")
GROUP_LABEL_RE = re.compile(r"^[-*]\s+\*\*([^*]+)\*\*[:：]\s*(.*)$")
BARE_VENDOR_RE = re.compile(r"^[-*]\s+([^*：:\[]{1,24}?)[：:]\s*(.+)$")

KNOWN_VENDORS = {
    "NVIDIA", "AMD", "Intel", "Apple", "AWS", "Google", "Microsoft", "Meta",
    "Anthropic", "OpenAI", "xAI", "DeepSeek", "Mistral", "Cohere",
    "Databricks", "Snowflake", "Cloudflare", "HuggingFace", "Hugging Face",
    "IBM", "Oracle", "SAP", "Salesforce", "ServiceNow", "Workday",
    "华为", "华为昇腾", "阿里", "百度", "腾讯", "字节",
    "高通", "Qualcomm", "联发科", "MediaTek", "瑞芯微", "Rockchip",
}

VENDOR_ALIASES = {"华为昇腾": "华为", "Hugging Face": "HuggingFace"}

MAIN_BRANCHES = [
    ("A", "LLM / Agent"), ("B", "科学计算"), ("C", "机器人"),
    ("D", "自动驾驶"), ("E", "世界模型 / 3D"), ("F", "经典 CV"),
    ("G", "量化金融"), ("H", "游戏"), ("I", "影视娱乐"),
]


def canonical_vendor(label: str) -> str | None:
    plain = re.sub(r"（[^）]*）|\([^)]*\)", "", label).strip()
    if plain in KNOWN_VENDORS:
        return VENDOR_ALIASES.get(plain, plain)
    return None


def slugify(prefix: str, name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = _DECO_RE.sub("", s)
    s = _PUNCT_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    if not s:
        s = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return f"{prefix.lower()}-{s}"


def clean_name(s: str) -> str:
    s = _DECO_RE.sub("", s)
    s = re.sub(r"^[\s\-+]+|[\s\-+:：]+$", "", s)
    return s.strip()


def is_valid_name(name: str) -> bool:
    if not name:
        return False
    if name.startswith(("//", ")", "）", "/")):
        return False
    if "://" in name:
        return False
    if re.fullmatch(r"[（(].*[）)]", name):
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


def extract_entries_from_text(text: str):
    out = []
    for m in REF_LINK_RE.finditer(text):
        ref_num = int(m.group(1))
        url = m.group(2)
        before = text[:m.start()]
        parts = NAME_SPLIT_RE.split(before)
        raw_name = parts[-1] if parts else ""
        name = clean_name(raw_name)
        if not is_valid_name(name):
            continue
        notes = extract_trailing_notes(text, m.end())
        out.append({"name": name, "url": url, "ref": ref_num, "notes": notes})
    return out


def classify_cell(text: str) -> str:
    t = text.strip()
    if t in ("—", "-", "–"):
        return "none"
    if t.startswith("同 A"):
        return "same_a"
    if t.startswith("与 ") and "共用" in t:
        return "shared"
    return "normal"


# ---------------------------------------------------------------------------
# derive indexes (blocks → layers / branches / refs / entries / cells)

def derive_indexes(blocks: list[dict]) -> dict:
    layers: dict[str, dict] = {}
    branches: dict[str, dict] = {b: {"code": b, "name": n, "parent": None, "pos": i}
                                  for i, (b, n) in enumerate(MAIN_BRANCHES, 1)}
    refs: dict[int, dict] = {}
    entries: dict[str, dict] = {}
    entry_refs: set[tuple[str, int]] = set()
    branch_cells: list[dict] = []
    sub_pos = 100

    for blk in blocks:
        if blk["block_type"] == "layer" and blk["title"]:
            m = LAYER_TITLE_RE.match(blk["title"])
            if m:
                lc, lname = m.group(1), m.group(2).strip()
                layers[lc] = {"code": lc, "position": int(lc[1:]), "name": lname}
        elif blk["block_type"] in ("branch", "subbranch") and blk["title"]:
            m = BRANCH_TITLE_RE.match(blk["title"])
            if m:
                code, bname = m.group(1), m.group(2).strip()
                parent = code[0] if len(code) > 1 else None
                branches[code] = {
                    "code": code, "name": bname, "parent": parent,
                    "pos": sub_pos,
                }
                sub_pos += 1

    for blk in blocks:
        body = blk["body"]
        if blk["block_type"] == "refs":
            for line in body.split("\n"):
                m = REF_ENTRY_RE.match(line)
                if m:
                    refs[int(m.group(1))] = {
                        "num": int(m.group(1)),
                        "citation": m.group(2).strip(),
                        "url": m.group(3),
                    }
            continue
        if blk["block_type"] == "summary_table":
            parse_summary_table_cells(body, layers, branch_cells)
            continue

        layer_code = blk.get("layer_code")
        branch_code = blk.get("branch_code")
        if not layer_code and not branch_code:
            continue
        parse_block_entries(blk, layer_code, branch_code,
                            entries, entry_refs)

    return {
        "layers": layers, "branches": branches, "refs": refs,
        "entries": entries, "entry_refs": list(entry_refs),
        "branch_cells": branch_cells,
    }


def parse_summary_table_cells(body: str, layers: dict, branch_cells: list):
    for line in body.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not re.match(r"^L\d{2}\b", cells[0]):
            continue
        m = re.match(r"^(L\d{2})\s+(.+)$", cells[0])
        if not m:
            continue
        lc, lname = m.group(1), m.group(2).strip()
        layers.setdefault(lc, {"code": lc, "position": int(lc[1:]), "name": lname})
        for i, raw_cell in enumerate(cells[1:]):
            if i >= len(MAIN_BRANCHES):
                break
            bcode = MAIN_BRANCHES[i][0]
            branch_cells.append({
                "layer": lc, "branch": bcode,
                "raw": raw_cell, "marker": classify_cell(raw_cell),
            })


def parse_block_entries(blk: dict, layer_code: str | None,
                        branch_code: str | None,
                        entries: dict, entry_refs: set):
    body = blk["body"]
    block_key = blk["key"]
    state_vendor = None
    state_category = None
    slug_prefix = layer_code or branch_code
    if not slug_prefix:
        return
    for ln_idx, line in enumerate(body.split("\n"), 1):
        m = VENDOR_BLOCK_RE.match(line)
        if m:
            label = m.group(1).strip()
            cv = canonical_vendor(label)
            if cv:
                state_vendor, state_category = cv, None
            else:
                state_category, state_vendor = label, None
            continue
        if not REF_LINK_RE.search(line):
            continue
        local_vendor = state_vendor
        local_category = state_category
        rest = line
        if line.lstrip().startswith(("-", "*")):
            rest = line.lstrip()[1:].strip()
            m = GROUP_LABEL_RE.match(line)
            if m:
                label = m.group(1).strip()
                if (cv := canonical_vendor(label)):
                    local_vendor = cv
                local_category = label
                rest = m.group(2)
            else:
                m2 = BARE_VENDOR_RE.match(line)
                if m2 and (cv := canonical_vendor(m2.group(1).strip())):
                    local_vendor = cv
                    rest = m2.group(2)
        for e in extract_entries_from_text(rest):
            slug = slugify(slug_prefix, e["name"])
            if slug not in entries:
                entries[slug] = {
                    "slug": slug, "name": e["name"], "url": e["url"],
                    "layer": layer_code, "branch": branch_code,
                    "vendor": local_vendor, "category": local_category,
                    "notes": e["notes"], "block_key": block_key,
                    "source_line": ln_idx,
                }
            entry_refs.add((slug, e["ref"]))


# ---------------------------------------------------------------------------
# db io

def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        sys.exit(f"db not found: {DB_PATH}; run `init` first.")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def read_blocks(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT key, order_idx, block_type, title, body, layer_code, branch_code "
        "FROM blocks ORDER BY order_idx"
    ).fetchall()
    return [
        {"key": r[0], "order_idx": r[1], "block_type": r[2],
         "title": r[3], "body": r[4],
         "layer_code": r[5], "branch_code": r[6]}
        for r in rows
    ]


def write_derived(conn, data: dict):
    cur = conn.cursor()
    cur.executescript(
        "DELETE FROM entry_refs; DELETE FROM entries;"
        "DELETE FROM branch_cells; DELETE FROM refs;"
        "DELETE FROM branches; DELETE FROM layers;"
    )
    for l in sorted(data["layers"].values(), key=lambda x: x["position"]):
        cur.execute(
            "INSERT INTO layers(code, position, name) VALUES (?, ?, ?)",
            (l["code"], l["position"], l["name"]),
        )
    for b in sorted(data["branches"].values(), key=lambda x: x["pos"]):
        cur.execute(
            "INSERT INTO branches(code, parent_code, position, name) "
            "VALUES (?, ?, ?, ?)",
            (b["code"], b.get("parent"), b["pos"], b["name"]),
        )
    for r in data["refs"].values():
        cur.execute(
            "INSERT INTO refs(num, citation, url) VALUES (?, ?, ?)",
            (r["num"], r["citation"], r["url"]),
        )
    slug_to_id: dict[str, int] = {}
    for slug, e in data["entries"].items():
        cur.execute(
            "INSERT INTO entries(slug, name, url, layer_code, branch_code, "
            "vendor, category, notes, block_key, source_line) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slug, e["name"], e["url"], e.get("layer"), e.get("branch"),
             e.get("vendor"), e.get("category"), e.get("notes"),
             e.get("block_key"), e.get("source_line")),
        )
        slug_to_id[slug] = cur.lastrowid
    for slug, ref_num in data["entry_refs"]:
        if slug not in slug_to_id or ref_num not in data["refs"]:
            continue
        cur.execute(
            "INSERT OR IGNORE INTO entry_refs(entry_id, ref_num) VALUES (?, ?)",
            (slug_to_id[slug], ref_num),
        )
    for c in data["branch_cells"]:
        if c["layer"] not in data["layers"] or c["branch"] not in data["branches"]:
            continue
        cur.execute(
            "INSERT INTO branch_cells(layer_code, branch_code, raw_text, marker) "
            "VALUES (?, ?, ?, ?)",
            (c["layer"], c["branch"], c["raw"], c["marker"]),
        )
    cur.execute(
        "INSERT OR REPLACE INTO sync_meta(key, value) VALUES (?, ?)",
        ("last_render_ts", str(int(time.time()))),
    )
    conn.commit()


def rebuild_derived(conn):
    blocks = read_blocks(conn)
    data = derive_indexes(blocks)
    write_derived(conn, data)
    return data


def render_md(conn) -> str:
    rows = conn.execute(
        "SELECT block_type, title, body FROM blocks ORDER BY order_idx"
    ).fetchall()
    parts: list[str] = []
    for btype, title, body in rows:
        if btype == "doc_top":
            parts.append(body)
            continue
        prefix = "###" if btype in ("branch", "subbranch") else "##"
        parts.append(f"\n\n{prefix} {title}\n\n{body}")
    return "".join(parts).rstrip() + "\n"


# ---------------------------------------------------------------------------
# block mutators

def get_block_body(conn, key: str) -> str | None:
    row = conn.execute("SELECT body FROM blocks WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def get_block_row(conn, key: str):
    return conn.execute(
        "SELECT order_idx FROM blocks WHERE key=?", (key,)
    ).fetchone()


def cmd_add_block(args):
    conn = connect()
    cur = conn.cursor()
    if cur.execute("SELECT 1 FROM blocks WHERE key=?", (args.key,)).fetchone():
        sys.exit(f"block '{args.key}' already exists")

    if args.after:
        row = cur.execute("SELECT order_idx FROM blocks WHERE key=?",
                          (args.after,)).fetchone()
        if not row:
            sys.exit(f"--after key '{args.after}' not found")
        new_order = row[0] + 1
    elif args.before:
        row = cur.execute("SELECT order_idx FROM blocks WHERE key=?",
                          (args.before,)).fetchone()
        if not row:
            sys.exit(f"--before key '{args.before}' not found")
        new_order = row[0]
    else:
        row = cur.execute(
            "SELECT COALESCE(MAX(order_idx), -1) FROM blocks"
        ).fetchone()
        new_order = row[0] + 1

    cur.execute(
        "UPDATE blocks SET order_idx = order_idx + 1 WHERE order_idx >= ?",
        (new_order,),
    )
    cur.execute(
        "INSERT INTO blocks(key, order_idx, block_type, title, body, "
        "layer_code, branch_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (args.key, new_order, args.type, args.title, args.body or "",
         args.layer_code, args.branch_code),
    )
    conn.commit()
    print(f"added block '{args.key}' at order_idx={new_order}")


def cmd_delete_block(args):
    conn = connect()
    row = conn.execute("SELECT order_idx FROM blocks WHERE key=?",
                       (args.key,)).fetchone()
    if not row:
        sys.exit(f"block '{args.key}' not found")
    conn.execute("DELETE FROM blocks WHERE key=?", (args.key,))
    conn.execute("UPDATE blocks SET order_idx = order_idx - 1 WHERE order_idx > ?",
                 (row[0],))
    conn.commit()
    print(f"deleted block '{args.key}'")


def cmd_replace(args):
    conn = connect()
    body = get_block_body(conn, args.key)
    if body is None:
        sys.exit(f"block '{args.key}' not found")
    count = body.count(args.old)
    if count == 0:
        sys.exit(f"--old text not found in block '{args.key}'")
    if count > 1 and not args.all:
        sys.exit(f"--old appears {count} times in '{args.key}'; "
                 f"use --all to replace all, or include more context.")
    new_body = body.replace(args.old, args.new, -1 if args.all else 1)
    conn.execute("UPDATE blocks SET body=? WHERE key=?", (new_body, args.key))
    conn.commit()
    print(f"replaced {count if args.all else 1} occurrence(s) in '{args.key}'")


def cmd_append(args):
    conn = connect()
    body = get_block_body(conn, args.key)
    if body is None:
        sys.exit(f"block '{args.key}' not found")
    new_body = body.rstrip("\n") + "\n" + args.text
    conn.execute("UPDATE blocks SET body=? WHERE key=?", (new_body, args.key))
    conn.commit()
    print(f"appended {len(args.text)} chars to '{args.key}'")


def cmd_add_ref(args):
    """追加 [N] citation 行到 refs block，返回新 ref 号。"""
    conn = connect()
    body = get_block_body(conn, "refs")
    if body is None:
        sys.exit("refs block not found")
    nums = [int(m.group(1)) for m in re.finditer(r"^\[(\d+)\]", body, re.MULTILINE)]
    next_num = max(nums) + 1 if nums else 1
    new_line = f"\n\n[{next_num}] {args.citation}"
    new_body = body.rstrip("\n") + new_line
    conn.execute("UPDATE blocks SET body=? WHERE key='refs'", (new_body,))
    conn.commit()
    print(next_num)


# ---------------------------------------------------------------------------
# read-only commands

def cmd_init(args):
    init_db()
    print(f"initialized {DB_PATH}")


def cmd_render(args):
    conn = connect()
    data = rebuild_derived(conn)
    md = render_md(conn)
    MD_PATH.write_text(md, encoding="utf-8")
    rows = conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
    print(
        f"rendered {rows} blocks → {MD_PATH}\n"
        f"  layers={len(data['layers'])} branches={len(data['branches'])} "
        f"entries={len(data['entries'])} refs={len(data['refs'])} "
        f"cells={len(data['branch_cells'])}"
    )


def cmd_stats(args):
    conn = connect()
    for table in ("blocks", "layers", "branches", "entries", "entry_refs",
                  "refs", "branch_cells"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:18s} {n}")


def cmd_query(args):
    conn = connect()
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(args.sql).fetchall()
    except sqlite3.Error as e:
        print(f"sql error: {e}", file=sys.stderr)
        sys.exit(1)
    if not rows:
        if args.sql.strip().lower().startswith("select"):
            print("(no rows)")
        else:
            conn.commit()
        return
    cols = rows[0].keys()
    print("\t".join(cols))
    for r in rows:
        print("\t".join("" if r[c] is None else str(r[c]) for c in cols))


def cmd_next_ref(args):
    conn = connect()
    body = get_block_body(conn, "refs")
    if body is None:
        sys.exit("refs block not found")
    nums = [int(m.group(1)) for m in re.finditer(r"^\[(\d+)\]", body, re.MULTILINE)]
    print(max(nums) + 1 if nums else 1)


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("render").set_defaults(func=cmd_render)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sub.add_parser("next-ref").set_defaults(func=cmd_next_ref)

    pq = sub.add_parser("query")
    pq.add_argument("sql")
    pq.set_defaults(func=cmd_query)

    pa = sub.add_parser("add-block")
    pa.add_argument("key")
    pa.add_argument("--type", required=True,
                    choices=["doc_top", "summary_table", "main_overview",
                             "layer", "branch_intro", "branch", "subbranch",
                             "crosscut", "refs", "other"])
    pa.add_argument("--title", default=None,
                    help="excluding '## ' or '### ' prefix; None for doc_top")
    pa.add_argument("--body", default="")
    pa.add_argument("--layer-code", default=None)
    pa.add_argument("--branch-code", default=None)
    g = pa.add_mutually_exclusive_group()
    g.add_argument("--after", help="insert after this block key")
    g.add_argument("--before", help="insert before this block key")
    pa.set_defaults(func=cmd_add_block)

    pd = sub.add_parser("delete-block")
    pd.add_argument("key")
    pd.set_defaults(func=cmd_delete_block)

    pr = sub.add_parser("replace")
    pr.add_argument("key", help="block key")
    pr.add_argument("--old", required=True)
    pr.add_argument("--new", required=True)
    pr.add_argument("--all", action="store_true",
                    help="replace all occurrences (default: require unique)")
    pr.set_defaults(func=cmd_replace)

    pap = sub.add_parser("append")
    pap.add_argument("key", help="block key")
    pap.add_argument("--text", required=True)
    pap.set_defaults(func=cmd_append)

    par = sub.add_parser("add-ref")
    par.add_argument("--citation", required=True,
                     help="IEEE-style citation, excluding [N] prefix")
    par.set_defaults(func=cmd_add_ref)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
