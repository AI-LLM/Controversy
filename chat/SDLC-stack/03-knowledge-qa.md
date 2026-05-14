# 2026-05-14：SDLC 栈 / 知识与答疑 层深度研究

> 系列子报告 D9。研究范畴：开发者获取"该怎么写这行代码 / 这个 API 是什么"答案的所有渠道。这一层是整个 SDLC 栈里被 Coding Agent 时代"完全掏空"的第一案例——不是被替代品打败，而是用户行为整体跳过这一层级，连"去找答案"这个动作本身都消失了。

## 1. 流量数据：从中枢到墓园

### 1.1 Pre-Agent 时代的基准

Stack Overflow 在 ChatGPT 出现前是开发者答疑事实上的中心节点。
- 2014 年峰值：约 **200,000 个新问题/月** [[1]](https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero)
- 2022 年 11 月（ChatGPT 发布前夕）：月活跃访客 **逾 1 亿** [[2]](https://expandedramblings.com/index.php/stack-overflow-statistics-and-facts/)
- 历史峰值时段 PV：早在 2014 年就已达 560M pageviews/月 [[3]](https://highscalability.com/stackoverflow-update-560m-pageviews-a-month-25-servers-and-i/)

Stack Overflow 2025 年的开发者调查（85,000+ 受访者）显示，AI 工具普及前 Google 搜索 + Stack Overflow 是开发者答疑的默认组合，使用 AI 工具的开发者从 2023 年的 70%、2024 年的 76% 增长到 2025 年的 **84%** [[4]](https://survey.stackoverflow.co/2025/ai/)。

### 1.2 ChatGPT 之后：80% 以上的崩塌

依 Stack Overflow Data Explorer 的官方数据：
- 2025 年 4 月新帖（问题+回答）比 2024 年 4 月下降 **64%**，比 2020 年峰值下降 **逾 90%** [[5]](https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/)
- 2024 年 6 月新问题同比下降 **34.8%**；2024 年 12 月同比下降 **40.2%** [[5]](https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/)
- 自 2022 年 11 月（ChatGPT 发布）以来，新问题量下降 **77%** [[6]](https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/)
- 2025 年 5 月月新问题已回落到 Stack Overflow 2009 年刚上线时的水平 [[5]](https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/)
- 据 2026 年 1 月 Slashdot/DevClass 综合数据，月新问题已从峰值 200,000 跌至 **接近 0**（约 300 量级） [[1]](https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero), [[6]](https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/)
- Similarweb 数据：2026 年 3 月 stackoverflow.com 流量环比下降 **10.28%**，全球排名从 1,501 跌至 1,962 [[7]](https://www.similarweb.com/website/stackoverflow.com/)

15 年的内容积累 + 6 亿月 PV 的中枢地位（⚠ 解读：依据 [[3]](https://highscalability.com/stackoverflow-update-560m-pageviews-a-month-25-servers-and-i/) 的 560M PV 与 2008-2023 时间跨度推断），被一个 chatbot 在 30 个月内基本归零。

### 1.3 流量去哪了：分流图

2025 年 Stack Overflow 开发者调查中的 AI 工具使用比例（"过去一年使用过"）[[4]](https://survey.stackoverflow.co/2025/ai/)：

| 工具 | 使用率 | 性质 |
|---|---:|---|
| ChatGPT | 82% | 通用对话 |
| GitHub Copilot | 68% | IDE 内 Chat + 补全 |
| Google Gemini | 47% | 通用对话 |
| Claude (Sonnet/Code) | 41% | 通用 + Agent |
| Perplexity | ~5% | 带引用的搜索 |

- **51% 的专业开发者每天使用 AI 工具** [[4]](https://survey.stackoverflow.co/2025/ai/)
- Claude Sonnet 在专业开发者中使用率（45%）高于学习者（30%），是少见的"专业向上偏移"工具 [[4]](https://survey.stackoverflow.co/2025/ai/)
- 23% 的开发者**经常**使用 AI agent，进一步从"问答"走向"代办" [[8]](https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/)

需要注意：通用搜索本身并未崩。Google 2024 年全球搜索量同比增 **21.6%**，约 14 billion/day，是 ChatGPT 的 373 倍 [[9]](https://sparktoro.com/blog/new-research-google-search-grew-20-in-2024-receives-373x-more-searches-than-chatgpt/)。被掏空的是 **"开发者问 Google 找 Stack Overflow"** 这一条特定的信息检索链路，而非整个 Web 搜索。

## 2. Stack Overflow 自救：裁员、卖数据、改名

### 2.1 两轮以上裁员

- 2023 年 5 月：裁员 **10%** [[10]](https://www.infoworld.com/article/2338488/developer-focused-portal-stack-overflow-lays-off-10-of-staff.html)
- 2023 年 10 月：裁员 **28%**（约 100+ 人），CEO Prashanth Chandrasekar 以"宏观经济和回归盈利路径"为由 [[11]](https://techcrunch.com/2023/10/17/stack-overflow-cuts-28-of-its-staff/)
- 2024 年又有一轮 **10% 量级** 的裁员（⚠ 作者综合估算：公开报道中未见 2024 年单独的裁员公告，可能与 2023-10 那轮 28% 被部分二手媒体重复报道有关；待进一步核实，本文按"已有不止两轮"的保守说法处理）

公司从约 540 人（2022 年峰值）压缩至约 400 人量级（⚠ 解读：540 来自 [10] 系列报道里"2022 年扩张"语境，400 为依两轮裁员推算），CEO 在 2024 年中报中提到 **10% 员工聚焦于 AI 战略** [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)。

### 2.2 卖数据：OverflowAPI 与三大客户

Stack Overflow 把 15 年累积的问答库做成订阅 API（OverflowAPI），向 LLM 厂商售卖：
- 2024 年 2 月：与 **Google Cloud** 合作，Gemini 模型可使用 Stack Overflow Google Cloud 相关问答；非排他 [[13]](https://itmagazine.com/2024/03/01/unpacking-googles-latest-deal-with-stack-overflow-a-testament-to-ai-giants-investing-in-data/)
- 2024 年 5 月：与 **OpenAI** 签 OverflowAPI 协议，财务条款未披露 [[14]](https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/)
- 后续与 **GitHub / 微软** 也有类似 partnership [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)

财务条款均未公开。可比参照：Reddit 与 Google 的内容许可约 **$60M/年** [[30]](https://aublr.org/2024/03/the-google-reddit-ai-deal-strategic-move-or-a-harbinger-of-licensing-agreements-to-come/)，与 OpenAI 估计 **$70M/年** [[14]](https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/)。Stack Overflow 实际授权金额预计低于 Reddit（用户基数/最新增量都不如 Reddit），但仍是其 2024-25 财年扭亏的关键变量。

### 2.3 收入反而增长？

母公司 Prosus 的 FY2025 年报（2025 年 3 月止）披露 [[15]](https://www.prosus.com/~/media/Files/P/prosus-corp-v2/results-reports-and-events-archive/latest-results/fy-2025/prosus-financial-results-fy25-booklet.pdf)：
- Stack Overflow 营收 **$115M**，本币口径同比 **+17%**
- EBIT 由 -$57M 改善至 **-$22M**
- 现金流接近盈亏平衡

收入逆势增长的来源：
1. **数据授权一次性入账 + 持续订阅**（OverflowAPI）
2. **Stack Overflow for Teams**（2025 年 11 月改名 **Stack Internal**），按 $6.50/seat/月起，企业内私域 Q&A 库 [[16]](https://stackoverflow.co/internal/)
3. **OverflowAI**（2024 年 5 月推出）—— 在 Teams 上叠加 AI 检索 add-on，捆绑提价 [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)
4. 招聘与广告业务（下滑中，但基数仍在）

**关键张力**：公开站的内容生产已近停摆——没有新问答，模型迟早把 2022 年之前的存量学完（⚠ 解读）。Stack Overflow 在卖一份正在贬值的资产（⚠ 解读）。devclass 2025 年 5 月报道其公开品牌正在 rebrand，与此同时月新问题已跌至个位百 [[17]](https://www.devclass.com/ai-ml/2025/05/13/stack-overflow-seeks-rebrand-as-traffic-continues-to-plummet-which-is-bad-news-for-developers/1623624)（"个位百"为依 [1]、[6] 综合估算的量级口径）。

## 3. 新需求与新基建：从"人读文档"到"Agent 读文档"

崩塌的不是"需要文档"，而是"人去翻文档"。新需求三条：

### 3.1 llms.txt 规范

由 Jeremy Howard（Answer.AI 联合创始人，fast.ai 作者）在 **2024 年 9 月** 提出 [[18]](https://www.answer.ai/posts/2024-09-03-llmstxt.html)：

- 放在 `/llms.txt`，类比 `robots.txt`
- 用 Markdown（不是 XML / JSON）写，因为读者是 LLM 而非传统爬虫，Markdown 更省 token、结构化又自然
- 文件结构：H1 项目名（必需）+ blockquote 摘要 + 若干 H2 区块链接到具体文档页 [[19]](https://llmstxt.org/)
- 解决的核心问题：LLM 上下文窗口装不下整站；HTML 转纯文本嘈杂；导航/广告/JS 干扰严重 [[19]](https://llmstxt.org/)
- 配套有 `llms-full.txt`（整站文档拼接版）供模型一次性吃进去

到 2025 年中已被 Mintlify、GitBook、Fern、Docusaurus、VitePress 等文档平台原生支持 [[31]](https://www.mintlify.com/library/best-llms-txt-platforms)（GitBook 2025-01 加入 llms.txt，2025-06 加入 llms-full.txt / 单页 .md）；Anthropic、Instructor、fast.ai 等已上线 [[20]](https://www.mintlify.com/blog/simplifying-docs-with-llms-txt), [[21]](https://python.useinstructor.com/blog/2025/03/19/instructor-adopts-llms-txt/)。

### 3.2 Context7：MCP 文档服务的标杆

Upstash 出品，GitHub 约 **55,100 stars**（2026 年 5 月） [[22]](https://github.com/upstash/context7)。工作原理 [[23]](https://upstash.com/blog/context7-mcp), [[24]](https://apidog.com/blog/context7-mcp-server/)：

1. **离线索引**：把成千上万个开源库的官方文档抓取、按版本切片、用 LLM 标注 / 改写为 snippet 形式存进数据库
2. **MCP 端点**：暴露两个工具
   - `resolve-library-id(name)` —— 把 `"react"` 解析为内部库 ID
   - `get-library-docs(id, topic, version)` —— 返回相关 snippet
3. **在 prompt 里触发**：用户在 Cursor / Claude Code / Windsurf 中写 `use context7` 关键词，agent 会先调 MCP 取最新文档，再生成代码
4. **服务化**：`https://mcp.context7.com/mcp` + `CONTEXT7_API_KEY` HTTP header，免本地维护

它把 "我需要查 Next.js 15 App Router 的 server action 写法" 这种问题，从"开浏览器 → 搜 SO / Google → 翻三个过期答案"压缩为一次 tool call。

### 3.3 IDE 内置答疑：Cursor @Web、Claude Code docs MCP

- **Cursor `@Web`**：通过 Exa.ai 检索 + 文档站爬虫，可在 chat 里实时查 Web 信息；可配置为"每次回答前都先 Web 搜" [[25]](https://docs.cursor.com/context/@-symbols/@-web)。`@library_name`（如 `@PyTorch`）直接调用内置文档索引
- **Claude Code**：通过 MCP 协议挂载任意文档服务器，官方推荐组合 Context7 + 各 SaaS 的 docs MCP（Stripe、Supabase、Vercel 等都已自建）
- **GitHub Copilot Chat**：嵌入 VS Code，68% 开发者使用 [[4]](https://survey.stackoverflow.co/2025/ai/)
- **Sourcegraph Cody**：从开源代码搜索起家，2025 年砍掉 Cody Free/Pro（2025 年 7 月 23 日终止免费/Pro 服务），只保留 Cody Enterprise，对应推出按 credit 计费的 Amp 产品 [[26]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans)。Cody 索引规模：单客户最高 250,000 repos / 10M LOC [[27]](https://sourcegraph.com/blog/cody-is-enterprise-ready)

三条线指向同一句话：**开发者不再"问网上有没有人问过这个问题"，而是让 agent 直接读项目代码 + 读官方文档 + 读 MCP 索引，自己出答案。**

## 4. 同行尸首：Phind 的速死

Phind 是 YC 系 AI 搜索引擎，专为开发者设计，2022-2024 年靠"LLM + Stack Overflow / GitHub issues / 文档检索 + 引用"快速起势 [[28]](https://intelligenttools.co/blog/improved-phind-shutdown-post)。

- 月搜索量 2024 年初峰值 **27,000+** 后两年跌 **91%** [[28]](https://intelligenttools.co/blog/improved-phind-shutdown-post)
- 2025 年末刚融资 **$10M**
- **2026 年 1 月 16 日突然关停**，无 sunset 期，融资到账后一个多月 [[29]](https://x.com/edzitron/status/2010932551511122050)

死因明确：当基础模型厂商（OpenAI / Anthropic / Google）原生具备 Web search + 文档检索后，"在 LLM 外面套一层开发者 UI"的差异化消失。Phind 既不掌握模型，也不掌握 IDE，也不掌握私域数据，**夹层产品的命运在大模型每升级一代时被收紧一次**。Kagi 这类付费搜索引擎在开发者群体里仍有小众价值（无追踪、无广告），但 5% 量级的渗透率谈不上替代品。

## 5. 本质判断：这是"行为整体跳过"的第一案例

把这一层级看清楚很重要——它不是"被新工具替代"，而是 **用户连"去找答案"这个动作都不再做**。这与"出租车被网约车替代"完全不同；那是同一动作（叫车）换载具。这一次的对应物是 **"叫车"这件事消失了，因为我已经在目的地"**。

具体语义层：

1. **"问代码本身"取代"问网上有没有人问过"**：Cursor / Claude Code 直接读 repo，agent 知道你这个 codebase 的 type、import path、test fixture 长什么样，比 SO 上的通用答案更精准。
2. **"Agent 读文档"取代"人读文档"**：llms.txt + MCP docs server 把文档从"网页"变成"工具调用"。文档站的 PV 也将进入下行通道（已有早期信号但数据未公开）。
3. **私域知识照样需要，但形态变了**：Stack Internal、Confluence + AI、Notion AI 这类把内部文档转成可被 agent 调用的 MCP / RAG 服务，仍有需求；但**前提是它们能成为 agent 的工具，而不是要求人去搜**。

### 5.1 对中型 SaaS 的命运预演

Zendesk、Intercom、Confluence search、Notion 这些 "知识/答疑/帮助" 中型 SaaS 在未来 3 年的可能轨迹（按 Stack Overflow 路径外推）：

| 路径 | 描述 | 时间窗 |
|---|---|---|
| **被掏空 + 卖数据** | Stack Overflow 模式：公开内容生产停摆，靠卖训练数据 / 私域托管续命 | 2026-2028 |
| **被 IDE / 平台原生吸收** | Phind 模式：差异化被基础模型覆盖后突然死亡 | 触发条件：所在垂直被原生平台覆盖 |
| **MCP 化转型** | Context7 模式：放弃直面用户，转做 agent 的工具供应商 | 需要 1-2 年改造产品形态 |
| **私域 + Agent ready** | Stack Internal / Notion AI 模式：以"被 agent 调用的可信内部知识层"重新定位 | 已有迹象，2026 起放量 |

Confluence 搜索、Zendesk Help Center 之类的 "人去搜的内部 Q&A 库" 大概率会经历与 Stack Overflow 公开站类似的流量损耗，但因为是私域内容，"卖给训练"这一退路不存在；唯一的出路是把自己重做成"对 agent 友好的工具调用层"。Notion 已经在做 Notion MCP；Atlassian 在 2025 年推出 Rovo 也是同方向尝试。

### 5.2 几条具体判断

- **Stack Overflow 2026 财年大概率仍会盈利**，但靠的是 Teams/Internal + 数据授权一次性收入，而非公开站。公开站作为"模型训练语料的来源"价值正在贬值，因为后 2022 年的新内容几乎没有。
- **官方文档站本身**（MDN、Python docs、React docs、AWS docs）在 2026-2027 进入流量下降通道。预测信号：搜索框流量先降，机器人 / MCP 调用先升；最终各 SaaS 会显式提供 `/llms.txt` 与 docs MCP 端点作为一等公民。
- **"AI 搜索"作为独立产品类别会被压扁成两端**：通用层（ChatGPT / Claude / Gemini 原生 search）+ 垂直 MCP 工具（Context7、Stripe MCP、AWS MCP……）。中间的 Phind、Kagi-for-devs、You.com 难以为继。
- **Stack Overflow 仍可能存在十年以上**，但作为"开发者答疑的中枢"角色已经死亡。它的内容将变成训练语料的化石层与企业内部知识库的产品壳，类似 Britannica 从知识中枢到品牌挂靠的轨迹。

## 信源

[1] Slashdot, "Stack Overflow Went From 200,000 Monthly Questions To Nearly Zero," Jan 2026. (峰值 200K → 现近零) [Online]. Available: <https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero>

[2] Expanded Ramblings, "Stack Overflow Statistics 2026: Q&A Volume, Community Reach," 2026. (峰期月活逾 1 亿) [Online]. Available: <https://expandedramblings.com/index.php/stack-overflow-statistics-and-facts/>

[3] High Scalability, "StackOverflow Update: 560M Pageviews a Month, 25 Servers," Jul 2014. (560M PV/月，25 台服务器) [Online]. Available: <https://highscalability.com/stackoverflow-update-560m-pageviews-a-month-25-servers-and-i/>

[4] Stack Overflow, "2025 Developer Survey – AI section," 2025. (84% 用 AI；ChatGPT 82%、Copilot 68%、Gemini 47%、Claude 41%；51% 每日使用) [Online]. Available: <https://survey.stackoverflow.co/2025/ai/>

[5] G. Orosz, "Stack Overflow is almost dead," *The Pragmatic Engineer*, 2025. (官方 Data Explorer：2025-04 新帖 vs 2024-04 −64%；vs 2020 −90%+；2025-05 回到 2009 水平) [Online]. Available: <https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/>

[6] T. Anderson, "Dramatic drop in Stack Overflow questions as devs look elsewhere for help," *DevClass*, Jan 2026. (自 ChatGPT 发布以来 −77%) [Online]. Available: <https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/>

[7] Similarweb, "stackoverflow.com Traffic Analytics," Mar 2026. (环比 −10.28%；全球排名 1,501 → 1,962) [Online]. Available: <https://www.similarweb.com/website/stackoverflow.com/>

[8] D. Mello, "23% of Devs Regularly Use AI Agents, per Stack Overflow Survey," *The New Stack*, 2025. [Online]. Available: <https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/>

[9] R. Fishkin, "Google Search Grew 20%+ in 2024; receives ~373X more searches than ChatGPT," *SparkToro*, 2025. (Google 5T 次/年，+21.6%) [Online]. Available: <https://sparktoro.com/blog/new-research-google-search-grew-20-in-2024-receives-373x-more-searches-than-chatgpt/>

[10] InfoWorld, "Developer-focused portal Stack Overflow lays off 10% of staff," 2023. [Online]. Available: <https://www.infoworld.com/article/2338488/developer-focused-portal-stack-overflow-lays-off-10-of-staff.html>

[11] D. Wiggers, "Stack Overflow cuts 28% of its staff," *TechCrunch*, Oct 17 2023. (CEO Prashanth Chandrasekar 以盈利路径为由) [Online]. Available: <https://techcrunch.com/2023/10/17/stack-overflow-cuts-28-of-its-staff/>

[12] P. Chandrasekar, "CEO Update: Building trust in AI is key to a thriving knowledge ecosystem," *Stack Overflow Blog*, Oct 22 2024. (10% 员工聚焦 AI；2024 H1 损失从 $44M 缩至 $13M) [Online]. Available: <https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/>

[13] IT Magazine, "Unpacking Google's Latest Deal With Stack Overflow," Mar 2024. (Google Cloud + Gemini 数据合作，非排他) [Online]. Available: <https://itmagazine.com/2024/03/01/unpacking-googles-latest-deal-with-stack-overflow-a-testament-to-ai-giants-investing-in-data/>

[14] K. Wiggers, "Stack Overflow signs deal with OpenAI to supply data to its models," *TechCrunch*, May 6 2024. (OverflowAPI；财务未披露；Reddit-OpenAI 估 ~$70M/年作对比) [Online]. Available: <https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/>

[15] Prosus, "FY2025 Financial Results Booklet," 2025. (Stack Overflow 营收 $115M；本币 +17%；EBIT -$57M → -$22M) [Online]. Available: <https://www.prosus.com/~/media/Files/P/prosus-corp-v2/results-reports-and-events-archive/latest-results/fy-2025/prosus-financial-results-fy25-booklet.pdf>

[16] Stack Overflow, "Stack Internal (formerly Stack Overflow for Teams)," 2025. ($6.50/seat/月起；2025-11 更名) [Online]. Available: <https://stackoverflow.co/internal/>

[17] T. Anderson, "Stack Overflow seeks rebrand as traffic continues to plummet," *DevClass*, May 13 2025. [Online]. Available: <https://www.devclass.com/ai-ml/2025/05/13/stack-overflow-seeks-rebrand-as-traffic-continues-to-plummet-which-is-bad-news-for-developers/1623624>

[18] J. Howard, "/llms.txt—a proposal to provide information to help LLMs use websites," *Answer.AI*, Sep 3 2024. [Online]. Available: <https://www.answer.ai/posts/2024-09-03-llmstxt.html>

[19] llms-txt, "The /llms.txt file – specification," 2024-2025. (H1 + blockquote + H2 链接清单；放在 `/llms.txt`) [Online]. Available: <https://llmstxt.org/>

[20] Mintlify, "Simplifying docs for AI with /llms.txt," 2025. [Online]. Available: <https://www.mintlify.com/blog/simplifying-docs-with-llms-txt>

[21] Instructor, "Instructor Adopts llms.txt: Making Documentation AI-Friendly," Mar 19 2025. [Online]. Available: <https://python.useinstructor.com/blog/2025/03/19/instructor-adopts-llms-txt/>

[22] upstash, "context7 — Up-to-date code documentation for LLMs and AI code editors," *GitHub*, 2024-2026. (约 55.1k stars) [Online]. Available: <https://github.com/upstash/context7>

[23] Upstash, "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt," Upstash Blog, 2024. (`resolve-library-id`、`get-library-docs` 两工具；版本切片) [Online]. Available: <https://upstash.com/blog/context7-mcp>

[24] Apidog, "How to Install and Use Context7 MCP Server," 2025. (HTTP MCP 端点 + API Key) [Online]. Available: <https://apidog.com/blog/context7-mcp-server/>

[25] Cursor, "@Web context documentation," 2025. (Exa.ai 检索；可配置每次回答前 Web 搜) [Online]. Available: <https://docs.cursor.com/context/@-symbols/@-web>

[26] Sourcegraph, "Changes to Cody Free, Pro, and Enterprise Starter plans," 2025. (2025-06-25 停止新签 Free/Pro；2025-07-23 终止；只剩 Enterprise + Amp) [Online]. Available: <https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans>

[27] Sourcegraph, "Cody is enterprise ready," 2024. (250K repos / 10M LOC 索引规模；2.5M 开发者使用 Sourcegraph) [Online]. Available: <https://sourcegraph.com/blog/cody-is-enterprise-ready>

[28] Intelligent Tools, "Why Did Phind Shut Down? The Real Story," 2026. (峰值 27K 搜索/月；两年跌 91%) [Online]. Available: <https://intelligenttools.co/blog/improved-phind-shutdown-post>

[29] E. Zitron, X post, 2026. (Phind 融资 $10M 后一个多月，2026-01-16 关停) [Online]. Available: <https://x.com/edzitron/status/2010932551511122050>
