---
name: aiswstack
description: Query and edit the AISW-stack knowledge base at chat/AISW-stack/. Use when the user asks about the layered AI software stack (L01–L38 × A–I branches × vendors like NVIDIA / 高通 / 联发科 / 瑞芯微), wants to add a new technology / product / layer / branch, edits an entry's URL or ref, or regenerates the README. The Model (index.sqlite3) is source of truth; the View (README.md) is rendered from it via the Controller (scripts/aiswstack_controller.py). All modifications go through Controller commands — never edit README.md by hand and never write SQL UPDATE/INSERT to the derived tables.
---

# AISW-stack skill

知识库：`chat/AISW-stack/` 下的 AI 软件栈分层索引。**MVC 单向流**：

| 角色 | 文件 | 修改方式 |
|---|---|---|
| **Model** | `chat/AISW-stack/index.sqlite3` | 通过 Controller 命令 |
| **Controller** | `scripts/aiswstack_controller.py` | 结构性调整时编辑此文件 |
| **View** | `chat/AISW-stack/README.md` | **只读输出**，由 `render` 生成 |

**铁律**：

1. **永远不要手工编辑 `README.md`**。它是 `render` 的产物，下次 `render` 会覆盖任何手工改动。
2. **永远不要写 SQL `UPDATE` / `INSERT` 改 db**。所有写操作走 Controller 命令（`add-block` / `replace` / `append` / `add-ref` / `delete-block`）。
3. **永远不要 UPDATE / INSERT 派生表**（layers / branches / entries / refs / branch_cells / entry_refs）——它们由 `render` 从 `blocks` 重建。
4. **每次改完都跑 `render`**。它重建派生索引并写出 README.md。

## Controller 命令速查

```bash
python3 scripts/aiswstack_controller.py <subcmd>

# 只读
  stats                              表行数
  query "SELECT ..."                 任意 SELECT（不要写 UPDATE / INSERT 到派生表）
  next-ref                           看下一可用引用号

# 写：所有修改必须通过下列命令
  add-ref --citation "..."           追加新引用到 refs block；stdout 输出新 ref 号
  add-block KEY --type T --title "..." --body "..." [--after KEY | --before KEY]
                                     新建 block（自动 shift order_idx）
  delete-block KEY                   删除 block
  replace KEY --old X --new Y [--all]
                                     在 block.body 中替换字符串（默认要求唯一匹配）
  append KEY --text "..."            追加到 block.body 末尾

# 输出
  render                             重建派生索引 + 写 README.md
```

## Schema

```
blocks(key PK, order_idx, block_type, title, body, layer_code, branch_code)
  block_type ∈ {doc_top, summary_table, main_overview, layer, branch_intro,
                branch, subbranch, crosscut, refs, other}
  key 示例: 'top', 'summary-table', 'main-overview', 'L13', 'parallel-intro',
           'C', 'C1', 'crosscut', 'refs'

# 派生（不要直接改）：
layers(code, position, name)
branches(code, parent_code, position, name)
refs(num, citation, url)
entries(id, slug, name, url, layer_code, branch_code, vendor, category,
        notes, block_key, source_line)
entry_refs(entry_id, ref_num)
branch_cells(layer_code, branch_code, raw_text, marker)
```

## 决策树

```
用户请求
├── 只是问问题（查询，没让改）
│   └── 用 query SELECT；不要改 db
├── 加 / 改 / 删一个 entry（已知信息）
│   └── 按"加 entry"配方
├── 加 entry 但用户没给名字 / 链接
│   └── 先 WebSearch / WebFetch 找资料，再走"加 entry"
├── 加 / 删一个子分支或一个 L 层
│   └── 按"加子分支" / "加 L 层"配方
└── 加新主分支 / 改 block 切分粒度 / 新 vendor 白名单
    └── 结构性调整：先告知用户改动范围，编辑 aiswstack_controller.py
```

## 常见任务配方

### 查询（只读）

```bash
# 某厂商所有 entries
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, name, url FROM entries WHERE vendor='高通' ORDER BY layer_code"

# 某层全部 entries
python3 scripts/aiswstack_controller.py query \
  "SELECT vendor, name, url FROM entries WHERE layer_code='L13'"

# 查某 block 当前内容（修改前必须先看）
python3 scripts/aiswstack_controller.py query \
  "SELECT body FROM blocks WHERE key='L13'"

# 哪些 ref 未被引用过（孤儿）
python3 scripts/aiswstack_controller.py query "
SELECT r.num, r.url FROM refs r
LEFT JOIN entry_refs er ON r.num = er.ref_num
WHERE er.entry_id IS NULL"
```

### 加 entry（已知 name / url / 所属 layer 或 branch）

```bash
# 1) 看目标 block 当前内容，决定插入位置
python3 scripts/aiswstack_controller.py query "SELECT body FROM blocks WHERE key='L13'"

# 2) 追加新引用条目，捕获新 ref 号
NEW=$(python3 scripts/aiswstack_controller.py add-ref \
  --citation 'VendorName, "Product Name," [Online]. Available: <https://product-home/>')
echo "got ref num: $NEW"

# 3) 找一个唯一锚点（最好是某个完整的 entry markdown 串）
#    在它后面追加 " + Product[[N]](url)"
python3 scripts/aiswstack_controller.py replace L13 \
  --old 'Qualcomm Genie[[882]](https://www.qualcomm.com/developer/software/genie-sdk)' \
  --new "Qualcomm Genie[[882]](https://www.qualcomm.com/developer/software/genie-sdk) + Product[[${NEW}]](https://product-home/)"

# 4) 渲染（重建索引 + 写 README）
python3 scripts/aiswstack_controller.py render

# 5) 验证
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, vendor, name, url FROM entries WHERE name='Product'"
git diff chat/AISW-stack/README.md
```

注意：

- `--old` 必须在该 block 内唯一匹配，否则 `replace` 报错；这时把 `--old` 加更多上下文让它唯一，或加 `--all`（谨慎）
- 用 `+` 把新 entry 接到现有 entry 后是约定格式（`A + B` 表示并列两个 entry；parser 把 ` + ` 视作分隔符）
- 若想新起一行 bullet，`--new` 里嵌入 `\n- ` 即可

### 加 entry（agent 需要先搜索）

```bash
# 1) WebSearch 找候选官方主页
# 2) WebFetch 确认存在并抓产品全名
# 3) 走"加 entry"流程
```

### 改 entry 的 url

```bash
# 找该 entry 所在 block 与现 url
python3 scripts/aiswstack_controller.py query \
  "SELECT block_key, url FROM entries WHERE slug='l13-vllm'"

# replace url 字符串（在 ](old) → ](new) 上做替换）
python3 scripts/aiswstack_controller.py replace L13 \
  --old '](https://old-url/)' \
  --new '](https://new-url/)'

python3 scripts/aiswstack_controller.py render
```

### 删 entry

```bash
# 1) 找 entry 所在 block 与精确 markdown 串
python3 scripts/aiswstack_controller.py query \
  "SELECT block_key FROM entries WHERE slug='...'"

# 2) replace 把 "、Name[[N]](url)" 替换为 ""
python3 scripts/aiswstack_controller.py replace L13 \
  --old '、Old Product[[N]](url)' --new ''

python3 scripts/aiswstack_controller.py render

# 注意：ref 号永不复用。如果该 ref 不再被任何 entry 引用，可以选择
# 从 refs block 删除 [N] 条目；但留着也无害（会成为 orphan ref）。
```

### 加子分支（如 C6）

```bash
python3 scripts/aiswstack_controller.py add-block C6 \
  --type subbranch \
  --title 'C6 新子分支名' \
  --body '一段 inline 列表内容，含至少一个 [[N]](url) 才会派生 entries。
例：示例方案[[N]](https://example.com/)、另一方案[[M]](https://other.com/)' \
  --branch-code C6 \
  --after C5

python3 scripts/aiswstack_controller.py render
```

### 加 L 层（如 L39）

涉及三处联动：新 layer block + summary-table 加新行 + main-overview 段表加新行。

```bash
# 1) 新 layer block，放在 L38 之后
python3 scripts/aiswstack_controller.py add-block L39 \
  --type layer \
  --title 'L39 新层名' \
  --body '一段引介散文。

**NVIDIA**：
- Product A[[N]](url)
- Product B[[M]](url)' \
  --layer-code L39 \
  --after L38

# 2) summary-table 加一行（9 列 cells）
python3 scripts/aiswstack_controller.py append summary-table \
  --text '| L39 新层名 | NVIDIA 方案 | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A |'

# 3) main-overview 段表加一行
python3 scripts/aiswstack_controller.py replace main-overview \
  --old '| | L34 | 垂直 Agent 应用 | 给开发者 / 设计师 / 等用 |' \
  --new '| | L34 | 垂直 Agent 应用 | 给开发者 / 设计师 / 等用 |
| 新段名 | L39 | 新层名 | 一句话视角 |'

python3 scripts/aiswstack_controller.py render
```

### 加新主分支（结构性调整）

⚠ 这是最重的一类任务，需要改 `scripts/aiswstack_controller.py` + 主表全表加列 + 新建总览 / 子分支块 + **逐层调研填新列**。先告知用户改动范围。**完整范例见文末"完整示例 3"**。骨架步骤：

1. 改 `MAIN_BRANCHES` 加 `("J", "新主分支名")`；如果用了 `J` 之外的字母确认 `BRANCH_TITLE_RE` 字符类够宽（脚本默认 `[A-Z]` 已够）
2. **必须**：扩展主表表头 + 分隔行 + 38 个 L 行末尾加新列。**不要全部默认填 `同 A`**——很多层在新分支有真实差异，需要起 subagent 逐层调研后再写入
3. 改 `top` block 引介里 `B–I 8 条并列分支` → `B–J 9 条并列分支`；改 `summary-table` 引介里同款描述；改 `parallel-intro` 里 "6 条分支" / "C–G 用数字后缀" 这种历史措辞
4. `add-block J --type branch` 总览段
5. `add-block J1 / J2 / ...` 子分支段
6. 把原"## 并列应用分支"H2 段尾的 `---` 分隔从原最末子分支移到新最末子分支
7. `render`

### 修 entry 名字 / 多处替换

把 `--old` 写完整（含 `[[N]](url)` 链接），`--new` 写新版完整文本。replace 默认要求 `--old` 在 block 内唯一；不唯一时加 `--all` 或把 `--old` 加更多上下文。

## 边界与陷阱

- **`/` 不作分隔符**：parser 把 `A / B` 当一个 entry 名。要表达两个 entry 用 `A + B`。
- **ref 号永不复用**：`add-ref` 总用 max+1。删除 ref 号会在序列留洞，正常。
- **entry slug 由 (layer/branch_code, name) 决定**：改 name 会改 slug，旧索引上的链接会断。
- **vendor 字段靠白名单**：扩列表需改 Controller 的 `KNOWN_VENDORS`，否则新 vendor 会归入 `category`。
- **render 完全无损**：连续两次 render 输出 md 应相同。若某次 render 让 md 变了别的（不是你想改的），说明 derive_indexes 与 render 之间的关系被破坏，反馈用户。
- **block.body 末尾的 `---\n`** 是 H2 之间的分隔符，保留它。
- **加内容前先 query 看 body**：盲改 `--old` 不在 body 中会报错，浪费 turn。

## 完整示例 1：用户说"加上华为 MindStudio 到 L05 编译器层"

```bash
# 1) 看 L05 当前 body，定位插入点
python3 scripts/aiswstack_controller.py query "SELECT body FROM blocks WHERE key='L05'"
# → 看到 "华为：CANN Graph Engine[[309]](...) ... + TBE / AscendC 算子编译器"

# 2) 搜索 + 确认资料
# WebSearch: "Huawei MindStudio Ascend developer tools"
# WebFetch:  https://www.hiascend.com/developer/devkit/mindstudio
# → 产品全名 "MindStudio"，官方页存在

# 3) 检查是否已存在
python3 scripts/aiswstack_controller.py query \
  "SELECT * FROM entries WHERE name LIKE '%MindStudio%'"

# 4) 加引用
NEW=$(python3 scripts/aiswstack_controller.py add-ref \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>')
echo "ref num: $NEW"

# 5) 把 MindStudio 接在 "AscendC 算子编译器" 后
python3 scripts/aiswstack_controller.py replace L05 \
  --old '+ TBE / AscendC 算子编译器' \
  --new "+ TBE / AscendC 算子编译器 + MindStudio[[${NEW}]](https://www.hiascend.com/developer/devkit/mindstudio)"

# 6) 渲染
python3 scripts/aiswstack_controller.py render

# 7) 验证
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, vendor, name, url FROM entries WHERE name='MindStudio'"
git diff chat/AISW-stack/README.md
```

## 完整示例 2：用户说"加上 MindStudio 到合适的层"

与示例 1 区别：层归属由 agent 判断。多两步：**了解产品功能**，**对照候选层挑最贴近的**。

```bash
# 1) 搞清楚 MindStudio 是什么
# WebSearch: "Huawei MindStudio Ascend toolkit"
# WebFetch:  https://www.hiascend.com/developer/devkit/mindstudio
# → 华为昇腾的桌面 IDE，集成模型转换 / 算子开发与调优 / profiling /
#   debugger / 推理部署辅助。定位类似 NVIDIA Nsight + TensorRT
#   converter 的合体。属于 CANN 工具链前端。

# 2) 看华为已经在哪些层有 entries，理解既有归属习惯
python3 scripts/aiswstack_controller.py query "
SELECT layer_code, name FROM entries WHERE vendor='华为' ORDER BY layer_code"
# → L01 davinci_manager / HCCN driver / npu-smi / Ascend Docker Runtime（驱动）
#   L02 HCCS / HCCL（互连 + 通信）
#   L03 CANN / AscendC（编程模型）
#   L04 CANN AOL / ACLNN（内核库）
#   L05 CANN Graph Engine / MindSpore Graph Engine（编译器）
#   L06 MindSpore（训练框架）
#   L07 MindFormers / ModelLink（分布式训练）
#   L13 MindIE / MindSpore Lite / Ascend vLLM（推理引擎）
#   L14 MindCluster / MindX / ModelArts（模型服务）
#   L15 华为云 ModelArts + Atlas 900（GPU 云）

# 3) 列候选层 + 用对照判断
#    MindStudio 含两类功能：
#      a) 模型转换 / 算子编译 / 图编译 → 紧贴 L05 编译器
#      b) profiling / debugger → 现有 38 层中没有专用"开发工具"层
#    Nsight / Nsight Compute 在原 md 中没有独立条目，开发者工具
#    历史上是和编译器一起归 L05（看 NVIDIA 那行：NVCC + NVRTC + PTX）。
#    → 选 L05，与 CANN Graph Engine 同 vendor 块；与 NVIDIA Nsight 走法一致。

# 4) 确认未存在 + 看 L05 当前结构定位插入点
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, name FROM entries WHERE name LIKE '%MindStudio%'"
python3 scripts/aiswstack_controller.py query \
  "SELECT body FROM blocks WHERE key='L05'"
# → 华为段："CANN Graph Engine[[309]](...)（GE）+ TBE / AscendC 算子编译器；
#   MindSpore Graph Engine[[310]](...)（MindSpore IR / MindIR）"

# 5) 后续与示例 1 相同
NEW=$(python3 scripts/aiswstack_controller.py add-ref \
  --citation 'Huawei, "MindStudio," [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>')

python3 scripts/aiswstack_controller.py replace L05 \
  --old '+ TBE / AscendC 算子编译器' \
  --new "+ TBE / AscendC 算子编译器 + MindStudio[[${NEW}]](https://www.hiascend.com/developer/devkit/mindstudio)（IDE：模型转换 / 算子调优 / profiling）"

python3 scripts/aiswstack_controller.py render

python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, vendor, name, url, notes FROM entries WHERE name='MindStudio'"
```

**判断层时的启发**：

- 先搜清楚**产品的主要功能**（一句话能说清属于"训练 / 推理 / 编译 / 工具链 / ..."哪类）
- 看**同 vendor 在其他层的归位习惯**，与之保持一致比"理论最准"重要
- 看**同类竞品**已经归到哪一层（NVIDIA Nsight ↔ Huawei MindStudio；NCCL ↔ HCCL）
- 候选层超过一个时，**告知用户两到三个选项 + 理由**，让用户选；不要静默挑一个
- 没有合适层时，**先停下来询问**：是建议加新层（L39）还是放到最贴近的现有层并加注

## 完整示例 3：用户说"加 J 学习 / 教育 主分支"

加新主分支是最重的结构性调整，做错最容易留漏洞。**先看四个不变量**：

1. **改 `MAIN_BRANCHES` + 确认 `BRANCH_TITLE_RE`**：是 `[A-Z]`（已够）；写死成 `[A-I]` 会让 `derive_indexes` 找不到 J 子分支、render FOREIGN KEY 报错
2. **主表 cell 必须挂 `[[N]](url)` 引用**：cell 里每个具名产品 / 数据集 / 基准 / 法规都要带引用号——既方便读者点链接，又强制 cell 内的每个名字都有溯源；引用号 == 该实体在子分支段的注册号（详见下文工作流）
3. **必须先全栈调研、后划子分支**：错误顺序（先建 5 个"应用类"子分支再调研主表）会让 cell 里出现的非应用类实体（数据集、评测基准、合规法规、仿真工具…）在子分支段无处安放
4. **散文措辞要同步**：`top` / `summary-table` 引介 / `parallel-intro` 都会带"B–I" / "8 条 / 6 条" / "C–G" / "A 主干" 之类，必须 grep 全清

### 标准流程（按此顺序执行）——七步

```
1. 改 Controller 源码（MAIN_BRANCHES、必要时 BRANCH_TITLE_RE）
2. 改散文：top / summary-table 引介 / parallel-intro / crosscut 里所有 B–I 类措辞
3. 起 subagent 全栈深调研 → 输出：
      a) 38 行主表 cell（产品名 + url，不含 ref 号——号 agent 后续分配）
      b) 子分支 J1..Jn 划分建议（每个 Jk 名 + 主题 + 应包含 entries）
      c) 完整 entity 列表（name + url + 在哪些 L 行 + 在哪些 Jk）
4. agent 注册所有 entity 引用（每个 url 一个 ref 号；查重复用）
5. 用 add-block 建 J 总览 + J1..Jn 子分支，body 含 [[N]](url)
6. 用 set-body 写主表 J 列，cell 内每个名字挂 [[N]](url)
7. render + 验证：主表每个 [[N]] 都能在 refs 表找到；J1..Jn entries 覆盖主表 cell 中的所有产品
```

#### 第 1 步：改 Controller 源码

```python
# scripts/aiswstack_controller.py
MAIN_BRANCHES = [
    ("A", "LLM / Agent"), ..., ("I", "影视娱乐"),
    ("J", "学习 / 教育"),     # ← 新加
]

BRANCH_TITLE_RE = re.compile(r"^([A-Z](?:\d+)?)\s+(.+)$")  # 确认是 [A-Z]，不是 [A-I]
```

#### 第 2 步：扩展主表（先全填占位 `同 A`）

用脚本：表头加 J 列、分隔行加 `---`、L01–L38 每行末尾加 `同 A`：

```bash
python3 << 'EOF' > /dev/null
import sqlite3, re
conn = sqlite3.connect("chat/AISW-stack/index.sqlite3")
body = conn.execute("SELECT body FROM blocks WHERE key='summary-table'").fetchone()[0]
def append_col(line, cell):
    return line.rstrip() + (" " if line.rstrip().endswith("|") else "") + cell + " |"
out = []
for ln in body.split("\n"):
    if ln.startswith("| L |"):
        out.append(append_col(ln, "J. 学习 / 教育"))
    elif re.match(r"^\|---\|", ln):
        out.append(append_col(ln, "---"))
    elif re.match(r"^\| L\d{2}\b", ln):
        out.append(append_col(ln, "同 A"))
    else:
        out.append(ln)
open("/tmp/summary-J-placeholder.txt", "w").write("\n".join(out))
EOF

python3 scripts/aiswstack_controller.py set-body summary-table \
  --file /tmp/summary-J-placeholder.txt
```

#### 第 3 步：起 subagent 逐层调研 J 列实际内容

⚠ 这一步**绝对不能跳**。教育栈在 L08 数据集、L10 垂直模型、L11 考试基准、L21 学生模型 / 知识图谱、L24 Socratic 循环、L29 COPPA / FERPA / 防作弊、L31 发音 ASR、L33 ChatGPT Edu / Claude for Education / Gemini for Education、L34 J1–J5 产品集合、L37 PhET / GeoGebra / Tinkercad 都有真实差异。盲填 `同 A` 是骗用户。

```bash
# 准备 subagent 的输入资料（dump 主表 38 行 A-I 列）
python3 << 'EOF' > /tmp/main-table-rows.md
import sqlite3, re
conn = sqlite3.connect("chat/AISW-stack/index.sqlite3")
body = conn.execute("SELECT body FROM blocks WHERE key='summary-table'").fetchone()[0]
for line in body.split("\n"):
    if re.match(r"^\| L\d{2}\b", line):
        cells = [c.strip() for c in line.strip("|").split("|")]
        L = cells[0]
        labels = ["A. LLM/Agent", "B. 科学计算", "C. 机器人", "D. 自动驾驶",
                  "E. 世界模型/3D", "F. 经典 CV", "G. 量化金融", "H. 游戏", "I. 影视娱乐"]
        print(f"## {L}")
        for lab, val in zip(labels, cells[1:10]):
            print(f"  - {lab}: {val}")
        print()
EOF
```

然后用 `Agent` 工具发起 subagent（**类型必须是 general-purpose，能调 WebSearch / WebFetch**）。
prompt 关键要点：

- 给出新分支名 / 覆盖范围（"J 学习 / 教育，含 AI 辅导 / 备课 / 评估 / 语言学习 / K-12 / 高校"）
- 给出 cell 写作约定（`同 A` / `同 A + 补丁` / 具体方案 / `—`）+ 现有 A–I 列的长度风格
- **要求 cell 中每个具名产品 / 数据集 / 基准 / 法规都附 url**——cell 输出格式为 `Name{{url}}, Name{{url}}, ...`，让 agent 后续替换 `{{url}}` 为 `[[N]](url)`。**不要让 subagent 输出"纯名字 / 无 url" 的 cell**——这正是上次的错误，导致主表 cell 没法点链接、且与子分支段失联。
- **要求 subagent 同步输出子分支划分建议**：不是预定 J1–J5 让 subagent 凑数，而是让 subagent 根据调研结果建议子分支数量与边界——如果发现教育数据集 / 评测基准 / 合规法规 / STEM 仿真这类"非应用类"差异，应建议独立成子分支
- 明列**重点调研层**：L08 数据集 / L09 后训练 / L10 垂直模型 / L11 评测基准 / L17 教育 API / L20 RAG / L21 学生模型 / L24 教学 Agent 模式 / L29 合规 + 防作弊 / L31 发音 / L32 教学课件 / L33 Edu 版对话 / L34 终端产品 / L37 STEM 仿真
- 明令搜索语言：英文优先，中国实体（作业帮 / 学而思 / 科大讯飞等）用中文
- 严格输出格式：(a) 38 行 `Lxx: <cell 含 {{url}} 占位>`；(b) 子分支建议 markdown 列表；(c) entity 表格 `| name | url | layers | sub-branches |`；(d) 一段总结

subagent 返回后：
1. 逐行检查 cell：太长精简到 4–6 个最有代表性的；确认每个具名实体都带 `{{url}}` 占位
2. 检查 entity 表格：去重，对每个 url 检查 refs 表是否已注册（`SELECT num FROM refs WHERE url=?`），有则复用号，无则 `add-ref` 新建
3. 形成 `url → ref_num` 映射
4. 用此映射把 cell 与子分支 body 里的 `Name{{url}}` 全部替换成 `Name[[N]](url)`

#### 第 4 步：把调研结果写入主表 J 列

```bash
python3 << 'EOF' > /dev/null
import sqlite3, re
J_CELLS = {
    "L01": "同 A",
    "L02": "同 A（多为单卡 / 推理）",
    ...
    "L34": "Khanmigo, Duolingo Max, MagicSchool, Gradescope, ...",
    "L37": "PhET, GeoGebra, Algodoo, Tinkercad（STEM 实验仿真）",
    "L38": "—",
}
conn = sqlite3.connect("chat/AISW-stack/index.sqlite3")
body = conn.execute("SELECT body FROM blocks WHERE key='summary-table'").fetchone()[0]
out = []
for line in body.split("\n"):
    m = re.match(r"^\| (L\d{2})\b", line)
    if m and line.rstrip().endswith("| 同 A |"):
        lc = m.group(1)
        new_line = line.rstrip()[:-len(" 同 A |")] + f" {J_CELLS[lc]} |"
        out.append(new_line)
    else:
        out.append(line)
open("/tmp/summary-J-final.txt", "w").write("\n".join(out))
EOF

python3 scripts/aiswstack_controller.py set-body summary-table \
  --file /tmp/summary-J-final.txt
```

#### 第 5 步：改散文里所有"B–I / 8 条 / 6 条 / C–G"措辞

```bash
# top block: "B–I. 并列应用分支" → "B–J"
python3 scripts/aiswstack_controller.py replace top \
  --old '**B–I. 并列应用分支**：...（旧列表）...影视娱乐——共享...' \
  --new '**B–J. 并列应用分支**：...（新列表，含 J 学习 / 教育）...共享...'

# summary-table 引介："9 列 / B–I 8 条" → "10 列 / B–J 9 条"
python3 scripts/aiswstack_controller.py replace summary-table \
  --old '横轴 9 列对应 **A 主干 + B–I 8 条并列分支**。' \
  --new '横轴 10 列对应 **A 主干 + B–J 9 条并列分支**。'

# parallel-intro: "6 条分支" / "C–G" 历史措辞
python3 scripts/aiswstack_controller.py replace parallel-intro \
  --old '下面 6 条分支（**B** 科学计算 ... / **G** 量化金融）与 L10–L34 ... C–G 用数字后缀（C1 / C2 / …）继续切。' \
  --new '下面 9 条分支（**B** 科学计算 ... / **J** 学习 / 教育）与 L10–L34 ... C–J 用数字后缀（C1 / C2 / …）继续切。'
```

#### 第 6 步：新建 J 总览 + 子分支 + 引用

```bash
# 1) 加 J1–J5 的引用（按需要的数量循环 add-ref）
NEW_J1_1=$(python3 scripts/aiswstack_controller.py add-ref \
  --citation 'Khan Academy, "Khanmigo," [Online]. Available: <https://www.khanmigo.ai/>')
# ...（每个 entry 一次）

# 2) 加 J 总览（引介散文）
python3 scripts/aiswstack_controller.py add-block J \
  --type branch \
  --title 'J 学习 / 教育栈：...（与 L33 / L34 并行）' \
  --body 'AI 进入教育栈分两条线...' \
  --branch-code J \
  --after I9

# 3) 加 J1–J5 子分支（每个 body 是 inline 列表，含 [[N]](url)）
python3 scripts/aiswstack_controller.py add-block J1 \
  --type subbranch \
  --title 'J1 智能辅导 / 答疑（Tutor / Q&A）' \
  --body "Khanmigo[[${NEW_J1_1}]](...)、..." \
  --branch-code J1 --after J
# ...（J2 / J3 / J4 / J5 类似，每个 --after 前一个）
```

#### 第 7 步：把 H2 段尾分隔移到新最末

```bash
# I9 原本是 H2 "## 并列应用分支" 段的末子分支，body 末尾有 "\n\n---"
python3 scripts/aiswstack_controller.py replace I9 \
  --old $'<I9 原末尾文字>\n\n---' \
  --new '<I9 原末尾文字>'

python3 scripts/aiswstack_controller.py append J5 --text $'\n---'
```

#### 第 8 步：render + 抽查

```bash
python3 scripts/aiswstack_controller.py render

# 抽查 J 列 + J 段
python3 scripts/aiswstack_controller.py query \
  "SELECT branch_code, name, url FROM entries WHERE branch_code LIKE 'J%'"

# 主表 J 列重点行
grep "^| L08\|^| L10\|^| L11\|^| L29\|^| L33\|^| L34\|^| L37" chat/AISW-stack/README.md

# 散文不再含 "B–I" / "8 条"
grep -E 'B–I|B-I|8 条' chat/AISW-stack/README.md && echo "⚠ 还有遗漏" || echo "散文已更新"

git diff --stat chat/AISW-stack/README.md
```

### 容易踩的坑

- `[A-I]` 写死在 `BRANCH_TITLE_RE`：加 J 后 `derive_indexes` 找不到 J 子分支，`render` 报 FOREIGN KEY 错。修：放宽到 `[A-Z]`
- 主表 J 列全 `同 A`：偷懒，不真。必须 subagent 调研
- 散文里"B–I" / "8 条" / "C–G"：3 处至少，全部要 replace
- `---` 分隔位置错：H2 段尾的 `---` 在原最末子分支 body 末尾，新加子分支后要挪到新最末
