#!/usr/bin/env python3
"""AISW-stack sqlite3 索引与 README.md 生成工具。

数据源：chat/AISW-stack/index.sqlite3
输出：  chat/AISW-stack/README.md

设计方向：db 是 source of truth，md 由 db 渲染。
  - `blocks` 表存 md 切片（按 ## / ### 拆段），是真正的可编辑内容
  - 其他表（layers / branches / entries / refs / cells / *_links）是
    从 blocks 派生的查询索引，每次 import / render 时自动重建

子命令：
  init        新建空 schema
  import      把 README.md 一次性导入 db（清空重建）
  render      从 db 生成 README.md（覆盖原文件）
  stats       统计行数
  query SQL   执行任意 SQL（含 SELECT）

日常工作流：
  1. （仅一次）`import` 把 md 灌进 db
  2. 编辑：`UPDATE blocks SET body=... WHERE key='L13'`
  3. `render` 重写 README.md
  4. 查询：`query "SELECT ... FROM entries WHERE vendor='高通'"`
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
# helpers

_PUNCT_RE = re.compile(r"[\s/（）()，,、；;:：&+]+")
_DECO_RE = re.compile(r"[*_`\"'·]")
SEP_CHARS = "、，,；;|。：:"
NAME_SPLIT_RE = re.compile(r"[" + re.escape(SEP_CHARS) + r"]|(?<=[）)\s])\+\s")
REF_LINK_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^\s)]+)\)")
REF_ENTRY_RE = re.compile(
    r"^\[(\d+)\]\s+(.+?)(?:\s*\[Online\]\.\s+Available:\s*<([^>]+)>)?\s*$"
)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
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
    """从一段文本中按 `Name[[N]](url)` 模式抽 entries。"""
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
# md → blocks

def split_into_blocks(text: str) -> list[dict]:
    """把 md 按 H2 切；并列应用分支段进一步按 H3 切。"""
    blocks = []
    order = 0
    h2_matches = list(H2_RE.finditer(text))

    # top
    if not h2_matches or h2_matches[0].start() > 0:
        top_end = h2_matches[0].start() if h2_matches else len(text)
        top_body = text[:top_end]
        if top_body.strip():
            blocks.append({
                "key": "top", "order_idx": order, "block_type": "doc_top",
                "title": None, "body": top_body.rstrip("\n"),
                "layer_code": None, "branch_code": None,
            })
            order += 1

    for i, m in enumerate(h2_matches):
        title = m.group(1).strip()
        body_start = m.end() + 1
        body_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(text)
        body = text[body_start:body_end].rstrip("\n")

        if title.startswith("L 层 × 分支 总表"):
            blocks.append({
                "key": "summary-table", "order_idx": order,
                "block_type": "summary_table", "title": title, "body": body,
                "layer_code": None, "branch_code": None,
            })
            order += 1
        elif title.startswith("A. LLM / Agent 主干"):
            blocks.append({
                "key": "main-overview", "order_idx": order,
                "block_type": "main_overview", "title": title, "body": body,
                "layer_code": None, "branch_code": None,
            })
            order += 1
        elif (lm := LAYER_TITLE_RE.match(title)):
            lc = lm.group(1)
            blocks.append({
                "key": lc, "order_idx": order, "block_type": "layer",
                "title": title, "body": body,
                "layer_code": lc, "branch_code": None,
            })
            order += 1
        elif title.startswith("并列应用分支"):
            h3_matches = list(H3_RE.finditer(body))
            if h3_matches:
                intro_body = body[:h3_matches[0].start()].rstrip("\n")
                blocks.append({
                    "key": "parallel-intro", "order_idx": order,
                    "block_type": "branch_intro", "title": title,
                    "body": intro_body, "layer_code": None, "branch_code": None,
                })
                order += 1
                for j, hm in enumerate(h3_matches):
                    h3_title = hm.group(1).strip()
                    h3_start = hm.end() + 1
                    h3_end = h3_matches[j + 1].start() if j + 1 < len(h3_matches) else len(body)
                    h3_body = body[h3_start:h3_end].rstrip("\n")
                    bm = BRANCH_TITLE_RE.match(h3_title)
                    if bm:
                        code = bm.group(1)
                        is_sub = bool(re.search(r"\d", code))
                        blocks.append({
                            "key": code, "order_idx": order,
                            "block_type": "subbranch" if is_sub else "branch",
                            "title": h3_title, "body": h3_body,
                            "layer_code": None, "branch_code": code,
                        })
                        order += 1
                    else:
                        blocks.append({
                            "key": f"h3-other-{order}", "order_idx": order,
                            "block_type": "other", "title": h3_title,
                            "body": h3_body, "layer_code": None, "branch_code": None,
                        })
                        order += 1
            else:
                blocks.append({
                    "key": "parallel-intro", "order_idx": order,
                    "block_type": "branch_intro", "title": title, "body": body,
                    "layer_code": None, "branch_code": None,
                })
                order += 1
        elif title.startswith("几条横切的观察"):
            blocks.append({
                "key": "crosscut", "order_idx": order, "block_type": "crosscut",
                "title": title, "body": body,
                "layer_code": None, "branch_code": None,
            })
            order += 1
        elif title == "参考文献":
            blocks.append({
                "key": "refs", "order_idx": order, "block_type": "refs",
                "title": title, "body": body,
                "layer_code": None, "branch_code": None,
            })
            order += 1
        else:
            blocks.append({
                "key": f"h2-other-{order}", "order_idx": order,
                "block_type": "other", "title": title, "body": body,
                "layer_code": None, "branch_code": None,
            })
            order += 1

    return blocks


# ---------------------------------------------------------------------------
# blocks → derived indexes

def derive_indexes(blocks: list[dict]) -> dict:
    layers: dict[str, dict] = {}
    branches: dict[str, dict] = {b: {"code": b, "name": n, "parent": None, "pos": i}
                                  for i, (b, n) in enumerate(MAIN_BRANCHES, 1)}
    refs: dict[int, dict] = {}
    entries: dict[str, dict] = {}
    entry_branches: set[tuple[str, str]] = set()
    entry_refs: set[tuple[str, int]] = set()
    branch_cells: list[dict] = []
    sub_pos = 100

    # 第一遍：从 block titles 注册 layers / branches
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

    # 第二遍：从 blocks body 解析 refs / cells / entries
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
        if blk["block_type"] == "branch":
            # 单字母总览块，本身的 entries 归 branch_code
            pass
        if blk["block_type"] == "subbranch":
            # 子分支块，entries 归 subbranch_code
            pass
        if not layer_code and not branch_code:
            continue
        parse_block_entries(blk, layer_code, branch_code,
                            entries, entry_branches, entry_refs)

    return {
        "layers": layers, "branches": branches, "refs": refs,
        "entries": entries, "entry_branches": list(entry_branches),
        "entry_refs": list(entry_refs), "branch_cells": branch_cells,
    }


def parse_summary_table_cells(body: str, layers: dict, branch_cells: list):
    """从主表 body 提取 layer 名 + cell 标记。"""
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


def parse_block_entries(blk: dict, layer_code: str | None, branch_code: str | None,
                        entries: dict, entry_branches: set, entry_refs: set):
    """扫 block body，提取所有 entries。"""
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
            if branch_code:
                entry_branches.add((slug, branch_code))
            entry_refs.add((slug, e["ref"]))


# ---------------------------------------------------------------------------
# db io

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection):
    conn.executescript(SCHEMA)
    conn.commit()


def write_db(conn: sqlite3.Connection, blocks: list, data: dict):
    cur = conn.cursor()
    cur.executescript(
        "DELETE FROM entry_refs; DELETE FROM entries;"
        "DELETE FROM branch_cells; DELETE FROM refs;"
        "DELETE FROM branches; DELETE FROM layers;"
        "DELETE FROM blocks;"
    )

    for b in blocks:
        cur.execute(
            "INSERT INTO blocks(key, order_idx, block_type, title, body, layer_code, branch_code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (b["key"], b["order_idx"], b["block_type"], b["title"],
             b["body"], b.get("layer_code"), b.get("branch_code")),
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
        ("last_import_ts", str(int(time.time()))),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# render: db blocks → md

def cmd_render(args):
    conn = connect()
    rows = conn.execute(
        "SELECT key, order_idx, block_type, title, body FROM blocks ORDER BY order_idx"
    ).fetchall()
    if not rows:
        print("no blocks in db; run `import` first.", file=sys.stderr)
        sys.exit(1)

    out_parts: list[str] = []
    for key, order_idx, btype, title, body in rows:
        if btype == "doc_top":
            out_parts.append(body)
            continue
        prefix = "###" if btype in ("branch", "subbranch") else "##"
        out_parts.append(f"\n\n{prefix} {title}\n\n{body}")

    rendered = "".join(out_parts).rstrip() + "\n"
    MD_PATH.write_text(rendered, encoding="utf-8")
    print(f"rendered {len(rows)} blocks → {MD_PATH}")


# ---------------------------------------------------------------------------
# CLI

def cmd_init(args):
    conn = connect()
    init_db(conn)
    print(f"initialized {DB_PATH}")


def cmd_import(args):
    text = MD_PATH.read_text(encoding="utf-8")
    conn = connect()
    init_db(conn)
    blocks = split_into_blocks(text)
    data = derive_indexes(blocks)
    write_db(conn, blocks, data)
    print(
        f"blocks={len(blocks)} layers={len(data['layers'])} "
        f"branches={len(data['branches'])} entries={len(data['entries'])} "
        f"refs={len(data['refs'])} cells={len(data['branch_cells'])}"
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
        print("(no rows)")
        return
    cols = rows[0].keys()
    print("\t".join(cols))
    for r in rows:
        print("\t".join("" if r[c] is None else str(r[c]) for c in cols))


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("import").set_defaults(func=cmd_import)
    sub.add_parser("render").set_defaults(func=cmd_render)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    pq = sub.add_parser("query")
    pq.add_argument("sql")
    pq.set_defaults(func=cmd_query)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
