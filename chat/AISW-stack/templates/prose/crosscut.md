## 几条横切的观察

不属于具体某一层，但跨层规律值得单列。

- **MCP 是这一栈唯一在 2024–2025 通过的"工具接口标准"**：从 L25 起，向上影响 L24 / L18，向下影响 L17（模型 API 内置 MCP connector）和 L22（gateway 必须懂 MCP）。
- **L13 推理引擎 与 L14 模型服务 的边界正在合并**：vLLM、SGLang[[109]](https://github.com/sgl-project/sglang) 自带 OpenAI 兼容 HTTP server，挤压了纯 L14 厂商（KServe、BentoML）的独立性。
- **L15 GPU 云、L16 模型 API 聚合、L17 前沿模型 API 三层正在相互渗透**：CoreWeave[[131]](https://www.coreweave.com/) 推自家模型；Together / Fireworks 自研推理引擎；Anthropic / OpenAI 转售他人模型（极少，但 Bedrock / Vertex 把这种关系制度化）。
- **L9 后训练 + L11 评测 + L24 Agent 框架 形成 RL 闭环**：RLVR / GRPO 把 L11 的评测器当 reward，把 L24 的 agent rollout 当 trajectory，是 2025 训练范式的核心变化。
- **L34 垂直 Agent 与 L24 Agent 框架的耦合方式分两类**：闭源垂直 Agent（Cursor、Devin、Sierra）几乎都不用第三方 Agent 框架，自己造控制循环；而中小垂直 Agent（Clay、Lovable 的部分组件）大量复用 LangGraph / Agents SDK。
- **L18 LLM 应用框架 在 2025 出现 "去 LangChain[[153]](https://www.langchain.com/) 化"信号**：原生 SDK（OpenAI Agents SDK、Claude Agent SDK）抢占了 LangChain 早期的功能位；LangChain 通过 LangGraph + LangSmith 上移到 L24 + L28。
- **B–J 各分支共享 L01–L09，但向上越走越像各自孤岛**：科学计算几乎不进 L13 推理服务（用 Slurm + 直接调脚本）；机器人 VLA / 自动驾驶端到端策略**根本不是 Agent**（没有 tool-loop、没有规划），用 A 列"Agent 框架"的话语去套是误读；只有 E 世界模型与 L32 视频生成在底层模型上真正同源。
- **NVIDIA 是唯一在全部 10 条领域分支都占重要席位的供应商**：CUDA + cuDNN[[21]](https://developer.nvidia.com/cudnn)（L03–L04）→ Megatron / NeMo（L07）→ Triton Inference（L14）→ BioNeMo / Earth-2 / Modulus（B3）→ Isaac / Cosmos / GR00T（C）→ DRIVE（D）→ Omniverse + ACE（E）→ DeepStream（F）。这是 2025 估值溢价相对于纯 LLM 厂商更稳的结构性原因。
- **移动 / 边缘 SoC 三巨头（高通 / 联发科 / 瑞芯微）走的是与 NVIDIA 正交的栈**：他们集中在 L01（自研 NPU 驱动）+ L03（QNN / NeuroPilot / RKNN 三套互不兼容的 SDK）+ L13（端侧 LLM 推理引擎 Genie / NeuroPilot / RKLLM），几乎不出现在 L06–L09 训练栈与 L18 以上 Agent 栈——他们卖的是"模型转出后跑在哪"的最后一公里。三家分工：高通占高端手机 / Copilot+ PC / 高端车载（Snapdragon Ride）、联发科占中高端手机 + 中端车机 + ChromeOS、瑞芯微占低成本边缘视觉 + 中低端国产车机 / IoT。共同对手是 Apple ANE + 内置 Core ML 闭环（Apple 自家硬件 / 自家 OS / 自家 SDK 不外销）。

---
