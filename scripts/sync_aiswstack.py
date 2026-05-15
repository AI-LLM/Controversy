#!/usr/bin/env python3
"""AISW-stack md 索引 ↔ sqlite3 同步工具。

数据源：chat/AISW-stack/README.md
数据库：chat/AISW-stack/index.sqlite3

分类系统对应总表结构：
  layers     L01..L38     纵轴，技术栈层
  branches   A/B/.../I    横轴主分支；B1/B2/B3/Ca/Cb...  子分支
  entries    一个技术 / 方案条目，主键 (layer, slug)
  refs       参考文献 [N]
  branch_cells  总表里 (layer × branch) 单元格的原始标记

抽取粒度：以 markdown 里每次出现的 `Name[[N]](url)` 为一个 entry。
理由：md 的 inline 列表（`A、B[[N]](u)、C[[M]](u)`）占内容 60%+，
按 ref-call 切是唯一能机械捕获全部命名实体的方式。

子命令：
  init       新建空 schema
  parse      md → db（清空后重建；幂等）
  stats      统计行数
  query SQL  执行任意 SQL（含 SELECT）
  anchor     给 md 里每个独立 bullet 条目插入 <!--e:slug--> 锚（一次性）
  writeback  根据 db.entries 当前字段重写带锚位置的 url / ref_num
  unanchor   移除所有 <!--e:slug--> 锚（撤销）

同步策略：
  md 是 source of truth。`parse` 总是清表重建——所以解析器要稳定。
  `anchor` + `writeback` 提供"在 db 改字段→回写 md"的有限通路，
  仅覆盖独立成行的 bullet entry（占比 ~30%）。inline entry 改动请直接改 md。
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
CREATE TABLE IF NOT EXISTS layers (
    code        TEXT PRIMARY KEY,
    position    INTEGER NOT NULL,
    name        TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS branches (
    code         TEXT PRIMARY KEY,
    parent_code  TEXT,
    position     INTEGER NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT,
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
    source_line  INTEGER,
    FOREIGN KEY (layer_code)  REFERENCES layers(code),
    FOREIGN KEY (branch_code) REFERENCES branches(code)
);

CREATE TABLE IF NOT EXISTS entry_refs (
    entry_id  INTEGER NOT NULL,
    ref_num   INTEGER NOT NULL,
    PRIMARY KEY (entry_id, ref_num),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (ref_num)  REFERENCES refs(num)
);

CREATE TABLE IF NOT EXISTS entry_branches (
    entry_id     INTEGER NOT NULL,
    branch_code  TEXT NOT NULL,
    PRIMARY KEY (entry_id, branch_code),
    FOREIGN KEY (entry_id)    REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_code) REFERENCES branches(code)
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
CREATE INDEX IF NOT EXISTS idx_entries_vendor ON entries(vendor);
CREATE INDEX IF NOT EXISTS idx_entry_refs_ref ON entry_refs(ref_num);
"""


# ---------------------------------------------------------------------------
# slug

_PUNCT_RE = re.compile(r"[\s/（）()，,、；;:：&+]+")
_DECO_RE = re.compile(r"[*_`\"'·]")


def slugify(prefix: str, name: str) -> str:
    s = unicodedata.normalize("NFKC", name)
    s = _DECO_RE.sub("", s)
    s = _PUNCT_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    if not s:
        s = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return f"{prefix.lower()}-{s}"


# ---------------------------------------------------------------------------
# parsing

LAYER_HEADING_RE = re.compile(r"^##\s+(L\d{2})\s+(.+?)\s*$")
SUBBRANCH_HEADING_RE = re.compile(r"^###\s+([A-I](?:[a-z]+|\d+))\s+(.+?)\s*$")
BRANCH_HEADING_RE = re.compile(r"^###\s+([A-I])\s+(.+?)\s*$")
SECTION_BREAK_RE = re.compile(r"^##\s+(.+?)\s*$")
VENDOR_BLOCK_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*$")
INLINE_VENDOR_RE = re.compile(r"^[-*]\s+\*\*([^*]+)\*\*[:：]")
GROUP_LABEL_RE = re.compile(r"^[-*]\s+\*\*([^*]+)\*\*[:：]\s*(.*)$")
BARE_VENDOR_RE = re.compile(r"^[-*]\s+([^*：:\[]{1,24}?)[：:]\s*(.+)$")
REF_LINK_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^\s)]+)\)")
REF_ENTRY_RE = re.compile(
    r"^\[(\d+)\]\s+(.+?)(?:\s*\[Online\]\.\s+Available:\s*<([^>]+)>)?\s*$"
)
SEP_CHARS = "、，,；;|。：:"
NAME_SPLIT_RE = re.compile(r"[" + re.escape(SEP_CHARS) + r"]|(?<=[）)\s])\+\s")

# 已知 vendor 短名（去括号后比对）。不在表内的块标签一律视作 category。
KNOWN_VENDORS = {
    "NVIDIA", "AMD", "Intel", "Apple", "AWS", "Google", "Microsoft", "Meta",
    "Anthropic", "OpenAI", "xAI", "DeepSeek", "Mistral", "Cohere",
    "Databricks", "Snowflake", "Cloudflare", "HuggingFace", "Hugging Face",
    "IBM", "Oracle", "SAP", "Salesforce", "ServiceNow", "Workday",
    "华为", "华为昇腾", "阿里", "百度", "腾讯", "字节",
    "高通", "Qualcomm", "联发科", "MediaTek", "瑞芯微", "Rockchip",
}


def canonical_vendor(label: str) -> str | None:
    """块标签 → 已知 vendor 的规范名；无匹配则 None。"""
    plain = re.sub(r"（[^）]*）|\([^)]*\)", "", label).strip()
    if plain in KNOWN_VENDORS:
        # 同义合并
        aliases = {"华为昇腾": "华为", "Hugging Face": "HuggingFace"}
        return aliases.get(plain, plain)
    return None


# 总表横轴顺序——按 md 表头 "| L | A | B | C ... |"
MAIN_BRANCHES = [
    ("A", "LLM / Agent"),
    ("B", "科学计算"),
    ("C", "机器人"),
    ("D", "自动驾驶"),
    ("E", "世界模型 / 3D"),
    ("F", "经典 CV"),
    ("G", "量化金融"),
    ("H", "游戏"),
    ("I", "影视娱乐"),
]


def parse_md(text: str):
    lines = text.split("\n")
    layers: dict[str, dict] = {}
    branches: dict[str, dict] = {b: {"code": b, "name": n, "parent": None, "pos": i}
                                  for i, (b, n) in enumerate(MAIN_BRANCHES, 1)}
    branch_cells: list[dict] = []
    refs: dict[int, dict] = {}
    entries: dict[str, dict] = {}  # slug -> entry
    entry_branches: list[tuple[str, str]] = []  # (slug, branch_code)
    entry_refs_set: set[tuple[str, int]] = set()

    state = {
        "layer": None,        # current L code
        "branch": "A",         # default for L sections under "## L"
        "subbranch": None,     # current sub-branch like Ca, B1
        "vendor": None,        # current bold-line vendor
        "category": None,      # current bold-line category (non-vendor block label)
        "in_main_table": False,
        "main_table_header": None,
        "in_refs": False,
    }

    sub_pos = 100  # incremental position for sub-branches

    for ln_idx, raw in enumerate(lines, 1):
        line = raw.rstrip()

        # --- 参考文献段 ---
        if state["in_refs"]:
            m = REF_ENTRY_RE.match(line)
            if m:
                num = int(m.group(1))
                citation = m.group(2).strip()
                url = m.group(3)
                refs[num] = {"num": num, "citation": citation, "url": url}
            continue

        if line.startswith("## 参考文献"):
            state["in_refs"] = True
            state["layer"] = None
            continue

        # --- 总表识别（首行表头含 "A. LLM"）---
        if state["in_main_table"]:
            if not line.startswith("|"):
                state["in_main_table"] = False
            else:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if cells and re.match(r"^L\d{2}\b", cells[0]):
                    m = re.match(r"^(L\d{2})\s+(.+)$", cells[0])
                    if m:
                        lc, lname = m.group(1), m.group(2).strip()
                        layers.setdefault(lc, {
                            "code": lc, "position": int(lc[1:]),
                            "name": lname, "description": None,
                        })
                        for i, raw_cell in enumerate(cells[1:]):
                            if i >= len(MAIN_BRANCHES):
                                break
                            bcode = MAIN_BRANCHES[i][0]
                            marker = classify_cell(raw_cell)
                            branch_cells.append({
                                "layer": lc, "branch": bcode,
                                "raw": raw_cell, "marker": marker,
                            })
                continue

        if line.startswith("| L |") and "A. LLM" in line:
            state["in_main_table"] = True
            continue

        # --- ## L 段 ---
        m = LAYER_HEADING_RE.match(line)
        if m:
            lc, lname = m.group(1), m.group(2).strip()
            layers.setdefault(lc, {
                "code": lc, "position": int(lc[1:]),
                "name": lname, "description": None,
            })
            state["layer"] = lc
            state["branch"] = "A"
            state["subbranch"] = None
            state["vendor"] = None
            state["category"] = None
            continue

        # --- ### Xa 子分支（字母+小写或数字后缀） ---
        m = SUBBRANCH_HEADING_RE.match(line)
        if m:
            code = m.group(1)
            heading_name = m.group(2).strip()
            parent = code[0]
            branches.setdefault(code, {
                "code": code, "name": heading_name,
                "parent": parent,
                "pos": sub_pos,
            })
            sub_pos += 1
            state["subbranch"] = code
            state["branch"] = parent
            state["layer"] = None
            state["vendor"] = None
            state["category"] = None
            continue

        # --- ### X 分支总览（单字母） ---
        m = BRANCH_HEADING_RE.match(line)
        if m:
            code = m.group(1)
            heading_name = m.group(2).strip()
            branches.setdefault(code, {
                "code": code, "name": heading_name,
                "parent": None, "pos": ord(code) - ord("A"),
            })
            state["branch"] = code
            state["subbranch"] = None
            state["layer"] = None
            state["vendor"] = None
            state["category"] = None
            continue

        # --- 其他 ## 切出 layer 状态 ---
        if line.startswith("## ") and not LAYER_HEADING_RE.match(line):
            state["layer"] = None
            state["subbranch"] = None
            state["vendor"] = None

        if not state["layer"] and not state["subbranch"]:
            continue  # skip text outside known section

        # --- 块标题：单独一行的 **X**： ---
        m = VENDOR_BLOCK_RE.match(line)
        if m:
            label = m.group(1).strip()
            if (cv := canonical_vendor(label)):
                state["vendor"] = cv
                state["category"] = None
            else:
                state["category"] = label
                state["vendor"] = None
            continue

        if not REF_LINK_RE.search(line):
            continue  # 行内无引用，跳过

        # 处理 bullet 内的 vendor / category 前缀
        local_vendor = state["vendor"]
        local_category = state["category"]
        rest = line
        is_bullet = line.lstrip().startswith(("-", "*"))
        if is_bullet:
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

        if state["subbranch"]:
            layer_code = None
            branch_code = state["subbranch"]
        else:
            layer_code = state["layer"]
            branch_code = state["branch"]

        slug_prefix = layer_code or branch_code
        if not slug_prefix:
            continue

        for entry in extract_entries(rest, layer_code, ln_idx):
            entry["vendor"] = local_vendor
            entry["category"] = local_category
            entry["branch"] = branch_code
            slug = slugify(slug_prefix, entry["name"])
            if slug not in entries:
                entry["slug"] = slug
                entries[slug] = entry
            entry_branches.append((slug, branch_code))
            for ref_num in entry["refs"]:
                entry_refs_set.add((slug, ref_num))

    return {
        "layers": layers,
        "branches": branches,
        "branch_cells": branch_cells,
        "refs": refs,
        "entries": entries,
        "entry_branches": list(set(entry_branches)),
        "entry_refs": list(entry_refs_set),
    }


def classify_cell(text: str) -> str:
    t = text.strip()
    if t in ("—", "-", "–"):
        return "none"
    if t.startswith("同 A"):
        return "same_a"
    if t.startswith("与 ") and "共用" in t:
        return "shared"
    return "normal"


def extract_entries(text: str, layer_code: str, source_line: int):
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
        out.append({
            "name": name,
            "url": url,
            "layer": layer_code,
            "refs": [ref_num],
            "notes": notes,
            "source_line": source_line,
        })
    return out


def clean_name(s: str) -> str:
    s = _DECO_RE.sub("", s)
    s = re.sub(r"^[\s\-+]+|[\s\-+:：]+$", "", s)
    s = re.sub(r"^[\s　]+", "", s)
    return s.strip()


def is_valid_name(name: str) -> bool:
    """过滤明显是 url 残片 / 注释括号片段的伪 name。"""
    if not name:
        return False
    if name.startswith(("//", ")", "）", "/")):
        return False
    if "://" in name:
        return False
    # 整体是纯注释括号 `（...）`
    if re.fullmatch(r"[（(].*[）)]", name):
        return False
    return True


def extract_trailing_notes(text: str, pos: int) -> str | None:
    rest = text[pos:].lstrip()
    if rest.startswith("（"):
        depth = 0
        for i, ch in enumerate(rest):
            if ch == "（":
                depth += 1
            elif ch == "）":
                depth -= 1
                if depth == 0:
                    return rest[1:i]
    elif rest.startswith("("):
        depth = 0
        for i, ch in enumerate(rest):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return rest[1:i]
    return None


# ---------------------------------------------------------------------------
# db io

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection):
    conn.executescript(SCHEMA)
    conn.commit()


def write_db(conn: sqlite3.Connection, data: dict, md_sha: str):
    cur = conn.cursor()
    cur.executescript(
        "DELETE FROM entry_refs; DELETE FROM entry_branches; DELETE FROM entries;"
        "DELETE FROM branch_cells; DELETE FROM refs;"
        "DELETE FROM branches; DELETE FROM layers;"
    )

    for lc, l in sorted(data["layers"].items()):
        cur.execute(
            "INSERT INTO layers(code, position, name, description) VALUES (?, ?, ?, ?)",
            (l["code"], l["position"], l["name"], l.get("description")),
        )

    for bc, b in sorted(data["branches"].items(), key=lambda x: x[1]["pos"]):
        cur.execute(
            "INSERT INTO branches(code, parent_code, position, name, description) "
            "VALUES (?, ?, ?, ?, ?)",
            (b["code"], b.get("parent"), b["pos"], b["name"], b.get("description")),
        )

    for r in data["refs"].values():
        cur.execute(
            "INSERT INTO refs(num, citation, url) VALUES (?, ?, ?)",
            (r["num"], r["citation"], r["url"]),
        )

    slug_to_id: dict[str, int] = {}
    for slug, e in data["entries"].items():
        cur.execute(
            "INSERT INTO entries(slug, name, url, layer_code, branch_code, vendor, category, notes, source_line) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slug, e["name"], e["url"], e.get("layer"), e.get("branch"),
             e.get("vendor"), e.get("category"), e.get("notes"),
             e.get("source_line")),
        )
        slug_to_id[slug] = cur.lastrowid

    for slug, branch in data["entry_branches"]:
        if slug not in slug_to_id:
            continue
        try:
            cur.execute(
                "INSERT OR IGNORE INTO entry_branches(entry_id, branch_code) VALUES (?, ?)",
                (slug_to_id[slug], branch),
            )
        except sqlite3.IntegrityError:
            pass

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
        ("md_sha256", md_sha),
    )
    cur.execute(
        "INSERT OR REPLACE INTO sync_meta(key, value) VALUES (?, ?)",
        ("last_sync_ts", str(int(time.time()))),
    )
    conn.commit()


def md_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# anchor / writeback

ANCHOR_RE = re.compile(r"<!--e:([^\s>]+)-->")


def cmd_anchor(args):
    text = MD_PATH.read_text(encoding="utf-8")
    data = parse_md(text)
    lines = text.split("\n")

    # 收集每个独立 bullet entry 的目标行——一个 bullet 行内只生成一个锚
    # 锁定独立 bullet 的判据：bullet 内引用数 == 1 且名字非空
    anchored = 0
    skipped = 0
    new_lines = []
    line_to_slug: dict[int, str] = {}
    for slug, e in data["entries"].items():
        ln = e["source_line"]
        if ln and ln not in line_to_slug:
            line_to_slug[ln] = slug

    for idx, line in enumerate(lines, 1):
        if ANCHOR_RE.search(line):
            new_lines.append(line)
            continue
        slug = line_to_slug.get(idx)
        if slug and line.lstrip().startswith(("-", "*")):
            refs_in_line = REF_LINK_RE.findall(line)
            if len(refs_in_line) == 1:
                new_lines.append(line.rstrip() + f" <!--e:{slug}-->")
                anchored += 1
            else:
                skipped += 1
                new_lines.append(line)
        else:
            new_lines.append(line)

    MD_PATH.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"anchored {anchored} bullet entries; skipped {skipped} multi-ref lines.")


def cmd_unanchor(args):
    text = MD_PATH.read_text(encoding="utf-8")
    new = re.sub(r"\s*<!--e:[^\s>]+-->", "", text)
    MD_PATH.write_text(new, encoding="utf-8")
    print("removed all <!--e:slug--> anchors.")


def cmd_writeback(args):
    """对每个锚行，按 db.entries 重写其中的 [[ref]](url) 部分。"""
    conn = connect()
    text = MD_PATH.read_text(encoding="utf-8")
    lines = text.split("\n")
    rewrites = 0

    cur = conn.cursor()
    rows = cur.execute(
        "SELECT e.slug, e.name, e.url, ("
        "  SELECT GROUP_CONCAT(ref_num) FROM entry_refs WHERE entry_id = e.id"
        ") AS refs FROM entries e"
    ).fetchall()
    slug_data = {
        slug: {"name": name, "url": url,
               "refs": [int(x) for x in (refs or "").split(",") if x]}
        for slug, name, url, refs in rows
    }

    out = []
    for line in lines:
        m = ANCHOR_RE.search(line)
        if not m:
            out.append(line)
            continue
        slug = m.group(1)
        info = slug_data.get(slug)
        if not info or not info["refs"]:
            out.append(line)
            continue
        new_ref = info["refs"][0]
        new_url = info["url"]
        before_anchor = line[:m.start()].rstrip()
        # 找该行最后一个 [[N]](url)，替换为目标
        ref_match = list(REF_LINK_RE.finditer(before_anchor))
        if not ref_match:
            out.append(line)
            continue
        last = ref_match[-1]
        replaced = (before_anchor[:last.start()]
                    + f"[[{new_ref}]]({new_url})"
                    + before_anchor[last.end():])
        new_line = replaced + " " + line[m.start():]
        if new_line != line:
            rewrites += 1
        out.append(new_line)

    MD_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"writeback: {rewrites} lines updated.")


# ---------------------------------------------------------------------------
# CLI

def cmd_init(args):
    conn = connect()
    init_db(conn)
    print(f"initialized {DB_PATH}")


def cmd_parse(args):
    text = MD_PATH.read_text(encoding="utf-8")
    if DB_PATH.exists() and not args.force:
        conn = connect()
        old = conn.execute(
            "SELECT value FROM sync_meta WHERE key='md_sha256'"
        ).fetchone()
        if old and old[0] == md_hash(text):
            print("md unchanged; nothing to do (use --force to rebuild).")
            return
    else:
        conn = connect()
    init_db(conn)
    data = parse_md(text)
    write_db(conn, data, md_hash(text))
    print(
        f"layers={len(data['layers'])} branches={len(data['branches'])} "
        f"entries={len(data['entries'])} refs={len(data['refs'])} "
        f"cells={len(data['branch_cells'])}"
    )


def cmd_stats(args):
    conn = connect()
    for table in ("layers", "branches", "entries", "entry_refs",
                  "entry_branches", "refs", "branch_cells"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:18s} {n}")
    sha = conn.execute(
        "SELECT value FROM sync_meta WHERE key='md_sha256'"
    ).fetchone()
    if sha:
        text = MD_PATH.read_text(encoding="utf-8")
        in_sync = "in sync" if sha[0] == md_hash(text) else "OUT OF SYNC"
        print(f"md vs db          {in_sync}")


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

    pp = sub.add_parser("parse")
    pp.add_argument("--force", action="store_true")
    pp.set_defaults(func=cmd_parse)

    sub.add_parser("stats").set_defaults(func=cmd_stats)

    pq = sub.add_parser("query")
    pq.add_argument("sql")
    pq.set_defaults(func=cmd_query)

    sub.add_parser("anchor").set_defaults(func=cmd_anchor)
    sub.add_parser("unanchor").set_defaults(func=cmd_unanchor)
    sub.add_parser("writeback").set_defaults(func=cmd_writeback)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
