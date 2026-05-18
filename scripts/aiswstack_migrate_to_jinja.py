#!/usr/bin/env python3
"""One-shot migration: split each section's body into (prose intro, body)
and emit Jinja2 partials for all prose, while keeping the structured-entries
markdown inside `sections.body`.

After this runs:

  - `sections.body` for layer/subbranch holds ONLY the entries part
    (vendor-block headers + bullets / inline lists). The prose intro line(s)
    that previously sat at the top of the body are moved out.

  - `sections.body` for prose-only types (doc_top, main_overview,
    branch_intro, branch, crosscut, other) is cleared; the full content goes
    to templates/prose/<key>.md.

  - `templates/prose/<key>.md` is the new authoritative location for prose
    (intros, narrative paragraphs, branch overviews, crosscut, top, etc.).
    Users edit these files directly.

  - `templates/readme.md.j2` + `templates/_macros.j2` get written with a
    correct render pipeline: include prose + emit sections.body verbatim for
    layer/subbranch + build summary-table from cells + build refs from refs.

  - `entries` / `entry_refs` / `refs` / `cells` / `layers` / `branches` are
    untouched (still source of truth for queries and structural CRUD).
"""

from __future__ import annotations

import re
import sqlite3
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "chat/AISW-stack/index.sqlite3"
TEMPLATES_DIR = ROOT / "chat/AISW-stack/templates"

REF_LINK_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^\s)]+)\)")
VENDOR_BLOCK_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*$")
VENDOR_INLINE_RE = re.compile(r"^\*\*([^*]+)\*\*[:：]\s*(\S.*)$")

LAYER_LIKE = {"layer", "subbranch"}
PROSE_TYPES = {"doc_top", "main_overview", "branch_intro", "branch",
               "crosscut", "other"}


def split_intro_from_body(body: str) -> tuple[str, str]:
    """Return (intro_prose, remaining_body) for a layer/subbranch body.

    Intro is everything before the first 'entry-bearing' line:
      - a `**Vendor**：` block header
      - a `**Vendor**：...` inline
      - a bullet line (- or *)
      - a bare line that contains `[[N]](url)` ref tokens
    """
    lines = body.split("\n")
    first_entry_line = len(lines)
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue
        if VENDOR_BLOCK_RE.match(s) or VENDOR_INLINE_RE.match(s):
            first_entry_line = i; break
        if s.startswith(("-", "*")):
            first_entry_line = i; break
        if REF_LINK_RE.search(ln):
            first_entry_line = i; break
    intro = "\n".join(lines[:first_entry_line]).rstrip()
    rest = "\n".join(lines[first_entry_line:]).rstrip()
    return intro, rest


def split_summary_intro(body: str) -> tuple[str, str, str]:
    """summary-table body has prose intro + markdown table + optional outro
    prose. Return (intro, table_markdown, outro)."""
    lines = body.split("\n")
    first_tbl = next((i for i, ln in enumerate(lines)
                      if ln.startswith("|")), None)
    last_tbl = next((i for i, ln in enumerate(reversed(lines))
                     if ln.startswith("|")), None)
    if first_tbl is None:
        return body.rstrip(), "", ""
    last_tbl_idx = len(lines) - 1 - last_tbl
    intro = "\n".join(lines[:first_tbl]).rstrip()
    table = "\n".join(lines[first_tbl:last_tbl_idx + 1])
    outro = "\n".join(lines[last_tbl_idx + 1:]).strip()
    return intro, table, outro


def migrate(conn: sqlite3.Connection):
    # NOTE: layers.name is the abbreviated form (e.g. "互连 / 集合通信") used
    # in the summary-table column. The full layer heading lives on
    # sections.heading (e.g. "L02 GPU 互连 / 集合通信") — render() loads it
    # separately. Don't touch layers.name here.
    rows = conn.execute(
        "SELECT key, section_type, body FROM sections ORDER BY position"
    ).fetchall()
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    prose_dir = TEMPLATES_DIR / "prose"
    prose_dir.mkdir(exist_ok=True)
    cur = conn.cursor()

    # heading depth per type
    H = {"doc_top": None, "summary_table": "##", "main_overview": "##",
         "branch_intro": "##", "branch": "###", "crosscut": "##",
         "other": "##"}

    def write_with_heading(key, depth, heading, body):
        """prose-only sections embed their heading line in the prose file so
        the template emits {{ prose[key] }} verbatim."""
        if depth is None or not heading:
            text = body.rstrip() + "\n"
        else:
            text = f"{depth} {heading}\n\n{body.rstrip()}\n"
        (prose_dir / f"{key}.md").write_text(text, encoding="utf-8")

    layer_n = prose_n = 0
    for key, stype, body in rows:
        body = body or ""
        heading = conn.execute(
            "SELECT heading FROM sections WHERE key=?", (key,)
        ).fetchone()[0]
        if stype in PROSE_TYPES:
            write_with_heading(key, H.get(stype), heading, body)
            cur.execute("UPDATE sections SET body='' WHERE key=?", (key,))
            prose_n += 1
        elif stype == "summary_table":
            intro, table, outro = split_summary_intro(body)
            payload = intro + ("\n\n---OUTRO---\n" + outro if outro else "")
            write_with_heading(key, "##", heading, payload)
            cur.execute("UPDATE sections SET body=? WHERE key=?", (table, key))
            prose_n += 1
        elif stype == "refs":
            # refs body is rebuilt from refs table at render time; clear it
            cur.execute("UPDATE sections SET body='' WHERE key=?", (key,))
        elif stype in LAYER_LIKE:
            # layer/sub intro is JUST the prose paragraph (heading comes from
            # sections.heading at render time so the user can rename a layer
            # via `section set-heading`).
            intro, rest = split_intro_from_body(body)
            if intro:
                (prose_dir / f"{key}.md").write_text(intro + "\n",
                                                     encoding="utf-8")
            cur.execute("UPDATE sections SET body=? WHERE key=?", (rest, key))
            layer_n += 1
        else:
            print(f"  ! unhandled section_type={stype} key={key}")

    conn.commit()
    print(f"migrated: {layer_n} layer/sub split, {prose_n} prose blocks "
          f"written to {prose_dir}")


def emit_templates():
    """Emit readme.md.j2 + _macros.j2."""
    (TEMPLATES_DIR / "_macros.j2").write_text(textwrap.dedent('''\
        {#- Shared rendering macros.

        Data layout passed by aiswstack_controller.py:
          layers          = [{code, position, name}]
          branches        = main branches [{code, name, name_short, parent_code, position}]
          sub_branches    = subbranches [{code, name, parent_code, position}]
          section_body    = {section_key: markdown_blob}  — entries part only
          section_heading = {section_key: heading_text}
          prose           = {section_key: markdown_text}  — narrative
          refs            = [{num, citation, url}]
          cells           = {(layer_code, branch_code): text}
        -#}

        {#- Emit "## heading\\n\\n<prose>\\n\\n<body>" with only ONE blank line
            between each non-empty piece. Used for layer / subbranch sections. -#}
        {%- macro section_block(key, heading, depth) -%}
        {{ depth }} {{ heading }}

        {% set p = (prose.get(key) or '').strip() -%}
        {% set b = (section_body.get(key) or '').strip() -%}
        {% if p %}{{ p }}{% if b %}

        {% endif %}{% endif -%}
        {% if b %}{{ b }}{% endif %}
        {%- endmacro -%}

        {%- macro render_summary_table(layers, branches, cells) -%}
        | L | {% for b in branches %}{{ b.code }}. {{ b.name_short or b.name }}{% if not loop.last %} | {% endif %}{% endfor %} |
        |---|{% for b in branches %}---|{% endfor %}
        {% for lyr in layers -%}
        | {{ lyr.code }} {{ lyr.name }} | {% for b in branches %}{{ cells.get((lyr.code, b.code), '') }}{% if not loop.last %} | {% endif %}{% endfor %} |
        {% endfor -%}
        {%- endmacro -%}

        {%- macro render_refs(refs) -%}
        {% for r in refs -%}
        [{{ r.num }}] {{ r.citation }}{% if r.url %} [Online]. Available: <{{ r.url }}>{% endif %}

        {% endfor -%}
        {%- endmacro -%}
        '''), encoding="utf-8")

    (TEMPLATES_DIR / "readme.md.j2").write_text(textwrap.dedent('''\
        {%- from '_macros.j2' import render_summary_table, render_refs, section_block with context -%}
        {#- 主模版。散文从 prose[]（templates/prose/<key>.md）来；entries
            部分从 section_body[]（sections.body）来；层级标题从
            section_heading[]（sections.heading）来。-#}
        {{ prose.get('top', '') | trim }}

        {%- set st = prose.get('summary-table', '') %}
        {%- if '---OUTRO---' in st %}
        {%- set st_intro, st_outro = st.split('\\n\\n---OUTRO---\\n', 1) %}
        {%- else %}
        {%- set st_intro, st_outro = st, '' %}
        {%- endif %}

        {{ st_intro | trim }}

        {{ render_summary_table(layers, branches, cells) | trim }}
        {% if st_outro.strip() %}
        {{ st_outro | trim }}
        {%- endif %}

        {{ prose.get('main-overview', '') | trim }}
        {%- for lyr in layers if lyr.code in section_heading %}

        {{ section_block(lyr.code, section_heading[lyr.code], '##') }}
        {%- endfor %}

        {{ prose.get('parallel-intro', '') | trim }}
        {%- for br in branches if br.code != 'A' %}
        {%- if br.code in prose %}

        {{ prose[br.code] | trim }}
        {%- endif %}
        {%- for sub in sub_branches if sub.parent_code == br.code %}

        {{ section_block(sub.code, section_heading.get(sub.code, sub.code ~ ' ' ~ sub.name), '###') }}
        {%- endfor %}
        {%- endfor %}

        {{ prose.get('crosscut', '') | trim }}

        ## 参考文献

        {{ render_refs(refs) }}
        '''), encoding="utf-8")

    print(f"wrote templates to {TEMPLATES_DIR}/")


def main():
    if not DB_PATH.exists():
        sys.exit(f"db not found: {DB_PATH}")
    if (TEMPLATES_DIR / "prose").exists() and "--force" not in sys.argv:
        sys.exit(
            f"prose dir exists: {TEMPLATES_DIR/'prose'}\n"
            f"This script overwrites prose files with content extracted from "
            f"sections.body — running it after you've hand-edited prose "
            f"files will destroy those edits.\n"
            f"Pass --force to proceed anyway (backup first!)."
        )
    conn = sqlite3.connect(DB_PATH)
    migrate(conn)
    emit_templates()
    conn.close()


if __name__ == "__main__":
    main()
