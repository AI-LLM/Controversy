## A. LLM / Agent — 全栈总览（34 层）

按"运行时 → 框架 → 模型 → 推理服务 → 应用中间件 → Agent 核心 → 可观测 / 安全 → 多模态外围 → 终端应用"九大段组织。

| 段 | 层号 | 层名 | 自然视角 / 解决的事 |
| --- | --- | --- | --- |
| 底层运行时 | L01 | GPU 驱动 / 固件 | 让 OS 看到 GPU |
| | L02 | GPU 互连 / 集合通信 | 多 GPU、多机之间搬数据 |
| | L03 | GPU 编程模型 / 计算 API | 让程序员写 kernel |
| | L04 | GPU 内核库（DNN / BLAS / 通信） | 别人写好的高性能算子 |
| | L05 | 编译器 / IR | 把模型图编译成 GPU 代码 |
| 框架 | L06 | 张量 / 训练框架 | 写模型与训练循环 |
| | L07 | 分布式训练框架 | 千卡 / 万卡并行 |
| | L08 | 训练数据 pipeline | 喂数据的工业管线 |
| | L09 | 后训练 / 微调框架 | SFT / RLHF / DPO / GRPO |
| 模型 | L10 | 基础模型权重 | 可下载或可调用的模型本体 |
| | L11 | 评测 / 基准 | 能力打分 |
| | L12 | 实验追踪 / MLOps | run / sweep / artifact 管理 |
| 推理服务 | L13 | 推理引擎 | KV cache、batching、speculative |
| | L14 | 模型服务 / 编排 | 把引擎包成 service |
| | L15 | GPU 云 / 算力市场 | 谁来出 GPU |
| | L16 | 模型 API 聚合 / 路由 | 一个 endpoint 调多家模型 |
| | L17 | 前沿模型 API | 直接调闭源旗舰模型 |
| LLM 应用中间件 | L18 | LLM 应用框架 | prompt 链 / 工作流 |
| | L19 | Embedding / 重排序模型 | 把文本变向量 |
| | L20 | 向量数据库 / 检索 | 存与查向量 |
| | L21 | 长期记忆系统 | Agent 跨会话状态 |
| | L22 | LLM 网关 / 路由 | 限流 / 配额 / fallback |
| | L23 | Prompt 管理 / 缓存 | prompt 版本、cache 命中 |
| Agent 核心 | L24 | Agent 框架 | tool-loop、规划、多 agent |
| | L25 | 工具协议 / MCP / 集成 | Agent 怎么调外部世界 |
| | L26 | 浏览器 / Computer Use | Agent 操作 GUI |
| | L27 | 代码 / Agent 沙箱 | Agent 跑代码的安全环境 |
| 可观测 / 安全 | L28 | LLM 观测 / 追踪 | trace、token、成本 |
| | L29 | Guardrails / 安全 / 红队 | 注入防御、PII、越狱 |
| | L30 | LLM 评测 / 测试 | CI 里跑 prompt 测试 |
| 多模态外围 | L31 | 语音（TTS / ASR） | 听 / 说 |
| | L32 | 图像 / 视频生成 | 画 / 拍 |
| 终端用户 Agent 应用 | L33 | 通用对话 / 搜索 Agent | 给所有人用 |
| | L34 | 垂直 Agent 应用 | 给开发者 / 设计师 / 等用 |

---
