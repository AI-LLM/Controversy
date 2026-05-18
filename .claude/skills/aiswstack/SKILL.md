---
name: aiswstack
description: Query and edit the AISW-stack knowledge base at chat/AISW-stack/. Use when the user asks about the layered AI software stack (L01–L38 × A–J branches × vendors like NVIDIA / 高通 / 联发科 / 瑞芯微), wants to add a new technology / product / layer / branch, edits an entry's URL or ref, or regenerates the README. **MVC + Jinja2**：数据（branches / layers / entries / refs / cells）存 index.sqlite3；散文（每层 intro、branch overview、crosscut、preamble）存 `chat/AISW-stack/templates/prose/<key>.md`；模版组装由 `templates/readme.md.j2` + `_macros.j2` 完成。Controller (`scripts/aiswstack_controller.py`) 提供结构化 CRUD（entry / ref / cell / section body for entries），render 走 Jinja2。改散文 = 直接编辑对应 prose/<key>.md。改 entry / ref / cell = 走 Controller 命令。
---

# AISW-stack skill

知识库：`chat/AISW-stack/`。**MVC + Jinja2 view**：

| 角色 | 文件 | 修改方式 |
|---|---|---|
| **Model（数据）** | `chat/AISW-stack/index.sqlite3` | Controller 命令 |
| **Model（散文）** | `chat/AISW-stack/templates/prose/<key>.md` | 直接编辑 `.md` 文件 |
| **View (templates)** | `chat/AISW-stack/templates/readme.md.j2` + `_macros.j2` | 直接编辑，改结构 / 排版 |
| **Controller** | `scripts/aiswstack_controller.py` | 改 CLI / 数据操作时编辑 |
| **Output** | `chat/AISW-stack/README.md` | **只读输出**，由 `render` 生成 |

**铁律**：

1. **永远不要手工编辑 `README.md`**——`render` 会覆盖。
2. **散文（每层 intro / branch overview / preamble / crosscut）改 prose 文件**：`chat/AISW-stack/templates/prose/<key>.md`。Controller 不动散文。
3. **entries / refs / cells 通过 Controller 命令改**。手工编辑 sections.body 是高级操作（结构化大改时才用）。
4. **每次改完跑 `render`** 才会更新 README.md。需要 Jinja2：`.venv/bin/python scripts/aiswstack_controller.py render`（项目根有 `.venv` 装了 jinja2）。

## 文件布局

```
chat/AISW-stack/
├── README.md                 (render 产物，勿手改)
├── index.sqlite3             (数据 source of truth)
└── templates/
    ├── readme.md.j2          (主模版：document 骨架 + 章节顺序)
    ├── _macros.j2            (summary_table / section_block / refs 渲染宏)
    └── prose/
        ├── top.md            (# 文档大标题 + 总览段)
        ├── summary-table.md  (`## L 层 × 分支 总表` + intro + `---OUTRO---` + outro)
        ├── main-overview.md  (`## A. LLM / Agent — 全栈总览（34 层）` + 段)
        ├── parallel-intro.md (`## 各领域分支细节...` + intro)
        ├── crosscut.md       (`## 几条横切的观察` + 内容)
        ├── L01.md … L34.md   (每层 intro 段，纯文本，不含 ## 标题——标题由 layer.code+name 动态来)
        ├── B1.md … J6.md     (每子分支 intro)
        └── C.md … J.md       (branch overview 段，含 ### 标题)
scripts/
├── aiswstack_controller.py        (主 Controller)
├── aiswstack_migrate_to_jinja.py  (一次性迁移脚本，已跑过；勿重跑)
└── aiswstack_controller_legacy.py (历史版本)
```

## 数据模型

```
sections   key PK, position, section_type, heading, body, layer_code, branch_code
             section_type ∈ {doc_top, summary_table, main_overview, layer,
                              branch_intro, branch, subbranch, crosscut,
                              refs, other}
             body 现在 **只放 layer/subbranch 的 entries markdown**；prose-only
             section（doc_top / main_overview / branch_intro / branch /
             crosscut / other / summary_table prose / refs）body 为空，
             其内容在 templates/prose/<key>.md。

entries    slug PK, name, url, notes, section_key, layer_code, branch_code,
             vendor, category, position
             由 sections.body 派生（refresh-index 重建），用于按 slug 定位。

refs       num PK, citation, url                  source of truth
cells      layer_code, branch_code, text, marker  source of truth

layers     code PK, position, name      派生（layers.name 是总表用的短名）
branches   code PK, parent_code, ...    派生
```

## Render 流程

```bash
.venv/bin/python scripts/aiswstack_controller.py render
```

内部步骤：

1. 加载 db：layers / branches / refs / cells / sections.body / sections.heading
2. 加载 templates/prose/*.md → `prose` dict
3. `jinja2.Environment(FileSystemLoader('templates/'))` 渲染 `readme.md.j2`
4. 写 `README.md`

模版会：
- 输出 `prose.top`（含 `#` 标题）
- 输出 `prose['summary-table']` 的 intro 部分 → 用 cells 数据生成表 → 输出 outro（`---`）
- 输出 `prose['main-overview']`（含 `## A. LLM / Agent...` 标题）
- 对每层（按 layer.code 顺序）：emit `## {{ section.heading }}` + `prose[L01]` + `sections.body[L01]`
- 输出 `prose['parallel-intro']`（含 `## 各领域分支细节...` 标题）
- 对每主分支 B–J：可选 emit `prose[C]`（含 `### C ...` 标题，B 无 overview） + 各子分支 `### B1 ...` + `prose[B1]` + `sections.body[B1]`
- 输出 `prose['crosscut']`（含 `## 几条横切的观察` 标题）
- 输出 `## 参考文献` + 从 refs 表渲染引用列表

## Controller CLI 速查

```bash
.venv/bin/python scripts/aiswstack_controller.py <subcmd>

# 读
  stats
  query "SELECT ..."            只读 SELECT
  section list
  section show KEY              打印 heading + body（layer/sub 的 body 即 entries markdown）
  entry list [--section K] [--layer L] [--branch B] [--vendor V]
  entry show SLUG
  ref list [--orphan]
  ref show NUM
  ref next-num
  cell get LAYER BRANCH
  prose list                    列所有 prose 文件 + 首行预览
  prose path KEY                打印 templates/prose/<KEY>.md 的绝对路径
  prose show KEY                dump prose 文件内容

# 写 entries / refs / cells（不涉及散文）
  entry add SECTION_KEY --vb-label LBL --name N --url U --ref R
            [--notes T] [--separator SEP]
  entry remove SLUG
  entry set-url SLUG --url U
  entry set-name SLUG --name N
  entry set-notes SLUG --notes T

  ref add --citation TXT [--url URL]    按 url 去重，返回 num
  ref set NUM [--citation T] [--url U]
  ref remove NUM

  cell set LAYER BRANCH --text TEXT     自动重建总表 cells 索引

# section
  section set-heading KEY --heading TEXT
  section set-body KEY (--body TEXT | --file F)
        — 只允许 layer/sub（操作的是 entries markdown 部分）
        — prose-only 类型会报错，让用户直接改 prose 文件

# 输出
  render                        Jinja2 渲染 → README.md
  refresh-index                 从 sections.body 重建 entries/cells/refs/layers/branches
                                （手改 layer/sub body 后跑一次）
```

## 决策树

```
用户请求
├── 只是问问题（查询，没让改）
│   └── 用 query / entry list / ref list / cell get / prose show
│
├── 改散文（每层 intro / branch overview / preamble / crosscut）
│   ├── 找到文件：prose path KEY    或 ls chat/AISW-stack/templates/prose/
│   ├── 用 Read / Edit / Write 改对应 .md 文件
│   └── render
│
├── 加 / 改 / 删一个 entry（已知所有信息）
│   ├── 改 url：entry set-url SLUG --url NEW
│   ├── 改名字：entry set-name SLUG --name NEW
│   ├── 改注解：entry set-notes SLUG --notes NEW
│   ├── 删除：entry remove SLUG
│   └── 新增：先 ref add 拿 num，再 entry add KEY --vb-label LBL ...
│
├── 加 entry 但用户没给名字 / 链接
│   └── 先 WebSearch / WebFetch 找资料，再走"新增"
│
├── 改总表某 cell
│   └── cell set LAYER BRANCH --text "新内容（含 [[N]](url) 引用）"
│
├── 改文档骨架 / 章节顺序 / 渲染细节
│   └── 编辑 templates/readme.md.j2 或 templates/_macros.j2，再 render
│
├── 加一个新子分支（如 K1）
│   └── SQL INSERT 新 section（subbranch 类型）+ 写 templates/prose/K1.md
│       + 改 templates/readme.md.j2 的 main_branches 迭代逻辑（如需）
│
└── 加新主分支 / 改 block 切分粒度 / 新 vendor 白名单
    └── 结构性调整：先告知用户改动范围，编辑 aiswstack_controller.py +
        templates/
```

## 常见任务配方

### 改散文（每层 intro / branch overview / 前言）

```bash
# 1) 找文件
.venv/bin/python scripts/aiswstack_controller.py prose path L13
# → /Users/luwei/work/Controversy/chat/AISW-stack/templates/prose/L13.md

# 2) 编辑（用 Read / Edit / Write）
#    L01–L34 / B1–J6 的 prose 文件**不含** ## 标题（标题由 layer/sub 名动态生成）
#    其他 prose 文件**包含** ## 或 ### 标题

# 3) 渲染
.venv/bin/python scripts/aiswstack_controller.py render
git diff chat/AISW-stack/README.md
```

### 查询（只读）

```bash
# 按 vendor 查 entries
.venv/bin/python scripts/aiswstack_controller.py entry list --vendor 高通

# 按 layer 查
.venv/bin/python scripts/aiswstack_controller.py entry list --layer L13

# 看某 entry 详情
.venv/bin/python scripts/aiswstack_controller.py entry show l13-sglang

# 看某 section 的 body（entries markdown）
.venv/bin/python scripts/aiswstack_controller.py section show L13

# 看某 section 的 prose
.venv/bin/python scripts/aiswstack_controller.py prose show L13

# 看某 cell
.venv/bin/python scripts/aiswstack_controller.py cell get L13 C

# 查孤儿 ref
.venv/bin/python scripts/aiswstack_controller.py ref list --orphan

# 自定义 SQL
.venv/bin/python scripts/aiswstack_controller.py query "
  SELECT layer_code, vendor, name, url
  FROM entries WHERE vendor='华为' ORDER BY layer_code"
```

### 改一个 entry 的 url

```bash
# 1) 找 slug
.venv/bin/python scripts/aiswstack_controller.py entry list --layer L13 --vendor 高通
# → l13-qualcomm-genie  L13  高通  Qualcomm Genie  https://...

# 2) 改
.venv/bin/python scripts/aiswstack_controller.py entry set-url l13-qualcomm-genie \
  --url https://www.qualcomm.com/developer/software/genie-sdk-v2

# 3) render
.venv/bin/python scripts/aiswstack_controller.py render
```

### 加一个 entry（已知 name / url / 所属 layer 与 vendor）

```bash
# 1) 看目标 section 现有 vendor-block 标签
.venv/bin/python scripts/aiswstack_controller.py section show L05 | head -30

# 2) 加 ref（按 url 去重）
NEW=$(.venv/bin/python scripts/aiswstack_controller.py ref add \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>' \
  --url https://www.hiascend.com/developer/devkit/mindstudio)

# 3) 加 entry
.venv/bin/python scripts/aiswstack_controller.py entry add L05 \
  --vb-label '华为' \
  --name 'MindStudio' \
  --url 'https://www.hiascend.com/developer/devkit/mindstudio' \
  --ref $NEW \
  --notes 'IDE：模型转换 / 算子调优 / profiling'

# 4) render + 验证
.venv/bin/python scripts/aiswstack_controller.py render
.venv/bin/python scripts/aiswstack_controller.py entry show l05-mindstudio
git diff chat/AISW-stack/README.md
```

### 改总表 cell

```bash
.venv/bin/python scripts/aiswstack_controller.py cell set L13 C \
  --text 'Isaac ROS[[113]](https://developer.nvidia.com/isaac/ros) GEMs runtime + 新方案[[X]](https://...)'

.venv/bin/python scripts/aiswstack_controller.py render
```

### 加 / 改 layer 段的 entries（不动散文）

如果改动复杂到不适合 `entry set-name` / `entry set-notes` 等粒度操作：

```bash
# 1) dump 当前 entries body
.venv/bin/python scripts/aiswstack_controller.py section show L13 > /tmp/L13.txt
# 提取 'body (NN chars):' 之后的内容到 /tmp/L13.md，编辑

# 2) 写回
.venv/bin/python scripts/aiswstack_controller.py section set-body L13 --file /tmp/L13.md

# 3) refresh-index + render
.venv/bin/python scripts/aiswstack_controller.py refresh-index
.venv/bin/python scripts/aiswstack_controller.py render
```

### 加 / 改 layer 段的散文（intro）

```bash
.venv/bin/python scripts/aiswstack_controller.py prose path L13
# → templates/prose/L13.md
# 用 Read / Edit / Write 改这个文件
.venv/bin/python scripts/aiswstack_controller.py render
```

### 改 ref

```bash
.venv/bin/python scripts/aiswstack_controller.py ref set 13 \
  --citation 'NVIDIA, "CUDA Toolkit," [Online]. Available: <https://developer.nvidia.com/cuda-toolkit>' \
  --url https://developer.nvidia.com/cuda-toolkit

.venv/bin/python scripts/aiswstack_controller.py render
```

注：layer 段 body 里 `[[13]](old_url)` 的 url **不会自动跟 ref.url 同步**。要批量更新所有引用该 ref 的 entry，逐个 `entry set-url`，或先查影响范围：

```bash
.venv/bin/python scripts/aiswstack_controller.py query "
  SELECT e.slug, e.url FROM entries e
  JOIN entry_refs er ON e.id = er.entry_id
  WHERE er.ref_num = 13"
```

### 改主模版（章节顺序 / 渲染细节）

```bash
# 直接编辑 templates/readme.md.j2 或 templates/_macros.j2
# Jinja2 语法；变量 layers / branches / sub_branches / section_body /
# section_heading / prose / refs / cells

.venv/bin/python scripts/aiswstack_controller.py render
```

### 加一个新主分支（结构性大改）

⚠ 最重的一类任务。流程：

1. 编辑 `scripts/aiswstack_controller.py` 扩 `MAIN_BRANCHES` 加 `("K", "新主分支名")`
2. 改散文：`templates/prose/top.md`、`summary-table.md`、`parallel-intro.md` 里所有 B–J / 9 条 之类措辞——直接编辑文件
3. 起 subagent 全栈深调研（参考"网络搜索语言"段；英文为主，中国实体走中文）→ 38 行 cell 内容 + 子分支 K1..Kn 划分 + entity 列表
4. 注册所有新 url 为 ref（`ref add`，按 url 去重）
5. `cell set L?? K --text ...` 写 38 个 cell
6. SQL `INSERT INTO sections` 新建 K 总览（branch type）+ K1..Kn 子分支（subbranch type）
7. 写 `templates/prose/K.md`（branch overview）和 `templates/prose/K1.md` ... `templates/prose/K6.md`（子分支 intro）
8. 用 `section set-body Kx --file ...` 注入各子分支的 entries markdown
9. `refresh-index` + `render` + 抽查

## 边界与陷阱

- **render 通过 Jinja2**：模版变量为 `layers` / `branches` / `sub_branches` / `section_body` / `section_heading` / `prose` / `refs` / `cells`。改模版后要保证这些变量名 / 结构没变。
- **section.body 现在只放 entries 部分**：layer/sub 的 intro 散文已搬到 prose 文件；改散文请改 prose 文件。
- **派生表 refresh-index 重建**：entries / layers / branches / entry_refs 都从 sections.body 派生。
- **ref 号永不复用**：`ref add` 总用 max+1。
- **`/` 不作分隔符**：parser 把 `A / B` 当一个 entry 名。要表达两个 entry 用 `A + B` 或 `A、B`。
- **vendor 白名单**：扩列表要改 Controller `KNOWN_VENDORS`，否则新 vendor 归入 `category`。
- **render 必须最后跑**：mutation 只动 db 或 prose 文件，render 才更新 README.md。
- **不要重跑 `aiswstack_migrate_to_jinja.py`**：它会用 sections.body 重新覆盖 prose 文件。脚本有 `--force` 守门。
- **使用 .venv 跑命令**：`jinja2` 装在 `.venv` 里，用 `.venv/bin/python` 调 controller。直接 `python3` 跑会 `ModuleNotFoundError: jinja2`。

## 网络搜索语言

默认用**英文**关键词搜索——英文一手信源覆盖面广、噪声少。

**例外**：搜索对象是**中国本土实体**（公司 / 产品 / 人名 / 政策 / 平台 / 微信公众号等）时用中文。双语都有的情况（华为 Ascend / DeepSeek / Qwen…）：先英文，再补中文交叉核对。

## 完整示例：用户说"把华为 MindStudio 加到 L05"

```bash
# 1) 看 L05 当前 body（entries 部分），确认 "华为" 标签存在
.venv/bin/python scripts/aiswstack_controller.py section show L05 | grep '\*\*'

# 2) 看是否已经有 MindStudio
.venv/bin/python scripts/aiswstack_controller.py query \
  "SELECT slug FROM entries WHERE name LIKE '%MindStudio%'"

# 3) WebSearch + WebFetch 确认官方页 → https://www.hiascend.com/developer/devkit/mindstudio

# 4) 加 ref
NEW=$(.venv/bin/python scripts/aiswstack_controller.py ref add \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>' \
  --url https://www.hiascend.com/developer/devkit/mindstudio)

# 5) 加 entry
.venv/bin/python scripts/aiswstack_controller.py entry add L05 \
  --vb-label '华为' \
  --name 'MindStudio' \
  --url 'https://www.hiascend.com/developer/devkit/mindstudio' \
  --ref $NEW \
  --notes 'IDE：模型转换 / 算子调优 / profiling'

# 6) render + 验证
.venv/bin/python scripts/aiswstack_controller.py render
.venv/bin/python scripts/aiswstack_controller.py entry show l05-mindstudio
git diff chat/AISW-stack/README.md
```

## 完整示例：用户说"L13 的 intro 段改一下措辞"

```bash
# 1) 找文件
.venv/bin/python scripts/aiswstack_controller.py prose path L13
# → /Users/luwei/work/Controversy/chat/AISW-stack/templates/prose/L13.md

# 2) 用 Read / Edit / Write 改这个文件（标题不在这里——标题由 layer 表的 name 来）

# 3) render
.venv/bin/python scripts/aiswstack_controller.py render
git diff chat/AISW-stack/README.md
```

## 改 Controller 源码时的注意点

需要改 `scripts/aiswstack_controller.py` 的场景：

- 新增主分支字母（A–J 之外）：改 `MAIN_BRANCHES`
- 新增 vendor 白名单：`KNOWN_VENDORS` / `VENDOR_ALIASES`
- 改 section_type 枚举
- 新增结构化命令（如 `section add` / `prose set`）
- 改 render 输出顺序（更常见的是改 templates/readme.md.j2）

改完跑：

```bash
.venv/bin/python scripts/aiswstack_controller.py refresh-index
.venv/bin/python scripts/aiswstack_controller.py render
git diff chat/AISW-stack/README.md
```
