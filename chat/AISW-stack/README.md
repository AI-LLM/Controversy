# AI 软件栈分层索引：从 GPU 驱动到终端用户 Agent 应用

从最底层的 GPU 驱动 / 固件，一直到最终用户接触的 Agent 应用（ChatGPT、Cursor、Devin），完整一根栈。每层至少列 3 个代表性软件 / 项目 / 厂商；同层多个候选时尽量覆盖闭源前沿、开源主流、新兴挑战者三类。

## 全栈总览（34 层）

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

## L01 GPU 驱动 / 固件

负责把硬件能力暴露给操作系统与上层运行时；包括内核态驱动、固件、用户态运行时 stub。

- **NVIDIA Display / Compute Driver**（含 `nvidia.ko` 内核模块、GSP 固件、`nvidia-smi`、MIG / vGPU）
- **NVIDIA Open GPU Kernel Modules**（2022 起开源的 R515+ 内核侧驱动，仅支持 Turing 及更新架构）
- **AMD ROCm / amdgpu / amdkfd driver**（`amdgpu` DRM 驱动 + KFD 计算子系统）
- **Intel Habana Gaudi driver**（`habanalabs` 内核驱动）
- **Apple Silicon GPU driver**（macOS / iOS 内置，与 Metal 紧绑定）
- **NVIDIA Container Toolkit / nvidia-container-runtime**（让容器看到 GPU；事实上的 K8s GPU 接入标准）

## L02 GPU 互连 / 集合通信

多卡 / 多机之间的物理与协议层；性能瓶颈往往不在 FLOPS 而在这层。

- **NVLink / NVSwitch**（节点内 GPU↔GPU，H100 900 GB/s、B200 1.8 TB/s）
- **InfiniBand（NVIDIA Quantum-2 / Quantum-X800）+ Mellanox OFED**（节点间 RDMA）
- **RoCE v2 / Ultra Ethernet（UEC）**（以太网上的 RDMA；Ultra Ethernet Consortium 2024 推出 1.0）
- **AWS EFA（Elastic Fabric Adapter）+ SRD 协议**
- **UALink 1.0**（AMD / Intel / Google / Meta 等 2024 联盟，对位 NVLink）
- **NCCL / RCCL / oneCCL**（NVIDIA / AMD / Intel 各自的集合通信库；allreduce / allgather / sendrecv）
- **MSCCL / MSCCL++**（微软在 NCCL 之上的可编程调度层）

## L03 GPU 编程模型 / 计算 API

让开发者写并行 kernel；下层各家硬件的统一抽象。

- **NVIDIA CUDA**（含 `nvcc`、PTX、CUDA Runtime / Driver API）
- **AMD ROCm / HIP**（HIP 提供 CUDA 源码级近似兼容）
- **Apple Metal / Metal Performance Shaders（MPS）**
- **Intel oneAPI / SYCL / DPC++**
- **OpenCL 3.0**（跨厂商，地位下滑但仍在嵌入式 / Android）
- **Vulkan Compute**（图形 + 计算合一，llama.cpp 用作便携后端）
- **WebGPU / wgpu**（浏览器内 GPU 计算；Chrome 113 起默认开启）

## L04 GPU 内核库（DNN / BLAS / 通信 / Attention）

预编译好的高性能算子，框架直接调用。

- **cuBLAS / cuBLASLt**（GEMM）
- **cuDNN**（卷积、RNN、Attention 等深度学习算子）
- **CUTLASS**（NVIDIA 开源的 GEMM 模板库，FlashAttention / vLLM 大量复用）
- **FlashAttention 1 / 2 / 3**（Tri Dao；FA3 针对 Hopper Tensor Core + TMA）
- **xFormers**（Meta；memory-efficient attention 集合）
- **Triton kernels**（OpenAI；社区贡献的 fused MoE、RMSNorm、SwiGLU 等）
- **NCCL / RCCL**（同 L02，也属于"内核库"中的通信类）

## L05 编译器 / IR

把模型图或 Python 代码编译成 GPU 可执行体；过去十年从单一图编译器演化为多层 IR + JIT 混合。

- **OpenAI Triton**（Python 嵌入式 DSL，事实上的 GPU kernel 写法新标准）
- **PyTorch torch.compile / TorchInductor + TorchDynamo**（PT 2.x 默认编译路径，下接 Triton / C++ / Halide）
- **XLA / OpenXLA**（JAX 与 TF 默认；Google + AWS + NVIDIA + Meta 共治）
- **MLIR**（LLVM 项目；TPU、IREE、Mojo、torch-mlir 共享的中间表示）
- **TVM / Apache TVM + Unity**（陈天奇主导的端到端深度学习编译栈）
- **IREE**（Google；MLIR-based，定位移动 / 边缘）
- **Mojo / MAX**（Modular；Chris Lattner，Python 超集 + MLIR 后端）

## L06 张量 / 训练框架

定义计算图、autograd、optimizer；用户写 `nn.Module` 的那一层。

- **PyTorch**（Meta；2025 LLM 训练事实标准，份额 >70%）
- **JAX + Flax / NNX / Equinox**（Google；Gemini / Anthropic 训练栈核心）
- **TensorFlow + Keras 3**（Google；Keras 3 后端可切 JAX / PyTorch / TF）
- **MLX**（Apple；Apple Silicon 原生）
- **MindSpore**（华为）
- **PaddlePaddle**（百度）
- **tinygrad**（George Hotz；研究 / 教学）

## L07 分布式训练框架

把模型与数据切到上千 / 上万卡上，并管 checkpoint / 容错 / 恢复。

- **DeepSpeed**（Microsoft；ZeRO-1/2/3、ZeRO-Infinity、MoE）
- **Megatron-LM / Megatron-Core**（NVIDIA；3D 并行：TP / PP / DP）
- **PyTorch FSDP / FSDP2**（PyTorch 官方；FSDP2 2024 GA）
- **NVIDIA NeMo**（Megatron-Core 上的端到端训练 + 数据 + 评测套件）
- **Colossal-AI**（HPC-AI Tech）
- **Ray Train**（Anyscale；调度层在 Ray 上）
- **MosaicML Composer / LLM Foundry**（被 Databricks 收购）
- **TorchTitan**（PyTorch 官方 2024 推出的 LLM 训练参考实现）

## L08 训练数据 pipeline

数据集构建、清洗、去重、tokenize、streaming。这一层 2023 后被独立看待。

- **datatrove**（HuggingFace；FineWeb 的生产工具）
- **MosaicML Streaming**（云对象存储到训练机的流式 dataset）
- **WebDataset**（POSIX tar 流，PyTorch 生态早期事实标准）
- **Nemo Curator**（NVIDIA；GPU 加速去重 / 分类）
- **Dolma toolkit**（AI2；OLMo 数据集工具）
- **llm-foundry**（Mosaic / Databricks）
- **数据集本体**：FineWeb / FineWeb-Edu（HF）、RedPajama-V2（Together）、Dolma（AI2）、The Stack v2（BigCode）、Common Crawl

## L09 后训练 / 微调框架

SFT、RLHF / DPO / IPO / GRPO / RLVR、reward modeling、合成数据。这一层 2024-2025 爆发。

- **TRL**（HuggingFace；SFT / DPO / GRPO / PPO trainer，事实标准）
- **Unsloth**（QLoRA 极致优化，单卡微调首选）
- **Axolotl**（OpenAccess AI Collective；config-driven 微调）
- **LLaMA-Factory**（北航；中文社区主流）
- **OpenRLHF**（OpenLLMAI；分布式 RLHF，Ray 调度）
- **verl**（字节；HybridFlow，veRL，DeepSeek-R1 风格 RLVR）
- **NeMo-Aligner**（NVIDIA）

## L10 基础模型权重

可下载（开源 / 开放权重）或可 API 调用的模型本体。这一层 2025 已分裂为开放权重与闭源前沿两轨。

- **开放权重 / 开源**：Llama 3 / 4（Meta）、Qwen 3（阿里）、DeepSeek-V3 / R1、Mistral / Mixtral、Gemma 3（Google）、Kimi K2（Moonshot）、GLM-4.6（智谱）、Phi-4（Microsoft）、OLMo 2（AI2，真·全开源）
- **闭源前沿**：GPT-5 / GPT-5.1（OpenAI）、Claude Opus / Sonnet / Haiku 4.x（Anthropic）、Gemini 2.5 / 3（Google DeepMind）、Grok 4（xAI）
- **模型枢纽 / 发现**：HuggingFace Hub、ModelScope（阿里）、Replicate models、Ollama Library、Civitai（图像 / Stable Diffusion 衍生）

## L11 评测 / 基准

公开打分系统；越来越多被用作 RL reward 的代理。

- **lm-evaluation-harness**（EleutherAI；HF Open LLM Leaderboard 后端）
- **HELM**（Stanford CRFM）
- **OpenCompass**（上海 AI Lab）
- **任务类**：MMLU / MMLU-Pro、GSM8K / MATH、HumanEval / MBPP、SWE-bench / SWE-bench Verified、GPQA、ARC-AGI、HLE（Humanity's Last Exam）
- **Agent / 长 horizon**：METR Time Horizons、TAU-bench、WebArena、OSWorld、AgentBench
- **Embedding / 检索**：MTEB、BEIR
- **对战 / 人类偏好**：LMSYS Chatbot Arena、SEAL（Scale）
- **代码定制平台**：Inspect AI（UK AISI）、OpenAI Evals、DeepEval（参 L30）

## L12 实验追踪 / MLOps

run、metric、artifact、sweep、模型 registry。

- **Weights & Biases (W&B)**
- **MLflow**（Databricks 开源）
- **Neptune.ai**
- **ClearML**
- **Comet ML**
- **TensorBoard**（仍是免费默认）
- **DVC / DVC Studio**（Iterative；偏数据版本）

## L13 推理引擎

负责 KV cache、continuous batching、speculative decoding、量化、PagedAttention 等推理侧硬核优化。

- **vLLM**（UC Berkeley → 公司化；PagedAttention 发起者，开源吞吐量基准）
- **NVIDIA TensorRT-LLM**（NVIDIA 官方；CUDA Graph + FP8）
- **SGLang**（LMSYS / xAI；RadixAttention，结构化输出强）
- **HuggingFace TGI（Text Generation Inference）**
- **llama.cpp / GGUF**（Georgi Gerganov；CPU / Apple Silicon / 任意后端）
- **MLC-LLM**（陈天奇团队；TVM Unity 后端，Web / 移动）
- **DeepSpeed-FastGen / DeepSpeed-MII**
- **LMDeploy**（上海 AI Lab；InternLM 配套）
- **Ollama**（llama.cpp 之上的本地一键运行）

## L14 模型服务 / 编排（GPU orchestration）

把推理引擎封装成 service：自动伸缩、多模型、A/B、批处理。

- **NVIDIA Triton Inference Server**
- **Ray Serve**（Anyscale）
- **KServe**（K8s 原生，原 KFServing）
- **BentoML / Yatai**
- **Modal**（serverless GPU 函数）
- **Beam / Beam Cloud**
- **Replicate Cog**（容器规范 + Replicate 平台）
- **Seldon Core**

## L15 GPU 云 / 算力市场

物理 GPU 容量提供方；neocloud 与超大云共存。

- **超大云 GPU**：AWS (P5 / P5e / Trainium2 Ultra)、Azure (ND H100 / ND GB200 v6)、Google Cloud (A3 Ultra / TPU v5p / v6e Trillium)、Oracle Cloud (OCI GPU bare-metal)
- **GPU neocloud**：CoreWeave、Lambda Labs、Crusoe、Nebius（前 Yandex 海外）、Voltage Park、Applied Digital
- **市场 / 撮合 / 长尾**：RunPod、Vast.ai、TensorDock、Salad、Hyperstack
- **训练 + 推理一体**：Together AI、Lepton AI（被 NVIDIA 收购）

## L16 模型 API 聚合 / 路由（推理服务市场）

不直接持有最前沿模型，但把开源 / 半开源模型托管成 OpenAI 兼容 endpoint，并互相竞价。

- **OpenRouter**（按 token 转售，覆盖 100+ 模型）
- **Together AI**（开源模型托管 + 训练 + 推理引擎自研）
- **Fireworks AI**（自研 FireAttention 引擎）
- **Groq Cloud**（自家 LPU；Llama 系超低延迟）
- **Cerebras Inference**（WSE-3；超长上下文 + 高速）
- **SambaNova Cloud**（SN40L Reconfigurable Dataflow）
- **Replicate**（按秒计费，模型即容器）
- **DeepInfra**、**Anyscale Endpoints**、**Hyperbolic**

## L17 前沿模型 API（闭源 / 半闭源）

直接调用模型厂商自营 endpoint；当前 90%+ 高端 token 流量在这层。

- **Anthropic API**（Claude Opus / Sonnet / Haiku，含 Tool Use、Computer Use、Skills、Prompt Caching、Files、Batch、Citations、Memory、MCP connector）
- **OpenAI API**（GPT-5.x、o-series、Realtime、Assistants → Responses API、Agents SDK、Files、Batch）
- **Google Gemini API / Vertex AI**（Gemini 2.5 / 3 Pro / Flash / Nano）
- **xAI API**（Grok 4）
- **DeepSeek API**（V3 / R1，价格屠夫）
- **企业转售层**：Azure OpenAI Service、AWS Bedrock、Google Vertex AI Model Garden、IBM watsonx、Databricks Foundation Model APIs、**SAP BTP GenAI Hub**（SAP 客户在 BTP 内调用 Anthropic / OpenAI / 自家 SAP-AI 的统一入口）、Oracle Cloud Generative AI Service

## L18 LLM 应用框架

prompt 链、工作流、retriever、tool calling 的高层抽象。

- **LangChain / LangChain Expression Language (LCEL)**
- **LlamaIndex**（原 GPT-Index；偏 RAG-first）
- **DSPy**（Stanford；prompt-as-program、optimizer 驱动）
- **Haystack**（deepset）
- **Vercel AI SDK**（TypeScript / React 生态最常见）
- **Semantic Kernel**（Microsoft）
- **Mastra**（TS，新兴）
- **Spring AI**（Java）

## L19 Embedding / 重排序模型与服务

把文本 / 图像变成向量；Reranker 给检索结果二次排序。

- **闭源**：OpenAI text-embedding-3、Cohere Embed v3 / Rerank、Google Vertex text-embedding-005、Voyage AI（被 MongoDB 收购）
- **开源**：BGE / BGE-M3（北京智源）、Jina Embeddings v3、Nomic Embed、E5（Microsoft）、GTE（阿里）、Stella、mxbai-embed
- **多模态**：CLIP / OpenCLIP、SigLIP、Jina-CLIP

## L20 向量数据库 / 检索引擎

- **专用向量库（SaaS-first）**：Pinecone、Weaviate、Qdrant、Milvus / Zilliz
- **开源 / 嵌入式**：Chroma、LanceDB、FAISS（Meta；库不是服务）、Annoy、ScaNN
- **关系数据库扩展**：pgvector、pg_vectorize、Supabase Vector、Neon + pgvector
- **搜索引擎类**：Elasticsearch dense vector、OpenSearch k-NN、Vespa、Typesense、Meilisearch、Turbopuffer
- **嵌入式 + KV**：Redis Vector Search、SQLite-vec

## L21 长期记忆系统

跨会话 / 跨 Agent 的状态层；从 RAG-of-chat 演化到结构化记忆图。

- **Mem0**（开源 + SaaS，事实图 + 向量混合）
- **Zep / Zep Cloud**（temporal knowledge graph）
- **Letta**（原 MemGPT；研究项目公司化）
- **LangMem**（LangChain 旗下记忆 SDK）
- **Cognee**
- **Anthropic Memory tool**（2025 推出，平台内置）

## L22 LLM 网关 / 路由

应用与 L17 / L16 之间的代理层：限流、配额、密钥、fallback、cost guard、A/B。

- **LiteLLM**（BerriAI；100+ provider 适配器，自部署最常用）
- **Portkey**
- **Cloudflare AI Gateway**（缓存 + WAF + 计费）
- **Kong AI Gateway**
- **Helicone Gateway**
- **Martian Router**（按 prompt 动态路由）
- **OpenRouter**（兼有 L16 与 L22 双重身份）
- **企业 / 系统记录层 gateway**：SAP Joule MCP Gateway（强制非 SAP Agent 经 Joule / BTP 路由到 S/4HANA 才"合规"）、Oracle AI Apps Gateway、Workday AGI Gateway——把"通行权"做到 ERP / HCM 入口

## L23 Prompt 管理 / 提示缓存

prompt 版本化、A/B、提示模板、prompt 级缓存命中分析。

- **PromptLayer**
- **Langfuse Prompt Management**
- **Helicone Prompts**
- **Braintrust prompt registry**
- **Latitude**（YC W24，prompt-as-code）
- **Agenta**
- **平台原生**：Anthropic Prompt Caching、OpenAI Prompt Caching、Gemini Context Caching

## L24 Agent 框架

tool-loop、规划、子任务分解、多 agent 协作。2025 这一层从"链式工作流"快速向"事件循环 + 控制平面"迁移。

- **LangGraph**（LangChain；graph + 持久化 state，企业部署最多）
- **OpenAI Agents SDK**（原 Swarm 演化；Responses API 配套）
- **Anthropic Claude Agent SDK / claude-agent-sdk**（Claude Code 同源）
- **AutoGen / AutoGen v0.4**（Microsoft Research；多 agent 对话）
- **CrewAI**
- **Pydantic AI**（type-safe，FastAPI 风格）
- **smolagents**（HuggingFace；code-as-action）
- **Mastra**、**Inngest Agent Kit**、**TaskWeaver**（Microsoft）
- **企业 / 云厂商一体化平台**：Azure AI Foundry（原 Azure AI Studio，含 Agent Service）、AWS Bedrock Agents、Google Vertex AI Agent Builder、Databricks Mosaic AI Agent Framework、SAP Joule Studio（企业级 Agent 构建器，35 解决方案集成、30+ 专属 Agent）、ServiceNow AI Agent Studio

## L25 工具协议 / MCP / 集成市场

Agent 怎么调外部世界——文件、API、SaaS、数据库。

- **Anthropic MCP（Model Context Protocol）**（2024-11 开源；2025 已被 OpenAI / Google / 主流框架普遍接入；事实标准）
- **Composio**（500+ SaaS 集成，认证 + 工具一站式）
- **Arcade.dev**（auth-first 的 tool runtime）
- **Toolhouse**
- **Pipedream Connect**
- **Zapier MCP / Zapier AI Actions**
- **厂商自营 MCP / Agent 工具（Vendor-side）**：Stripe Agent Toolkit、Cloudflare Agents SDK + Cloudflare MCP + **HTTP 402 pay-per-crawl**（把反 Bot 从成本中心变收入中心）、Anthropic Agent Skills（2025-10 公布；与 SAP Joule Skills 同类抽象）、SAP Joule MCP Gateway + Joule Skills（2 500+）、Atlassian Remote MCP、Notion MCP、Slack MCP、Figma MCP、GitHub MCP、Salesforce MCP for Agentforce
- **CLI 强 wrap 路径**：OpenCLI（开放规范，把任意 CLI 描述为 agent-callable tool）、CLI-Anything（GitHub 21K stars，社区驱动地把已有 CLI 包成 LLM 工具）——与厂商主动出 MCP 形成"第三方强 wrap"对照
- **服务器目录**：Smithery、MCP Hub、PulseMCP、Glama MCP Registry

## L26 浏览器 / Computer Use Agent

让 Agent 操作 GUI / 浏览器 / 桌面。

- **闭源平台**：Anthropic Computer Use（API 内置）、OpenAI Operator（ChatGPT 内）、Google Project Mariner / Gemini browser
- **托管浏览器基础设施**：Browserbase、Hyperbrowser、Steel.dev、Anchor Browser、AgentQL、Browserless
- **开源 agent 控制器**：browser-use、Skyvern、Stagehand（Browserbase）、Nut.js、Open Interpreter、Playwright MCP（Microsoft）、Vercel agent-browser（v0 / Vercel AI SDK 配套，把浏览器封装为 agent 可直调的 tool）
- **垂直自动化**：Manus（端侧通用 agent）、Reworkd、MultiOn

## L27 代码 / Agent 沙箱

Agent 跑代码 / 跑命令的隔离环境；MicroVM + 快照成为新基线。

- **E2B**（Firecracker microVM，开源 SDK）
- **Modal Sandboxes**（serverless GPU + sandbox 一体）
- **Daytona**（开源 dev environment manager，被 Agent 平台普遍用作 runner）
- **CodeSandbox SDK / CodeSandbox Containers**
- **Cloudflare Containers / Workers Sandbox**
- **Replit Agent runtime**（含 Nix-based 沙箱）
- **Devin VM**（Cognition 自营）

## L28 LLM 观测 / 追踪（LLM Observability）

trace、span、token / 成本、prompt / completion 日志，是 agent 时代的新 APM。

- **Langfuse**（开源 + cloud，主流之一）
- **Arize Phoenix / Arize AX**（OpenTelemetry GenAI 推手）
- **LangSmith**（LangChain 官方）
- **Helicone**（proxy-based，零代码接入）
- **Braintrust**（eval + observability 一体）
- **Logfire**（Pydantic 团队，OTel-native）
- **W&B Weave**
- **Datadog LLM Observability**、**New Relic AI Monitoring**、**Splunk AI Observability**（传统 APM 厂商扩展）

## L29 Guardrails / 安全 / 红队

提示注入防御、PII / 越狱检测、输出过滤、内容策略。

- **Guardrails AI**（开源 validator 框架）
- **NVIDIA NeMo Guardrails**（Colang DSL）
- **Lakera Guard / Lakera Red**
- **Protect AI（含 NB Defense、Guardian、Recon）**
- **Robust Intelligence**（被 Cisco 收购）
- **Prompt Security**、**HiddenLayer**、**CalypsoAI**
- **Llama Guard 3 / Prompt Guard**（Meta 开源策略模型）
- **Promptfoo red team**（开源越狱测试套件，参 L30）

## L30 LLM 评测 / 测试（CI 中的 prompt 测试）

把 prompt / agent 当作软件来跑回归测试。

- **Promptfoo**（YAML + CLI，开源主流）
- **DeepEval**（Confident AI；pytest 风格）
- **Ragas**（RAG-specific 指标）
- **Braintrust Evals**
- **Patronus AI**（合规向）
- **TruLens**（TruEra；被 Snowflake 收购）
- **OpenAI Evals**、**Inspect AI**（UK AISI；安全评测主流）
- **Galileo Evaluate**

## L31 语音（TTS / ASR / 实时对话）

- **TTS**：ElevenLabs、Cartesia、PlayHT、Hume AI、Resemble、OpenAI tts、Google Chirp 3、阿里 CosyVoice
- **ASR**：OpenAI Whisper / Whisper Large v3、Deepgram、AssemblyAI、Speechmatics、Rev AI、NVIDIA Parakeet、Google Chirp 2
- **实时语音 / 端到端**：OpenAI Realtime API、Google Gemini Live、Anthropic（暂无原生 voice，多用 Cartesia / ElevenLabs 拼接）、Sesame、Kyutai Moshi、LiveKit Agents、Pipecat（编排框架）、Vapi、Retell AI

## L32 图像 / 视频 / 3D 生成

- **图像（闭源 / SaaS）**：Midjourney、Ideogram、Adobe Firefly、Google Imagen 3、OpenAI DALL-E 3 / GPT-4o image、Recraft
- **图像（开源 / 工作流）**：Black Forest Labs FLUX.1 / FLUX.2、Stable Diffusion 3 / SD 3.5 / SDXL（Stability AI）、PixArt-Σ、HunyuanImage（腾讯）、ComfyUI（工作流编辑器）、Automatic1111 WebUI、Fooocus
- **视频**：Runway Gen-4、Pika 2.x、Luma Dream Machine / Ray2、Kling（快手）、Hailuo MiniMax、OpenAI Sora、Google Veo 3、HunyuanVideo（腾讯开源）、Wan 2.x（阿里开源）
- **3D / 场景**：Luma Genie、Meshy、Tripo3D、Rodin、World Labs（Fei-Fei Li）、CSM
- **托管 / 推理市场**：fal.ai、Replicate、RunPod Serverless（这一层与 L16 重合，但更偏 diffusion 工作负载）

## L33 通用对话 / 搜索 Agent（终端用户）

直接给非开发者用户用的"AI 助手"。

- **ChatGPT**（OpenAI；含 Tasks、Operator、Codex、Connectors）
- **Claude.ai**（Anthropic；含 Projects、Artifacts、Computer Use、Skills、Claude Memory、Claude Desktop）
- **Gemini app / Gemini Advanced**（Google）
- **Grok**（xAI；X 内嵌 + grok.com）
- **DeepSeek Chat**、**Kimi**（Moonshot）、**通义千问**、**豆包**（字节）
- **搜索类**：Perplexity、You.com、Brave Leo、Arc Search（Browser Company）、Komo
- **多模型聚合 / 隐私**：Poe（Quora）、Le Chat（Mistral）、HuggingChat、Msty（本地）、LM Studio（本地）
- **企业内 Copilot / 默认入口**：Microsoft 365 Copilot（$30/seat，企业 AI 默认入口；CIO 把它当 SAP / Workday / Slack 的统一抢前端）、Google Gemini for Workspace、Slack AI、Notion AI、Glean Assistant、SAP Joule（SAP 客户内嵌 Agent UI，生产采用率仅 3% 但是 SAP 战略中枢）

## L34 垂直 Agent 应用（终端用户）

按行业 / 角色划分的 Agent；2025 在编码、设计、营销、客服、医疗、法律均跑出独立公司。

- **编码 Agent**：Cursor、Claude Code（Anthropic）、Devin（Cognition）、Windsurf（被 OpenAI 收购）、Replit Agent、Codex CLI（OpenAI）、Aider、GitHub Copilot Workspace、Augment、Amp（Sourcegraph）、Lovable、Bolt.new、v0（Vercel）、Manus
- **设计 / 内容**：Figma AI / Make、Galileo AI、Framer AI、Canva Magic Studio、Jasper、Copy.ai、Notion AI
- **销售 / 营销 / 客服**：Decagon、Sierra、Ada、Intercom Fin、Cresta、Clay、11x.ai、AirOps、**Salesforce Agentforce**（CRM 数据上的 Agent 平台，per-conversation $2 定价）
- **企业知识 / 内部 IT**：Glean、Moveworks、Hebbia、Harvey（法律）、Casetext CoCounsel（被 Thomson Reuters 收购）
- **ERP / HCM / ITSM 内嵌 Agent（系统记录层自营）**：SAP Joule（覆盖 S/4HANA、SuccessFactors、Ariba、Concur、Fieldglass；30+ 专属 Agent，FY25 BTP 收入是 SAP "Agent toll booth" 押注核心）、Oracle AI Apps / Oracle Fusion AI Agents、Workday AGI / Workday Illuminate、ServiceNow Now Assist + AI Agents（ITSM / HRSD / CSM）、Microsoft Dynamics 365 Copilot
- **代码评审 / 测试 / 安全 Agent**：CodeRabbit、Greptile、Qodo、Meticulous、Snyk DeepCode AI（这一层与 SDLC 栈高度重合，详见 [`../SDLC-stack/README.md`](../SDLC-stack/README.md)）
- **医疗 / 科研**：Abridge、Hippocratic AI、Ambience、Future House、Scite

---

## 几条横切的观察

不属于具体某一层，但跨层规律值得单列。

- **MCP 是这一栈唯一在 2024–2025 通过的"工具接口标准"**：从 L25 起，向上影响 L24 / L18，向下影响 L17（模型 API 内置 MCP connector）和 L22（gateway 必须懂 MCP）。
- **L13 推理引擎 与 L14 模型服务 的边界正在合并**：vLLM、SGLang 自带 OpenAI 兼容 HTTP server，挤压了纯 L14 厂商（KServe、BentoML）的独立性。
- **L15 GPU 云、L16 模型 API 聚合、L17 前沿模型 API 三层正在相互渗透**：CoreWeave 推自家模型；Together / Fireworks 自研推理引擎；Anthropic / OpenAI 转售他人模型（极少，但 Bedrock / Vertex 把这种关系制度化）。
- **L9 后训练 + L11 评测 + L24 Agent 框架 形成 RL 闭环**：RLVR / GRPO 把 L11 的评测器当 reward，把 L24 的 agent rollout 当 trajectory，是 2025 训练范式的核心变化。
- **L34 垂直 Agent 与 L24 Agent 框架的耦合方式分两类**：闭源垂直 Agent（Cursor、Devin、Sierra）几乎都不用第三方 Agent 框架，自己造控制循环；而中小垂直 Agent（Clay、Lovable 的部分组件）大量复用 LangGraph / Agents SDK。
- **L18 LLM 应用框架 在 2025 出现 "去 LangChain 化"信号**：原生 SDK（OpenAI Agents SDK、Claude Agent SDK）抢占了 LangChain 早期的功能位；LangChain 通过 LangGraph + LangSmith 上移到 L24 + L28。
