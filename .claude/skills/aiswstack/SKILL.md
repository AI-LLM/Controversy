---
name: aiswstack
description: Query and edit the AISW-stack knowledge base at chat/AISW-stack/. Use when the user asks about the layered AI software stack (L01–L38 × A–I branches × vendors like NVIDIA / 高通 / 联发科 / 瑞芯微), wants to add a new technology / product / layer / branch, edits an entry's URL or ref, or regenerates the README. The Model (index.sqlite3) is source of truth; the View (README.md) is rendered from it via the Controller (scripts/aiswstack_controller.py).
---

# AISW-stack skill

知识库：`chat/AISW-stack/` 下的 AI 软件栈分层索引。MVC 架构：

| 角色 | 文件 |
|---|---|
| **Model** | `chat/AISW-stack/index.sqlite3` — source of truth |
| **View** | `chat/AISW-stack/README.md` — 由 Model 渲染 |
| **Controller** | `scripts/aiswstack_controller.py` — import / render / query |

**核心不变量**：编辑只动 `blocks` 表的 `body` 字段（或新增 block 行）。其他表（layers / branches / entries / refs / branch_cells / entry_refs）是 import 时从 `blocks` 自动派生的查询索引，**不要直接 UPDATE / INSERT 它们**——会被下次 import 覆盖。

## Controller 命令速查

```bash
python3 scripts/aiswstack_controller.py <subcmd>

  import        README.md → db（清空重建；只在结构性调整后或者首次用）
  render        db → README.md（覆盖；改完 blocks 一定要跑）
  query "SQL"   执行任意 SQL（SELECT / UPDATE / INSERT 均可）
  stats         表行数 + 同步状态
  next-ref      返回下一个可用引用号（max(refs.num) + 1）
```

## Schema

```
blocks(key PK, order_idx, block_type, title, body, layer_code, branch_code)
  block_type ∈ {doc_top, summary_table, main_overview, layer, branch_intro,
                branch, subbranch, crosscut, refs, other}
  - key 示例: 'top', 'summary-table', 'main-overview', 'L13', 'parallel-intro',
              'C', 'C1', 'crosscut', 'refs'

# 派生索引（不要直接改）：
layers(code PK, position, name)
branches(code PK, parent_code, position, name)
refs(num PK, citation, url)
entries(id PK, slug UNIQUE, name, url, layer_code, branch_code, vendor,
        category, notes, block_key, source_line)
entry_refs(entry_id, ref_num)
branch_cells(layer_code, branch_code, raw_text, marker)
```

## 工作流

1. 接到请求 → 判断是**查询**（只读）还是**修改**
2. 修改类需要资料 → 必要时 `WebSearch` / `WebFetch` 找官方主页与名称
3. 用 `query "UPDATE blocks SET body=... WHERE key='...'"` 改 Model
4. `import` 重建派生索引
5. `render` 输出新 README.md
6. 用 `git diff chat/AISW-stack/README.md` 给用户看变更

## 常见任务 cookbook

### 查询（只读）

```bash
# 查某厂商所有 entries
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, name, url FROM entries WHERE vendor='高通' ORDER BY layer_code"

# 某层全部 entries
python3 scripts/aiswstack_controller.py query \
  "SELECT vendor, name, url FROM entries WHERE layer_code='L13' ORDER BY id"

# 找未被引用过的孤儿 refs
python3 scripts/aiswstack_controller.py query \
  "SELECT r.num, r.url FROM refs r
   LEFT JOIN entry_refs er ON r.num = er.ref_num
   WHERE er.entry_id IS NULL"

# 看某 block 的原文
python3 scripts/aiswstack_controller.py query \
  "SELECT body FROM blocks WHERE key='L13'"
```

### 添加 entry —— 已知 name + url + 所属 layer/branch

定位 block → 改 body → import → render。

```bash
# 1) 取下一个 ref 号
NEXTREF=$(python3 scripts/aiswstack_controller.py next-ref)

# 2) 在 refs block 末尾追加引用条目（注意 IEEE 风格）
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = body || char(10) || char(10) ||
  '[${NEXTREF}] VendorName, \"Product Name,\" [Online]. Available: <https://example.com/>'
WHERE key='refs'"

# 3) 在目标 layer block 的 body 里插入 `Name[[N]](url)`
#    先看当前 body 决定插入位置：
python3 scripts/aiswstack_controller.py query "SELECT body FROM blocks WHERE key='L13'"
#    然后用 REPLACE 把 entry 加到合适的 vendor 块内：
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = REPLACE(body,
  '+ Adreno SDK[[873]](https://developer.qualcomm.com/software/adreno-gpu-sdk)',
  '+ Adreno SDK[[873]](https://developer.qualcomm.com/software/adreno-gpu-sdk) + Product Name[[${NEXTREF}]](https://example.com/)'
) WHERE key='L13'"

# 4) 重建派生索引并渲染
python3 scripts/aiswstack_controller.py import
python3 scripts/aiswstack_controller.py render
```

⚠ 用 SQL 字符串插入时，**单引号要转义** (`''`)，**`/` 不可作分隔符**（parser 会把 `A / B` 视为 entry 名而非两个 entry）。

### 添加 entry —— agent 需要先搜索

1. `WebSearch` 找候选官方主页
2. `WebFetch` 确认主页存在 + 抓产品全名 / 描述
3. 走"已知 name + url"流程

### 修改 entry 的 url

```bash
# 找该 entry 所在 block 与现 url
python3 scripts/aiswstack_controller.py query \
  "SELECT block_key, url FROM entries WHERE slug='l13-vllm'"

# REPLACE 旧 url 为新 url
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = REPLACE(body,
  '](https://old-url/)',
  '](https://new-url/)')
WHERE key='L13'"

python3 scripts/aiswstack_controller.py import && \
python3 scripts/aiswstack_controller.py render
```

### 添加新子分支（如 C6）

子分支 = 新 `### Cn 名称` 三级标题块，归属 parent C。

```bash
# 1) 计算插入位置：取当前 C5 的 order_idx，+1
ORDER=$(python3 scripts/aiswstack_controller.py query \
  "SELECT order_idx + 1 FROM blocks WHERE key='C5'" | tail -1)

# 2) 把 order >= 新值的 block 全部后移
python3 scripts/aiswstack_controller.py query \
  "UPDATE blocks SET order_idx = order_idx + 1 WHERE order_idx >= ${ORDER}"

# 3) 插入新 block
python3 scripts/aiswstack_controller.py query "
INSERT INTO blocks(key, order_idx, block_type, title, body, branch_code)
VALUES ('C6', ${ORDER}, 'subbranch', 'C6 新子分支名',
        'inline 内容，含至少一个 [[N]](url) 才会有 entries\n', 'C6')"

python3 scripts/aiswstack_controller.py import && \
python3 scripts/aiswstack_controller.py render
```

### 添加新 L 层（如 L39）

涉及三处联动：新建 layer block + 更新主表 + 更新主干总览段表。

```bash
# 1) 在合适位置（L38 之后）插入新 layer block —— 按"子分支"模式先腾位
ORDER=$(python3 scripts/aiswstack_controller.py query \
  "SELECT order_idx + 1 FROM blocks WHERE key='L38'" | tail -1)
python3 scripts/aiswstack_controller.py query \
  "UPDATE blocks SET order_idx = order_idx + 1 WHERE order_idx >= ${ORDER}"
python3 scripts/aiswstack_controller.py query "
INSERT INTO blocks(key, order_idx, block_type, title, body, layer_code)
VALUES ('L39', ${ORDER}, 'layer', 'L39 新层名',
        '一段引介散文。\n\n- **NVIDIA**: Item[[N]](url)\n', 'L39')"

# 2) 在 summary-table block 末尾追加 L39 行（9 列 A–I cells）
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = body || char(10) ||
  '| L39 新层名 | ... | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A | 同 A |'
WHERE key='summary-table'"

# 3) 在 main-overview block 段表里追加一行
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = REPLACE(body,
  '| | L34 | 垂直 Agent 应用 | 给开发者 / 设计师 / 等用 |',
  '| | L34 | 垂直 Agent 应用 | 给开发者 / 设计师 / 等用 |' || char(10) ||
  '| 新段 | L39 | 新层名 | 一句话视角 |')
WHERE key='main-overview'"

python3 scripts/aiswstack_controller.py import && \
python3 scripts/aiswstack_controller.py render
```

### 添加新主分支（如在 I 之后加 J）

**结构性调整**——需要改 Controller。先告知用户改动范围再做。

1. 在 `scripts/aiswstack_controller.py` 修改：
   - `MAIN_BRANCHES` 常量末尾加 `("J", "新分支名")`
2. 在 summary-table block 改表头和每行（加新列）：
   ```sql
   UPDATE blocks SET body = REPLACE(body,
     '| H. 游戏 | I. 影视娱乐 |',
     '| H. 游戏 | I. 影视娱乐 | J. 新分支名 |') WHERE key='summary-table';
   -- 每行 L01..L38 都得加一列
   ```
3. 新建 `### J 总览块` 和子分支 `### J1`/`### J2` block
4. `import` + `render` + 检查 `branches` 表里有 J

### 删除 entry

不能直接删 entries 表（派生）。要从 blocks.body 删 `Name[[N]](url)` 子串，再 import / render。如果该 ref 不再被引用，可选择从 refs block 删 `[N]` 条目（注意会留洞，**不要重排现有 ref 号**）。

## 边界与陷阱

- **`/` 不作分隔符**：parser 把 `A / B` 当一个 entry 名。`A + B` 才视作两个 entry。
- **ref 号永不复用**：`next-ref` 总返回 max+1。删除 ref 号会在序列留洞，正常。
- **entry slug 由 (layer/branch_code, name) 决定**：改 name 会改 slug。
- **vendor 字段靠白名单**：扩列表改 Controller 的 `KNOWN_VENDORS`，否则新 vendor 会归入 `category`。
- **render 完全无损**：import → render 后 `diff` 应为空。若有 diff，是 parser 缺陷，反馈用户而非吞下。
- **blocks 是切片不是模板**：渲染时直接拼接 `## title\n\nbody`，不重新生成主表 / 段表——这些表在对应 block 的 body 里。
- **结构性改动后必须 import**：纯改 body 改完直接 render 也行（派生表只在 import 时重建），但若新增 / 删除 / 移动 block，必须 import。

## 完整示例：用户说"加上华为 MindStudio 到 L05 编译器层"

```bash
# 1) 搜资料
WebSearch: "Huawei MindStudio Ascend developer tools site:hiascend.com"
WebFetch: https://www.hiascend.com/developer/devkit/mindstudio
# → 确认产品全名 "MindStudio"，官方页存在

# 2) 检查是否已存在
python3 scripts/aiswstack_controller.py query \
  "SELECT * FROM entries WHERE name LIKE '%MindStudio%'"

# 3) 取下一个 ref 号
NEXTREF=$(python3 scripts/aiswstack_controller.py next-ref)
echo $NEXTREF  # e.g. 884

# 4) 加引用
python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = body || char(10) || char(10) ||
  '[${NEXTREF}] Huawei, \"MindStudio,\" [Online]. Available: <https://www.hiascend.com/developer/devkit/mindstudio>'
WHERE key='refs'"

# 5) 把 MindStudio 加到 L05 华为那一项（查现状定位插入点）
python3 scripts/aiswstack_controller.py query "SELECT body FROM blocks WHERE key='L05'"
# → 看到 "华为：CANN Graph Engine[[309]] ... + TBE / AscendC 算子编译器" 这一行

python3 scripts/aiswstack_controller.py query "
UPDATE blocks SET body = REPLACE(body,
  '+ TBE / AscendC 算子编译器',
  '+ TBE / AscendC 算子编译器 + MindStudio[[${NEXTREF}]](https://www.hiascend.com/developer/devkit/mindstudio)')
WHERE key='L05'"

# 6) 重建 + 渲染
python3 scripts/aiswstack_controller.py import
python3 scripts/aiswstack_controller.py render

# 7) 检查
python3 scripts/aiswstack_controller.py query \
  "SELECT layer_code, vendor, name, url FROM entries WHERE name='MindStudio'"
git diff chat/AISW-stack/README.md
```
