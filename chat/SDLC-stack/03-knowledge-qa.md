# 2026-05-14：SDLC 栈 / 知识与答疑 层深度研究

> 系列说明：本系列每一层用一个最贴合的 lens 切入。L01 的 lens 是"消费者切换"（工单的读者从人脑切到 LLM）。**本篇（L03 知识 / 答疑）的 lens 是"询问对象切换 (interlocutor switch)"**——开发者遇到问题时，提问的对象从"人类社区"切换为"模型权重 + 工具调用"。流量塌方（SO 新问题量 −77%、Phind −91%）是这个切换的**下游症状**，不是本质。次级 lens："**知识载体迁移**"——可调用的工程知识从分布在 UGC web 上的帖子，迁移到训练进 LLM 权重里的语料 + 通过 MCP 暴露的工具端点。llms.txt / Context7 是新载体的接口层，不是新需求。

## 1. 视角：为什么 L03 的本质不是流量

L03 表面上是一个 "流量被掏空" 的故事——Stack Overflow 月新问题从 200,000 跌到接近 0、自 ChatGPT 发布以来 −77% [[1]](https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero) [[2]](https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/)；Phind 月搜索 27,000 后两年跌 91%、2026-01-16 关停 [[3]](https://intelligenttools.co/blog/improved-phind-shutdown-post) [[4]](https://x.com/edzitron/status/2010932551511122050)。但如果只看流量曲线，会得出"用户换了一个搜索引擎"的结论——这就是 Phind 押错的位置。

真正发生的是**询问对象的更换**：

- **Pre-Agent**：开发者卡住 → 描述问题 → 向**人类社区**（Stack Overflow / Reddit / Discord / Slack）提问 → 等人答 / 搜旧贴 → 把答案翻译成自己 codebase 的语境。
- **Post-Agent**：开发者卡住 → 把问题（连同当前 buffer / repo 上下文）丢给**模型权重 + 工具**（ChatGPT / Claude Code / Cursor agent）→ 模型直接吐答案，或调 MCP tool（Context7、docs server）查到最新文档后再答。

询问对象一换，三件事同时发生：

1. **生产侧激励瓦解**。没人答了，因为没人问了；没人问了，因为没人看了。Stack Overflow 答题者过去的奖励是声望积分 + 被全网开发者 google 到的"教师价值"。当全网开发者改问 LLM，这两个奖励同时归零。Pragmatic Engineer 的 Data Explorer 截图：2025 年 4 月新帖比 2020 年峰值跌 90%+，2025 年 5 月月新问题已回到 2009 年刚上线的水平 [[5]](https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/)。
2. **载体迁移**。可被检索的工程知识从"分布在 UGC web 上的人类对话"迁移到"训练进权重的 + 通过 tool call 实时取的"。llms.txt / Context7 / IDE 内置 docs MCP 都是新载体的**接口层**——给新询问对象提供更省 token、更结构化的访问路径。
3. **流量是副产物**。SO 的流量塌方、文档站 PV 即将进入下行通道、Phind 的速死，都是询问对象切换之后的自然结果。任何还假设"用户会主动来读/搜"的产品都要重审。

> ⚠ **解读**：以下章节把"询问对象切换"作为主轴，流量数据作为佐证。这与原版（namespace.so 的"流量框架"）的差别在于：流量框架只能描述"塌了多少"，无法解释"为什么内容生产同步停摆"和"为什么 MCP/llms.txt 是新基建"。切换框架直接给出机制。

## 2. 询问对象的三态

把三种询问对象并列对照，可以看出 L03 不是单向替代，而是**状态分裂**：

| 询问对象 | 代表产品 | 渠道 | 生产侧奖励 | 2025-26 状态 |
|---|---|---|---|---|
| 人问人 | Stack Overflow / Reddit / Discord | 浏览器搜索 + UGC 帖子 | 声望、SEO 长尾、社区身份 | 急剧萎缩（SO −77%、新问题接近 0） |
| 人问模型 | ChatGPT / Claude / Gemini | Web app + 桌面端 | 无（不需要生产侧） | 主流（专业开发者 51% 每日使用 [[6]](https://survey.stackoverflow.co/2025/ai/)） |
| Agent 问工具 | Claude Code + MCP / Cursor + Context7 | 工具调用 | 工具方按调用计费 / 生态卡位 | 高速放量（Context7 ~55.1k stars [[7]](https://github.com/upstash/context7)） |

2025 年 Stack Overflow 开发者调查（85,000+ 受访者）里的 AI 工具使用率，反映的是"**人问模型**"那一态 [[6]](https://survey.stackoverflow.co/2025/ai/)：

| 工具 | 使用率 |
|---|---:|
| ChatGPT | 82% |
| GitHub Copilot | 41%（IDE 内 Chat + 补全） |
| Google Gemini | 47% |
| Claude (Sonnet/Code) | 24% |
| Perplexity | ~5% |

AI 工具整体渗透率从 2023 年的 70%、2024 年的 76% 增长到 2025 年的 **84%** [[6]](https://survey.stackoverflow.co/2025/ai/)。51% 的专业开发者每日使用，23% 经常使用 agent，进一步把询问对象从"人问模型"推到"agent 问工具" [[8]](https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/)。

需要注意：通用搜索本身没有崩。Google 2024 年全球搜索量同比增 21.6%、约 14 billion/day、是 ChatGPT 的 373 倍 [[9]](https://sparktoro.com/blog/new-research-google-search-grew-20-in-2024-receives-373x-more-searches-than-chatgpt/)。被掏空的是"开发者问 Google 找 SO"这条**特定的人问人路径**，而非整个 Web 搜索。这点 §4（Phind）会回来。

## 3. SO 自救：旧载体资产的清算

询问对象切换之后，Stack Overflow 手里剩下的不再是"中枢节点"，而是一份**旧载体的存量化石**——15 年累积的高质量人类问答语料。它的所有自救动作都可以放在"清算旧资产 + 押宝私域"的框架下看，而不是"修复流量"。

### 3.1 裁员把成本结构对齐萎缩后的业务

- 2023 年 5 月：裁员 **10%** [[10]](https://www.infoworld.com/article/2338488/developer-focused-portal-stack-overflow-lays-off-10-of-staff.html)
- 2023 年 10 月：裁员 **28%**（约 100+ 人），CEO Prashanth Chandrasekar 以"宏观经济和回归盈利路径"为由 [[11]](https://techcrunch.com/2023/10/17/stack-overflow-cuts-28-of-its-staff/)
- 2024 年另有一轮 **10% 量级** 的调整（⚠ 公开报道未见独立公告，作者综合估算；本文保留"已有不止两轮"的保守口径）

CEO 在 2024 年中报里透露 **10% 员工聚焦于 AI 战略** [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)——把组织资源从"运营公开站"转向"包装数据 + 卖私域"。

### 3.2 OverflowAPI：把 UGC 化石卖给新询问对象的供应商

Stack Overflow 把 15 年累积的问答库做成订阅 API，向 LLM 厂商售卖：

- 2024 年 2 月：与 **Google Cloud** 合作，Gemini 模型可使用 SO Google Cloud 相关问答，非排他 [[13]](https://itmagazine.com/2024/03/01/unpacking-googles-latest-deal-with-stack-overflow-a-testament-to-ai-giants-investing-in-data/)
- 2024 年 5 月：与 **OpenAI** 签 OverflowAPI 协议，财务条款未披露 [[14]](https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/)
- 后续与 **GitHub / 微软** 也有 partnership [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)

可比参照：Reddit 与 Google 的内容许可约 **$60M/年** [[15]](https://aublr.org/2024/03/the-google-reddit-ai-deal-strategic-move-or-a-harbinger-of-licensing-agreements-to-come/)，与 OpenAI 估计 **$70M/年** [[14]](https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/)。SO 实际授权金额预计低于 Reddit（用户基数和最新增量都更弱），但仍是 2024-25 财年扭亏的关键变量。

这笔交易的本质：**询问对象切换后，旧载体上的存量内容仍有一次性的训练价值**——它们是新询问对象（模型权重）的食物。但这笔钱的可持续性受制于一个事实：后 2022 年的新内容几乎没有，模型迟早把存量学完（⚠ 解读）。

### 3.3 私域：Stack Internal + OverflowAI

- **Stack Overflow for Teams**（2025 年 11 月改名 **Stack Internal**）：$6.50/seat/月起，企业内私域 Q&A 库 [[16]](https://stackoverflow.co/internal/)
- **OverflowAI**（2024 年 5 月推出）：在 Teams 上叠加 AI 检索，捆绑提价 [[12]](https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/)

Prosus FY2025 年报（截至 2025 年 3 月）披露 SO 营收 **$115M**，本币口径同比 **+17%**；EBIT 由 -$57M 改善至 **-$22M** [[17]](https://www.prosus.com/~/media/Files/P/prosus-corp-v2/results-reports-and-events-archive/latest-results/fy-2025/prosus-financial-results-fy25-booklet.pdf)。收入逆势增长几乎全部来自数据授权 + Teams/Internal——**公开站作为产品的财务贡献已被替换为"内容资产 + 私域 SaaS"两条线**。devclass 2025 年 5 月报道 SO 公开品牌正在 rebrand，同时月新问题已跌至个位百量级 [[18]](https://www.devclass.com/ai-ml/2025/05/13/stack-overflow-seeks-rebrand-as-traffic-continues-to-plummet-which-is-bad-news-for-developers/1623624)（"个位百"为依 [[1]](https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero)、[[2]](https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/) 综合估算的量级口径）。

## 4. 新载体的接口层：llms.txt / Context7 / IDE @docs

新询问对象（模型权重 + 工具）有它自己的访问偏好：

- 上下文窗口装不下整站；HTML 转纯文本嘈杂；导航/广告/JS 干扰严重
- 偏好 Markdown 而非 XML/JSON（更省 token、结构化又自然）
- 偏好"工具调用一次取一段相关 snippet"而非"爬完再过滤"

llms.txt / Context7 / IDE @docs 是这三个偏好的回应——它们不是新需求，是**新询问对象的工具协议**。把它们和旧的 robots.txt / sitemap.xml 放在一起看就清楚：后者服务搜索引擎爬虫（旧载体的接口），前者服务模型与 agent（新载体的接口）。

### 4.1 llms.txt 规范

由 Jeremy Howard（Answer.AI 联合创始人、fast.ai 作者）在 **2024 年 9 月 3 日** 提出 [[19]](https://www.answer.ai/posts/2024-09-03-llmstxt.html)：

- 放在 `/llms.txt`，类比 `robots.txt`
- 用 Markdown 写
- 文件结构：H1 项目名（必需）+ blockquote 摘要 + 若干 H2 区块链接到具体文档页 [[20]](https://llmstxt.org/)
- 配套有 `llms-full.txt`（整站文档拼接版）供模型一次性吃进去

到 2025 年中已被 Mintlify、GitBook、Fern、Docusaurus、VitePress 等文档平台原生支持 [[21]](https://www.mintlify.com/library/best-llms-txt-platforms)；Anthropic、Instructor、fast.ai 等已上线 [[22]](https://www.mintlify.com/blog/simplifying-docs-with-llms-txt) [[23]](https://python.useinstructor.com/blog/2025/03/19/instructor-adopts-llms-txt/)。GitBook 2025-01 加入 llms.txt，2025-06 加入 llms-full.txt / 单页 .md。

### 4.2 Context7：MCP 文档服务的标杆

Upstash 出品，GitHub 约 **55,100 stars**（2026 年 5 月） [[7]](https://github.com/upstash/context7)。工作原理 [[24]](https://upstash.com/blog/context7-mcp) [[25]](https://apidog.com/blog/context7-mcp-server/)：

1. **离线索引**：把成千上万个开源库的官方文档抓取、按版本切片、用 LLM 标注 / 改写为 snippet 形式存进数据库
2. **MCP 端点**：暴露两个工具
   - `resolve-library-id(name)` —— 把 `"react"` 解析为内部库 ID
   - `get-library-docs(id, topic, version)` —— 返回相关 snippet
3. **在 prompt 里触发**：用户在 Cursor / Claude Code / Windsurf 中写 `use context7` 关键词，agent 会先调 MCP 取最新文档，再生成代码
4. **服务化**：`https://mcp.context7.com/mcp` + `CONTEXT7_API_KEY` HTTP header，免本地维护

它把"我需要查 Next.js 15 App Router 的 server action 写法"这种问题，从"开浏览器 → 搜 SO/Google → 翻三个过期答案"压缩为一次 tool call。**这是询问对象切换之后的新基础设施层**——和当年 Google Sitemap 之于搜索时代是同一类位置。

### 4.3 IDE 内置：Cursor @Web、Claude Code docs MCP

- **Cursor `@Web`**：通过 Exa.ai 检索 + 文档站爬虫，可在 chat 里实时查 Web 信息；可配置为"每次回答前都先 Web 搜" [[26]](https://docs.cursor.com/context/@-symbols/@-web)。`@library_name`（如 `@PyTorch`）直接调用内置文档索引
- **Claude Code**：通过 MCP 协议挂载任意文档服务器，官方推荐组合 Context7 + 各 SaaS 自建的 docs MCP（Stripe、Supabase、Vercel 等）
- **GitHub Copilot Chat**：嵌入 VS Code，41% 开发者使用 [[6]](https://survey.stackoverflow.co/2025/ai/)
- **Sourcegraph Cody**：2025 年 6 月 25 日停止新签 Free/Pro、7 月 23 日终止，只保留 Cody Enterprise + 按 credit 计费的 Amp 产品 [[27]](https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans)。Cody 索引规模：单客户最高 250,000 repos / 10M LOC [[28]](https://sourcegraph.com/blog/cody-is-enterprise-ready)

这三个产品方向放在一起的共同点：**开发者不再"问网上有没有人问过这个问题"，而是让 agent 直接读项目代码 + 调 docs MCP 取官方文档**。

## 5. Phind：押错询问对象的速死案例

Phind 是 YC 系 AI 搜索引擎，专为开发者设计，2022-2024 年靠"LLM + Stack Overflow / GitHub issues / 文档检索 + 引用"快速起势 [[3]](https://intelligenttools.co/blog/improved-phind-shutdown-post)。

- 月搜索量 2024 年初峰值 **27,000+** 后两年跌 **91%** [[3]](https://intelligenttools.co/blog/improved-phind-shutdown-post)
- 2025 年末刚融资 **$10M**
- **2026 年 1 月 16 日突然关停**，无 sunset 期，融资到账后一个多月 [[4]](https://x.com/edzitron/status/2010932551511122050)

如果用"流量"lens 解释 Phind 之死，只能说"被 ChatGPT 抢了"。但用"询问对象"lens，原因更清晰：**Phind 假设的询问对象仍是"人去搜索引擎里搜"**，只是换了一个比 Google 更聪明的搜索引擎。它没意识到询问对象本身在向"模型权重 + 工具"迁移——结果是：

- 当基础模型厂商（OpenAI / Anthropic / Google）原生具备 Web search + 文档检索，"人问模型"这一态直接被 ChatGPT 占据，Phind 在中间被压扁
- 当询问对象进一步切到"agent 问工具"，Phind 既不掌握 IDE（不是 Cursor），也不掌握 MCP 工具（不是 Context7），也不掌握私域数据（不是 Stack Internal）——三态全部错过

Phind 既不掌握模型，也不掌握 IDE，也不掌握工具协议；**夹层产品的命运在大模型每升级一代时被收紧一次**（⚠ 解读）。Kagi 这类付费搜索引擎在开发者群体里仍有小众价值（无追踪、无广告），但 5% 量级渗透率（⚠ 量级参考：[[6]](https://survey.stackoverflow.co/2025/ai/) 中 Perplexity 约 5%，Kagi 未单列）谈不上替代品。

## 6. 中型 SaaS 命运：按"能否成为 agent 的被询问对象"分类

把"询问对象切换"作为判据，Zendesk、Intercom、Confluence Search、Notion、MDN、各 SaaS 的 docs 站等"知识/答疑/帮助"中型产品在未来 3 年的命运可以分四类，**不是按流量存活分类，而是按"能否成为 agent 的被询问对象"分类**：

| 路径 | 能否被 agent 询问 | 代表 | 时间窗 |
|---|---|---|---|
| **MCP 化转型** | 能：把产品重做成 agent 的 tool 端点 | Context7、Stripe MCP、Supabase MCP、Atlassian Rovo | 已发生，2025-26 是窗口期 |
| **私域 + Agent ready** | 能：以"被 agent 调用的可信内部知识层"重新定位 | Stack Internal、Notion AI、Confluence + Rovo | 2026 起放量 |
| **被掏空 + 卖数据** | 不能直接被询问，但内容是新询问对象的训练食物 | Stack Overflow 公开站 | 2026-2028 持续清算 |
| **被 IDE / 平台原生吸收** | 不能：差异化被基础模型 / IDE 覆盖后突然死亡 | Phind、未转型的开发者搜索引擎 | 触发条件：所在垂直被原生平台覆盖 |

Confluence 搜索、Zendesk Help Center 之类"人去搜的内部 Q&A 库"会经历与 SO 公开站类似的流量损耗——**但因为是私域内容，"卖训练"这一退路不存在**；唯一出路是把自己重做成 agent 友好的工具调用层。Notion 已在做 Notion MCP；Atlassian 2025 年推出 Rovo 也是同方向尝试。

### 6.1 几条具体判断

- **Stack Overflow 2026 财年大概率仍会盈利**，但靠 Teams/Internal + 数据授权，而非公开站。公开站作为"模型训练语料的来源"价值正在贬值——因为后 2022 年的新内容几乎没有。
- **官方文档站本身**（MDN、Python docs、React docs、AWS docs）在 2026-2027 进入流量下降通道。预测信号：搜索框流量先降、机器人 / MCP 调用先升；最终各 SaaS 会显式提供 `/llms.txt` + docs MCP 端点作为一等公民。
- **"AI 搜索"作为独立产品类别会被压扁成两端**：通用层（ChatGPT / Claude / Gemini 原生 search）+ 垂直 MCP 工具（Context7、Stripe MCP、AWS MCP……）。中间的 Phind、Kagi-for-devs、You.com 难以为继。
- **SO 仍可能存在十年以上**，但作为"开发者答疑中枢"的角色已经死亡。它的内容将变成训练语料的化石层与企业内部知识库的产品壳——类似 Britannica 从知识中枢到品牌挂靠的轨迹。

## 信源

[1] Slashdot, "Stack Overflow Went From 200,000 Monthly Questions To Nearly Zero," Jan 2026. (峰值 200K → 现近零) [Online]. Available: <https://developers.slashdot.org/story/26/01/05/1431212/stack-overflow-went-from-200000-monthly-questions-to-nearly-zero>

[2] T. Anderson, "Dramatic drop in Stack Overflow questions as devs look elsewhere for help," *DevClass*, Jan 2026. (自 ChatGPT 发布以来 −77%) [Online]. Available: <https://devclass.com/2026/01/05/dramatic-drop-in-stack-overflow-questions-as-devs-look-elsewhere-for-help/>

[3] Intelligent Tools, "Why Did Phind Shut Down? The Real Story," 2026. (峰值 27K 搜索/月；两年跌 91%) [Online]. Available: <https://intelligenttools.co/blog/improved-phind-shutdown-post>

[4] E. Zitron, X post, 2026. (Phind 融资 $10M 后一个多月，2026-01-16 关停) [Online]. Available: <https://x.com/edzitron/status/2010932551511122050>

[5] G. Orosz, "Stack Overflow is almost dead," *The Pragmatic Engineer*, 2025. (官方 Data Explorer：2025-04 新帖 vs 2024-04 −64%；vs 2020 −90%+；2025-05 回到 2009 水平) [Online]. Available: <https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/>

[6] Stack Overflow, "2025 Developer Survey – AI section," 2025. (84% 用 AI；ChatGPT 82%、Copilot 41%、Gemini 47%、Claude 24%；51% 每日使用) [Online]. Available: <https://survey.stackoverflow.co/2025/ai/>

[7] upstash, "context7 — Up-to-date code documentation for LLMs and AI code editors," *GitHub*, 2024-2026. (约 55.1k stars) [Online]. Available: <https://github.com/upstash/context7>

[8] D. Mello, "23% of Devs Regularly Use AI Agents, per Stack Overflow Survey," *The New Stack*, 2025. [Online]. Available: <https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/>

[9] R. Fishkin, "Google Search Grew 20%+ in 2024; receives ~373X more searches than ChatGPT," *SparkToro*, 2025. (Google 5T 次/年，+21.6%) [Online]. Available: <https://sparktoro.com/blog/new-research-google-search-grew-20-in-2024-receives-373x-more-searches-than-chatgpt/>

[10] InfoWorld, "Developer-focused portal Stack Overflow lays off 10% of staff," 2023. [Online]. Available: <https://www.infoworld.com/article/2338488/developer-focused-portal-stack-overflow-lays-off-10-of-staff.html>

[11] D. Wiggers, "Stack Overflow cuts 28% of its staff," *TechCrunch*, Oct 17 2023. (CEO Prashanth Chandrasekar 以盈利路径为由) [Online]. Available: <https://techcrunch.com/2023/10/17/stack-overflow-cuts-28-of-its-staff/>

[12] P. Chandrasekar, "CEO Update: Building trust in AI is key to a thriving knowledge ecosystem," *Stack Overflow Blog*, Oct 22 2024. (10% 员工聚焦 AI；2024 H1 损失从 $44M 缩至 $13M) [Online]. Available: <https://stackoverflow.blog/2024/10/22/stack-overflow-ceo-update-first-half-1h-2024/>

[13] IT Magazine, "Unpacking Google's Latest Deal With Stack Overflow," Mar 2024. (Google Cloud + Gemini 数据合作，非排他) [Online]. Available: <https://itmagazine.com/2024/03/01/unpacking-googles-latest-deal-with-stack-overflow-a-testament-to-ai-giants-investing-in-data/>

[14] K. Wiggers, "Stack Overflow signs deal with OpenAI to supply data to its models," *TechCrunch*, May 6 2024. (OverflowAPI；财务未披露；Reddit-OpenAI 估 ~$70M/年作对比) [Online]. Available: <https://techcrunch.com/2024/05/06/stack-overflow-signs-deal-with-openai-to-supply-data-to-its-models/>

[15] American University Business Law Review, "The Google-Reddit AI Deal: Strategic Move or a Harbinger of Licensing Agreements to Come?," 2024. (Reddit-Google 内容许可约 $60M/年) [Online]. Available: <https://aublr.org/2024/03/the-google-reddit-ai-deal-strategic-move-or-a-harbinger-of-licensing-agreements-to-come/>

[16] Stack Overflow, "Stack Internal (formerly Stack Overflow for Teams)," 2025. ($6.50/seat/月起；2025-11 更名) [Online]. Available: <https://stackoverflow.co/internal/>

[17] Prosus, "FY2025 Financial Results Booklet," 2025. (Stack Overflow 营收 $115M；本币 +17%；EBIT -$57M → -$22M) [Online]. Available: <https://www.prosus.com/~/media/Files/P/prosus-corp-v2/results-reports-and-events-archive/latest-results/fy-2025/prosus-financial-results-fy25-booklet.pdf>

[18] T. Anderson, "Stack Overflow seeks rebrand as traffic continues to plummet," *DevClass*, May 13 2025. [Online]. Available: <https://www.devclass.com/ai-ml/2025/05/13/stack-overflow-seeks-rebrand-as-traffic-continues-to-plummet-which-is-bad-news-for-developers/1623624>

[19] J. Howard, "/llms.txt—a proposal to provide information to help LLMs use websites," *Answer.AI*, Sep 3 2024. [Online]. Available: <https://www.answer.ai/posts/2024-09-03-llmstxt.html>

[20] llms-txt, "The /llms.txt file – specification," 2024-2025. (H1 + blockquote + H2 链接清单；放在 `/llms.txt`) [Online]. Available: <https://llmstxt.org/>

[21] Mintlify, "Best llms.txt implementation platforms and tools in 2026," 2026. (Mintlify / Fern / GitBook / Docusaurus / VitePress 的 llms.txt 支持状态) [Online]. Available: <https://www.mintlify.com/library/best-llms-txt-platforms>

[22] Mintlify, "Simplifying docs for AI with /llms.txt," 2025. [Online]. Available: <https://www.mintlify.com/blog/simplifying-docs-with-llms-txt>

[23] Instructor, "Instructor Adopts llms.txt: Making Documentation AI-Friendly," Mar 19 2025. [Online]. Available: <https://python.useinstructor.com/blog/2025/03/19/instructor-adopts-llms-txt/>

[24] Upstash, "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt," Upstash Blog, 2024. (`resolve-library-id`、`get-library-docs` 两工具；版本切片) [Online]. Available: <https://upstash.com/blog/context7-mcp>

[25] Apidog, "How to Install and Use Context7 MCP Server," 2025. (HTTP MCP 端点 + API Key) [Online]. Available: <https://apidog.com/blog/context7-mcp-server/>

[26] Cursor, "@Web context documentation," 2025. (Exa.ai 检索；可配置每次回答前 Web 搜) [Online]. Available: <https://docs.cursor.com/context/@-symbols/@-web>

[27] Sourcegraph, "Changes to Cody Free, Pro, and Enterprise Starter plans," 2025. (2025-06-25 停止新签 Free/Pro；2025-07-23 终止；只剩 Enterprise + Amp) [Online]. Available: <https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans>

[28] Sourcegraph, "Cody is enterprise ready," 2024. (250K repos / 10M LOC 索引规模；2.5M 开发者使用 Sourcegraph) [Online]. Available: <https://sourcegraph.com/blog/cody-is-enterprise-ready>

[29] Expanded Ramblings, "Stack Overflow Statistics 2026: Q&A Volume, Community Reach," 2026. (峰期月活逾 1 亿；历史基准对比) [Online]. Available: <https://expandedramblings.com/index.php/stack-overflow-statistics-and-facts/>

[30] High Scalability, "StackOverflow Update: 560M Pageviews a Month, 25 Servers," Jul 2014. (560M PV/月，25 台服务器；旧载体中枢期规模) [Online]. Available: <https://highscalability.com/stackoverflow-update-560m-pageviews-a-month-25-servers-and-i/>

[31] Similarweb, "stackoverflow.com Traffic Analytics," Mar 2026. (环比 −10.28%；全球排名 1,501 → 1,962；流量塌方仍在持续) [Online]. Available: <https://www.similarweb.com/website/stackoverflow.com/>
