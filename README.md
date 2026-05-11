# Controversy

## 2026-05-11：Claude Mythos 在 METR 评测中"撞上了基准的天花板"

今天 METR 公布的评测显示，Claude Mythos Preview 在 Time Horizons 软件任务基准上的 **50% 时间视界达到至少 16 小时**——已经触及 METR 当前能够测量的上限——95% 置信区间从 **8.5 小时一直拉到 55 小时**，区间宽到这个程度的原因是 228 个任务里只有 5 个达到 16 小时级别，长尾数据点根本不够。这把上一代 Claude Opus 4.6 / GPT-5.2 的 5–6 小时、Sonnet 3.7 的约 2 小时、以及 2024 年中 GPT-4o 的约 7 分钟全部远远甩在身后，符合 METR 此前测出的"前沿模型时间视界约每 105 天翻倍"的指数曲线。

### 当事人各自的主张

- **METR 的主张**：他们明确**不认为这个数字在这个能力区间还能用来做精确比较或外推**，公开声明里没有把任何一个具体数字标成"权威结果"——只敢说"至少 16 小时"，并主动点出 228 个任务里只有 5 个进入 16 小时级别这一测量学事实。换句话说，METR 在用一种近乎"否认自己结果精度"的方式公布结果。
- **Anthropic 的主张**：[Claude Mythos Preview](https://red.anthropic.com/2026/mythos-preview/) 不是今天发布的——它于 **2026 年 4 月 7 日正式公布**（更早一次因 CMS 配置失误于 3 月 26 日意外泄出过草稿页），定位"整整一个能力档高于 Opus 4.7"。Anthropic 自己的宣发重点放在**计算机安全能力**而非时间视界：宣称该模型已经发现了"数千个高危漏洞"，每个主流操作系统和浏览器都中招（包括一个 27 年历史的 OpenBSD TCP SACK 漏洞、16 年历史的 FFmpeg H.264 编解码器漏洞），能自主串联多个漏洞构造 sandbox 逃逸、远程代码执行、提权链；相对 Opus 4.6，在 Firefox 上的 JavaScript shell 利用从几百次尝试里只有 2 次成功跳到 181 次。配套的 **Project Glasswing** 只对关键基础设施伙伴与开源开发者提供受限访问——**没有公开 API、没有 claude.ai 接入、Pro/Max/Team/Enterprise 任何档位都买不到**；协调披露用 SHA-3 哈希承诺方式，Anthropic 自陈披露过的漏洞中"超过 99% 尚未被修补"。今天的 METR 数据是这个 4 月模型在外部独立评测口径上的一次新读数，而非伴随发布的官方营销材料。

### 这条新闻的意义

1. **基准撞顶**：METR 的 Time Horizons 第一次出现"前沿模型的能力已经超出基准长度上限"的局面——以前是 AI 追着任务跑，现在是任务套件追不上 AI。这意味着接下来一段时间，"AI 能完成多长时间的任务"这个最被广泛引用的能力刻度，将暂时失去判别力。
2. **指数趋势的延续**：每约 105 天翻一倍的曲线没有出现拐点。如果 16 小时是真实下界，那么相对于 2024 年 7 分钟的 GPT-4o，约两年时间出现了 ~130 倍的扩张。
3. **领域偏置依然没解决**：METR 的任务集中在软件工程、机器学习、网络安全——结合 Anthropic 这次主推的恰好是网络安全能力，"模型擅长的领域"和"基准能测的领域"高度重合，这让 16 小时这个数字在向普通经济活动外推时格外不可靠（也是 METR 自己主动加的免责声明）。
4. **安全外部性提前到来**：Anthropic 自陈"99% 已发现漏洞未修补"，意味着即便是合作披露路径，攻防节奏也已经被这一代模型的发现速度甩开——这是新闻里最不舒服的一句话。

### 相关资料

- [METR Time Horizons 基准任务详解 (2026-05-11)](chat/METR%20Time%20Horizons%E5%9F%BA%E5%87%86%E4%BB%BB%E5%8A%A1%E8%AF%A6%E8%A7%A3%20(2026-05-11)-2.md) — 基准本身的任务构成（SWAA / HCAST / RE-Bench）、评分方法、已知批评

### 信源

- [Claude Mythos Shows 50% Time Horizon Of 16+ Hours On METR Benchmark — OfficeChai](https://officechai.com/ai/claude-mythos-shows-50-time-horizon-of-16-hours-on-metr-benchmark/)
- [METR says Claude Mythos is testing the limits of AI evaluation — Startup Fortune](https://startupfortune.com/metr-says-claude-mythos-is-testing-the-limits-of-ai-evaluation/)
- [Claude Mythos Preview hits 16hr eval window — Blockchain.news](https://blockchain.news/ainews/claude-mythos-preview-hits-16hr-eval-window)
- [Claude Mythos Preview — Anthropic (red.anthropic.com)](https://red.anthropic.com/2026/mythos-preview/)
- [Task-Completion Time Horizons of Frontier AI Models — METR](https://metr.org/time-horizons/)
