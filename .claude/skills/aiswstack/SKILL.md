---
name: aiswstack
description: Query and edit the AISW-stack knowledge base at chat/AISW-stack/. Use when the user asks about the layered AI software stack (L01–L38 × A–J branches × vendors like NVIDIA / 高通 / 联发科 / 瑞芯微), wants to add a new technology / product / layer / branch, edits an entry's URL or ref, or regenerates the README. The Model (index.sqlite3) is source of truth; the View (README.md) is rendered from it via the Controller (scripts/aiswstack_controller.py). All modifications go through Controller commands — never edit README.md by hand. Mutations operate by stable keys (section key / entry slug / ref num / (layer, branch)), never by `--old/--new` string matching.
---

# AISW-stack skill

知识库：`chat/AISW-stack/` 下的 AI 软件栈分层索引。**MVC 单向流**：

| 角色 | 文件 | 修改方式 |
|---|---|---|
| **Model** | `chat/AISW-stack/index.sqlite3` | 通过 Controller 命令 |
| **Controller** | `scripts/aiswstack_controller.py` | 结构性调整时编辑此文件 |
| **View** | `chat/AISW-stack/README.md` | **只读输出**，由 `render` 生成 |

**铁律**：

1. **永远不要手工编辑 `README.md`**——`render` 会覆盖。
2. **不要 UPDATE / INSERT 派生表**（entries / cells / layers / branches / entry_refs）。它们由 `refresh-index` 从 `sections.body` + `refs` + `cells` 重建。
3. **不要在 mutation 里写 `--old/--new` 字符串匹配**。本 Controller 已废弃这种用法。改 entry 用 slug，改 ref 用 num，改 cell 用 (layer, branch)。需要批量修改 section 散文时用 `section set-body --file`。
4. **每次改完跑 `render`** 才会更新 README.md。

## 数据模型

```
sections   key PK, position, section_type, heading, body, layer_code, branch_code
             section_type ∈ {doc_top, summary_table, main_overview, layer,
                              branch_intro, branch, subbranch, crosscut,
                              refs, other}
             body 是 markdown 原貌——source of truth。

entries    slug PK, name, url, notes, section_key, layer_code, branch_code,
             vendor, category, position
             由 sections.body 派生（refresh-index 重建），用于按 slug 定位。

refs       num PK, citation, url                  source of truth
cells      layer_code, branch_code, text, marker  source of truth
            （summary_table.body 在 `cell set` 时自动从 cells 重建）

layers     code PK, position, name      派生
branches   code PK, parent_code, ...    派生
```

## 类层级（Controller API 的形状）

```
Document
  section(key)                  → Section
  entry(slug)                   → Entry
  ref(num)                      → Ref
  render()                      → str

Section（基类）
  set_heading(text) / set_body(text)
  render() → str

  ├── DocTop / MainOverview / BranchIntro / Branch / Crosscut / Other
  │     纯散文。get_body / set_body 即可全段替换。
  │
  ├── Layer / SubBranch
  │     body 是 markdown，但额外提供：
  │       add_entry(vb_label, name, url, ref_num, notes=None, separator=None)
  │       remove_entry(slug)
  │       set_entry_url(slug, url)
  │       set_entry_name(slug, name)
  │       set_entry_notes(slug, notes)
  │     这些方法内部用 `[[N]](current_url)` token 在 body 里定点替换。
  │
  ├── SummaryTable
  │     get_intro / set_intro
  │     get_cell(L, B) / set_cell(L, B, text)
  │     set_cell 后 body 由 cells 表重建。
  │
  └── Refs
        next_num() / add(citation, url=None) / get(num) / set(num, …) / remove(num)
        任一 mutation 后 body 由 refs 表重建。
```

## Controller CLI 速查

```bash
python3 scripts/aiswstack_controller.py <subcmd>

# 一次性
  init                          建空 schema
  migrate-from-blocks           从旧 blocks 表迁移到 sections（已完成；勿重跑）

# 读
  stats
  query "SELECT ..."            只读 SELECT
  section list
  section show KEY              打印 heading + body 全文
  entry list [--section K] [--layer L] [--branch B] [--vendor V]
  entry show SLUG
  ref list [--orphan]
  ref show NUM
  ref next-num
  cell get LAYER BRANCH

# 写（全部走稳定标识符，不用字符串匹配）
  section set-heading KEY --heading TEXT
  section set-body KEY (--body TEXT | --file F)     整段替换 body
                                                     适用于：散文段大改 /
                                                     layer/sub 内部大重排

  entry add SECTION_KEY --vb-label LBL --name N --url U --ref R
            [--notes T] [--separator SEP]
  entry remove SLUG
  entry set-url SLUG --url U
  entry set-name SLUG --name N
  entry set-notes SLUG --notes T

  ref add --citation TXT [--url URL]                返回 num；按 url 去重
  ref set NUM [--citation T] [--url U]
  ref remove NUM

  cell set LAYER BRANCH --text TEXT                 自动重建总表 body

# 输出
  render                        写 README.md
  refresh-index                 从 sections.body 重建 entries/cells/refs/layers/branches
                                （手改 body 后跑一次）
```

## 决策树

```
用户请求
├── 只是问问题（查询，没让改）
│   └── 用 query / entry list / ref list / cell get
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
├── 加 / 删一个子分支
│   └── section set-body KEY --file F（新建 section 待 Controller 扩展）
│
└── 加新主分支 / 改 block 切分粒度 / 新 vendor 白名单
    └── 结构性调整：先告知用户改动范围，编辑 aiswstack_controller.py
```

## 常见任务配方

### 查询（只读）

```bash
# 按 vendor 查 entries
python3 scripts/aiswstack_controller.py entry list --vendor 高通

# 按 layer 查
python3 scripts/aiswstack_controller.py entry list --layer L13

# 看某 entry 详情
python3 scripts/aiswstack_controller.py entry show l13-sglang

# 看某 section 原始 body
python3 scripts/aiswstack_controller.py section show L13

# 看某 cell
python3 scripts/aiswstack_controller.py cell get L13 C

# 查孤儿 ref（没被任何 entry 引用）
python3 scripts/aiswstack_controller.py ref list --orphan

# 自定义 SQL
python3 scripts/aiswstack_controller.py query "
  SELECT layer_code, vendor, name, url
  FROM entries WHERE vendor='华为' ORDER BY layer_code"
```

### 改一个 entry 的 url

```bash
# 1) 找到 entry 的 slug（按名字 / vendor / layer）
python3 scripts/aiswstack_controller.py entry list --layer L13 --vendor 高通
# → l13-qualcomm-genie  L13  高通  Qualcomm Genie  https://...

# 2) 改 url
python3 scripts/aiswstack_controller.py entry set-url l13-qualcomm-genie \
  --url https://www.qualcomm.com/developer/software/genie-sdk-v2

# 3) 渲染
python3 scripts/aiswstack_controller.py render
git diff chat/AISW-stack/README.md
```

> Controller 内部把 body 里 `[[N]](old_url)` 改成 `[[N]](new_url)`。`(N, url)` 全局唯一，找不到匹配会显式报错而不是误改。

### 改 entry 的名字 / 注解

```bash
python3 scripts/aiswstack_controller.py entry set-name l13-sglang --name "SGLang v2"
python3 scripts/aiswstack_controller.py entry set-notes l13-sglang \
  --notes "LMSYS / xAI；RadixAttention，结构化输出强（v2 增加 prefill）"
python3 scripts/aiswstack_controller.py render
```

注：改名字后 slug 不会自动迁移（避免破坏外部引用），新 entry 会出现于 `refresh-index` 后的索引里。如果想强制重新 slugify，跑：

```bash
python3 scripts/aiswstack_controller.py refresh-index
```

### 加一个 entry（已知 name / url / 所属 layer 与 vendor）

```bash
# 1) 看目标 section 里现有 vendor-block 标签
python3 scripts/aiswstack_controller.py section show L05 | head -30
# → 找到形如 "**华为**：..." 的标签

# 2) 加引用（按 url 去重，已存在则返回原 num）
NEW=$(python3 scripts/aiswstack_controller.py ref add \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>' \
  --url https://www.hiascend.com/developer/devkit/mindstudio)
echo "ref num: $NEW"

# 3) 把新 entry 插到 L05 的 "华为" 块
python3 scripts/aiswstack_controller.py entry add L05 \
  --vb-label '华为' \
  --name 'MindStudio' \
  --url 'https://www.hiascend.com/developer/devkit/mindstudio' \
  --ref $NEW \
  --notes 'IDE：模型转换 / 算子调优 / profiling' \
  --separator ' + '          # 仅 inline 布局需指定；bullets 不需要

# 4) 渲染 + 验证
python3 scripts/aiswstack_controller.py render
python3 scripts/aiswstack_controller.py entry show l05-mindstudio
git diff chat/AISW-stack/README.md
```

注意：

- `--vb-label` 是 section body 里 `**…**：` 的标签名字（如 `NVIDIA` / `华为` / `Intel`）。一个 section 内标签唯一。
- layout：Controller 看 vendor-block 紧跟的是 bullet 行还是同行 inline 列表来决定。inline 时若需自定义分隔符传 `--separator`（默认按现有内容推断）。

### 加 entry（agent 需先搜索）

```bash
# 1) WebSearch 找候选官方主页（英文优先；中国实体用中文）
# 2) WebFetch 确认存在并抓产品全名
# 3) 走"加 entry"流程
```

### 删 entry

```bash
python3 scripts/aiswstack_controller.py entry remove l05-mindstudio
python3 scripts/aiswstack_controller.py render
```

Controller 自动找到 entry 所在 bullet/inline 位置并剔除：

- 如果该 entry 独占一个 bullet 行 → 整行删
- 如果该 entry 在 inline 列表里 → 只剔除它 + 相邻一个分隔符

### 改 ref

```bash
# 改 ref 13 的 url 与 citation
python3 scripts/aiswstack_controller.py ref set 13 \
  --citation 'NVIDIA, "CUDA Toolkit," [Online]. Available: <https://developer.nvidia.com/cuda-toolkit>' \
  --url https://developer.nvidia.com/cuda-toolkit

# 删 ref
python3 scripts/aiswstack_controller.py ref remove 999

python3 scripts/aiswstack_controller.py render
```

ref 表是 source of truth。改 ref 后，refs section 的 body 由该表重建——render 会同步到 README。

但 layer 段 body 里 `[[13]](https://developer.nvidia.com/cuda)` 的 URL **不会自动跟随** ref.url 变化——entry 引用的 url 是该 entry 的 `[[N]](url)` token 里的 url，不是 ref.url。如要批量更新所有引用该 ref 的 entry，需要逐个 `entry set-url`，或写 SQL 找出影响范围：

```bash
python3 scripts/aiswstack_controller.py query "
  SELECT e.slug, e.url FROM entries e
  JOIN entry_refs er ON e.id = er.entry_id
  WHERE er.ref_num = 13"
```

### 改总表 cell

```bash
# 查看
python3 scripts/aiswstack_controller.py cell get L13 C

# 改写。cell 内可包含 [[N]](url) 引用，照常工作
python3 scripts/aiswstack_controller.py cell set L13 C \
  --text 'Isaac ROS[[113]](https://developer.nvidia.com/isaac/ros) GEMs runtime + 新方案[[X]](https://...)'

python3 scripts/aiswstack_controller.py render
```

`cell set` 自动重建 `summary-table` section 的 body（保留 intro 散文 + 表后 outro）。

### 加 / 改 layer 段的散文（intro / outro）或重新组织

如果改动复杂到不适合 `entry set-name` / `entry set-notes` 等粒度操作（比如想重排多个 vendor block、改 intro 几段散文），就 dump body → 编辑 → set-body：

```bash
# 1) dump 当前 body 到临时文件
python3 scripts/aiswstack_controller.py section show L13 | \
  sed -n '/^body /,/^$/p' | tail -n +2 > /tmp/L13.md
# 或更直接：
python3 -c "
import sqlite3
b = sqlite3.connect('chat/AISW-stack/index.sqlite3').execute(
    \"SELECT body FROM sections WHERE key='L13'\").fetchone()[0]
print(b)" > /tmp/L13.md

# 2) 用你喜欢的方式编辑 /tmp/L13.md

# 3) 写回
python3 scripts/aiswstack_controller.py section set-body L13 --file /tmp/L13.md

# 4) 重建 entries 索引（因为 body 大改，已派生的 entries 可能与 body 不一致）
python3 scripts/aiswstack_controller.py refresh-index

# 5) 渲染
python3 scripts/aiswstack_controller.py render
```

> `section set-body` 之后 Controller 已自动重建该 section 的 entries 索引；
> 但若同时改了 refs（如在 body 里写了新 ref 编号但忘了 `ref add`），用
> `refresh-index` 做全库扫描更稳妥。

### 加一个新子分支（如 K1）

当前 Controller 没有 `section add` 子命令；走两步：

```bash
# 1) 用 SQL 直接 INSERT 新 section 行（这是少数允许直接写 sections 的场景）
python3 scripts/aiswstack_controller.py query "
  INSERT INTO sections(key, position, section_type, heading, body, layer_code, branch_code)
  VALUES ('K1', 99.5, 'subbranch', 'K1 示例新子分支', '', NULL, 'K1')"

# 2) section set-body 给 body
python3 scripts/aiswstack_controller.py section set-body K1 --file /tmp/K1.md

# 3) refresh-index + render
python3 scripts/aiswstack_controller.py refresh-index
python3 scripts/aiswstack_controller.py render
```

注意 `position` 需要在两个相邻 section 之间——用小数（如 99.5）插入，避免移位。如果要保持整数 position，跑：

```bash
python3 scripts/aiswstack_controller.py query "
  UPDATE sections SET position = position + 1 WHERE position >= TARGET"
```
然后用整数 TARGET 插。

### 加一个新 L 层（如 L39）

同上，再加：

```bash
# 1) 新建 section L39
python3 scripts/aiswstack_controller.py query "
  INSERT INTO sections(key, position, section_type, heading, body, layer_code, branch_code)
  VALUES ('L39', 36.5, 'layer', 'L39 新层名', '一段引介散文。', 'L39', NULL)"

# 2) 主表加一行（每 cell 用 cell set；layer 行由 layers 表驱动）
# layers 表会在 refresh-index 时被重建——但需要保证 summary-table.body 含 L39 行。
# 最简单：dump summary-table.body，手工添 L39 行，set-body 回去
python3 -c "
import sqlite3
b = sqlite3.connect('chat/AISW-stack/index.sqlite3').execute(
  \"SELECT body FROM sections WHERE key='summary-table'\").fetchone()[0]
print(b)" > /tmp/summary.md
# 手工在 L38 行后加一行 `| L39 新层名 | ...A 内容... | ... 9 列 ... |`
python3 scripts/aiswstack_controller.py section set-body summary-table --file /tmp/summary.md
python3 scripts/aiswstack_controller.py refresh-index

# 3) main-overview 段表也加一行
python3 -c "
import sqlite3
b = sqlite3.connect('chat/AISW-stack/index.sqlite3').execute(
  \"SELECT body FROM sections WHERE key='main-overview'\").fetchone()[0]
print(b)" > /tmp/mo.md
# 手工添新行
python3 scripts/aiswstack_controller.py section set-body main-overview --file /tmp/mo.md

# 4) render
python3 scripts/aiswstack_controller.py render
```

### 加一个新主分支（结构性大改）

⚠ 最重的一类任务。改 Controller 源码 + 主表全表加列 + 新建总览 / 子分支 + **逐层调研填新列**。先告知用户改动范围。骨架步骤（基于 v3 类 API）：

1. 编辑 `scripts/aiswstack_controller.py`，扩 `MAIN_BRANCHES` 加 `("K", "新主分支名")`
2. 改散文：`top` / `summary-table` 引介 / `parallel-intro` 里所有 `B–J`、`9 条` 之类措辞——用 `section set-body --file` 整段改
3. 起 subagent 全栈深调研 → 返回 38 行 cell 内容 + 子分支 K1..Kn 划分 + entity 列表（含 name / url）
4. 注册所有新 url 为 ref（`ref add --citation X --url Y`；按 url 去重）
5. 用 `cell set L?? K --text ...` 写 38 个 cell（每 cell 内的具名实体都带 `[[N]](url)`）
6. 用 SQL `INSERT INTO sections` 新建 K 总览 + K1..Kn 子分支 section，配合 `section set-body` 写 body
7. `refresh-index` + `render` + 抽查

完整流程比 v1 / v2 时代干净得多——主要因为 ref/cell/entry 操作都是结构化命令，不再需要拼字符串。

## 边界与陷阱

- **section.body 是 source of truth**：内容修改全部最终落到这里。`render` 只是把 body 重排出来；从不修改 body。
- **派生表会被 refresh-index 重建**：entries / layers / branches / entry_refs 都从 sections.body 派生。`refresh-index` 后 entry 的 slug 可能轻微变化（如果同名 entry 顺序变了），但 ref num 与 cell key 永不变。
- **ref 号永不复用**：`ref add` 总用 max+1。删除 ref 号会在序列留洞，正常。
- **`/` 不作分隔符**：parser 把 `A / B` 当一个 entry 名。要表达两个 entry 用 `A + B` 或 `A、B`。
- **vendor 白名单**：扩列表要改 Controller `KNOWN_VENDORS`，否则新 vendor 会被归入 `category`。
- **加 entry 找不到 vb_label**：可能是 section 没有那个 vendor block。先 `section show` 确认现有标签，或用 SQL 看 entries 的 vendor 字段。`--vb-label` 不传则附加为新 bullet 到 body 末尾。
- **render 必须最后跑**：mutation 只动 db，render 才更新 README.md。

## 网络搜索语言

默认用**英文**关键词搜索——英文一手信源覆盖面广、噪声少。

**例外**：搜索对象是**中国本土实体**（公司 / 产品 / 人名 / 政策 / 平台 / 微信公众号等）时用中文。双语都有的情况（华为 Ascend / DeepSeek / Qwen…）：先英文，再补中文交叉核对。

## 完整示例：用户说"把华为 MindStudio 加到 L05"

```bash
# 1) 看 L05 当前 body，确认 "华为" 标签存在
python3 scripts/aiswstack_controller.py section show L05 | grep '\*\*'

# 2) 看是否已经有 MindStudio
python3 scripts/aiswstack_controller.py query \
  "SELECT slug FROM entries WHERE name LIKE '%MindStudio%'"

# 3) WebSearch + WebFetch 确认官方页 → https://www.hiascend.com/developer/devkit/mindstudio

# 4) 加 ref
NEW=$(python3 scripts/aiswstack_controller.py ref add \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>' \
  --url https://www.hiascend.com/developer/devkit/mindstudio)
echo "ref: $NEW"

# 5) 加 entry
python3 scripts/aiswstack_controller.py entry add L05 \
  --vb-label '华为' \
  --name 'MindStudio' \
  --url 'https://www.hiascend.com/developer/devkit/mindstudio' \
  --ref $NEW \
  --notes 'IDE：模型转换 / 算子调优 / profiling'

# 6) 渲染 + 验证
python3 scripts/aiswstack_controller.py render
python3 scripts/aiswstack_controller.py entry show l05-mindstudio
git diff chat/AISW-stack/README.md
```

## 改 Controller 源码时的注意点

需要改 `scripts/aiswstack_controller.py` 的场景：

- 新增主分支字母（A–J 之外）：改 `MAIN_BRANCHES` + 确认 `BRANCH_TITLE_RE` 范围够宽
- 新增 vendor 白名单：`KNOWN_VENDORS` / `VENDOR_ALIASES`
- 改 section_type 枚举
- 新增结构化命令（如 `section add` / `section move-position`）
- 改 render 输出顺序

改完后跑：

```bash
python3 scripts/aiswstack_controller.py refresh-index
python3 scripts/aiswstack_controller.py render
git diff chat/AISW-stack/README.md
```

确认 render 与 git 中原 README 字节级 diff 只有意图改动 + 表分隔行的空格规整化（cosmetic，可接受）。
