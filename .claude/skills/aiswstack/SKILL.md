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

⚠ 需要改 `scripts/aiswstack_controller.py`。先告知用户改动范围。

1. 在 Controller 文件改 `MAIN_BRANCHES` 加 `("J", "新主分支名")`
2. 在 summary-table block 改表头加新列、每行加新单元格（用 replace 一行一行改）
3. 用 add-block 新建 `### J 总览块` 与子分支 `### J1` 等
4. `render`

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
