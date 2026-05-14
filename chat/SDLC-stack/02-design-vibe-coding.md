# 2026-05-14：SDLC 栈 / 设计与 Vibe coding 层深度研究

研究范围：D10 设计层 + 全新的 Vibe coding 子层。代表公司 Bolt.new (StackBlitz)、Lovable、v0 (Vercel)、Replit Agent、Tempo Labs、Subframe、Figma Make。挖"任务量模式突变 → 新需求 → 解决方案 → 案例代码"的本质。

---

## 1. Pre-Agent 时代：设计 → 代码的流量与摩擦

事实层面：Figma 在 2024 年披露的工作流数据显示，84% 的设计师每周至少与开发者协作一次，而"handoff 不是单一时间点，而是来回迭代的非线性过程"[[1]](https://www.figma.com/resource-library/design-statistics/)。Forrester 替 Figma 做的 TEI 报告给出量化值：启用 Dev Mode 后，每位开发者每周节省约 90 分钟，输出提升 20–30%；其中一家受访企业测得每周 98 分钟、HP 报告 500% ROI[[2]](https://tei.forrester.com/go/Figma/DevMode/?lang=en-us)。

**反推 Pre-Agent 状态**：1 个开发者每周在"读设计稿、对像素、查规范、复制 token"上花 ≥ 90 分钟，说明设计稿到代码这一段在 2024 年仍是显式人力 bottleneck。Figma 自己的 2026 数据也承认"三分之二的 Figma 用户已经不是设计师"[[3]](https://medium.com/@Workpage.dev/why-two-thirds-of-figma-users-are-not-designers-and-what-it-breaks-about-handoff-7a5700ea183b)——也就是说 Figma 文件正在被 PM、研究员、运营当成"半结构化需求文档"在用，handoff 的失败率天然就高。

**原型 → 生产代码转化率**（⚠ 解读）：传统流程下，Figma 高保真原型大多数被废弃，只留下页面截图当 spec；Builder.io 的 Visual Copilot 插件累计被近 100 万 Figma 用户安装[[35]](https://www.builder.io/blog/best-figma-to-code-plugin)，但相对全球 Figma 数千万级月活用户来说，"设计稿直转生产代码"仍是边缘工作流。这是 Vibe coding 工具切入的入口——它们直接跳过"画静态稿 → 标注 → 写代码"三步，把 prompt 当 spec。

---

## 2. Vibe coding 工具普及后：用户画像与流量

Vibe coding 一词由 Karpathy 于 2025-02-02 在 X 上一条"shower-of-thoughts"推文中提出[[36]](https://x.com/karpathy/status/1886192184808149383)，到 2026 年已是独立赛道。关键数据：

- **63% 的活跃 vibe coding 用户是非开发者**（PM、创始人、市场、运营），其中 44% 在生成 UI、20% 在生成全栈应用、11% 在生成"个人软件"[[4]](https://www.secondtalent.com/resources/vibe-coding-statistics/)。
- 市场规模 2025 年 47 亿美元，预计 2027 年 123 亿美元（CAGR ≈ 62%）[[4]](https://www.secondtalent.com/resources/vibe-coding-statistics/)。
- 全球开发者 2025 年共 28.7M 人[[5]](https://keyholesoftware.com/software-development-statistics-2026-market-size-developer-trends-technology-adoption/)；而 Replit 一家就在 2026 年 3 月报 50M+ 用户[[6]](https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/)、Lovable 接近 8M 用户[[7]](https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/)、v0 累计 >4M 用户[[8]](https://www.getpanto.ai/blog/v0-ai-platform-statistics)。仅这三家覆盖的用户数（>60M，⚠ 简单相加，未去重）就已经超过全球专业开发者总量两倍。

**解读**：这说明 vibe coding 主要在做**用户基数扩张**——把"想做软件但没工程能力"的人群拉进来——而不是从传统 28.7M 开发者预算池里切。增量证据见 §8。

**每天部署量**：Lovable 自报每天有 100,000+ 新项目被创建[[9]](https://www.getpanto.ai/blog/lovable-statistics)；Bolt.new + Netlify 联合发布的里程碑是"100 万个 AI 生成网站"于 2025 年达成[[10]](https://www.netlify.com/press/bolt-netlify-1-million-ai-generated-websites/)。

---

## 3. 增长曲线：四家头部数据

### Lovable（瑞典）

Anton Osika 2024 年 11 月底发布 vibe coder。已披露的 ARR 节点：$1M → $10M（2 个月）→ $17M（第 3 个月）→ **$50M（第 6 个月，即 2025-05）** → $100M（第 8 个月）→ $200M（2025-11）→ $400M（2026-03）[[11]](https://aifundingtracker.com/lovable-vibe-coding-revenue/), [[12]](https://www.bloomberg.com/news/articles/2026-03-12/vibe-coding-startup-lovable-hits-400-million-recurring-revenue)。融资节点：2025-02 $15M[[13]](https://techcrunch.com/2025/02/25/swedens-lovable-an-app-building-ai-platform-rakes-in-16m-after-spectacular-growth/)、2025-07 $150M @ $2B[[14]](https://techcrunch.com/2025/07/02/lovable-on-track-to-raise-150m-at-2b-valuation/)、2025-12 $330M Series B @ $6.6B[[15]](https://techcrunch.com/2025/12/18/vibe-coding-startup-lovable-raises-330m-at-a-6-6b-valuation/)。$50M ARR 时只有 18 人[[37]](https://getlatka.com/companies/lovable.dev/team)，零传统营销（⚠ 解读：基于 Osika 公开访谈中"no marketing budget"的表述）。典型用例（⚠ 解读）：MVP、投资人 demo、单人 SaaS（"Lovable 一个 app 48 小时赚 $3M"是真实社区案例）[[16]](https://www.linkedin.com/posts/antonosika_lovable-built-app-just-made-3m-in-48h-probably-activity-7338217572556795905-aD3O)。

### Bolt.new（StackBlitz）

2024 年 10 月发布。30 天内做到 $4M ARR、12 月 $20M、2025 年 3 月 **$40M ARR、5M 注册、1M DAU**[[17]](https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech)。StackBlitz 累计融资 $135M，2025-01 Series B 后估值约 $700M[[38]](https://sacra.com/c/bolt-new/), [[39]](https://www.bloomberg.com/news/articles/2025-01-21/ai-speech-to-code-startup-stackblitz-is-in-talks-for-a-700-million-valuation)。分析师预计 2025 年底 $80–100M ARR[[17]](https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech)。用户画像（⚠ 解读）：偏开发者向（因 Bolt 让"代码可改"），但也吸引 indie hacker、设计师。

### v0（Vercel）

2023-10 推出，2024 年底 GA，到 2025-09 累计 3.5M+ 用户、Teams & Enterprise 占 v0 营收 >50%（来自 Vercel Series F 公告）[[40]](https://vercel.com/blog/series-f)，后报 >4M 用户[[8]](https://www.getpanto.ai/blog/v0-ai-platform-statistics)。Vercel 2025-09-30 收 $300M Series F、估值 $9.3B[[40]](https://vercel.com/blog/series-f)。用户画像（⚠ 解读）：Next.js 工程师 + 设计师，因为输出是 React + Tailwind + shadcn/ui 组件文件，必须有人懂如何接进现有项目。

### Replit Agent

2024 年末上 usage-based agent pricing。Sacra 估 2025-09 年化 $150M，至 Q4 2025 ARR $253M，CEO Amjad Masad 公开目标 2026 年底 $1B ARR[[18]](https://sacra.com/c/replit/), [[6]](https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/)。用户基数最大（50M+，含历史教育用户），但 Fortune 500 中 85% 已有用户落点[[6]](https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/)——这是和 Lovable / Bolt 不一样的企业渗透。

---

## 4. 新需求：从 prompt 到生产化的完整链条

Vibe coding 工具栈跑通必须把 6 件事打包进同一个 URL：

1. **浏览器内 sandbox**：没人想装 Node。WebContainer（StackBlitz）解决了这一项，把 Node.js 编译到 WebAssembly，跑在标签页里、走 ServiceWorker 虚拟 TCP[[19]](https://blog.stackblitz.com/posts/introducing-webcontainers/)。
2. **模板生态**：v0 走 shadcn 注册表、Bolt 推 starter、Lovable 内置模板库——避免冷启空白页。
3. **一键部署**：Bolt 接 Netlify、Lovable 接 Lovable Cloud（Supabase 托管）、v0 原生 Vercel。
4. **版本回滚 / 分支**：Lovable v2 有 visual rollback，Bolt v2 加了 fork。
5. **生产化集成**：Auth、DB、Storage、Payments、Edge Functions——必须在 prompt 那一刻就被自动接好，不能让 PM 跳到 Stripe 控制台去拷 API key。
6. **真实数据库**：从 Supabase Postgres（Lovable / Figma Make）到 Bolt 自家 Cloud DB[[20]](https://bolt.new/blog/inside-bolt-v2-hidden-power-features)。

---

## 5. 架构对比：本质差异

| 维度 | Bolt.new | Lovable | v0 |
|---|---|---|---|
| 运行环境 | 浏览器内 WebContainer，整套 Node 跑在 tab 里[[19]](https://blog.stackblitz.com/posts/introducing-webcontainers/) | 远端云容器（Lovable Cloud，基于 Supabase 栈）[[21]](https://docs.lovable.dev/integrations/supabase) | 远端 Vercel 沙箱 + 客户端预览 |
| 后端 | 内置 Bolt Cloud DB，可"claim"到 Supabase[[20]](https://bolt.new/blog/inside-bolt-v2-hidden-power-features) | Supabase 全栈（Postgres + Auth + Storage + Edge Functions）默认开 | Vercel Functions / 任意外接 |
| 输出形态 | 完整 Node 工程，可下载、可在浏览器编辑 | 完整 React + Supabase 项目，可 GitHub sync | React 组件文件，落到既有项目的 `components/ui/`[[22]](https://vercel.com/blog/announcing-v0-generative-ui) |
| 模型 | Anthropic Claude 系列（Bolt 初代主打 Claude 3.5 Sonnet）[[17]](https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech) | 多模型路由 | Vercel 自研前端代码专用模型 |
| 经济模型本质 | 浏览器里跑 = 不烧云容器，毛利高 | 烧 Supabase + LLM token | 主要烧 LLM + Vercel infra |

**关键差异**：Bolt 押注"浏览器即 IDE 即运行时"——npm install < 500ms（CDN 预压缩层）、TCP 不通时走 WebSocket relay 回浏览器沙箱[[19]](https://blog.stackblitz.com/posts/introducing-webcontainers/)。Lovable 押注"完整云后端，自动管 schema"——非开发者从来不想懂迁移、不想懂 RLS。v0 押注"我只交付组件，你来接"——保留 Vercel 平台粘性，避免 lock-in 抗拒。

---

## 6. 案例：典型 prompt 与产出

**Bolt 实例**（Vue School 公开教程）：

> Prompt：*"Let's create a blog about video games using Nuxt and Nuxt Content. Use TailwindCSS, gamer vibe. Placeholder images from lorem picsum. Display date as relative ('1 day ago'), full date on hover via useTimeAgo from VueUse Nuxt module."*

Bolt 产出 Nuxt 项目骨架、`nuxt.config.ts`、`content/` markdown 集合、Tailwind 配置、组件 `<TimeAgo>` 调用 VueUse，全程在浏览器跑、Vite dev server 热更新[[23]](https://vueschool.io/articles/vuejs-tutorials/developing-a-full-stack-nuxt-app-with-bolt-new-an-ai-experiment/)。

**Lovable 实例**：用户 prompt "Build me a SaaS for invoicing with auth and Stripe checkout."。Lovable 自动：

1. 生成 React 前端；
2. 在 Lovable Cloud 创建 Supabase 项目，建 `invoices` 表、设 RLS；
3. 调 `supabase.auth.signUp` 接邮箱注册流；
4. 写一个 Supabase Edge Function 处理 `/api/checkout` 调 Stripe；
5. 把 anon key、Stripe secret 注入环境变量。

整个 prompt → 可部署项目 < 5 分钟[[24]](https://lovable.dev/video/building-a-saas-with-lovable-supabase-and-stripe)。

**v0 实例**：prompt "settings page with collapsible sidebar, dark mode toggle, account section"。v0 输出基于 shadcn/ui 的 `<Sidebar>`、`<Sheet>`、`<Switch>` 组合，`npx shadcn add v0.dev/xyz` 直接落到既有 Next.js 项目 `components/ui/`[[22]](https://vercel.com/blog/announcing-v0-generative-ui)。

---

## 7. 边界：vibe coding 在哪些情况下崩溃

事实层（已记录的事故）：2025–2026 共 7 起 vibe-coded 应用事故，包括 150 万个 API key 外泄、未鉴权拿到企业私数据、AI 删生产库；2026 年 3 月 Amazon 6 小时宕机、6.3M 订单受影响，内部 post-mortem 把根因关联到"激进 AI-coding mandate 下生成的代码"[[25]](https://getautonoma.com/blog/vibe-coding-failures), [[26]](https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/)。

模式层：vibe-coded 应用在 5 个维度持续掉链子——埋藏的业务逻辑、缺失的异常处理、无合规审计、逻辑漂移、零制度化知识沉淀[[27]](https://www.kognitos.com/blog/why-vibe-coding-breaks-in-production/)。James Gosling 原话："*as soon as your [vibe coding] project gets even slightly complicated, they pretty much always blow their brains out. […] In the enterprise, software has to work every fucking time.*"[[26]](https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/)

**临界点**（解读）：

- 当应用涉及多人协作 + 共享状态 + 多月演化时，vibe coding 输出的代码缺乏一致抽象，第 5–10 次大改后语义崩塌。
- 当合规（HIPAA / SOC2 / PCI）要求审计链条时，"我让 AI 帮我加了支付"那一刻就失败。
- 当性能瓶颈不在第一性原理而在系统级（DB 索引、CDN 边界、并发模型）时，Vibe coding 找不到入口。

界限：**MVP、内部工具、营销页、单人 SaaS、demo** 是甜区；**多团队协作的核心系统** 仍是工程师 + 真 IDE + 真 CI/CD。

---

## 8. 本质判断：是新增需求，不是抢预算

**判断 1：用户基数差一个数量级**。全球开发者 2025 年 28.7M，而 vibe coding 头部三家覆盖用户 60M+。即便假设有重叠，新增 30M+ 用户（PM / 设计师 / 创业者 / 学生）是从无到有，不是从 Cursor 那里挖走。

**判断 2：典型用例不重叠**。Lovable 的 "投资人 demo / MVP / 单人 SaaS"[[28]](https://www.designmonks.co/case-study/lovable-ai-app-builder)，传统开发栈在过去根本没赚到这部分钱——它们或者根本不存在（idea 死在 PPT 里），或者外包给上海/班加罗尔的外包团队。Vibe coding 把"想法 → 可点击 demo"的成本从 5 万美元拉到 $25/月订阅。

**判断 3：增量预算来源**。$4.7B → $12.3B 的 vibe coding 市场规模主要来自三处资金池：(a) 之前用 Webflow / Wix 的 no-code 预算上移；(b) 之前花在外包定制的 SMB 预算下移；(c) 完全新增的"个人软件"消费（11% 的 vibe coder 在做自用工具）[[4]](https://www.secondtalent.com/resources/vibe-coding-statistics/)。这三块都不是 Cursor、JetBrains、GitHub Copilot 的盘子。

**判断 4：传统设计层被压扁但不消失**。Figma 自身的反应是发布 Figma Make（2025-05 推出，Claude 3.7 Sonnet，可吃 Figma 文件做输入并接 Supabase）[[29]](https://www.cnbc.com/2025/05/07/figma-launches-premium-figma-make-vibe-coding-ai-software-designer.html), [[30]](https://www.figma.com/blog/figma-make-general-availability/)。Tempo、Subframe 走"设计原图保留 + 代码同步"路线[[31]](https://www.subframe.com/), [[32]](https://www.tempo.new/)。这一层在重组，不在消亡——但产值结构正从"画稿子的工时"转移到"原型即代码的订阅"。

**判断 5：开发者层不是输家，但中间地带（junior + 外包）被挤压**。Red Hat、Stack Overflow 等社区已开始记录开源参与下降、junior 入门路径被切断的现象[[33]](https://developers.redhat.com/articles/2026/02/17/uncomfortable-truth-about-vibe-coding), [[34]](https://stackoverflow.blog/2026/01/02/a-new-worst-coder-has-entered-the-chat-vibe-coding-without-code-knowledge/)。这是真实代价，但属于行业内劳动力再分配，而不是 vibe coding 公司从 Cursor 那里抢蛋糕。

---

## 参考文献

[1] Figma, "79+ design statistics: Tools, collaboration, and AI in 2026," 2026. [Online]. Available: <https://www.figma.com/resource-library/design-statistics/>

[2] Forrester Consulting, "The Total Economic Impact of Figma Dev Mode," Forrester TEI report, 2024. (≥90 min/week saved per developer; +20–30% output.) [Online]. Available: <https://tei.forrester.com/go/Figma/DevMode/?lang=en-us>

[3] Workpage, "Why Two-Thirds of Figma Users Are Not Designers (And What It Breaks About Handoff)," *Medium*, Mar. 2026. [Online]. Available: <https://medium.com/@Workpage.dev/why-two-thirds-of-figma-users-are-not-designers-and-what-it-breaks-about-handoff-7a5700ea183b>

[4] Second Talent, "Top Vibe Coding Statistics & Trends 2026," 2026. (63% non-developers; $4.7B → $12.3B market.) [Online]. Available: <https://www.secondtalent.com/resources/vibe-coding-statistics/>

[5] Keyhole Software, "Software Development Statistics: 2026 Market Size, Developer Trends & Technology Adoption," 2026. (28.7M global devs.) [Online]. Available: <https://keyholesoftware.com/software-development-statistics-2026-market-size-developer-trends-technology-adoption/>

[6] SaaStr, "By Late 2025, Replit Got Really Good," 2025. (50M+ users, 85% Fortune 500.) [Online]. Available: <https://www.saastr.com/by-late-2025-replit-got-really-good-imagine-if-it-could-run-24x7/>

[7] TechCrunch, "Lovable says it's nearing 8 million users," 2025-11-10. [Online]. Available: <https://techcrunch.com/2025/11/10/lovable-says-its-nearing-8-million-users-as-the-year-old-ai-coding-startup-eyes-more-corporate-employees/>

[8] Panto, "v0 AI Platform Statistics 2026," 2026. (>4M users, Teams/Enterprise >50% revenue.) [Online]. Available: <https://www.getpanto.ai/blog/v0-ai-platform-statistics>

[9] Panto, "Lovable Statistics 2026," 2026. (100K+ projects/day, 5M visits/day.) [Online]. Available: <https://www.getpanto.ai/blog/lovable-statistics>

[10] Netlify Press, "Bolt.new and Netlify Power 1 Million AI-Generated Websites," 2025. [Online]. Available: <https://www.netlify.com/press/bolt-netlify-1-million-ai-generated-websites/>

[11] AI Funding Tracker, "Lovable Revenue: $200M ARR in 12 Months," 2025. [Online]. Available: <https://aifundingtracker.com/lovable-vibe-coding-revenue/>

[12] Bloomberg, "AI Coding Tools Drive Lovable's Revenue to $400 Million Annually," 2026-03-12. [Online]. Available: <https://www.bloomberg.com/news/articles/2026-03-12/vibe-coding-startup-lovable-hits-400-million-recurring-revenue>

[13] TechCrunch, "Sweden's Lovable rakes in $15M after spectacular growth," 2025-02-25. [Online]. Available: <https://techcrunch.com/2025/02/25/swedens-lovable-an-app-building-ai-platform-rakes-in-16m-after-spectacular-growth/>

[14] TechCrunch, "Lovable on track to raise $150M at $2B valuation," 2025-07-02. [Online]. Available: <https://techcrunch.com/2025/07/02/lovable-on-track-to-raise-150m-at-2b-valuation/>

[15] TechCrunch, "Vibe-coding startup Lovable raises $330M at a $6.6B valuation," 2025-12-18. [Online]. Available: <https://techcrunch.com/2025/12/18/vibe-coding-startup-lovable-raises-330m-at-a-6-6b-valuation/>

[16] A. Osika, LinkedIn post: "Lovable-built app just made $3M in 48h," 2025. [Online]. Available: <https://www.linkedin.com/posts/antonosika_lovable-built-app-just-made-3m-in-48h-probably-activity-7338217572556795905-aD3O>

[17] L. Neu-ner, "From 0 to $40M ARR: Inside the Tech of Bolt.new," *Product for Engineers* (PostHog), 2025. [Online]. Available: <https://newsletter.posthog.com/p/from-0-to-40m-arr-inside-the-tech>

[18] Sacra, "Replit revenue, funding & news," 2025-2026. [Online]. Available: <https://sacra.com/c/replit/>

[19] StackBlitz, "Introducing WebContainers: Run Node.js natively in your browser," 2021 (foundational); updated coverage 2024-2025. [Online]. Available: <https://blog.stackblitz.com/posts/introducing-webcontainers/>

[20] Bolt's blog, "Inside Bolt V2 with Jakub Skrzypczak: What's new," 2025. [Online]. Available: <https://bolt.new/blog/inside-bolt-v2-hidden-power-features>

[21] Lovable Documentation, "Connect to Supabase," 2025-2026. [Online]. Available: <https://docs.lovable.dev/integrations/supabase>

[22] Vercel, "Announcing v0: Generative UI," 2023; updates 2025. [Online]. Available: <https://vercel.com/blog/announcing-v0-generative-ui>

[23] Vue School, "Developing a Full Stack Nuxt App with Bolt.new — An AI Experiment," 2024. [Online]. Available: <https://vueschool.io/articles/vuejs-tutorials/developing-a-full-stack-nuxt-app-with-bolt-new-an-ai-experiment/>

[24] Lovable, "Building a SaaS with Lovable, Supabase, and Stripe," 2025. [Online]. Available: <https://lovable.dev/video/building-a-saas-with-lovable-supabase-and-stripe>

[25] Autonoma, "Vibe Coding Failures: 7 Real Apps That Broke in Production," 2026. [Online]. Available: <https://getautonoma.com/blog/vibe-coding-failures>

[26] The New Stack, "Vibe Coding Fails Enterprise Reality Check," 2026. (Gosling quote.) [Online]. Available: <https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/>

[27] Kognitos, "Why Vibe Coding Breaks in Production — and How to Fix It," 2026. (5 failure modes.) [Online]. Available: <https://www.kognitos.com/blog/why-vibe-coding-breaks-in-production/>

[28] Design Monks, "Lovable.dev's Rapid Success Story," 2025. [Online]. Available: <https://www.designmonks.co/case-study/lovable-ai-app-builder>

[29] CNBC, "Figma launches premium Figma Make 'vibe-coding' AI software designer," 2025-05-07. [Online]. Available: <https://www.cnbc.com/2025/05/07/figma-launches-premium-figma-make-vibe-coding-ai-software-designer.html>

[30] Figma Blog, "Figma Make Is Now Available to All Users," 2025-07-24. [Online]. Available: <https://www.figma.com/blog/figma-make-general-availability/>

[31] Subframe, "The AI design tool built for code," 2025-2026. [Online]. Available: <https://www.subframe.com/>

[32] Tempo Labs, "Prompt. Develop. Design. Collaborate.," 2025. [Online]. Available: <https://www.tempo.new/>

[33] Red Hat Developer, "The uncomfortable truth about vibe coding," 2026-02-17. [Online]. Available: <https://developers.redhat.com/articles/2026/02/17/uncomfortable-truth-about-vibe-coding>

[34] Stack Overflow Blog, "A new worst coder has entered the chat: vibe coding without code knowledge," 2026-01-02. [Online]. Available: <https://stackoverflow.blog/2026/01/02/a-new-worst-coder-has-entered-the-chat-vibe-coding-without-code-knowledge/>
