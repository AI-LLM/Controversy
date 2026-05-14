# SDLC 栈 / 设计与 Vibe coding 层深度研究

L02 涵盖"从一句话到可部署 SaaS"这一段：设计稿、Vibe coding 工具（Lovable / Bolt / v0 / Replit Agent）、以及围绕它们的部署 / 数据库 / 认证集成。

## 1. 创造门槛崩塌：能力、成本、时间三重

L02 这一层的核心变量是**门槛**——造一个可部署 SaaS 需要什么，在 2024–2026 之间同时丢掉了能力门槛、成本门槛、时间门槛：

- **能力门槛**：从"会写 React + 接 DB + 部 Vercel"塌成"会写一段中文 prompt"；
- **成本门槛**：从外包基本款 MVP 的 **$15K–$50K**[[3]](https://www.creolestudios.com/mvp-development-cost/) 塌到 **$25–$50/月** 订阅；
- **时间门槛**：从"两个月外包档期 + 来回沟通"塌到 **<5 分钟** 一次 prompt 出可部署项目 [[4]](https://lovable.dev/video/building-a-saas-with-lovable-supabase-and-stripe)。

三重门槛同时崩塌时，**进来的人**和**进来的盘子**都不在原来的曲线上。Lovable 18 个人 6 个月做到 $50M ARR、零传统营销 [[1]](https://aifundingtracker.com/lovable-vibe-coding-revenue/) [[2]](https://getlatka.com/companies/lovable.dev/team) 这种数字，只能用"门槛塌掉、需求自来"解释，不能用"销售执行优秀"或"流量增长"解释。

Karpathy 2025-02-02 在 X 上一条 shower-of-thoughts 推文里命名了 "vibe coding"——"There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists" [[5]](https://x.com/karpathy/status/1886192184808149383)。这条推文出现的前提是上面三重门槛已经塌过一轮，不是反过来。

## 2. 三重门槛崩塌

### 2.1 能力门槛：非工程师可造

Pre-Agent 时代造一个登录 + 支付 + DB 的 SaaS，需要会以下 6 件事中的 5 件：前端框架（React/Vue）、状态管理、Auth flow、DB schema + 迁移、Stripe webhook、CI/CD + 域名。**这 6 件每一件都是一个学习曲线 ≥ 几周的子领域**（⚠ 行业经验值，依据：MDN、Supabase、Stripe 各自官方 quickstart 的章节数与样例长度，作者综合估算）。

Vibe coding 把这 6 件压成一句话。Lovable 内部把 "Build me a SaaS for invoicing with auth and Stripe checkout" 这种 prompt 自动展开为：(1) React 前端；(2) Lovable Cloud 建 Supabase 项目 + `invoices` 表 + RLS；(3) `supabase.auth.signUp` 邮箱注册；(4) Edge Function 处理 `/api/checkout` 调 Stripe；(5) 注入 anon key 和 Stripe secret——整链路 <5 分钟出可部署项目 [[4]](https://lovable.dev/video/building-a-saas-with-lovable-supabase-and-stripe) [[6]](https://docs.lovable.dev/integrations/supabase)。

直接的量化证据：**Vibe coding 活跃用户中 63% 是非开发者**——PM、创始人、市场、运营——其中 44% 在生成 UI、20% 在生成全栈应用、11% 在生成"个人软件"[[7]](https://www.secondtalent.com/resources/vibe-coding-statistics/)。这是 Pre-Agent 工具链不可能服务到的人群。

### 2.2 成本门槛：$15K–$50K → $25/月

外包定制 MVP 在 2026 年仍是 SMB 主流路径，Creole Studios 等行业报价指南给出的基本 MVP 区间是 **$15K–$50K**，外包代理商 MVP $10K–$35K [[3]](https://www.creolestudios.com/mvp-development-cost/)。这条价格曲线 10 年没变过，因为成本主体是人工时。

Vibe coding 直接砍掉人工时。Lovable Pro $25/月、Bolt $20/月起、v0 $20/月起——上限不是 $25K，而是 ~$200/月企业版（[[8]](https://lovable.dev/pricing) [[9]](https://bolt.new/pricing) [[10]](https://v0.dev/pricing)，价格层级，URL 见参考文献）。**对一个想验证 idea 的创始人，可决策范围从"要不要花 $30K"变成"要不要刷一个 $25 月费"**——决策摩擦量级下降。

Forrester 替 Figma 做的 Dev Mode TEI 报告给出的对照点：Pre-Agent 设计 → 代码这一段，每位开发者每周节省 ~90 分钟、输出 +20–30%，HP 报告 500% ROI [[11]](https://tei.forrester.com/go/Figma/DevMode/?lang=en-us)。Dev Mode 解决的是"专业开发者读设计稿的摩擦"——成本仍按工程师工时计；Vibe coding 解决的是"跳过专业开发者"——成本按订阅计。两者的成本基线不在一个量纲。

### 2.3 时间门槛：5 分钟出可部署项目

时间门槛崩塌依赖一组关键基础设施同时就位：

1. **浏览器内 sandbox**：StackBlitz WebContainer 把 Node.js 编进 WebAssembly、用 ServiceWorker 模拟 TCP，整套 Node 跑在标签页里 [[12]](https://blog.stackblitz.com/posts/introducing-webcontainers/)；npm/pnpm/yarn 装包比本地快 5–10× [[13]](https://blog.stackblitz.com/posts/announcing-native-package-manager-support/)。
2. **一键部署**：Bolt 接 Netlify、Lovable 接 Lovable Cloud（Supabase 托管）、v0 原生 Vercel。
3. **生产化集成被打包**：Auth、DB、Storage、Payments、Edge Functions 必须在 prompt 那一刻就被自动接好——非开发者不会跳到 Stripe 控制台拷 API key。
4. **真实数据库默认在线**：Bolt 自家 Cloud DB [[14]](https://bolt.new/blog/inside-bolt-v2-hidden-power-features)、Lovable 默认 Supabase Postgres。
5. **模板库 + 注册表**：v0 走 shadcn 注册表、Bolt 推 starter、Lovable 内置模板，避免冷启空白页。
6. **版本回滚 / 分支**：Lovable v2 visual rollback、Bolt v2 fork。

任何一项缺位，"<5 分钟" 都不成立——非开发者一遇 CLI 就退场。Bolt + Netlify 2025 年里程碑是 "100 万 AI 生成网站"[[15]](https://www.netlify.com/press/bolt-netlify-1-million-ai-generated-websites/)、Lovable 自报每天 100,000+ 新项目 [[16]](https://www.getpanto.ai/blog/lovable-statistics)——这是时间门槛真塌了之后的下游症状。

## 3. 新创造者画像与新盘子

### 3.1 用户基数差一个数量级

全球专业开发者 2025 年 **28.7M** 人 [[17]](https://keyholesoftware.com/software-development-statistics-2026-market-size-developer-trends-technology-adoption/)。Vibe coding 三家头部覆盖的用户：

- Replit 2026-03 报 **50M+ 用户**（含历史教育用户）[[18]](https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/)
- Lovable 2025-11 近 **8M 用户** [[19]](https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/)
- v0 累计 **>4M 用户** [[20]](https://www.getpanto.ai/blog/v0-ai-platform-statistics)

三家相加 >60M（⚠ 简单相加未去重；但即便假设三家重叠率 50%，独立用户仍 >30M，已超过全球专业开发者总数）。**这个数量级差距说明 vibe coding 不是从 28.7M 开发者池里挖客户，而是把"想做软件但没工程能力"的人群从无到有拉进来。**

### 3.2 典型用例不重叠

Pre-Agent 传统开发栈赚的钱集中在企业应用、电商、to-B 系统、内部工具。Vibe coding 的典型用例 [[21]](https://www.designmonks.co/case-study/lovable-ai-app-builder) [[19]](https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/)：

- **投资人 demo**：以前要么找朋友写、要么 PPT 假装能 demo
- **MVP / 概念验证**：以前外包 $15K–$50K，绝大多数因为算账不通而死在 idea 阶段
- **单人 SaaS**：以前几乎不存在，因为"个人 + 全栈 + 运维"的复合技能门槛太高
- **个人软件**：11% vibe coder 在做自用工具 [[7]](https://www.secondtalent.com/resources/vibe-coding-statistics/)，传统行业从未对这块定价过

社区典型案例：Lovable 一个 app 48 小时赚 $3M（创始人 Osika 转发，原作者公开身份）[[22]](https://www.linkedin.com/posts/antonosika_lovable-built-app-just-made-3m-in-48h-probably-activity-7338217572556795905-aD3O)。这种"1 人 + 1 周末"的产值模式，在 Pre-Agent 时代不在任何工具链的目标用户画像里。

### 3.3 增量预算来源（⚠ 解读）

⚠ **声明**：以下资金池分解为作者综合推断，仅 (c) 项有 [[7]](https://www.secondtalent.com/resources/vibe-coding-statistics/) 直接证据。

$4.7B (2025) → $12.3B (2027) 的 vibe coding 市场规模 [[7]](https://www.secondtalent.com/resources/vibe-coding-statistics/) 主要来自三处：

(a) **Webflow / Wix 等 no-code 预算上移**——这些用户原本就在为"无代码搭页面"付月费，现在升级到能造完整 SaaS；
(b) **SMB 外包定制预算下移**——原本花 $15K–$50K 外包的功能，转成 vibe coding 月费；
(c) **完全新增的"个人软件"消费**——11% 的 vibe coder 在做自用工具 [[7]](https://www.secondtalent.com/resources/vibe-coding-statistics/)，这是过去不存在的支付场景。

这三块都不是 Cursor、JetBrains、GitHub Copilot 的盘子——后者卖给已经会编程的开发者，不卖给"门槛塌掉后新进场"的人。

## 4. 四家头部如何把门槛压低（架构对比 + Lovable 案例升格）

### 4.1 架构对比

| 维度 | Bolt.new | Lovable | v0 | Replit Agent |
|---|---|---|---|---|
| 运行环境 | 浏览器内 WebContainer，整套 Node 跑 tab 里 [[12]](https://blog.stackblitz.com/posts/introducing-webcontainers/) | 远端云容器（Lovable Cloud / Supabase 栈）[[6]](https://docs.lovable.dev/integrations/supabase) | 远端 Vercel 沙箱 + 客户端预览 | Replit Workspaces（云容器） |
| 后端 | Bolt Cloud DB，可 claim 到 Supabase [[14]](https://bolt.new/blog/inside-bolt-v2-hidden-power-features) | Supabase 全栈默认开 | Vercel Functions / 任意外接 | Replit DB / 任意外接 |
| 输出形态 | 完整 Node 工程，可下载 | 完整 React + Supabase 项目，GitHub sync | React 组件，落到既有 `components/ui/` [[23]](https://vercel.com/blog/announcing-v0-generative-ui) | 完整云项目 + 长跑 agent |
| 模型 | Anthropic Claude 系列 [[24]](https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech) | 多模型路由 | Vercel 自研前端模型 | 多模型 |
| 门槛压低重点 | "浏览器即 IDE 即运行时"——免装环境 | "全栈一句话"——后端自动接好 | "组件落地"——保留专业开发者工作流 | "agent 24×7"——超长任务 |
| 用户画像（⚠ 解读）| Indie hacker、设计师、轻代码工程师 | 非开发者、创始人、PM | Next.js 工程师 + 设计师 | 教育、企业、长跑任务 |
| 经济模型本质 | 浏览器跑 = 不烧云容器，毛利高 | 烧 Supabase + LLM token | 烧 LLM + Vercel infra | 烧云容器 + LLM |

**关键差异**：四家在"压哪一段门槛"上分工不同。Bolt 压**环境门槛**（不装 Node）；Lovable 压**全栈门槛**（后端自动接好，非开发者最大障碍）；v0 压**最后一公里**（专业开发者把生成组件接进既有项目）；Replit 压**时长门槛**（agent 长跑、企业渗透）。**不是同质化竞争，而是分别拆掉门槛的不同维度。**

### 4.2 Lovable 案例升格：18 人 + $50M ARR + 零营销

Anton Osika 2024-11 底发布 Lovable。已披露 ARR 节点：$1M → $10M（2 个月）→ $17M（第 3 个月）→ **$50M（第 6 个月，2025-05）** → $100M（第 8 个月）→ $200M（2025-11）→ $400M（2026-03）[[1]](https://aifundingtracker.com/lovable-vibe-coding-revenue/) [[25]](https://www.bloomberg.com/news/articles/2026-03-12/vibe-coding-startup-lovable-hits-400-million-recurring-revenue)。融资节点：2025-02 $15M [[26]](https://techcrunch.com/2025/02/25/swedens-lovable-an-app-building-ai-platform-rakes-in-16m-after-spectacular-growth/)、2025-07 $150M @ $2B [[27]](https://techcrunch.com/2025/07/02/lovable-on-track-to-raise-150m-at-2b-valuation/)、2025-12 $330M Series B @ $6.6B [[28]](https://techcrunch.com/2025/12/18/vibe-coding-startup-lovable-raises-330m-at-a-6-6b-valuation/)。

$50M ARR 时只有 **18 人** [[2]](https://getlatka.com/companies/lovable.dev/team)，**零传统营销**（⚠ 解读：基于 Osika 公开访谈中"no marketing budget"表述）。Pre-Agent 时代 $50M ARR SaaS 标准员工数 200–500 人——18 人这个比例只能用"门槛塌了，需求自来"解释，不能用"销售执行优秀"解释。

其他三家对照：

- **Bolt.new（StackBlitz）**：2024-10 发布。30 天 $4M ARR、12 月 $20M、2025-03 **$40M ARR、5M 注册、1M DAU** [[24]](https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech)。StackBlitz 累计融资 $135M、2025-01 Series B 估值 ~$700M [[29]](https://sacra.com/c/bolt-new/) [[30]](https://www.bloomberg.com/news/articles/2025-01-21/ai-speech-to-code-startup-stackblitz-is-in-talks-for-a-700-million-valuation)。
- **v0（Vercel）**：2023-10 推出、2024 年底 GA、2025-09 累计 3.5M+ 用户、Teams & Enterprise 占 v0 营收 >50% [[31]](https://vercel.com/blog/series-f)，后报 >4M 用户 [[20]](https://www.getpanto.ai/blog/v0-ai-platform-statistics)。Vercel 2025-09-30 收 $300M Series F @ $9.3B [[31]](https://vercel.com/blog/series-f)。
- **Replit Agent**：Sacra 估 2025-09 ARR $150M、Q4 2025 **$253M**，CEO Amjad Masad 目标 2026 年底 **$1B ARR**；50M+ 用户，Fortune 500 中 85% 已有用户落点 [[32]](https://sacra.com/c/replit/) [[18]](https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/)。

## 5. 复杂度天花板（甜区 / 雷区）

门槛塌了不代表能造任何东西——复杂度天花板就在那里。

### 5.1 已记录事故

2025–2026 共记录 7 起 vibe-coded 应用事故，包括 150 万 API key 外泄、未鉴权拿到企业私数据、AI 删生产库 [[33]](https://getautonoma.com/blog/vibe-coding-failures)。2026-03-05 **Amazon 北美零售站 6 小时宕机、估计 6.3M 订单损失**，外部分析把根因关联到 Amazon 内部 "Kiro 80% 周使用率" mandate 下生成的代码 [[34]](https://securityboulevard.com/2026/03/amazon-lost-6-3-million-orders-to-vibe-coding-your-soc-is-next/) [[35]](https://getautonoma.com/blog/amazon-vibe-coding-lessons)。

### 5.2 持续掉链子的 5 个维度

Kognitos 整理出 vibe-coded 应用在生产环境的 5 类失败：埋藏的业务逻辑、缺失的异常处理、无合规审计、逻辑漂移、零制度化知识沉淀 [[36]](https://www.kognitos.com/blog/why-vibe-coding-breaks-in-production/)。James Gosling 原话："*as soon as your [vibe coding] project gets even slightly complicated, they pretty much always blow their brains out. […] In the enterprise, software has to work every fucking time.*" [[37]](https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/)

### 5.3 甜区与雷区

⚠ **解读**：边界从事故记录与各家自报核心用例反推：

| 区域 | 内容 | 依据 |
|---|---|---|
| **甜区** | MVP、内部工具、营销页、单人 SaaS、demo、个人软件 | §3.2 各家自报核心用例 [[21]](https://www.designmonks.co/case-study/lovable-ai-app-builder) [[19]](https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/)；事故记录里未出现 |
| **灰区** | 早期产品到 product-market fit 之间、轻合规 SMB SaaS | 5–10 次大改后语义漂移、第 N+1 个 feature 引入回归 |
| **雷区** | 多团队协作核心系统、PCI/HIPAA/SOC2、高并发、关键数据 | Amazon 6M 订单 [[34]](https://securityboulevard.com/2026/03/amazon-lost-6-3-million-orders-to-vibe-coding-your-soc-is-next/)、150 万 API key 外泄、删生产库 [[33]](https://getautonoma.com/blog/vibe-coding-failures) |

临界点观察：当应用涉及多人协作 + 共享状态 + 多月演化时，vibe coding 输出的代码缺乏一致抽象，第 5–10 次大改后语义崩塌；合规要求审计链条时，"我让 AI 帮我加了支付"那一刻就失败；性能瓶颈在系统级（DB 索引、CDN 边界、并发模型）时，vibe coding 找不到入口。

## 6. 传统设计层重组而非消亡

门槛崩塌不等于既有玩家被消灭——它逼着既有玩家**重组**自己在新栈中的位置。

### 6.1 Figma：自己做 vibe coding

Figma 2024 年披露 84% 设计师每周至少与开发者协作一次、"handoff 不是单一时间点而是来回迭代"[[38]](https://www.figma.com/resource-library/design-statistics/)；2026 年 Figma 自报"三分之二的 Figma 用户已不是设计师"[[39]](https://medium.com/@Workpage.dev/why-two-thirds-of-figma-users-are-not-designers-and-what-it-breaks-about-handoff-7a5700ea183b)——PM / 研究员 / 运营把 Figma 当半结构化需求文档用。

Figma 的反应：**2025-05 推 Figma Make**（Claude 3.7 Sonnet，可吃 Figma 文件做输入、接 Supabase）[[40]](https://www.cnbc.com/2025/05/07/figma-launches-premium-figma-make-vibe-coding-ai-software-designer.html) [[41]](https://www.figma.com/blog/figma-make-general-availability/)。Builder.io Visual Copilot 插件累计被近 100 万 Figma 用户安装 [[42]](https://www.builder.io/blog/best-figma-to-code-plugin)——这是"原型 → 生产代码"工作流被外挂式重塑。Figma Make 出现说明：**做平面稿这门生意的天花板已经清楚——下一段产值在"原型即代码"的订阅，不在画稿子的工时**。

### 6.2 Tempo / Subframe：原图保留 + 代码同步

Tempo、Subframe 走"设计原图保留 + 代码同步"路线 [[43]](https://www.subframe.com/) [[44]](https://www.tempo.new/)——把"设计师可继续在原图工作"与"工程师可继续在代码工作"这两条并行通道挂钩。这是承认 Figma Make / Lovable 这类工具能压低门槛，但同时承认专业团队仍然需要"原图 ↔ 代码"双轨。

### 6.3 不是切传统盘子，而是补盘子

Figma Make 和 Cursor 不冲突——Figma Make 卖给"以前不会接 Supabase 的 PM"，Cursor 卖给"已经在写 React 的工程师"。**两者用户画像不重叠，产品形态不可替换。** 真正受挤压的是中间地带——junior 入门路径、外包代理商基本款 MVP 业务、Webflow 升级版的"会拖控件但不会接后端"的人群。Red Hat、Stack Overflow 等社区已开始记录开源参与下降、junior 入门路径切断 [[45]](https://developers.redhat.com/articles/2026/02/17/uncomfortable-truth-about-vibe-coding) [[46]](https://stackoverflow.blog/2026/01/02/a-new-worst-coder-has-entered-the-chat-vibe-coding-without-code-knowledge/)——这是行业内劳动力再分配，不是 vibe coding 公司从 Cursor 那里抢蛋糕。

## 参考文献

[1] AI Funding Tracker, "Lovable Revenue: $200M ARR in 12 Months," 2025. [Online]. Available: <https://aifundingtracker.com/lovable-vibe-coding-revenue/>

[2] Latka, "How Lovable hit $50M revenue with an 18 person team in 2025," GetLatka company page. [Online]. Available: <https://getlatka.com/companies/lovable.dev/team>

[3] Creole Studios, "MVP Development Cost: Startup Budget & Pricing Guide," 2026. (Basic MVPs $15K–$50K; outsourced agency MVPs $10K–$35K.) [Online]. Available: <https://www.creolestudios.com/mvp-development-cost/>

[4] Lovable, "Building a SaaS with Lovable, Supabase, and Stripe," 2025. [Online]. Available: <https://lovable.dev/video/building-a-saas-with-lovable-supabase-and-stripe>

[5] A. Karpathy, X (Twitter) post: "There's a new kind of coding I call 'vibe coding'…", 2025-02-02. [Online]. Available: <https://x.com/karpathy/status/1886192184808149383>

[6] Lovable Documentation, "Connect to Supabase," 2025-2026. [Online]. Available: <https://docs.lovable.dev/integrations/supabase>

[7] Second Talent, "Top Vibe Coding Statistics & Trends 2026," 2026. (63% non-developers; $4.7B → $12.3B market.) [Online]. Available: <https://www.secondtalent.com/resources/vibe-coding-statistics/>

[8] Lovable, "Pricing," 2026. [Online]. Available: <https://lovable.dev/pricing>

[9] Bolt.new, "Pricing," 2026. [Online]. Available: <https://bolt.new/pricing>

[10] v0 by Vercel, "Pricing," 2026. [Online]. Available: <https://v0.dev/pricing>

[11] Forrester Consulting, "The Total Economic Impact of Figma Dev Mode," Forrester TEI report, 2024. (≥90 min/week saved per developer; +20–30% output; HP 500% ROI.) [Online]. Available: <https://tei.forrester.com/go/Figma/DevMode/?lang=en-us>

[12] StackBlitz, "Introducing WebContainers: Run Node.js natively in your browser," 2021 (foundational); updated 2024-2025. [Online]. Available: <https://blog.stackblitz.com/posts/introducing-webcontainers/>

[13] StackBlitz Blog, "npm, yarn and pnpm are now supported natively in WebContainers," 2024. (Up to 5–10× faster installs than local.) [Online]. Available: <https://blog.stackblitz.com/posts/announcing-native-package-manager-support/>

[14] Bolt's blog, "Inside Bolt V2 with Jakub Skrzypczak: What's new," 2025. [Online]. Available: <https://bolt.new/blog/inside-bolt-v2-hidden-power-features>

[15] Netlify Press, "Bolt.new and Netlify Power 1 Million AI-Generated Websites," 2025. [Online]. Available: <https://www.netlify.com/press/bolt-netlify-1-million-ai-generated-websites/>

[16] Panto, "Lovable Statistics 2026," 2026. (100K+ projects/day, 5M visits/day.) [Online]. Available: <https://www.getpanto.ai/blog/lovable-statistics>

[17] Keyhole Software, "Software Development Statistics: 2026 Market Size, Developer Trends & Technology Adoption," 2026. (28.7M global devs.) [Online]. Available: <https://keyholesoftware.com/software-development-statistics-2026-market-size-developer-trends-technology-adoption/>

[18] SaaStr, "By Late 2025, Replit Got Really Good," 2025. (50M+ users, 85% Fortune 500.) [Online]. Available: <https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/>

[19] TechCrunch, "Lovable says it's nearing 8 million users," 2025-11-10. [Online]. Available: <https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/>

[20] Panto, "v0 AI Platform Statistics 2026," 2026. (>4M users; Teams/Enterprise >50% revenue.) [Online]. Available: <https://www.getpanto.ai/blog/v0-ai-platform-statistics>

[21] Design Monks, "Lovable.dev's Rapid Success Story," 2025. [Online]. Available: <https://www.designmonks.co/case-study/lovable-ai-app-builder>

[22] A. Osika, LinkedIn post: "Lovable-built app just made $3M in 48h," 2025. [Online]. Available: <https://www.linkedin.com/posts/antonosika_lovable-built-app-just-made-3m-in-48h-probably-activity-7338217572556795905-aD3O>

[23] Vercel, "Announcing v0: Generative UI," 2023; updates 2025. [Online]. Available: <https://vercel.com/blog/announcing-v0-generative-ui>

[24] L. Neu-ner, "From 0 to $40M ARR: Inside the Tech of Bolt.new," *Product for Engineers* (PostHog), 2025. [Online]. Available: <https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech>

[25] Bloomberg, "AI Coding Tools Drive Lovable's Revenue to $400 Million Annually," 2026-03-12. [Online]. Available: <https://www.bloomberg.com/news/articles/2026-03-12/vibe-coding-startup-lovable-hits-400-million-recurring-revenue>

[26] TechCrunch, "Sweden's Lovable rakes in $15M after spectacular growth," 2025-02-25. [Online]. Available: <https://techcrunch.com/2025/02/25/swedens-lovable-an-app-building-ai-platform-rakes-in-16m-after-spectacular-growth/>

[27] TechCrunch, "Lovable on track to raise $150M at $2B valuation," 2025-07-02. [Online]. Available: <https://techcrunch.com/2025/07/02/lovable-on-track-to-raise-150m-at-2b-valuation/>

[28] TechCrunch, "Vibe-coding startup Lovable raises $330M at a $6.6B valuation," 2025-12-18. [Online]. Available: <https://techcrunch.com/2025/12/18/vibe-coding-startup-lovable-raises-330m-at-a-6-6b-valuation/>

[29] Sacra, "Bolt.new revenue, funding & news," 2025-2026. (StackBlitz total funding $135M incl. $105.5M Series B Jan 2025.) [Online]. Available: <https://sacra.com/c/bolt-new/>

[30] Bloomberg, "AI Text-to-Code Startup StackBlitz in Talks for $700M Valuation," 2025-01-21. [Online]. Available: <https://www.bloomberg.com/news/articles/2025-01-21/ai-speech-to-code-startup-stackblitz-is-in-talks-for-a-700-million-valuation>

[31] Vercel, "Towards the AI Cloud: Our Series F," 2025-09-30. (3.5M+ v0 users; Teams & Enterprise >50% of v0 revenue; $300M Series F at $9.3B post.) [Online]. Available: <https://vercel.com/blog/series-f>

[32] Sacra, "Replit revenue, funding & news," 2025-2026. [Online]. Available: <https://sacra.com/c/replit/>

[33] Autonoma, "Vibe Coding Failures: 7 Real Apps That Broke in Production," 2026. [Online]. Available: <https://getautonoma.com/blog/vibe-coding-failures>

[34] Security Boulevard, "Amazon Lost 6.3 Million Orders to Vibe Coding. Your SOC Is Next.," 2026-03. (March 5 2026 6-hour outage; 6.3M lost orders.) [Online]. Available: <https://securityboulevard.com/2026/03/amazon-lost-6-3-million-orders-to-vibe-coding-your-soc-is-next/>

[35] Autonoma, "Amazon Vibe Coding Failures: 4 Sev-1s in 90 Days," 2026. (Kiro 80% weekly-use mandate; 4 Sev-1 incidents Dec 2025 – Mar 2026.) [Online]. Available: <https://getautonoma.com/blog/amazon-vibe-coding-lessons>

[36] Kognitos, "Why Vibe Coding Breaks in Production — and How to Fix It," 2026. (5 failure modes.) [Online]. Available: <https://www.kognitos.com/blog/why-vibe-coding-breaks-in-production/>

[37] The New Stack, "Vibe Coding Fails Enterprise Reality Check," 2026. (Gosling quote.) [Online]. Available: <https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/>

[38] Figma, "79+ design statistics: Tools, collaboration, and AI in 2026," 2026. [Online]. Available: <https://www.figma.com/resource-library/design-statistics/>

[39] Workpage, "Why Two-Thirds of Figma Users Are Not Designers (And What It Breaks About Handoff)," *Medium*, Mar. 2026. [Online]. Available: <https://medium.com/@Workpage.dev/why-two-thirds-of-figma-users-are-not-designers-and-what-it-breaks-about-handoff-7a5700ea183b>

[40] CNBC, "Figma launches premium Figma Make 'vibe-coding' AI software designer," 2025-05-07. [Online]. Available: <https://www.cnbc.com/2025/05/07/figma-launches-premium-figma-make-vibe-coding-ai-software-designer.html>

[41] Figma Blog, "Figma Make Is Now Available to All Users," 2025-07-24. [Online]. Available: <https://www.figma.com/blog/figma-make-general-availability/>

[42] Builder.io, "Visual Copilot — The Best Figma to Code Plugin," 2025-2026. (Nearly 1M Figma users have installed the plugin.) [Online]. Available: <https://www.builder.io/blog/best-figma-to-code-plugin>

[43] Subframe, "The AI design tool built for code," 2025-2026. [Online]. Available: <https://www.subframe.com/>

[44] Tempo Labs, "Prompt. Develop. Design. Collaborate.," 2025. [Online]. Available: <https://www.tempo.new/>

[45] Red Hat Developer, "The uncomfortable truth about vibe coding," 2026-02-17. [Online]. Available: <https://developers.redhat.com/articles/2026/02/17/uncomfortable-truth-about-vibe-coding>

[46] Stack Overflow Blog, "A new worst coder has entered the chat: vibe coding without code knowledge," 2026-01-02. [Online]. Available: <https://stackoverflow.blog/2026/01/02/a-new-worst-coder-has-entered-the-chat-vibe-coding-without-code-knowledge/>
