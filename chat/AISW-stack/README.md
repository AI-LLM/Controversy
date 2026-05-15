# AI 软件栈分层索引：从 GPU 驱动到终端用户 Agent 应用

从最底层的 GPU 驱动 / 固件，一直到最终用户接触的应用，完整一根栈。每层至少列 3 个代表性软件 / 项目 / 厂商；同层多个候选时尽量覆盖闭源前沿、开源主流、新兴挑战者三类。

文件分两大段：

- **A. LLM / Agent 主干（L01–L34）**：当前舆论焦点，从 GPU 驱动到 ChatGPT[[1]](https://chatgpt.com/) / Cursor[[2]](https://cursor.com/) / Devin[[3]](https://devin.ai/) 一根通。
- **B–G. 并列应用分支**：**B** 科学计算 / AI4Science、**C** 机器人、**D** 自动驾驶、**E** 世界模型 / 3D、**F** 经典视觉、**G** 量化金融——共享 **L01–L09** 的硬件 / 内核 / 框架底座，但从 L10 起走自己的领域模型 + 部署路径，不进 LLM 推理服务和 Agent 中间件那条线。

## L 层 × 分支 总表

横轴 7 列对应 **A 主干 + B–G 6 条并列分支**。纵轴每一行是一个 L 层，每个条目**严格归属**到当行 L，不跨层。规则：

- `同 A`：该层在该分支与主干基本沿用同款（驱动 / 内核 / 编译器 / 实验追踪多数如此）。
- `—`：该层在该分支不存在或可忽略。
- **L35–L38** 是 A 主干没有、但 B–G 必需的新增层；A 列保持空。
  - L35 HPC 作业调度 / 工作流（B 专属：Slurm[[4]](https://slurm.schedmd.com/) / PBS / Spack 这一段在 LLM 训练里被 K8s[[5]](https://kubernetes.io/) + Ray[[6]](https://docs.ray.io/en/latest/index.html) 取代）
  - L36 机器人 / 实时中间件（C / D 共用：ROS 2[[7]](https://www.ros.org/) / DriveWorks / AUTOSAR / Holoscan）
  - L37 物理仿真 / 数字孪生引擎（B / C / D / E 共用：Isaac Sim / MuJoCo[[8]](https://mujoco.org/) / GROMACS[[9]](https://www.gromacs.org/) / CARLA / Omniverse）
  - L38 高精地图 / 定位（D 专属）

| L | A. LLM / Agent | B. 科学计算 | C. 机器人 | D. 自动驾驶 | E. 世界模型 / 3D | F. 经典 CV | G. 量化金融 |
|---|---|---|---|---|---|---|---|
| L01 GPU 驱动 / 固件 | NVIDIA / ROCm / Metal / Gaudi driver | 同 A | 同 A | 同 A + NVIDIA DRIVE OS driver | 同 A | 同 A + Hailo / Qualcomm QNN driver | 同 A |
| L02 互连 / 集合通信 | NVLink[[10]](https://www.nvidia.com/en-us/data-center/nvlink/), NCCL[[11]](https://developer.nvidia.com/nccl), InfiniBand[[12]](https://www.nvidia.com/en-us/networking/products/infiniband/) | 同 A，重 MPI + InfiniBand | NVLink for AGI rig；车端 PCIe | NVLink-C2C 整车 + 仿真集群 IB | 同 A | 边缘多无互连 | 同 A |
| L03 GPU 编程模型 | CUDA[[13]](https://developer.nvidia.com/cuda), ROCm[[14]](https://www.amd.com/en/products/software/rocm.html), Metal[[15]](https://developer.apple.com/metal/), SYCL[[16]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html) | 同 A + Julia CUDA.jl[[17]](https://github.com/JuliaGPU/CUDA.jl) | 同 A | 同 A | 同 A | 同 A + Apple Metal | 同 A + RAPIDS[[18]](https://rapids.ai/) |
| L04 GPU 内核库 | cuBLAS[[19]](https://developer.nvidia.com/cublas), cuDNN[[20]](https://developer.nvidia.com/cudnn), FlashAttention[[21]](https://github.com/dao-ailab/flash-attention), NCCL, CUTLASS[[22]](https://github.com/NVIDIA/cutlass) | cuFFT[[23]](https://developer.nvidia.com/cufft), cuSolver[[24]](https://developer.nvidia.com/cusolver), cuSPARSE[[25]](https://developer.nvidia.com/cusparse), cuQuantum[[26]](https://developer.nvidia.com/cuquantum-sdk), NVSHMEM[[27]](https://developer.nvidia.com/nvshmem) | cuDNN + Isaac CUDA kernels | cuDNN + TensorRT plugins | 3DGS rasterizer, NeRF CUDA kernels | cuDNN + TensorRT INT8 | cuDF, cuML, cuOpt |
| L05 编译器 / IR | Triton[[28]](https://github.com/triton-lang/triton), XLA[[29]](https://openxla.org/xla), MLIR[[30]](https://mlir.llvm.org/), TVM[[31]](https://tvm.apache.org/), torch.compile | 同 A + Codon[[32]](https://github.com/exaloop/codon) | 同 A | TensorRT, NVIDIA DLA, TVM | 同 A | TensorRT, OpenVINO, Apple Core ML compiler | 同 A |
| L06 张量 / 训练框架 | PyTorch[[33]](https://pytorch.org/), JAX[[34]](https://github.com/jax-ml/jax), MLX[[35]](https://github.com/ml-explore/mlx), TensorFlow[[36]](https://www.tensorflow.org/) | NumPy[[37]](https://numpy.org/), SciPy[[38]](https://scipy.org/), CuPy[[39]](https://cupy.dev/), JAX, PyTorch, Julia[[40]](https://julialang.org/) | PyTorch + ROS DDS | PyTorch + DriveWorks | PyTorch, JAX, threestudio | PyTorch + OpenMMLab | scikit-learn[[41]](https://scikit-learn.org/), XGBoost[[42]](https://xgboost.readthedocs.io/), LightGBM[[43]](https://github.com/microsoft/LightGBM), PyTorch |
| L07 分布式训练 | DeepSpeed[[44]](https://www.deepspeed.ai/), Megatron[[45]](https://github.com/NVIDIA/Megatron-LM), FSDP[[46]](https://docs.pytorch.org/docs/stable/fsdp.html), NeMo[[47]](https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html), Ray Train[[48]](https://docs.ray.io/en/latest/train/train.html) | MPI[[49]](https://www.mpi-forum.org/) + NCCL（HPC 风格而非 ZeRO） | 多在单 / 几卡 | 同 A（仿真 + 路采联训） | 同 A（video diffusion 训练） | 同 A | 多单卡 |
| L08 训练数据 pipeline | FineWeb[[50]](https://huggingface.co/datasets/HuggingFaceFW/fineweb), datatrove[[51]](https://github.com/huggingface/datatrove), Mosaic Streaming[[52]](https://github.com/mosaicml/streaming) | 实验数据 + 仿真合成 | Open X-Embodiment[[53]](https://robotics-transformer-x.github.io/), DROID[[54]](https://droid-dataset.github.io/), LeRobot[[55]](https://github.com/huggingface/lerobot) dataset | 路采 + 影子模式 + Auto-labeling | 多视角视频 / 3D scan | Roboflow, Encord, Labelbox, FiftyOne | 时间序列 + 因子库 |
| L09 后训练 / 微调 | TRL[[56]](https://github.com/huggingface/trl), verl[[57]](https://github.com/volcengine/verl), Unsloth[[58]](https://unsloth.ai/), Axolotl[[59]](https://github.com/axolotl-ai-cloud/axolotl) | 极少（预训练即终态） | LeRobot, Diffusion Policy[[60]](https://github.com/real-stanford/diffusion_policy), ACT | RLHF on driving sims | 极少 | YOLO finetune + 蒸馏 | sklearn 训练即生产 |
| L10 基础模型权重 | Llama[[61]](https://ai.meta.com/llama/), Claude[[62]](https://www.anthropic.com/claude), GPT[[63]](https://openai.com/api/), Qwen[[64]](https://github.com/QwenLM/Qwen), DeepSeek[[65]](https://www.deepseek.com/en/) | AlphaFold 3[[66]](https://alphafoldserver.com/), GraphCast[[67]](https://deepmind.google/technologies/graphcast/), MatterGen[[68]](https://www.microsoft.com/en-us/research/blog/mattergen-a-new-paradigm-of-materials-design-with-generative-ai/), scGPT[[69]](https://github.com/bowang-lab/scGPT), Evo 2[[70]](https://arcinstitute.org/news/blog/evo2) | GR00T[[71]](https://developer.nvidia.com/isaac/gr00t) N1, π0[[72]](https://www.physicalintelligence.company/) / π0.5, RT-2[[73]](https://robotics-transformer2.github.io/), OpenVLA[[74]](https://openvla.github.io/), RDT-1B[[75]](https://rdt-robotics.github.io/rdt-robotics/) | Tesla FSD[[76]](https://www.tesla.com/support/autopilot) V13/14, Waymo Driver[[77]](https://waymo.com/), Wayve LINGO[[78]](https://wayve.ai/thinking/lingo-natural-language-autonomous-driving/) | Genie 3[[79]](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/), Marble[[80]](https://www.worldlabs.ai/), Cosmos[[81]](https://www.nvidia.com/en-us/ai/cosmos/) | YOLOv11[[82]](https://docs.ultralytics.com/models/yolo11/), SAM 2[[83]](https://ai.meta.com/sam2/), Florence-2[[84]](https://huggingface.co/microsoft/Florence-2-large), RT-DETR[[85]](https://github.com/lyuwenyu/RT-DETR) | BloombergGPT[[86]](https://www.bloomberg.com/company/press/bloomberggpt-50-billion-parameter-llm-tuned-finance/), FinGPT[[87]](https://github.com/AI4Finance-Foundation/FinGPT), TimeGPT[[88]](https://www.nixtla.io/), Chronos[[89]](https://github.com/amazon-science/chronos-forecasting) |
| L11 评测 / 基准 | MMLU[[90]](https://arxiv.org/abs/2009.03300), SWE-bench[[91]](https://www.swebench.com/), MTEB[[92]](https://github.com/embeddings-benchmark/mteb/), METR Time Horizons[[93]](https://metr.org/time-horizons/) | CASP[[94]](https://predictioncenter.org/), WeatherBench[[95]](https://github.com/pangeo-data/WeatherBench), Matbench Discovery[[96]](https://matbench-discovery.materialsproject.org/) | RLBench[[97]](https://github.com/stepjam/RLBench), CALVIN, LIBERO | nuScenes[[98]](https://www.nuscenes.org/), KITTI, Argoverse, CARLA Leaderboard | VBench, 3D-FUTURE | COCO[[99]](https://cocodataset.org/), ImageNet[[100]](https://www.image-net.org/), Open Images | Sharpe / Sortino / IR |
| L12 实验追踪 / MLOps | W&B[[101]](https://wandb.ai/site/), MLflow[[102]](https://mlflow.org/), Neptune[[103]](https://neptune.ai/) | 同 A | 同 A | 同 A + 闭源整车数据平台 | 同 A | 同 A | 同 A |
| L13 推理引擎 | vLLM[[104]](https://github.com/vllm-project/vllm), TensorRT-LLM[[105]](https://github.com/NVIDIA/TensorRT-LLM), SGLang[[106]](https://github.com/sgl-project/sglang), llama.cpp[[107]](https://github.com/ggerganov/llama.cpp) | BioNeMo NIM[[108]](https://www.nvidia.com/en-us/clara/bionemo/) 引擎, Modulus runtime | Isaac ROS[[109]](https://developer.nvidia.com/isaac/ros) GEMs runtime | NVIDIA DRIVE OS[[110]](https://developer.nvidia.com/drive/drive-os), Mobileye EyeQ[[111]](https://www.mobileye.com/technology/eyeq-chip/) runtime, openpilot[[112]](https://github.com/commaai/openpilot) | 3DGS[[113]](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) renderer, Instant-NGP[[114]](https://github.com/NVlabs/instant-ngp) runtime | NVIDIA DeepStream[[115]](https://developer.nvidia.com/deepstream-sdk), Intel OpenVINO[[116]](https://docs.openvino.ai/), Apple Core ML[[117]](https://developer.apple.com/machine-learning/core-ml/) | 通常无独立引擎 |
| L14 模型服务 / 编排 | Triton Inference[[118]](https://github.com/triton-inference-server/server), Ray Serve[[119]](https://docs.ray.io/en/latest/serve/index.html), BentoML[[120]](https://www.bentoml.com/) | BioNeMo NIM Microservices[[121]](https://www.nvidia.com/en-us/clara/bionemo/), Earth-2 Studio[[122]](https://www.nvidia.com/en-us/high-performance-computing/earth-2/) | Isaac Manipulator, MoveIt 2[[123]](https://moveit.ai/) servers | Tesla inference fleet, Mobileye OTA | NVIDIA Omniverse Kit[[124]](https://developer.nvidia.com/omniverse/kit-sdk) | DeepStream pipeline, VMS 平台 | 自建 Python / QuantConnect cloud |
| L15 GPU 云 / 算力市场 | CoreWeave[[125]](https://www.coreweave.com/), Lambda[[126]](https://lambda.ai/), Crusoe[[127]](https://www.crusoe.ai/), Nebius[[128]](https://nebius.com/) | Rescale[[129]](https://rescale.com/), AWS HPC[[130]](https://aws.amazon.com/hpc/), Azure CycleCloud[[131]](https://azure.microsoft.com/en-us/products/cyclecloud) | Tesla 自建, Figure GPU farm | Tesla Dojo[[132]](https://www.tesla.com/AI), Mobileye 自建 | RunPod[[133]](https://www.runpod.io/), fal.ai[[134]](https://fal.ai/) | AWS Panorama[[135]](https://aws.amazon.com/panorama/) 边缘 | 通用 AWS / GCP |
| L16 模型 API 聚合 | OpenRouter[[136]](https://openrouter.ai/), Together[[137]](https://www.together.ai/), Fireworks[[138]](https://fireworks.ai/), Groq[[139]](https://groq.com/) | — | — | — | fal.ai 3D 模型托管 | Replicate[[140]](https://replicate.com/)（YOLO / SAM 托管） | — |
| L17 前沿模型 API | Anthropic[[141]](https://www.anthropic.com/api), OpenAI[[142]](https://openai.com/api/), Gemini[[143]](https://ai.google.dev/), xAI[[144]](https://x.ai/), DeepSeek | Isomorphic AlphaFold Server, Schrödinger LiveDesign API | Skild Brain API, π API（内部） | — | World Labs Marble API, Decart Mirage | — | Bloomberg API |
| L18 LLM 应用框架 | LangChain[[145]](https://www.langchain.com/), LlamaIndex[[146]](https://www.llamaindex.ai/), DSPy[[147]](https://github.com/stanfordnlp/dspy), Vercel AI SDK[[148]](https://ai-sdk.dev/) | — | — | — | — | — | — |
| L19 Embedding / 重排序 | OpenAI text-embedding-3[[149]](https://platform.openai.com/docs/guides/embeddings), Cohere Embed[[150]](https://cohere.com/embed), BGE[[151]](https://github.com/FlagOpen/FlagEmbedding) | ESM-2 / 3（蛋白）, MolE（分子） | — | — | OpenCLIP, SigLIP | CLIP, SigLIP, DINOv2 | FinBERT embedding |
| L20 向量数据库 / 检索 | Pinecone[[152]](https://www.pinecone.io/), Weaviate[[153]](https://weaviate.io/), Qdrant[[154]](https://qdrant.tech/), Milvus[[155]](https://milvus.io/) | FAISS[[156]](https://github.com/facebookresearch/faiss)（蛋白 / 分子搜索） | — | — | 3D scene 索引（少） | Roboflow Universe[[157]](https://universe.roboflow.com/) | — |
| L21 长期记忆 | Mem0[[158]](https://mem0.ai/), Zep[[159]](https://www.getzep.com/), Letta[[160]](https://www.letta.com/) | — | （仅 in-context） | — | — | — | — |
| L22 LLM 网关 / 路由 | LiteLLM[[161]](https://github.com/BerriAI/litellm), Portkey[[162]](https://portkey.ai/), Cloudflare AI Gateway[[163]](https://developers.cloudflare.com/ai-gateway/) | — | — | — | — | — | — |
| L23 Prompt 管理 / 缓存 | PromptLayer[[164]](https://www.promptlayer.com/), Langfuse[[165]](https://langfuse.com/) Prompts, Braintrust[[166]](https://www.braintrust.dev/) | — | — | — | — | — | — |
| L24 Agent 框架 | LangGraph[[167]](https://www.langchain.com/langgraph), AutoGen[[168]](https://github.com/microsoft/autogen), Claude Agent SDK[[169]](https://docs.anthropic.com/en/docs/agents-and-tools) | — | VLA 控制循环（**非 Agent 概念**） | 端到端策略（**非 Agent**） | — | — | — |
| L25 工具协议 / MCP | Anthropic MCP[[170]](https://modelcontextprotocol.io/), Composio[[171]](https://composio.dev/), Arcade[[172]](https://www.arcade.dev/) | — | — | — | — | — | — |
| L26 浏览器 / Computer Use | Browserbase[[173]](https://www.browserbase.com/), Operator[[174]](https://openai.com/index/introducing-operator/), browser-use[[175]](https://github.com/browser-use/browser-use) | — | — | — | — | — | — |
| L27 代码 / Agent 沙箱 | E2B[[176]](https://e2b.dev/), Modal Sandbox[[177]](https://modal.com/), Daytona[[178]](https://www.daytona.io/) | — | — | — | — | — | — |
| L28 LLM 观测 / 追踪 | Langfuse, Arize[[179]](https://arize.com/), LangSmith[[180]](https://www.langchain.com/langsmith-platform) | — | Foxglove[[181]](https://foxglove.dev/), Datadog | 自动驾驶闭源遥测平台 | — | Prometheus[[182]](https://prometheus.io/) + Grafana[[183]](https://grafana.com/) | — |
| L29 Guardrails / 安全 | Guardrails AI[[184]](https://github.com/guardrails-ai/guardrails), NeMo Guardrails[[185]](https://github.com/NVIDIA-NeMo/Guardrails), Lakera[[186]](https://www.lakera.ai/) | — | ISO 13482[[187]](https://www.iso.org/standard/53820.html) 服务机器人安全 | ISO 26262[[188]](https://www.iso.org/standard/68383.html) + 21448 SOTIF + UNECE R157[[189]](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-157-automated-lane-keeping-systems-alks) | — | — | — |
| L30 LLM 评测 / 测试 | Promptfoo[[190]](https://www.promptfoo.dev/), DeepEval[[191]](https://github.com/confident-ai/deepeval), Ragas[[192]](https://github.com/explodinggradients/ragas) | — | — | — | — | — | — |
| L31 语音 (TTS / ASR) | ElevenLabs[[193]](https://elevenlabs.io/), Whisper[[194]](https://github.com/openai/whisper), Cartesia[[195]](https://cartesia.ai/), Deepgram[[196]](https://deepgram.com/) | — | Figure 接 ElevenLabs; NVIDIA Riva[[197]](https://developer.nvidia.com/riva) | Cerence[[198]](https://www.cerence.com/) 车载语音 | — | — | — |
| L32 图像 / 视频 / 3D 生成 | Midjourney[[199]](https://www.midjourney.com/), Sora[[200]](https://openai.com/sora/), FLUX[[201]](https://bfl.ai/), Runway[[202]](https://runwayml.com/) | — | — | — | 与 E 段相互渗透 | — | — |
| L33 通用对话 / 搜索 Agent | ChatGPT, Claude.ai[[203]](https://claude.ai/), Gemini, M365 Copilot[[204]](https://www.microsoft.com/en-us/microsoft-365-copilot), SAP Joule[[205]](https://www.sap.com/products/artificial-intelligence/ai-assistant.html) | — | — | — | — | — | — |
| L34 垂直 Agent 应用 | Cursor, Devin, Salesforce Agentforce[[206]](https://www.salesforce.com/agentforce/), SAP Joule | AlphaFold Server, Schrödinger LiveDesign client | Tesla Optimus, Figure 02, 1X Neo, Unitree GD01 | Tesla FSD, Waymo One, Mobileye Chauffeur | World Labs Marble app, Genie 3 playground | Hikvision, Cognex, Aidoc, Standard AI | Bloomberg Terminal, FactSet Mercury, AlphaSense, Hebbia |
| L35 HPC 作业调度 / 工作流 | — | Slurm, PBS[[207]](https://www.altair.com/pbs-professional/), LSF, Spack[[208]](https://spack.io/), EasyBuild | — | — | — | — | — |
| L36 机器人 / 实时中间件 | — | — | ROS 2, micro-ROS, MoveIt 2, NVIDIA Holoscan[[209]](https://developer.nvidia.com/holoscan-sdk), PX4, QNX | NVIDIA DriveWorks[[210]](https://developer.nvidia.com/drive/driveworks), AUTOSAR[[211]](https://www.autosar.org/) Classic / Adaptive | — | — | — |
| L37 物理仿真 / 数字孪生引擎 | — | GROMACS, OpenMM[[212]](https://openmm.org/), LAMMPS, NAMD, JAX-CFD, PhiFlow | Isaac Sim[[213]](https://developer.nvidia.com/isaac/sim), MuJoCo, Gazebo, Genesis, Drake, Habitat | NVIDIA DRIVE Sim[[214]](https://developer.nvidia.com/drive/simulation), Applied Intuition, CARLA[[215]](https://carla.org/), AirSim | NVIDIA Omniverse[[216]](https://www.nvidia.com/en-us/omniverse/) + USD, Unity ML-Agents | — | — |
| L38 高精地图 / 定位 | — | — | — | HERE[[217]](https://www.here.com/), TomTom[[218]](https://www.tomtom.com/), 四维图新, Mapbox[[219]](https://www.mapbox.com/) | — | — | — |

---

## A. LLM / Agent 主干 — 全栈总览（34 层）

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

**NVIDIA**：
- Display / Compute Driver[[221]](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html)（`nvidia.ko` 内核模块、GSP 固件、`nvidia-smi`、MIG / vGPU）
- Open GPU Kernel Modules[[220]](https://github.com/NVIDIA/open-gpu-kernel-modules)（2022 起开源的 R515+ 内核侧驱动，仅支持 Turing 及更新架构）
- NVIDIA Container Toolkit[[221]](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html) / `nvidia-container-runtime`（K8s / Docker 接入事实标准）

**AMD**：
- `amdgpu` DRM driver[[222]](https://rocm.docs.amd.com/) + `amdkfd` KFD 计算子系统
- ROCm[[14]](https://www.amd.com/en/products/software/rocm.html) runtime + `rocm-smi`
- AMD GPU Operator[[223]](https://instinct.docs.amd.com/projects/gpu-operator/en/latest/)（K8s 接入）

**Intel**：
- `i915` / `xe` driver[[224]](https://docs.kernel.org/gpu/i915.html)（消费 / 数据中心 Xe / Ponte Vecchio / Falcon Shores）
- `habanalabs`[[225]](https://docs.habana.ai/en/latest/Installation_Guide/Driver_Installation.html) 内核驱动（Habana Gaudi 2 / 3）
- Intel GPU Tools (`igt`)[[224]](https://docs.kernel.org/gpu/i915.html) + `xpu-smi`

**华为昇腾（Ascend）**：
- `davinci_manager`[[226]](https://www.hiascend.com/en/hardware/firmware-drivers/community) + `devmm_svm` + `drv_npu` 内核驱动（Atlas / Ascend 910B / 910C）
- HCCN driver[[226]](https://www.hiascend.com/en/hardware/firmware-drivers/community)（互连专用）
- `npu-smi`[[226]](https://www.hiascend.com/en/hardware/firmware-drivers/community)（对位 `nvidia-smi`）
- Ascend Docker Runtime[[226]](https://www.hiascend.com/en/hardware/firmware-drivers/community)

**Apple**：
- Apple Silicon GPU / ANE driver[[227]](https://developer.apple.com/metal/)（macOS / iOS 内置，与 Metal 紧绑定，闭源）
- AGX / DCP（Display Controller Processor）固件[[227]](https://developer.apple.com/metal/)
- AMX co-processor（M 系列 CPU 内置矩阵单元）通过私有 ABI 暴露给 Accelerate[[258]](https://developer.apple.com/documentation/accelerate)
- `powermetrics` / `sysdiagnose`[[227]](https://developer.apple.com/metal/)（对位 `nvidia-smi` 的功耗 / 利用率读取入口）

**AWS（Annapurna / Trainium 阵营）**：
- Neuron driver[[228]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html)（Trainium / Trainium2 / Inferentia2 的内核驱动 `neuron-driver`）
- Neuron Runtime[[229]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html)（用户态运行时；负责 NEFF 加载、DMA、collective）
- `neuron-ls` / `neuron-top`[[229]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html)（对位 `nvidia-smi`）
- AWS Neuron Container Toolkit[[228]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html)（EKS / ECS 接入）

## L02 GPU 互连 / 集合通信

多卡 / 多机之间的物理与协议层；性能瓶颈往往不在 FLOPS 而在这层。

**节点内互连（芯片 ↔ 芯片）**：
- NVIDIA：NVLink[[10]](https://www.nvidia.com/en-us/data-center/nvlink/) / NVSwitch（H100 900 GB/s、B200 1.8 TB/s、GB200 NVL72 全互连域）
- AMD：Infinity Fabric / xGMI[[230]](https://www.amd.com/en/technologies/infinity-architecture)（MI300X 7 路全互连）
- Intel：Xe Link[[231]](https://www.intel.com/content/www/us/en/products/docs/processors/max-series/overview.html)（Ponte Vecchio）
- 华为：HCCS[[232]](https://www.hiascend.com/en/hardware/cluster)（HyperLink；Ascend 910B 内 8 卡 fullmesh，节点内 392 GB/s）
- Apple：UltraFusion[[233]](https://www.apple.com/newsroom/2022/03/apple-unveils-m1-ultra-the-worlds-most-powerful-chip-for-a-personal-computer/)（M Ultra 把两颗 M Max 缝合为单一逻辑芯片，2.5 TB/s）；M 系列内部 fabric 闭源
- AWS：NeuronLink-v3[[234]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)（Trainium2 内 16 芯片 fullmesh）+ Trn2 UltraServer 64 芯片域

**节点间网络**：
- NVIDIA / Mellanox Quantum-2[[235]](https://www.nvidia.com/en-us/networking/quantum2/) / Quantum-X800 InfiniBand + OFED
- AWS EFA[[236]](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html)（Elastic Fabric Adapter）+ SRD 协议（EFA v2 / v3，Trn2 UltraServer 用 EFAv3）
- Ultra Ethernet[[237]](https://ultraethernet.org/)（UEC 1.0，2024）；RoCE v2
- UALink[[238]](https://ualinkconsortium.org/) 1.0（AMD / Intel / Google / Meta 联盟，对位 NVLink 跨节点版）
- 华为：200 GE RoCE（CloudEngine 8800 / 16800 系列；Atlas 900[[377]](https://www.hiascend.com/en/hardware/cluster) 集群）
- Apple：无（Apple 不卖训练集群，节点间网络不在产品线内）

**集合通信库（NCCL 对应面）**：
- NVIDIA NCCL[[11]](https://developer.nvidia.com/nccl)
- AMD RCCL[[239]](https://github.com/ROCm/rccl)（NCCL API 兼容 fork）
- Intel oneCCL[[240]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/oneccl.html)
- 华为 HCCL[[241]](https://www.hiascend.com/cann/hccl)（Huawei Collective Communication Library）
- Apple：MLX[[35]](https://github.com/ml-explore/mlx) Distributed `mlx.distributed`（基于 MPI 或 ring；规模偏研究）
- AWS：Neuron Collective Communication[[242]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/about/collectives.html)（NCCL-style API，跑在 NeuronLink + EFA 上）
- 微软 MSCCL[[243]](https://github.com/microsoft/mscclpp) / MSCCL++（在 NCCL 之上的可编程调度层）

## L03 GPU 编程模型 / 计算 API

让开发者写并行 kernel；下层各家硬件的统一抽象。

**厂商专有 GPU / 加速器计算栈**：
- NVIDIA：CUDA[[13]](https://developer.nvidia.com/cuda)（`nvcc` 编译器、PTX 中间码、CUDA Runtime / Driver API、NVRTC、CUDA Graphs）
- AMD：ROCm / HIP[[244]](https://rocm.docs.amd.com/projects/HIP/en/latest/)（HIP 提供 CUDA 源码级近似兼容，`hipify` 自动迁移）+ HIPCC
- Intel：oneAPI / SYCL / DPC++[[245]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html)（`icpx`）；Habana SynapseAI[[246]](https://docs.habana.ai/en/latest/Gaudi_Overview/Intel_Gaudi_Software_Suite.html)（Gaudi 专用，Python + C++ 接口）
- 华为：CANN[[247]](https://www.hiascend.com/en/cann)（Compute Architecture for Neural Networks）+ AscendC[[248]](https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html)L[[249]](https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/)（runtime C API，对位 CUDA Runtime）+ AscendC（C++ kernel DSL，对位 CUDA C++）
- Apple：Metal[[15]](https://developer.apple.com/metal/) + Metal Performance Shaders（MPS）+ Metal Shading Language（MSL）+ MetalFX；ANE（Apple Neural Engine）通过 Core ML / BNNS 间接暴露，无公开 kernel-level API
- AWS：AWS Neuron SDK[[250]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html) + NKI[[251]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/)（Neuron Kernel Interface，Python DSL，对位 CUDA C++ + Triton）+ Neuron PyTorch / JAX 适配层

**跨厂商 / 便携后端**：
- OpenCL 3.0[[252]](https://www.khronos.org/opencl/)（跨厂商，地位下滑但仍在嵌入式 / Android）
- Vulkan Compute[[253]](https://www.khronos.org/vulkan/)（图形 + 计算合一；llama.cpp 用作便携后端）
- WebGPU[[254]](https://www.w3.org/TR/webgpu/) / wgpu（浏览器内 GPU 计算；Chrome 113 起默认开启）
- Codeplay oneAPI for CUDA[[13]](https://developer.nvidia.com/cuda) / for ROCm（SYCL 跨硬件适配层）

## L04 GPU 内核库（DNN / BLAS / 通信 / Attention）

预编译好的高性能算子，框架直接调用。四大硬件厂商各自一套，再叠加跨厂商的 Attention / fused kernel。

**GEMM / BLAS**：
- NVIDIA：cuBLAS[[19]](https://developer.nvidia.com/cublas) / cuBLASLt
- AMD：rocBLAS[[255]](https://rocm.docs.amd.com/projects/rocBLAS/en/latest/) / hipBLASLt
- Intel：oneMKL[[256]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html)（含 BLAS / LAPACK / FFT / Sparse）
- 华为：CANN AOL[[257]](https://www.hiascend.com/en/cann)（Ascend Operator Library；含 BLAS / Vector kernels）
- Apple：Accelerate / vecLib BLAS[[258]](https://developer.apple.com/documentation/accelerate) + AMX 内置加速；Metal Performance Shaders MPSMatrixMultiplication[[259]](https://developer.apple.com/documentation/metalperformanceshaders)
- AWS：Neuron BLAS kernels（Trainium / Inferentia2[[379]](https://aws.amazon.com/ai/machine-learning/inferentia/) 上的 matmul / GEMM 算子）

**深度学习 primitive（卷积 / RNN / Attention / Norm）**：
- NVIDIA：cuDNN[[20]](https://developer.nvidia.com/cudnn)
- AMD：MIOpen[[260]](https://rocm.docs.amd.com/projects/MIOpen/en/latest/)
- Intel：oneDNN[[261]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onednn.html)（原 MKL-DNN / DNNL）
- 华为：CANN ACLNN[[262]](https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/)（Ascend Neural Network Operator Library）
- Apple：BNNS / BNNSGraph[[263]](https://developer.apple.com/documentation/accelerate/bnns)（Accelerate 内 Basic Neural Network Subroutines）+ MPS Graph + Core ML kernel library
- AWS：Neuron Custom Operators 库 + AWS Neuron[[250]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html) `libnrt` 算子集

**GEMM 模板 / kernel 编写库**：
- NVIDIA：CUTLASS（FlashAttention[[21]](https://github.com/dao-ailab/flash-attention) / vLLM 大量复用）
- AMD：Composable Kernel[[264]](https://github.com/ROCm/composable_kernel) (CK)
- Intel：XeTLA[[265]](https://github.com/intel/xetla)、TileLang
- 华为：AscendC[[248]](https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html) kernel 套件（含 TBE / Tensor Boost Engine 老接口）
- Apple：MLX kernel DSL（C++ + Metal 后端，对位 CUTLASS[[22]](https://github.com/NVIDIA/cutlass) 但远更轻量）
- AWS：NKI[[251]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/)（Neuron Kernel Interface，Trainium 上写 fused kernel 的 Python DSL）

**集合通信**：
- NVIDIA NCCL / AMD RCCL / Intel oneCCL / 华为 HCCL / Apple MLX Distributed[[296]](https://ml-explore.github.io/mlx/build/html/usage/distributed.html) / AWS Neuron Collective Communication（见 L02 集合通信库一节）

**FFT / Sparse / Solver / 量子**：
- NVIDIA：cuFFT、cuSPARSE、cuSolver、cuQuantum[[26]](https://developer.nvidia.com/cuquantum-sdk)、NVSHMEM
- AMD：rocFFT[[266]](https://rocm.docs.amd.com/projects/rocFFT/en/latest/)、rocSPARSE、rocSOLVER
- Intel：oneMKL[[256]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html) DFT / Sparse / Solver
- 华为：CANN AOL[[257]](https://www.hiascend.com/en/cann) 内置 FFT / Sparse / Solver 子集
- Apple：Accelerate vDSP（FFT / DSP）+ Sparse Solvers + LAPACK；Metal[[15]](https://developer.apple.com/metal/) Performance Shaders MPSMatrixDecomposition
- AWS：通过 Neuron 调用上层 JAX / PyTorch[[33]](https://pytorch.org/) 走 XLA → Neuron Compiler；专用 FFT / Solver 库未独立公开

**跨厂商 / 高层 attention 与 fused kernel**：
- FlashAttention[[21]](https://github.com/dao-ailab/flash-attention) 1 / 2 / 3（Tri Dao；FA3 针对 Hopper Tensor Core + TMA；AMD 有 `flash-attention` ROCm fork；Intel Habana 自研 FusedSDPA）
- xFormers[[267]](https://github.com/facebookresearch/xformers)（Meta；memory-efficient attention 集合）
- Triton[[28]](https://github.com/triton-lang/triton) kernels（OpenAI；社区贡献的 fused MoE / RMSNorm / SwiGLU；AMD Triton 与 Intel Triton 在各自硬件上接后端）
- MSCCL / MSCCL++（微软在 NCCL[[11]](https://developer.nvidia.com/nccl) 之上的可编程调度层）

## L05 编译器 / IR

把模型图或 Python 代码编译成 GPU 可执行体；过去十年从单一图编译器演化为多层 IR + JIT 混合。

**厂商专有图编译器 / 设备编译器**：
- NVIDIA：NVCC[[268]](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/) + NVRTC + PTX → SASS（ptxas）
- AMD：HIPCC[[269]](https://github.com/ROCm/HIPCC) + LLVM AMDGPU backend；ROCm Compute Profile (RCP)
- Intel：oneAPI DPC++ compiler[[270]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html)（`icpx`）；Habana SynapseAI Graph Compiler[[271]](https://docs.habana.ai/en/latest/Gaudi_Overview/SynapseAI_Software_Suite.html)
- 华为：CANN Graph Engine[[272]](https://www.hiascend.com/en/cann)（GE）+ TBE / AscendC 算子编译器；MindSpore Graph Engine[[273]](https://github.com/mindspore-ai/mindspore)（MindSpore IR / MindIR）
- Apple：Metal Compiler[[274]](https://developer.apple.com/documentation/metal/metal-libraries)（`metal` + `metallib`）+ Core ML Compiler[[275]](https://developer.apple.com/documentation/coreml)（`coremlcompiler`，把 `.mlmodel` / `.mlpackage` 编成 ANE / GPU / CPU 多目标 program）+ MLX JIT[[276]](https://github.com/ml-explore/mlx)
- AWS：Neuron Compiler[[277]](https://awsdocs-neuron.readthedocs-hosted.com/)（接 PyTorch / JAX / XLA HLO → NEFF 二进制格式）+ XLA-Neuron 后端

**跨厂商 / 上层 IR 与 JIT**：
- OpenAI Triton[[278]](https://github.com/triton-lang/triton)（Python 嵌入式 DSL，事实上的 GPU kernel 写法新标准；NVIDIA / AMD / Intel 各自维护后端）
- PyTorch torch.compile[[279]](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) / TorchInductor + TorchDynamo（PT 2.x 默认编译路径，下接 Triton / C++ / Halide）
- XLA / OpenXLA[[280]](https://github.com/openxla/xla)（JAX 与 TF 默认；Google + AWS + NVIDIA + Meta + Intel + AMD 共治）
- MLIR[[30]](https://mlir.llvm.org/)（LLVM 项目；TPU、IREE、Mojo、torch-mlir、CANN 共享的中间表示）
- TVM / Apache TVM[[281]](https://github.com/apache/tvm) + Unity（陈天奇主导的端到端深度学习编译栈；MLC-LLM 后端）
- IREE[[282]](https://github.com/iree-org/iree)（Google；MLIR-based，定位移动 / 边缘）
- Mojo / MAX[[283]](https://www.modular.com/open-source/mojo)（Modular；Chris Lattner，Python 超集 + MLIR 后端）

## L06 张量 / 训练框架

定义计算图、autograd、optimizer；用户写 `nn.Module` 的那一层。

- **PyTorch[[33]](https://pytorch.org/)**（Meta；2025 LLM 训练事实标准，份额 >70%）
- **JAX + Flax[[284]](https://github.com/google/flax) / NNX / Equinox**（Google；Gemini / Anthropic 训练栈核心）
- **TensorFlow + Keras 3[[285]](https://github.com/keras-team/keras)**（Google；Keras 3 后端可切 JAX / PyTorch / TF）
- **MLX[[35]](https://github.com/ml-explore/mlx)**（Apple；Apple Silicon 原生）
- **MindSpore[[286]](https://github.com/mindspore-ai/mindspore)**（华为）
- **PaddlePaddle[[287]](https://github.com/PaddlePaddle/Paddle)**（百度）
- **tinygrad[[288]](https://github.com/tinygrad/tinygrad)**（George Hotz；研究 / 教学）

## L07 分布式训练框架

把模型与数据切到上千 / 上万卡上，并管 checkpoint / 容错 / 恢复。

- **DeepSpeed[[44]](https://www.deepspeed.ai/)**（Microsoft；ZeRO-1/2/3、ZeRO-Infinity、MoE）
- **Megatron[[45]](https://github.com/NVIDIA/Megatron-LM)-LM / Megatron-Core**（NVIDIA；3D 并行：TP / PP / DP）
- **PyTorch[[33]](https://pytorch.org/) FSDP / FSDP2**（PyTorch 官方；FSDP2 2024 GA）
- **NVIDIA NeMo[[289]](https://github.com/NVIDIA/NeMo)**（Megatron-Core 上的端到端训练 + 数据 + 评测套件）
- **Colossal-AI[[290]](https://github.com/hpcaitech/ColossalAI)**（HPC-AI Tech）
- **Ray Train[[48]](https://docs.ray.io/en/latest/train/train.html)**（Anyscale；调度层在 Ray 上）
- **MosaicML Composer[[291]](https://github.com/mosaicml/composer) / LLM Foundry[[292]](https://github.com/mosaicml/llm-foundry)**（被 Databricks 收购）
- **TorchTitan[[293]](https://github.com/pytorch/torchtitan)**（PyTorch 官方 2024 推出的 LLM 训练参考实现）
- **厂商专有训练栈**：AMD ROCm Megatron-LM fork + ROCm DeepSpeed；Intel Habana Gaudi 上的 Optimum-Habana + DeepSpeed-Habana 集成；华为 MindFormers[[294]](https://github.com/mindspore-lab/mindformers) / MindSpore Distributed（基于 MindSpore 的大模型并行套件，对位 Megatron + DeepSpeed）+ ModelLink[[295]](https://gitee.com/ascend/ModelLink)（昇腾 PyTorch 适配大模型训练套件）；Apple MLX Distributed[[296]](https://ml-explore.github.io/mlx/build/html/usage/distributed.html)（`mlx.distributed`，定位研究 / 小集群）；AWS Neuron Distributed Training + SageMaker HyperPod[[297]](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html)（Trainium2 + EFAv3，支持 FSDP / 张量并行）

## L08 训练数据 pipeline

数据集构建、清洗、去重、tokenize、streaming。这一层 2023 后被独立看待。

- **datatrove[[51]](https://github.com/huggingface/datatrove)**（HuggingFace；FineWeb 的生产工具）
- **MosaicML Streaming**[[52]](https://github.com/mosaicml/streaming)（云对象存储到训练机的流式 dataset）
- **WebDataset[[298]](https://github.com/webdataset/webdataset)**（POSIX tar 流，PyTorch 生态早期事实标准）
- **Nemo Curator[[299]](https://github.com/NVIDIA-NeMo/Curator)**（NVIDIA；GPU 加速去重 / 分类）
- **Dolma toolkit[[300]](https://github.com/allenai/dolma)**（AI2；OLMo 数据集工具）
- **llm-foundry**[[292]](https://github.com/mosaicml/llm-foundry)（Mosaic / Databricks）
- **数据集本体**：FineWeb / FineWeb-Edu（HF）、RedPajama-V2[[301]](https://github.com/togethercomputer/RedPajama-Data)（Together）、Dolma[[302]](https://huggingface.co/datasets/allenai/dolma)（AI2）、The Stack v2[[303]](https://huggingface.co/datasets/bigcode/the-stack-v2)（BigCode）、Common Crawl[[304]](https://commoncrawl.org/)

## L09 后训练 / 微调框架

SFT、RLHF / DPO / IPO / GRPO / RLVR、reward modeling、合成数据。这一层 2024-2025 爆发。

- **TRL[[56]](https://github.com/huggingface/trl)**（HuggingFace；SFT / DPO / GRPO / PPO trainer，事实标准）
- **Unsloth[[58]](https://unsloth.ai/)**（QLoRA 极致优化，单卡微调首选）
- **Axolotl[[59]](https://github.com/axolotl-ai-cloud/axolotl)**（OpenAccess AI Collective；config-driven 微调）
- **LLaMA-Factory[[305]](https://github.com/hiyouga/LLaMA-Factory)**（北航；中文社区主流）
- **OpenRLHF[[306]](https://github.com/OpenRLHF/OpenRLHF)**（OpenLLMAI；分布式 RLHF，Ray 调度）
- **verl**（字节；HybridFlow，veRL，DeepSeek[[65]](https://www.deepseek.com/en/)-R1 风格 RLVR）
- **NeMo-Aligner[[307]](https://github.com/NVIDIA/NeMo-Aligner)**（NVIDIA）

## L10 基础模型权重

可下载（开源 / 开放权重）或可 API 调用的模型本体。这一层 2025 已分裂为开放权重与闭源前沿两轨。

- **开放权重 / 开源**：Llama 3 / 4（Meta）、Qwen 3（阿里）、DeepSeek-V3 / R1、Mistral / Mixtral[[308]](https://mistral.ai/)、Gemma 3[[309]](https://ai.google.dev/gemma)（Google）、Kimi K2[[310]](https://github.com/MoonshotAI/Kimi-K2)（Moonshot）、GLM-4.6[[311]](https://github.com/THUDM/GLM-4)（智谱）、Phi-4[[312]](https://huggingface.co/microsoft/phi-4)（Microsoft）、OLMo 2[[313]](https://github.com/allenai/OLMo)（AI2，真·全开源）
- **闭源前沿**：GPT-5 / GPT-5.1（OpenAI）、Claude[[62]](https://www.anthropic.com/claude) Opus / Sonnet / Haiku 4.x（Anthropic）、Gemini 2.5 / 3（Google DeepMind）、Grok 4（xAI）
- **模型枢纽 / 发现**：HuggingFace Hub[[314]](https://huggingface.co/)、ModelScope[[315]](https://github.com/modelscope/modelscope)（阿里）、Replicate models、Ollama Library[[316]](https://ollama.com/library)、Civitai[[317]](https://civitai.com/models)（图像 / Stable Diffusion 衍生）

## L11 评测 / 基准

公开打分系统；越来越多被用作 RL reward 的代理。

- **lm-evaluation-harness[[318]](https://github.com/EleutherAI/lm-evaluation-harness)**（EleutherAI；HF Open LLM Leaderboard 后端）
- **HELM[[319]](https://github.com/stanford-crfm/helm)**（Stanford CRFM）
- **OpenCompass[[320]](https://github.com/open-compass/opencompass)**（上海 AI Lab）
- **任务类**：MMLU / MMLU-Pro、GSM8K[[321]](https://arxiv.org/abs/2110.14168) / MATH、HumanEval[[322]](https://arxiv.org/abs/2107.03374) / MBPP、SWE-bench / SWE-bench Verified、GPQA[[323]](https://arxiv.org/abs/2311.12022)、ARC-AGI[[324]](https://arcprize.org/arc-agi)、HLE[[325]](https://github.com/centerforaisafety/hle)（Humanity's Last Exam）
- **Agent / 长 horizon**：METR Time Horizons、TAU-bench[[326]](https://github.com/sierra-research/tau-bench)、WebArena[[327]](https://github.com/web-arena-x/webarena)、OSWorld[[328]](https://github.com/xlang-ai/OSWorld)、AgentBench[[329]](https://github.com/THUDM/AgentBench)
- **Embedding / 检索**：MTEB、BEIR[[330]](https://github.com/beir-cellar/beir)
- **对战 / 人类偏好**：LMSYS Chatbot Arena[[331]](https://lmarena.ai/)、SEAL[[332]](https://scale.com/leaderboard)（Scale）
- **代码定制平台**：Inspect AI[[333]](https://github.com/UKGovernmentBEIS/inspect_ai)（UK AISI）、OpenAI Evals[[334]](https://github.com/openai/evals)、DeepEval（参 L30）

## L12 实验追踪 / MLOps

run、metric、artifact、sweep、模型 registry。

- **Weights & Biases (W&B[[101]](https://wandb.ai/site/))**
- **MLflow[[102]](https://mlflow.org/)**（Databricks 开源）
- **Neptune[[103]](https://neptune.ai/).ai**
- **ClearML[[335]](https://clear.ml/)**
- **Comet ML[[336]](https://www.comet.com/site/)**
- **TensorBoard[[337]](https://github.com/tensorflow/tensorboard)**（仍是免费默认）
- **DVC[[338]](https://dvc.org/) / DVC Studio**（Iterative；偏数据版本）

## L13 推理引擎

负责 KV cache、continuous batching、speculative decoding、量化、PagedAttention 等推理侧硬核优化。

**跨厂商 / 通用**：
- vLLM（UC Berkeley → 公司化；PagedAttention 发起者，开源吞吐量基准；CUDA[[13]](https://developer.nvidia.com/cuda) 主线 + ROCm / Intel / Ascend 后端）
- SGLang[[106]](https://github.com/sgl-project/sglang)（LMSYS / xAI；RadixAttention，结构化输出强）
- HuggingFace TGI[[339]](https://github.com/huggingface/text-generation-inference)（Text Generation Inference）
- llama.cpp / GGUF[[340]](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)（Georgi Gerganov；CPU / Apple Silicon / CUDA / ROCm / Vulkan / SYCL 任意后端）
- MLC-LLM[[341]](https://github.com/mlc-ai/mlc-llm)（陈天奇团队；TVM Unity 后端，Web / 移动 / 任意硬件）
- DeepSpeed-FastGen / DeepSpeed-MII[[342]](https://github.com/deepspeedai/DeepSpeed-MII)
- LMDeploy[[343]](https://github.com/InternLM/lmdeploy)（上海 AI Lab；InternLM 配套，NVIDIA + Ascend 双后端）
- Ollama[[344]](https://ollama.com/)（llama.cpp 之上的本地一键运行）

**厂商专有推理栈**：
- NVIDIA：TensorRT-LLM（CUDA[[13]](https://developer.nvidia.com/cuda) Graph + FP8 / FP4，Hopper / Blackwell 专属优化）+ TensorRT 通用
- AMD：AITER[[345]](https://github.com/ROCm/aiter)（AMD Inference Throughput Engine for ROCm）+ vLLM-ROCm 官方分支 + Composable Kernel attention
- Intel：OpenVINO[[346]](https://github.com/openvinotoolkit/openvino)（Xe / Habana / CPU 通吃）+ IPEX-LLM[[347]](https://github.com/intel/ipex-llm)（Intel Extension for PyTorch LLM 分支，原 BigDL-LLM）+ Habana TGI / vLLM-fork
- 华为：MindIE[[348]](https://www.hiascend.com/en/developer/software/mindie)（Mind Inference Engine，对位 TensorRT-LLM）+ MindSpore Lite[[349]](https://www.mindspore.cn/lite/en)（端边一体）+ Ascend vLLM 适配层
- Apple：Core ML（端侧默认推理路径，自动分派 ANE / GPU / CPU）+ MLX（M 系列 GPU 上的 PyTorch-like 框架，含 mlx-lm）+ MPSGraph[[350]](https://developer.apple.com/documentation/metalperformanceshadersgraph) + llama.cpp Metal 后端
- AWS：AWS Neuron + Transformers-Neuronx[[351]](https://aws.amazon.com/ai/machine-learning/neuron/)（Trainium / Inferentia2 上 LLM 推理库）+ vLLM Neuron 后端 + DJLServing[[352]](https://github.com/deepjavalibrary/djl-serving) Neuron

## L14 模型服务 / 编排（GPU orchestration）

把推理引擎封装成 service：自动伸缩、多模型、A/B、批处理。

**跨厂商 / 通用**：
- Ray Serve[[119]](https://docs.ray.io/en/latest/serve/index.html)（Anyscale）
- KServe[[353]](https://github.com/kserve/kserve)（K8s 原生，原 KFServing）
- BentoML[[120]](https://www.bentoml.com/) / Yatai
- Modal（serverless GPU[[620]](https://lammps.org/) 函数）
- Beam[[354]](https://www.beam.cloud/) / Beam Cloud
- Replicate Cog[[355]](https://github.com/replicate/cog)（容器规范 + Replicate 平台）
- Seldon Core[[356]](https://github.com/SeldonIO/seldon-core)

**厂商专有 model server**：
- NVIDIA：Triton Inference Server（事实标准；多框架 / 多模型并行）+ NIM Microservices[[357]](https://developer.nvidia.com/nim)（OpenAI-API 兼容容器）
- AMD：AMD Inference Server[[358]](https://github.com/Xilinx/inference-server)（原 ZenDNN serving，CPU + GPU）+ ROCm Triton Inference 后端
- Intel：OpenVINO Model Server[[359]](https://github.com/openvinotoolkit/model_server)（OVMS，对位 Triton）+ Habana SynapseAI Model Server
- 华为：MindCluster[[360]](https://www.hiascend.com/en)（推理集群管理）+ MindX（昇腾推理参考方案，电力 / 制造 / 金融分行业 SDK）+ ModelArts[[361]](https://www.huaweicloud.com/intl/en-us/product/modelarts.html) 推理服务
- Apple：Core ML 仅端侧，无独立 model server 产品；服务侧 Apple 自家用 Apple Private Cloud Compute[[362]](https://security.apple.com/documentation/private-cloud-compute)（Apple Silicon Server 集群 + Swift on Server，私有不外销）
- AWS：Amazon SageMaker Inference[[363]](https://aws.amazon.com/sagemaker/) + SageMaker MMS（Multi-Model Server）+ Amazon Bedrock[[364]](https://aws.amazon.com/bedrock/)（托管前沿模型，含 Anthropic / Meta / Mistral / Amazon Nova）+ DJL Serving

## L15 GPU 云 / 算力市场

物理 GPU 容量提供方；neocloud 与超大云共存。

- **超大云 GPU**：AWS (P5 / P5e / Trainium2[[378]](https://aws.amazon.com/ai/machine-learning/trainium/) Ultra)、Azure (ND H100 / ND GB200 v6)、Google Cloud (A3 Ultra / TPU v5p / v6e Trillium)、Oracle Cloud (OCI GPU bare-metal)
- **GPU neocloud**：CoreWeave、Lambda Labs、Crusoe、Nebius（前 Yandex 海外）、Voltage Park[[365]](https://www.voltagepark.com/)、Applied Digital[[366]](https://www.applieddigital.com/)
- **市场 / 撮合 / 长尾**：RunPod、Vast.ai[[367]](https://vast.ai/)、TensorDock[[368]](https://www.tensordock.com/)、Salad[[369]](https://salad.com/)、Hyperstack[[370]](https://www.hyperstack.cloud/)
- **训练 + 推理一体**：Together AI、Lepton AI[[371]](https://www.lepton.ai/)（被 NVIDIA 收购）
- **AMD 算力供给**：TensorWave[[372]](https://tensorwave.com/)（北美首家 MI300X 专营 neocloud）、Hot Aisle[[373]](https://hotaisle.xyz/)、Vultr MI300X[[374]](https://www.vultr.com/products/cloud-gpu/)、Oracle OCI MI300X、Microsoft Azure ND MI300X v5
- **Intel Gaudi 算力**：Intel Tiber AI Cloud[[375]](https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html)（原 Intel Developer Cloud）、IBM Cloud Gaudi 3
- **华为昇腾算力**：华为云 ModelArts[[376]](https://www.huaweicloud.com/intl/en-us/product/modelarts.html) + Atlas 900[[377]](https://www.hiascend.com/en/hardware/cluster)（910B / 910C 集群）、运营商云（移动 / 联通 / 电信）昇腾 AI 算力、地方智算中心（如武汉昇腾、济南昇腾）
- **AWS 自研芯片算力**：Trn2 / Trn2 UltraServer（Trainium2[[378]](https://aws.amazon.com/ai/machine-learning/trainium/)，64 芯片 NeuronLink 域）、Inf2（Inferentia2[[379]](https://aws.amazon.com/ai/machine-learning/inferentia/)）；SageMaker HyperPod（训练）、Bedrock（推理 API 直供）
- **Apple 算力供给**：无对外 GPU / NPU 云租赁；服务端仅 Apple Private Cloud Compute[[362]](https://security.apple.com/documentation/private-cloud-compute) 自用，外部不可访问（Apple Intelligence 后端）

## L16 模型 API 聚合 / 路由（推理服务市场）

不直接持有最前沿模型，但把开源 / 半开源模型托管成 OpenAI 兼容 endpoint，并互相竞价。

- **OpenRouter[[136]](https://openrouter.ai/)**（按 token 转售，覆盖 100+ 模型）
- **Together[[137]](https://www.together.ai/) AI**（开源模型托管 + 训练 + 推理引擎自研）
- **Fireworks[[138]](https://fireworks.ai/) AI**（自研 FireAttention 引擎）
- **Groq Cloud**（自家 LPU；Llama[[61]](https://ai.meta.com/llama/) 系超低延迟）
- **Cerebras Inference[[380]](https://www.cerebras.ai/inference)**（WSE-3；超长上下文 + 高速）
- **SambaNova Cloud[[381]](https://sambanova.ai/products/sambacloud)**（SN40L Reconfigurable Dataflow）
- **Replicate[[140]](https://replicate.com/)**（按秒计费，模型即容器）
- **DeepInfra[[382]](https://deepinfra.com/)**、**Anyscale Endpoints[[383]](https://www.anyscale.com/)**、**Hyperbolic[[384]](https://www.hyperbolic.ai/)**

## L17 前沿模型 API（闭源 / 半闭源）

直接调用模型厂商自营 endpoint；当前 90%+ 高端 token 流量在这层。

- **Anthropic[[141]](https://www.anthropic.com/api) API**（Claude Opus / Sonnet / Haiku，含 Tool Use、Computer Use、Skills、Prompt Caching、Files、Batch、Citations、Memory、MCP connector）
- **OpenAI[[142]](https://openai.com/api/) API**（GPT-5.x、o-series、Realtime、Assistants → Responses API、Agents SDK、Files、Batch）
- **Google Gemini API / Vertex AI[[385]](https://cloud.google.com/vertex-ai)**（Gemini 2.5 / 3 Pro / Flash / Nano）
- **xAI API[[386]](https://x.ai/api)**（Grok 4）
- **DeepSeek API[[387]](https://api-docs.deepseek.com/)**（V3 / R1，价格屠夫）
- **企业转售层**：Azure OpenAI Service[[388]](https://azure.microsoft.com/en-us/products/ai-foundry/models/openai/)、AWS Bedrock、Google Vertex AI Model Garden、IBM watsonx[[389]](https://www.ibm.com/products/watsonx)、Databricks Foundation Model APIs[[390]](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)、**SAP BTP GenAI Hub[[391]](https://www.sap.com/products/artificial-intelligence/generative-ai-hub.html)**（SAP 客户在 BTP 内调用 Anthropic / OpenAI / 自家 SAP-AI 的统一入口）、Oracle Cloud Generative AI Service[[392]](https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/)

## L18 LLM 应用框架

prompt 链、工作流、retriever、tool calling 的高层抽象。

- **LangChain[[145]](https://www.langchain.com/) / LangChain Expression Language (LCEL)**
- **LlamaIndex[[146]](https://www.llamaindex.ai/)**（原 GPT-Index；偏 RAG-first）
- **DSPy[[147]](https://github.com/stanfordnlp/dspy)**（Stanford；prompt-as-program、optimizer 驱动）
- **Haystack[[393]](https://haystack.deepset.ai/)**（deepset）
- **Vercel AI SDK[[148]](https://ai-sdk.dev/)**（TypeScript / React 生态最常见）
- **Semantic Kernel[[394]](https://learn.microsoft.com/en-us/semantic-kernel/)**（Microsoft）
- **Mastra[[395]](https://mastra.ai/)**（TS，新兴）
- **Spring AI[[396]](https://spring.io/projects/spring-ai/)**（Java）

## L19 Embedding / 重排序模型与服务

把文本 / 图像变成向量；Reranker 给检索结果二次排序。

- **闭源**：OpenAI text-embedding-3[[397]](https://platform.openai.com/docs/guides/embeddings)、Cohere Embed v3 / Rerank[[398]](https://cohere.com/rerank)、Google Vertex text-embedding-005[[399]](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings)、Voyage AI[[400]](https://www.voyageai.com/)（被 MongoDB 收购）
- **开源**：BGE / BGE-M3（北京智源）、Jina Embeddings v3[[401]](https://jina.ai/embeddings/)、Nomic Embed[[402]](https://www.nomic.ai/)、E5[[403]](https://github.com/microsoft/unilm/tree/master/e5)（Microsoft）、GTE[[404]](https://huggingface.co/collections/Alibaba-NLP/gte-models)（阿里）、Stella[[405]](https://huggingface.co/NovaSearch/stella_en_1.5B_v5)、mxbai-embed[[406]](https://www.mixedbread.com/)
- **多模态**：CLIP[[407]](https://github.com/openai/CLIP) / OpenCLIP[[408]](https://github.com/mlfoundations/open_clip)、SigLIP[[409]](https://huggingface.co/docs/transformers/model_doc/siglip)、Jina-CLIP[[410]](https://jina.ai/models/jina-clip-v2/)

## L20 向量数据库 / 检索引擎

- **专用向量库（SaaS-first）**：Pinecone[[152]](https://www.pinecone.io/)、Weaviate、Qdrant、Milvus / Zilliz
- **开源 / 嵌入式**：Chroma[[411]](https://www.trychroma.com/)、LanceDB[[412]](https://www.lancedb.com/)、FAISS（Meta；库不是服务）、Annoy[[413]](https://github.com/spotify/annoy)、ScaNN[[414]](https://github.com/google-research/google-research/tree/master/scann)
- **关系数据库扩展**：pgvector[[415]](https://github.com/pgvector/pgvector)、pg_vectorize、Supabase Vector[[416]](https://supabase.com/modules/vector)、Neon + pgvector[[417]](https://neon.com/)
- **搜索引擎类**：Elasticsearch dense vector[[418]](https://www.elastic.co/elasticsearch)、OpenSearch k-NN[[419]](https://opensearch.org/)、Vespa[[420]](https://vespa.ai/)、Typesense[[421]](https://typesense.org/)、Meilisearch[[422]](https://www.meilisearch.com/)、Turbopuffer[[423]](https://turbopuffer.com/)
- **嵌入式 + KV**：Redis Vector Search[[424]](https://redis.io/solutions/vector-database/)、SQLite-vec[[425]](https://github.com/asg017/sqlite-vec)

## L21 长期记忆系统

跨会话 / 跨 Agent 的状态层；从 RAG-of-chat 演化到结构化记忆图。

- **Mem0[[158]](https://mem0.ai/)**（开源 + SaaS，事实图 + 向量混合）
- **Zep[[159]](https://www.getzep.com/) / Zep Cloud**（temporal knowledge graph）
- **Letta[[160]](https://www.letta.com/)**（原 MemGPT；研究项目公司化）
- **LangMem[[426]](https://github.com/langchain-ai/langmem)**（LangChain 旗下记忆 SDK）
- **Cognee[[427]](https://www.cognee.ai/)**
- **Anthropic Memory tool[[428]](https://docs.anthropic.com/en/docs/build-with-claude/memory-tool)**（2025 推出，平台内置）

## L22 LLM 网关 / 路由

应用与 L17 / L16 之间的代理层：限流、配额、密钥、fallback、cost guard、A/B。

- **LiteLLM[[161]](https://github.com/BerriAI/litellm)**（BerriAI；100+ provider 适配器，自部署最常用）
- **Portkey[[162]](https://portkey.ai/)**
- **Cloudflare AI Gateway[[163]](https://developers.cloudflare.com/ai-gateway/)**（缓存 + WAF + 计费）
- **Kong AI Gateway[[429]](https://konghq.com/products/kong-ai-gateway)**
- **Helicone[[487]](https://www.helicone.ai/) Gateway**
- **Martian Router[[430]](https://withmartian.com/)**（按 prompt 动态路由）
- **OpenRouter[[136]](https://openrouter.ai/)**（兼有 L16 与 L22 双重身份）
- **企业 / 系统记录层 gateway**：SAP Joule MCP Gateway[[431]](https://www.sap.com/products/artificial-intelligence/ai-assistant.html)（强制非 SAP Agent 经 Joule / BTP 路由到 S/4HANA 才"合规"）、Oracle AI Apps Gateway、Workday AGI Gateway——把"通行权"做到 ERP / HCM 入口

## L23 Prompt 管理 / 提示缓存

prompt 版本化、A/B、提示模板、prompt 级缓存命中分析。

- **PromptLayer[[164]](https://www.promptlayer.com/)**
- **Langfuse Prompt Management[[432]](https://langfuse.com/docs/prompts)**
- **Helicone Prompts[[433]](https://www.helicone.ai/)**
- **Braintrust[[166]](https://www.braintrust.dev/) prompt registry**
- **Latitude[[434]](https://latitude.so/)**（YC W24，prompt-as-code）
- **Agenta[[435]](https://agenta.ai/)**
- **平台原生**：Anthropic Prompt Caching[[436]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)、OpenAI Prompt Caching[[437]](https://platform.openai.com/docs/guides/prompt-caching)、Gemini Context Caching[[438]](https://ai.google.dev/gemini-api/docs/caching)

## L24 Agent 框架

tool-loop、规划、子任务分解、多 agent 协作。2025 这一层从"链式工作流"快速向"事件循环 + 控制平面"迁移。

- **LangGraph**（LangChain[[145]](https://www.langchain.com/)；graph + 持久化 state，企业部署最多）
- **OpenAI Agents SDK[[439]](https://openai.github.io/openai-agents-python/)**（原 Swarm 演化[[440]](https://github.com/openai/swarm)；Responses API 配套）
- **Anthropic Claude Agent SDK[[169]](https://docs.anthropic.com/en/docs/agents-and-tools) / claude-agent-sdk**（Claude Code 同源）
- **AutoGen[[168]](https://github.com/microsoft/autogen) / AutoGen v0.4**（Microsoft Research；多 agent 对话）
- **CrewAI[[441]](https://crewai.com/)**
- **Pydantic AI[[442]](https://ai.pydantic.dev/)**（type-safe，FastAPI 风格）
- **smolagents[[443]](https://github.com/huggingface/smolagents)**（HuggingFace；code-as-action）
- **Mastra**、**Inngest Agent Kit[[444]](https://agentkit.inngest.com/)**、**TaskWeaver[[445]](https://github.com/microsoft/TaskWeaver)**（Microsoft）
- **企业 / 云厂商一体化平台**：Azure AI Foundry[[446]](https://azure.microsoft.com/en-us/products/ai-foundry/)（原 Azure AI Studio，含 Agent Service）、AWS Bedrock Agents[[447]](https://aws.amazon.com/bedrock/agents/)、Google Vertex AI Agent Builder[[448]](https://cloud.google.com/products/agent-builder)、Databricks Mosaic AI Agent Framework[[449]](https://www.databricks.com/product/machine-learning/retrieval-augmented-generation)、SAP Joule Studio[[450]](https://www.sap.com/products/artificial-intelligence/joule-studio.html)（企业级 Agent 构建器，35 解决方案集成、30+ 专属 Agent）、ServiceNow AI Agent Studio[[451]](https://www.servicenow.com/products/ai-agents.html)

## L25 工具协议 / MCP / 集成市场

Agent 怎么调外部世界——文件、API、SaaS、数据库。

- **Anthropic MCP[[170]](https://modelcontextprotocol.io/)（Model Context Protocol）**（2024-11 开源；2025 已被 OpenAI / Google / 主流框架普遍接入；事实标准）
- **Composio[[171]](https://composio.dev/)**（500+ SaaS 集成，认证 + 工具一站式）
- **Arcade[[172]](https://www.arcade.dev/).dev**（auth-first 的 tool runtime）
- **Toolhouse[[452]](https://toolhouse.ai/)**
- **Pipedream Connect[[453]](https://pipedream.com/connect)**
- **Zapier MCP[[454]](https://zapier.com/mcp) / Zapier AI Actions**
- **厂商自营 MCP / Agent 工具（Vendor-side）**：Stripe Agent Toolkit[[455]](https://github.com/stripe/agent-toolkit)、Cloudflare Agents SDK[[456]](https://developers.cloudflare.com/agents/) + Cloudflare MCP[[457]](https://developers.cloudflare.com/agents/model-context-protocol/) + **HTTP 402 pay-per-crawl[[458]](https://blog.cloudflare.com/introducing-pay-per-crawl/)**（把反 Bot 从成本中心变收入中心）、Anthropic Agent Skills[[459]](https://www.anthropic.com/news/agent-skills)（2025-10 公布；与 SAP Joule Skills 同类抽象）、SAP Joule MCP Gateway + Joule Skills（2 500+）、Atlassian Remote MCP[[460]](https://www.atlassian.com/platform/remote-mcp-server)、Notion MCP、Slack MCP、Figma MCP、GitHub MCP、Salesforce MCP for Agentforce
- **CLI 强 wrap 路径**：OpenCLI[[461]](https://opencli.org/)（开放规范，把任意 CLI 描述为 agent-callable tool）、CLI-Anything[[462]](https://github.com/HKUDS/CLI-Anything)（GitHub 21K stars，社区驱动地把已有 CLI 包成 LLM 工具）——与厂商主动出 MCP 形成"第三方强 wrap"对照
- **服务器目录**：Smithery[[463]](https://smithery.ai/)、MCP Hub、PulseMCP[[464]](https://www.pulsemcp.com/)、Glama MCP Registry[[465]](https://glama.ai/mcp)

## L26 浏览器 / Computer Use Agent

让 Agent 操作 GUI / 浏览器 / 桌面。

- **闭源平台**：Anthropic Computer Use[[466]](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)（API 内置）、OpenAI Operator（ChatGPT 内）、Google Project Mariner[[467]](https://deepmind.google/models/project-mariner/) / Gemini browser
- **托管浏览器基础设施**：Browserbase、Hyperbrowser[[468]](https://www.hyperbrowser.ai/)、Steel.dev[[469]](https://steel.dev/)、Anchor Browser[[470]](https://anchorbrowser.io/)、AgentQL[[471]](https://www.agentql.com/)、Browserless[[472]](https://www.browserless.io/)
- **开源 agent 控制器**：browser-use、Skyvern[[473]](https://www.skyvern.com/)、Stagehand[[474]](https://github.com/browserbase/stagehand)（Browserbase）、Nut.js[[475]](https://nutjs.dev/)、Open Interpreter[[476]](https://www.openinterpreter.com/)、Playwright MCP[[477]](https://github.com/microsoft/playwright-mcp)（Microsoft）、Vercel agent-browser[[478]](https://github.com/vercel-labs/agent-browser)（v0 / Vercel AI SDK 配套，把浏览器封装为 agent 可直调的 tool）
- **垂直自动化**：Manus[[479]](https://manus.im/)（端侧通用 agent）、Reworkd[[480]](https://www.reworkd.ai/)、MultiOn[[481]](https://multion.ai/)

## L27 代码 / Agent 沙箱

Agent 跑代码 / 跑命令的隔离环境；MicroVM + 快照成为新基线。

- **E2B[[176]](https://e2b.dev/)**（Firecracker microVM，开源 SDK）
- **Modal Sandboxes**（serverless GPU[[620]](https://lammps.org/) + sandbox 一体）
- **Daytona[[178]](https://www.daytona.io/)**（开源 dev environment manager，被 Agent 平台普遍用作 runner）
- **CodeSandbox SDK[[482]](https://codesandbox.io/sdk) / CodeSandbox Containers**
- **Cloudflare Containers[[483]](https://developers.cloudflare.com/containers/) / Workers Sandbox**
- **Replit Agent runtime[[484]](https://replit.com/products/agent)**（含 Nix-based 沙箱）
- **Devin VM**[[3]](https://devin.ai/)（Cognition 自营）

## L28 LLM 观测 / 追踪（LLM Observability）

trace、span、token / 成本、prompt / completion 日志，是 agent 时代的新 APM。

- **Langfuse[[165]](https://langfuse.com/)**（开源 + cloud，主流之一）
- **Arize Phoenix[[485]](https://phoenix.arize.com/) / Arize AX[[486]](https://arize.com/)**（OpenTelemetry GenAI 推手）
- **LangSmith**（LangChain[[145]](https://www.langchain.com/) 官方）
- **Helicone[[487]](https://www.helicone.ai/)**（proxy-based，零代码接入）
- **Braintrust[[166]](https://www.braintrust.dev/)**（eval + observability 一体）
- **Logfire[[488]](https://logfire.pydantic.dev/)**（Pydantic 团队，OTel-native）
- **W&B Weave[[489]](https://wandb.ai/site/weave/)**
- **Datadog LLM Observability[[490]](https://www.datadoghq.com/product/ai/llm-observability/)**、**New Relic AI Monitoring[[491]](https://newrelic.com/platform/ai-monitoring)**、**Splunk AI Observability[[492]](https://www.splunk.com/en_us/products/observability-cloud.html)**（传统 APM 厂商扩展）

## L29 Guardrails / 安全 / 红队

提示注入防御、PII / 越狱检测、输出过滤、内容策略。

- **Guardrails AI[[184]](https://github.com/guardrails-ai/guardrails)**（开源 validator 框架）
- **NVIDIA NeMo Guardrails[[185]](https://github.com/NVIDIA-NeMo/Guardrails)**（Colang DSL）
- **Lakera Guard / Lakera Red[[493]](https://www.lakera.ai/lakera-guard)**
- **Protect AI[[494]](https://protectai.com/)（含 NB Defense[[495]](https://github.com/protectai/nbdefense)、Guardian、Recon）**
- **Robust Intelligence[[496]](https://www.robustintelligence.com/)**（被 Cisco 收购）
- **Prompt Security[[497]](https://prompt.security/)**、**HiddenLayer[[498]](https://www.hiddenlayer.com/)**、**CalypsoAI[[499]](https://calypsoai.com/)**
- **Llama Guard 3 / Prompt Guard[[500]](https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/)**（Meta 开源策略模型）
- **Promptfoo[[190]](https://www.promptfoo.dev/) red team**（开源越狱测试套件，参 L30）

## L30 LLM 评测 / 测试（CI 中的 prompt 测试）

把 prompt / agent 当作软件来跑回归测试。

- **Promptfoo[[190]](https://www.promptfoo.dev/)**（YAML + CLI，开源主流）
- **DeepEval[[191]](https://github.com/confident-ai/deepeval)**（Confident AI；pytest 风格）
- **Ragas[[192]](https://github.com/explodinggradients/ragas)**（RAG-specific 指标）
- **Braintrust[[166]](https://www.braintrust.dev/) Evals**
- **Patronus AI[[501]](https://www.patronus.ai/)**（合规向）
- **TruLens[[502]](https://www.trulens.org/)**（TruEra；被 Snowflake 收购）
- **OpenAI Evals[[334]](https://github.com/openai/evals)**、**Inspect AI**（UK AISI；安全评测主流）
- **Galileo Evaluate[[503]](https://galileo.ai/)**

## L31 语音（TTS / ASR / 实时对话）

- **TTS**：ElevenLabs、Cartesia、PlayHT[[504]](https://play.ht/)、Hume AI[[505]](https://www.hume.ai/)、Resemble[[506]](https://www.resemble.ai/)、OpenAI tts[[507]](https://platform.openai.com/docs/guides/text-to-speech)、Google Chirp 3[[508]](https://cloud.google.com/text-to-speech/docs/chirp3-hd)、阿里 CosyVoice[[509]](https://github.com/FunAudioLLM/CosyVoice)
- **ASR**：OpenAI Whisper / Whisper Large v3、Deepgram、AssemblyAI[[510]](https://www.assemblyai.com/)、Speechmatics[[511]](https://www.speechmatics.com/)、Rev AI[[512]](https://www.rev.ai/)、NVIDIA Parakeet[[513]](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/)、Google Chirp 2[[514]](https://cloud.google.com/speech-to-text/docs/models/chirp-3)
- **实时语音 / 端到端**：OpenAI Realtime API[[515]](https://platform.openai.com/docs/guides/realtime)、Google Gemini Live[[516]](https://ai.google.dev/gemini-api/docs/live-api)、Anthropic（暂无原生 voice，多用 Cartesia / ElevenLabs 拼接）、Sesame[[517]](https://www.sesame.com/)、Kyutai Moshi[[518]](https://kyutai.org/)、LiveKit Agents[[519]](https://livekit.io/)、Pipecat[[520]](https://www.pipecat.ai/)（编排框架）、Vapi[[521]](https://vapi.ai/)、Retell AI[[522]](https://www.retellai.com/)

## L32 图像 / 视频 / 3D 生成

- **图像（闭源 / SaaS）**：Midjourney、Ideogram[[523]](https://ideogram.ai/)、Adobe Firefly[[524]](https://firefly.adobe.com/)、Google Imagen 3[[525]](https://deepmind.google/technologies/imagen-3/)、OpenAI DALL-E 3[[526]](https://openai.com/index/dall-e-3/) / GPT-4o image、Recraft[[527]](https://www.recraft.ai/)
- **图像（开源 / 工作流）**：Black Forest Labs FLUX.1 / FLUX.2、Stable Diffusion 3[[528]](https://stability.ai/) / SD 3.5 / SDXL（Stability AI）、PixArt-Σ[[529]](https://github.com/PixArt-alpha/PixArt-sigma)、HunyuanImage[[530]](https://github.com/Tencent-Hunyuan/HunyuanImage-3.0)（腾讯）、ComfyUI[[531]](https://github.com/Comfy-Org/ComfyUI)（工作流编辑器）、Automatic1111 WebUI[[532]](https://github.com/AUTOMATIC1111/stable-diffusion-webui)、Fooocus[[533]](https://github.com/lllyasviel/Fooocus)
- **视频**：Runway Gen-4、Pika 2.x[[534]](https://pika.art/)、Luma Dream Machine[[535]](https://lumalabs.ai/dream-machine) / Ray2、Kling[[536]](https://app.klingai.com/global)（快手）、Hailuo MiniMax[[537]](https://hailuoai.video/)、OpenAI Sora、Google Veo 3[[538]](https://deepmind.google/technologies/veo/)、HunyuanVideo[[539]](https://github.com/Tencent-Hunyuan/HunyuanVideo)（腾讯开源）、Wan 2.x[[540]](https://github.com/Wan-Video/Wan2.2)（阿里开源）
- **3D / 场景**：Luma Genie[[541]](https://lumalabs.ai/)、Meshy[[542]](https://www.meshy.ai/)、Tripo3D[[543]](https://www.tripo3d.ai/)、Rodin[[544]](https://hyper3d.ai/)、World Labs[[545]](https://www.worldlabs.ai/)（Fei-Fei Li）、CSM[[546]](https://www.csm.ai/)
- **托管 / 推理市场**：fal.ai、Replicate[[140]](https://replicate.com/)、RunPod Serverless（这一层与 L16 重合，但更偏 diffusion 工作负载）

## L33 通用对话 / 搜索 Agent（终端用户）

直接给非开发者用户用的"AI 助手"。

- **ChatGPT**（OpenAI；含 Tasks、Operator[[174]](https://openai.com/index/introducing-operator/)、Codex、Connectors）
- **Claude.ai**（Anthropic[[141]](https://www.anthropic.com/api)；含 Projects、Artifacts、Computer Use、Skills、Claude Memory、Claude Desktop）
- **Gemini app[[547]](https://gemini.google.com/) / Gemini Advanced**（Google）
- **Grok[[548]](https://grok.com/)**（xAI；X 内嵌 + grok.com）
- **DeepSeek Chat[[549]](https://chat.deepseek.com/)**、**Kimi[[550]](https://kimi.moonshot.cn/)**（Moonshot）、**通义千问[[551]](https://tongyi.aliyun.com/)**、**豆包[[552]](https://www.doubao.com/)**（字节）
- **搜索类**：Perplexity[[553]](https://www.perplexity.ai/)、You.com[[554]](https://you.com/)、Brave Leo[[555]](https://brave.com/leo/)、Arc Search[[556]](https://arc.net/search)（Browser Company）、Komo[[557]](https://komo.ai/)
- **多模型聚合 / 隐私**：Poe[[558]](https://poe.com/)（Quora）、Le Chat[[559]](https://mistral.ai/products/le-chat)（Mistral）、HuggingChat[[560]](https://huggingface.co/chat/)、Msty[[561]](https://msty.ai/)（本地）、LM Studio[[562]](https://lmstudio.ai/)（本地）
- **企业内 Copilot / 默认入口**：Microsoft 365 Copilot（$30/seat，企业 AI 默认入口；CIO 把它当 SAP / Workday / Slack 的统一抢前端）、Google Gemini for Workspace[[563]](https://workspace.google.com/solutions/ai/)、Slack AI[[564]](https://slack.com/features/ai)、Notion AI[[565]](https://www.notion.com/)、Glean Assistant[[566]](https://www.glean.com/)、SAP Joule（SAP 客户内嵌 Agent UI，生产采用率仅 3% 但是 SAP 战略中枢）

## L34 垂直 Agent 应用（终端用户）

按行业 / 角色划分的 Agent；2025 在编码、设计、营销、客服、医疗、法律均跑出独立公司。

- **编码 Agent**：Cursor、Claude Code[[567]](https://claude.ai/code)（Anthropic）、Devin（Cognition）、Windsurf[[568]](https://windsurf.com/)（被 OpenAI 收购）、Replit Agent[[569]](https://replit.com/products/agent)、Codex CLI[[570]](https://github.com/openai/codex)（OpenAI）、Aider[[571]](https://aider.chat/)、GitHub Copilot Workspace[[572]](https://githubnext.com/projects/copilot-workspace/)、Augment[[573]](https://www.augmentcode.com/)、Amp[[574]](https://ampcode.com/)（Sourcegraph）、Lovable[[575]](https://lovable.dev/)、Bolt.new[[576]](https://bolt.new/)、v0[[577]](https://v0.app/)（Vercel）、Manus
- **设计 / 内容**：Figma AI[[578]](https://www.figma.com/ai/) / Make[[579]](https://www.figma.com/make/)、Galileo AI[[580]](https://www.figma.com/make/)、Framer AI[[581]](https://www.framer.com/ai/)、Canva Magic Studio[[582]](https://www.canva.com/canva-ai/)、Jasper[[583]](https://www.jasper.ai/)、Copy.ai[[584]](https://www.copy.ai/)、Notion AI
- **销售 / 营销 / 客服**：Decagon[[585]](https://decagon.ai/)、Sierra[[586]](https://sierra.ai/)、Ada[[587]](https://www.ada.cx/)、Intercom Fin[[588]](https://fin.ai/)、Cresta[[589]](https://cresta.com/)、Clay[[590]](https://www.clay.com/)、11x.ai[[591]](https://www.11x.ai/)、AirOps[[592]](https://www.airops.com/)、**Salesforce Agentforce**（CRM 数据上的 Agent 平台，per-conversation $2 定价）
- **企业知识 / 内部 IT**：Glean[[593]](https://www.glean.com/)、Moveworks[[594]](https://www.moveworks.com/)、Hebbia[[595]](https://www.hebbia.com/)、Harvey[[596]](https://www.harvey.ai/)（法律）、Casetext CoCounsel[[597]](https://cocounsel.thomsonreuters.com/)（被 Thomson Reuters 收购）
- **ERP / HCM / ITSM 内嵌 Agent（系统记录层自营）**：SAP Joule（覆盖 S/4HANA、SuccessFactors、Ariba、Concur、Fieldglass；30+ 专属 Agent，FY25 BTP 收入是 SAP "Agent toll booth" 押注核心）、Oracle AI Apps[[598]](https://www.oracle.com/applications/fusion-ai/ai-agents/) / Oracle Fusion AI Agents、Workday AGI / Workday Illuminate[[599]](https://www.workday.com/en-us/artificial-intelligence.html)、ServiceNow Now Assist[[600]](https://www.servicenow.com/platform/now-assist.html) + AI Agents（ITSM / HRSD / CSM）、Microsoft Dynamics 365 Copilot[[601]](https://www.microsoft.com/en-us/dynamics-365/)
- **代码评审 / 测试 / 安全 Agent**：CodeRabbit[[602]](https://www.coderabbit.ai/)、Greptile[[603]](https://www.greptile.com/)、Qodo[[604]](https://www.qodo.ai/)、Meticulous[[605]](https://www.meticulous.ai/)、Snyk DeepCode AI[[606]](https://snyk.io/platform/deepcode-ai/)（这一层与 SDLC 栈高度重合，详见 [`../SDLC-stack/README.md`](../SDLC-stack/README.md)）
- **医疗 / 科研**：Abridge[[607]](https://www.abridge.com/)、Hippocratic AI[[608]](https://hippocraticai.com/)、Ambience[[609]](https://www.ambiencehealthcare.com/)、Future House[[610]](https://www.futurehouse.org/)、Scite[[611]](https://scite.ai/)

---

## 并列应用分支（共享 L01–L09，从 L10 起分叉）

LLM 不是 GPU 的唯一负载。下面 6 条分支（**B** 科学计算 / **C** 机器人 / **D** 自动驾驶 / **E** 世界模型 / 3D / **F** 经典 CV / **G** 量化金融）与 L10–L34 并列存在，物理上跑在同一批 GPU 上，逻辑上各自独立。B 因为最早成形而拆出 B1 / B2 / B3 三个子层；C–G 用字母 + 小写后缀（Ca / Cb / …）继续切。

### B1 科学计算 / HPC 通用底座（与 L06–L09 并行）

数值仿真、PDE 求解、分子动力学、量子模拟、线性 / 整数规划——这一段比深度学习古老 30 年，但 2023 后被 GPU 与 AI 重新激活。

- **数值 / 张量底座（与深度学习共享）**：NumPy、SciPy、CuPy、JAX、PyTorch[[33]](https://pytorch.org/)（autograd 也用作物理仿真）、Julia + CUDA.jl
- **经典 HPC 运行时**：OpenMP[[612]](https://www.openmp.org/)I[[613]](https://www.open-mpi.org/)、MPICH[[614]](https://www.mpich.org/)、NVIDIA HPC-X[[615]](https://developer.nvidia.com/networking/hpc-x)、UCX[[616]](https://openucx.org/)；OpenMP；Slurm、PBS[[617]](https://altair.com/pbs-professional)、LSF[[618]](https://www.ibm.com/products/hpc-workload-management)；Spack、EasyBuild[[619]](https://easybuild.io/)（HPC 包管理）
- **分子 / 化学 / 生物仿真**：GROMACS（CUDA / SYCL）、OpenMM、LAMMPS-GPU[[620]](https://lammps.org/)、NAMD-CUDA[[621]](https://www.ks.uiuc.edu/Research/namd/)、AMBER[[622]](https://ambermd.org/)、Schrödinger Suite（商业）[[623]](https://www.schrodinger.com/)
- **量子模拟 / 编程**：NVIDIA cuQuantum + CUDA-Q[[624]](https://developer.nvidia.com/cuda-q)、IBM Qiskit[[625]](https://www.ibm.com/quantum/qiskit)、Google Cirq[[626]](https://quantumai.google/cirq)、Xanadu PennyLane[[627]](https://pennylane.ai/)、Quantinuum TKET[[628]](https://www.quantinuum.com/products-solutions/developer-tools)
- **优化 / 运筹**：NVIDIA cuOpt（GPU 路径规划）[[629]](https://www.nvidia.com/en-us/ai-data-science/products/cuopt/)、Gurobi[[630]](https://www.gurobi.com/)、IBM CPLEX[[631]](https://www.ibm.com/products/ilog-cplex-optimization-studio)、Google OR-Tools[[632]](https://developers.google.com/optimization)、COIN-OR[[633]](https://www.coin-or.org/)
- **CFD / 工程仿真**：Ansys Fluent (GPU)[[634]](https://www.ansys.com/products/fluids/ansys-fluent)、Siemens Simcenter STAR-CCM+[[635]](https://www.siemens.com/en-us/products/simcenter/fluids-thermal-simulation/star-ccm/)、NVIDIA Modulus（物理信息 NN）[[636]](https://developer.nvidia.com/physicsnemo)、PhiFlow[[637]](https://github.com/tum-pbs/PhiFlow)、JAX-CFD[[638]](https://github.com/google/jax-cfd)

### B2 AI4Science 领域基础模型（与 L10 并行）

把"基础模型"的范式从语言迁到分子、天气、材料、基因、数学。2024–2025 是 AlphaFold 3 + GraphCast + MatterGen 三个里程碑同年发生的一年。

- **蛋白质 / 抗体 / 复合物**：AlphaFold 3（Google DeepMind / Isomorphic Labs，2024-05；2024-11 开放权重学术非商用）、RoseTTAFold All-Atom（Baker Lab）[[639]](https://github.com/baker-laboratory/RoseTTAFold-All-Atom)、ESM-3（EvolutionaryScale）[[640]](https://www.evolutionaryscale.ai/)、Boltz-1 / Boltz-2（MIT，2024–2025；Boltz-2 含亲和力预测）[[641]](https://github.com/jwohlwend/boltz)、Chai-1（Chai Discovery）[[642]](https://www.chaidiscovery.com/)
- **小分子 / 药物 / 反应**：NVIDIA BioNeMo MolMIM[[643]](https://docs.nvidia.com/nim/bionemo/molmim/latest/overview.html)、OpenFold[[644]](https://openfold.io/)、DiffDock（Gabriele Corso）[[645]](https://github.com/gcorso/DiffDock)、AlphaFold-Multimer、Insilico Medicine Pharma.AI[[646]](https://pharma.ai/)
- **天气 / 气候**：GraphCast、GenCast（DeepMind）[[647]](https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/)、Pangu-Weather（华为，2023 Nature）[[648]](https://github.com/198808xc/Pangu-Weather)、FourCastNet（NVIDIA）[[649]](https://github.com/NVlabs/FourCastNet)、Aurora（Microsoft，2024）[[650]](https://www.microsoft.com/en-us/research/project/aurora-forecasting/)、Fuxi（复旦）[[651]](https://github.com/tpys/FuXi)、ECMWF AIFS[[652]](https://www.ecmwf.int/en/newsletter/178/news/aifs-new-ecmwf-forecasting-system)
- **材料 / 凝聚态**：MatterGen（Microsoft Research，2024）、MACE（Cambridge）[[653]](https://github.com/ACEsuit/mace)、NequIP[[654]](https://github.com/mir-group/nequip)、Allegro（MIT）[[655]](https://github.com/mir-group/allegro)、GNoME（DeepMind，220 万新晶体）[[656]](https://deepmind.google/blog/millions-of-new-materials-discovered-with-deep-learning/)、Orb（Orbital Materials）[[657]](https://www.orbitalindustries.com/)
- **数学 / 形式化推理**：AlphaProof + AlphaGeometry 2（DeepMind，2024 IMO 银牌）[[658]](https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/)、FunSearch[[659]](https://github.com/google-deepmind/funsearch)、Lean + Lean Copilot[[660]](https://leanprover-community.github.io/)、DeepSeek-Prover-V2[[661]](https://github.com/deepseek-ai/DeepSeek-Prover-V2)
- **单细胞 / 基因组**：scGPT（Wang Bo）、Geneformer（Christina Theodoris）[[662]](https://huggingface.co/ctheodoris/Geneformer)、scFoundation（清华 + 百图生科）[[663]](https://github.com/biomap-research/scFoundation)、GeneCompass[[664]](https://github.com/xCompass-AI/GeneCompass)、Evo 2（Arc Institute，1.7T 核苷酸训练）
- **医学影像**：MONAI（NVIDIA + KCL）[[665]](https://monai.io/)、MedSAM[[666]](https://github.com/bowang-lab/MedSAM)、TotalSegmentator[[667]](https://github.com/wasserth/TotalSegmentator)、Google MedGemini[[668]](https://research.google/blog/advancing-medical-ai-with-med-gemini/)、Microsoft RAD-DINO[[669]](https://huggingface.co/microsoft/rad-dino)

### B3 科学 / 工程平台与服务（与 L13–L17 并行）

把 B2 的模型工程化、API 化、SaaS 化。

- **NVIDIA 自研栈**：BioNeMo Framework + BioNeMo NIM Microservices[[670]](https://www.nvidia.com/en-us/clara/bionemo/)、Earth-2 + Earth-2 Studio[[671]](https://www.nvidia.com/en-us/omniverse/)、Modulus（PINN / Neural Operator）、CUDA-Q Cloud[[672]](https://developer.nvidia.com/cuda-q)
- **闭源 / 公司化研发平台**：Isomorphic Labs AlphaFold Server[[673]](https://alphafoldserver.com/)、Schrödinger LiveDesign（药物发现 SaaS）[[674]](https://www.schrodinger.com/platform/products/livedesign/)、Recursion Pharmaceuticals BioHive-2（自营超算 + 模型）[[675]](https://www.recursion.com/)、Cradle.bio[[676]](https://www.cradle.bio/)、Profluent[[677]](https://www.profluent.bio/)
- **科学计算云**：Rescale、CoreWeave Mission Control（HPC + AI 双模）、AWS HPC（ParallelCluster）、Azure CycleCloud、Google Cluster Toolkit[[678]](https://docs.cloud.google.com/cluster-toolkit/docs/overview)
- **科学数据 / Notebook**：Quarto[[679]](https://quarto.org/)、Jupyter + JupyterHub[[680]](https://jupyter.org/hub)、Anaconda[[681]](https://www.anaconda.com/)、Hugging Face Datasets for Science（PubMedQA、OpenProteinSet）

### C 机器人栈：从中间件到 VLA 模型（与 L18–L26 并行）

物理具身 AI 自己一根栈。2024–2025 关键变化是 VLA（Vision-Language-Action）取代了过去的"感知 + 规划 + 控制"三段式。

- **Ca 机器人中间件 / 实时 OS**：ROS 2（事实标准，Humble / Iron / Jazzy）、NVIDIA Isaac ROS、MoveIt 2、micro-ROS（MCU 上的 ROS）[[682]](https://micro.ros.org/)、PX4 / ArduPilot[[683]](https://ardupilot.org/)（无人机）[[684]](https://px4.io/)；实时层 NVIDIA Holoscan、QNX[[685]](https://blackberry.qnx.com/en)、VxWorks[[686]](https://www.windriver.com/products/vxworks)、Xenomai[[687]](https://xenomai.org/)
- **Cb 仿真 / 数字孪生**：NVIDIA Isaac Sim + Isaac Lab[[688]](https://developer.nvidia.com/isaac/lab)、NVIDIA Cosmos（世界基础模型，2025-01 发布）[[689]](https://www.nvidia.com/en-us/ai/cosmos/)、MuJoCo + MuJoCo-MJX（DeepMind 2021 收购后开源 + JAX 化）、Gazebo / Ignition、Genesis（CMU + 多校，2024-12，零样本物理仿真）[[690]](https://genesis-embodied-ai.github.io/)、Drake（TRI）[[691]](https://drake.mit.edu/)、Habitat 3（Meta）[[692]](https://aihabitat.org/)、AI2-THOR[[693]](https://ai2thor.allenai.org/)、Unity ML-Agents[[694]](https://github.com/unity-technologies/ml-agents)
- **Cc 机器人基础模型 / VLA**：NVIDIA GR00T N1 / GR00T-Dreams[[695]](https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks)、Physical Intelligence π0 / π0.5（2024–2025，Sergey Levine、Chelsea Finn）[[696]](https://www.pi.website/blog/pi0)、Google DeepMind RT-2 / Open X-Embodiment / Gemini Robotics（2025-03）[[697]](https://deepmind.google/models/gemini-robotics/)、Skild AI Skild Brain（$300M Series A）[[698]](https://www.skild.ai/)、Figure Helix[[699]](https://www.figure.ai/helix)、1X World Model[[700]](https://www.1x.tech/discover/1x-world-model)、OpenVLA（Stanford）、RDT-1B（清华）、Octo（UC Berkeley）[[701]](https://octo-models.github.io/)
- **Cd 数据 / 训练框架**：LeRobot（HuggingFace；社区主流）、Diffusion Policy（哥伦比亚 + TRI）、ACT（Tony Zhao）[[702]](https://github.com/tonyzhaozh/act)、Open X-Embodiment 数据集（22 机器人形态、527 任务）、DROID 数据集
- **Ce 终端机器人产品**：人形 Tesla Optimus[[703]](https://www.tesla.com/AI)、Figure 02 / 03[[704]](https://www.figure.ai/)、1X Neo Beta[[705]](https://www.1x.tech/neo)、Apptronik Apollo[[706]](https://apptronik.com/apollo)、Unitree H1 / G1 / GD01[[707]](https://www.unitree.com/h1/)；四足 Boston Dynamics Spot[[708]](https://bostondynamics.com/products/spot/)、ANYmal[[709]](https://www.anybotics.com/robotics/anymal/)、Unitree Go2[[710]](https://www.unitree.com/go2/)；服务 / 物流 Agility Robotics Digit[[711]](https://www.agilityrobotics.com/)、Covariant Brain（被 Amazon "聘走团队"）；手术 Intuitive da Vinci 5[[712]](https://www.intuitive.com/en-us/products-and-services/da-vinci/5)

### D 自动驾驶栈（与 L18–L34 并行）

闭源端到端神经网络栈已成为主流；HD 地图 + 规则栈正在被替代。

- **Da 闭源端到端 / 整车**：Tesla FSD V13 / V14（HW4 → HW5）、Waymo Driver（Multi-Modal Foundation Model 路线）、Mobileye SuperVision / Chauffeur / Drive[[713]](https://www.mobileye.com/solutions/super-vision/)、华为 ADS 3.0 / 4.0、小鹏 XNGP、理想 AD Max、Momenta、Pony.ai、Wayve（伦敦，端到端 self-driving 模型 LINGO + GAIA）[[714]](https://wayve.ai/)
- **Db 车载 AI 平台 / 芯片栈**：NVIDIA DRIVE Thor + DRIVE AV / DRIVE OS[[715]](https://developer.nvidia.com/drive/agx)、Mobileye EyeQ6 / EyeQ Ultra[[716]](https://www.mobileye.com/solutions/super-vision/)、Qualcomm Snapdragon Ride[[717]](https://www.qualcomm.com/automotive/solutions/snapdragon-ride)、Horizon Robotics Journey 6（中国主流国产替代）[[718]](https://en.horizon.auto/)、地平线 SuperDrive
- **Dc 开源 / 开放栈**：百度 Apollo[[719]](https://www.apollo.auto/en/)、Autoware (Foundation)[[720]](https://autoware.org/)、Comma.ai openpilot、CARLA（仿真）、AirSim（已停维但仍流行）
- **Dd 仿真 / 数据闭环**：NVIDIA DRIVE Sim + Omniverse、Applied Intuition（仿真 + 数据平台）[[721]](https://www.appliedintuition.com/)、Foretellix[[722]](https://www.foretellix.com/)、Cognata、Parallel Domain、Helm.ai
- **De 高精地图 / 定位（被端到端架构挤压但未消失）**：HERE、TomTom、四维图新、Mapbox、Atlatec[[723]](https://www.bosch.com/)（被 Bosch 收购）

### E 世界模型 / 3D 重建 / 游戏 AI（与 L32 并行但目标不同）

L32 偏"生成图像 / 视频"；这一支偏"生成可交互的 3D 世界"。

- **Ea 通用世界模型**：Google DeepMind Genie 2 / Genie 3（2025-08，从一张图生成可交互 1 分钟世界）[[724]](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)、World Labs Marble（Fei-Fei Li，2025-12 GA）[[725]](https://www.worldlabs.ai/)、Wayve GAIA-2[[726]](https://wayve.ai/science/gaia/)、NVIDIA Cosmos World Foundation Models、Decart Mirage、Odyssey
- **Eb 3D 重建 / 新视角合成**：NeRF / Instant-NGP（NVIDIA）、3D Gaussian Splatting（Inria 2023；事实标准）、Mip-Splatting[[727]](https://github.com/autonomousvision/mip-splatting)、Luma Genie、Polycam[[728]](https://poly.cam/)、KIRI Engine[[729]](https://www.kiriengine.app/)
- **Ec 文本 → 3D / Mesh**：Meshy、Tripo3D（VAST）、Rodin（DeemosTech）[[730]](https://hyperhuman.deemos.com/)、Hunyuan3D 2.5（腾讯）[[731]](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)、Trellis（Microsoft）[[732]](https://github.com/microsoft/TRELLIS)、CSM、Spline AI[[733]](https://spline.design/)
- **Ed 游戏内 NPC / 引擎 AI**：NVIDIA ACE（Audio2Face、Riva、NeMo Retriever 套件）[[734]](https://developer.nvidia.com/ace-for-games)、Inworld AI[[735]](https://inworld.ai/)、Convai[[736]](https://convai.com/)、Charisma.ai[[737]](https://charisma.ai/)
- **Ee 工业 / 编辑器**：NVIDIA Omniverse + USD、Unity Sentis（端内 ONNX 推理）[[738]](https://unity.com/products/sentis)、Unreal NNE（Neural Network Engine）、Pixar OpenUSD[[739]](https://openusd.org/)、Houdini Copernicus[[740]](https://www.sidefx.com/products/whats-new-in-h205/copernicus/)

### F 经典计算机视觉 / 边缘感知（与 L13–L14 并行，但模型不属 LLM）

工业视觉、安防、医学影像、OCR、文档智能——这一段在 LLM 大火前就有，2024–2025 又被 VLM 部分蚕食但远未消失。

- **Fa 检测 / 分割 / Pose**：YOLOv10 / v11 / v12（Ultralytics）[[741]](https://www.ultralytics.com/)、RT-DETR（百度）、Detectron2（Meta）[[742]](https://github.com/facebookresearch/detectron2)、MMDetection / MMPose / MMSegmentation（OpenMMLab）[[743]](https://github.com/open-mmlab)、SAM 2（Meta，视频分割）、Grounding DINO[[744]](https://github.com/IDEA-Research/GroundingDINO)、Florence-2（Microsoft）
- **Fb OCR / 文档智能**：PaddleOCR（百度，开源主流）[[745]](https://github.com/PaddlePaddle/PaddleOCR)、Tesseract[[746]](https://github.com/tesseract-ocr/tesseract)、Surya[[747]](https://github.com/VikParuchuri/surya)、DocLayout-YOLO[[748]](https://github.com/opendatalab/DocLayout-YOLO)、Nougat（Meta，学术 PDF）[[749]](https://github.com/facebookresearch/nougat)、MinerU（上海 AI Lab）[[750]](https://github.com/opendatalab/MinerU)、Mistral OCR[[751]](https://mistral.ai/news/mistral-ocr)、Reducto[[752]](https://reducto.ai/)、Unstructured.io[[753]](https://unstructured.io/)
- **Fc 视频理解**：InternVideo 2.5[[754]](https://github.com/OpenGVLab/InternVideo)、VideoLLaMA 3[[755]](https://github.com/DAMO-NLP-SG/VideoLLaMA3)、Qwen2.5-VL[[756]](https://github.com/QwenLM/Qwen-VL)、TwelveLabs Marengo[[757]](https://www.twelvelabs.io/product/models-overview)、Video-CCAM[[758]](https://github.com/QQ-MM/Video-CCAM)
- **Fd 边缘 / 嵌入式部署**：NVIDIA DeepStream + TensorRT、Intel OpenVINO、Qualcomm AI Engine Direct（QNN）[[759]](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk)、Arm NN[[760]](https://www.arm.com/products/silicon-ip-cpu/ethos/arm-nn)、Apple Core ML、MediaPipe（Google）[[761]](https://developers.google.com/mediapipe)、Hailo Dataflow Compiler[[762]](https://hailo.ai/products/hailo-software/hailo-ai-software-suite/)
- **Fe 数据 / 训练平台**：Roboflow[[763]](https://roboflow.com/)、Encord[[764]](https://encord.com/)、Labelbox[[765]](https://labelbox.com/)、Voxel51 FiftyOne[[766]](https://voxel51.com/fiftyone)、CVAT[[767]](https://www.cvat.ai/)、Supervisely[[768]](https://supervisely.com/)
- **Ff 终端应用**：工业 Cognex VisionPro Deep Learning[[769]](https://www.cognex.com/en/products/machine-vision-software/visionpro-software)、Keyence[[770]](https://www.keyence.com/products/vision/)、Landing AI（Andrew Ng）[[771]](https://landing.ai/)；安防 Hikvision[[772]](https://www.hikvision.com/en/)、Dahua[[773]](https://www.dahuasecurity.com/)；医学影像 Aidoc[[774]](https://www.aidoc.com/)、Annalise.ai[[775]](https://annalise.ai/)、Viz.ai[[776]](https://www.viz.ai/)；零售 Standard AI[[777]](https://standard.ai/)、Trigo[[778]](https://www.trigoretail.com/)

### G 量化金融 / 经典 ML 应用（轻量分支）

绝大多数金融 AI 跑在 L06 PyTorch / JAX 通用框架上，没有独立"基础模型"层；但工具链与终端用户面孔与 LLM 分支差异大。

- **Ga 经典 ML 框架**：scikit-learn、XGBoost、LightGBM、CatBoost[[779]](https://catboost.ai/)、RAPIDS cuML（GPU 加速 sklearn）[[780]](https://rapids.ai/)、H2O.ai[[781]](https://h2o.ai/)
- **Gb 时间序列 / 预测**：Prophet（Meta）[[782]](https://facebook.github.io/prophet/)、NeuralProphet[[783]](https://neuralprophet.com/)、Nixtla（StatsForecast / NeuralForecast / TimeGPT）[[784]](https://www.nixtla.io/)、Salesforce Merlion[[785]](https://github.com/salesforce/Merlion)、Amazon Chronos[[786]](https://github.com/amazon-science/chronos-forecasting)
- **Gc 量化 / 回测平台**：QuantConnect[[787]](https://www.quantconnect.com/)、Backtrader[[788]](https://www.backtrader.com/)、vectorbt / vectorbt-pro[[789]](https://vectorbt.dev/)、Zipline-reloaded[[790]](https://github.com/stefan-jansen/zipline-reloaded)、QuantLib（衍生品定价库）[[791]](https://www.quantlib.org/)、NVIDIA cuOpt + Risk Pricing
- **Gd 金融领域模型**：BloombergGPT、FinGPT、FinBERT[[792]](https://github.com/yya518/FinBERT)、PIXIU[[793]](https://github.com/The-FinAI/PIXIU)；金融具体应用大多复用 GPT / Claude，没有独立分发
- **Ge 终端 / 平台**：Bloomberg Terminal + AI[[794]](https://professional.bloomberg.com/products/bloomberg-terminal/)、FactSet Mercury[[795]](https://www.factset.com/ai)、Two Sigma Venn[[796]](https://www.venn.twosigma.com/)、AlphaSense[[797]](https://www.alpha-sense.com/)、Hebbia（这一项已在 L34 列出）

---

## 各分支与主干共享 / 分叉点速查

| 主干层 | LLM / Agent（A 段） | 科学计算（B1–B3） | 机器人（C） | 自动驾驶（D） | 世界模型 / 3D（E） | 经典 CV（F） |
|---|---|---|---|---|---|---|
| L01–L05 驱动 / 内核库 / 编译器 | 共享 | 共享 + 加 OpenMM / cuQuantum kernel | 共享 + 实时 OS | 共享 + 车规级 BSP | 共享 | 共享 + OpenVINO / TensorRT |
| L06–L07 框架 / 分布式 | PyTorch / JAX / DeepSpeed | PyTorch / JAX / Julia / MPI | PyTorch + ROS DDS | PyTorch + DriveWorks | PyTorch + JAX | PyTorch + OpenMMLab |
| L08 数据 pipeline | FineWeb / datatrove | 实验数据 + 仿真生成 | Open X-Embodiment / DROID | 路采 + Replay + 仿真 | 多视角 / 视频对 | Roboflow / Labelbox |
| L09 后训练 | TRL / verl | 极少（多预训练即终态） | LeRobot + ACT + Diffusion Policy | 半监督 + RLHF 仿真 | 极少 | 微调 + 蒸馏 |
| L10 模型 | Llama / Claude / GPT | AlphaFold 3 / GraphCast / MatterGen | π0 / GR00T / RT-2 | Tesla FSD / Waymo | Genie 3 / Marble | YOLO / SAM 2 |
| L13–L14 推理 / 服务 | vLLM / Triton Inference | BioNeMo NIM / Earth-2 Studio | Isaac ROS / 车载 NN runtime | DRIVE OS / EyeQ runtime | Gaussian Splatting renderer | DeepStream / OpenVINO |
| L24–L26 Agent / 工具 | LangGraph / MCP / Computer Use | 多数无（人在闭环） | VLA 控制循环（非 LLM Agent） | 端到端策略，无 Agent 层 | 编辑器内交互 | 无 |
| L33–L34 终端 | ChatGPT / Cursor | AlphaFold Server / Schrödinger | Tesla Optimus / Figure | Tesla FSD / Robotaxi | Marble / Genie 3 | 工业 / 医疗 / 零售视觉 |

---

## 几条横切的观察

不属于具体某一层，但跨层规律值得单列。

- **MCP 是这一栈唯一在 2024–2025 通过的"工具接口标准"**：从 L25 起，向上影响 L24 / L18，向下影响 L17（模型 API 内置 MCP connector）和 L22（gateway 必须懂 MCP）。
- **L13 推理引擎 与 L14 模型服务 的边界正在合并**：vLLM、SGLang[[106]](https://github.com/sgl-project/sglang) 自带 OpenAI 兼容 HTTP server，挤压了纯 L14 厂商（KServe、BentoML）的独立性。
- **L15 GPU 云、L16 模型 API 聚合、L17 前沿模型 API 三层正在相互渗透**：CoreWeave[[125]](https://www.coreweave.com/) 推自家模型；Together / Fireworks 自研推理引擎；Anthropic / OpenAI 转售他人模型（极少，但 Bedrock / Vertex 把这种关系制度化）。
- **L9 后训练 + L11 评测 + L24 Agent 框架 形成 RL 闭环**：RLVR / GRPO 把 L11 的评测器当 reward，把 L24 的 agent rollout 当 trajectory，是 2025 训练范式的核心变化。
- **L34 垂直 Agent 与 L24 Agent 框架的耦合方式分两类**：闭源垂直 Agent（Cursor、Devin、Sierra）几乎都不用第三方 Agent 框架，自己造控制循环；而中小垂直 Agent（Clay、Lovable 的部分组件）大量复用 LangGraph / Agents SDK。
- **L18 LLM 应用框架 在 2025 出现 "去 LangChain[[145]](https://www.langchain.com/) 化"信号**：原生 SDK（OpenAI Agents SDK、Claude Agent SDK）抢占了 LangChain 早期的功能位；LangChain 通过 LangGraph + LangSmith 上移到 L24 + L28。
- **并列分支 B–G 共享 L01–L09，但向上越走越像各自孤岛**：科学计算几乎不进 L13 推理服务（用 Slurm + 直接调脚本）；机器人 VLA / 自动驾驶端到端策略**根本不是 Agent**（没有 tool-loop、没有规划），用主干"Agent 框架"的话语去套是误读；只有 E 世界模型与 L32 视频生成在底层模型上真正同源。
- **NVIDIA 是唯一在 A 主干 + B–G 全部 6 个分支都占重要席位的供应商**：CUDA + cuDNN[[20]](https://developer.nvidia.com/cudnn)（L03–L04）→ Megatron / NeMo（L07）→ Triton Inference（L14）→ BioNeMo / Earth-2 / Modulus（B3）→ Isaac / Cosmos / GR00T（C）→ DRIVE（D）→ Omniverse + ACE（E）→ DeepStream（F）。这是 2025 估值溢价相对于纯 LLM 厂商更稳的结构性原因。

---

## 参考文献

[1] OpenAI, "ChatGPT," [Online]. Available: <https://chatgpt.com/>

[2] Anysphere, "Cursor: The best way to code with AI," [Online]. Available: <https://cursor.com/>

[3] Cognition, "Devin: The AI Software Engineer," [Online]. Available: <https://devin.ai/>

[4] SchedMD, "Slurm Workload Manager," [Online]. Available: <https://slurm.schedmd.com/>

[5] The Linux Foundation, "Kubernetes," [Online]. Available: <https://kubernetes.io/>

[6] Anyscale, "Ray," [Online]. Available: <https://docs.ray.io/en/latest/index.html>

[7] Open Source Robotics Foundation, "ROS: Robot Operating System," [Online]. Available: <https://www.ros.org/>

[8] Google DeepMind, "MuJoCo — Advanced Physics Simulation," [Online]. Available: <https://mujoco.org/>

[9] GROMACS Development Team, "GROMACS," [Online]. Available: <https://www.gromacs.org/>

[10] NVIDIA, "NVLink & NVLink Switch," [Online]. Available: <https://www.nvidia.com/en-us/data-center/nvlink/>

[11] NVIDIA, "NVIDIA Collective Communications Library (NCCL)," [Online]. Available: <https://developer.nvidia.com/nccl>

[12] NVIDIA, "InfiniBand Networking," [Online]. Available: <https://www.nvidia.com/en-us/networking/products/infiniband/>

[13] NVIDIA, "CUDA Platform for Accelerated Computing," [Online]. Available: <https://developer.nvidia.com/cuda>

[14] AMD, "AMD ROCm Software," [Online]. Available: <https://www.amd.com/en/products/software/rocm.html>

[15] Apple, "Metal," [Online]. Available: <https://developer.apple.com/metal/>

[16] Intel, "Intel oneAPI," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html>

[17] JuliaGPU, "CUDA.jl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/JuliaGPU/CUDA.jl>

[18] NVIDIA / RAPIDS AI, "RAPIDS: GPU Accelerated Data Science," [Online]. Available: <https://rapids.ai/>

[19] NVIDIA, "cuBLAS," [Online]. Available: <https://developer.nvidia.com/cublas>

[20] NVIDIA, "CUDA Deep Neural Network (cuDNN)," [Online]. Available: <https://developer.nvidia.com/cudnn>

[21] Dao-AILab, "FlashAttention," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/dao-ailab/flash-attention>

[22] NVIDIA, "CUTLASS," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/cutlass>

[23] NVIDIA, "cuFFT," [Online]. Available: <https://developer.nvidia.com/cufft>

[24] NVIDIA, "cuSOLVER," [Online]. Available: <https://developer.nvidia.com/cusolver>

[25] NVIDIA, "cuSPARSE," [Online]. Available: <https://developer.nvidia.com/cusparse>

[26] NVIDIA, "cuQuantum SDK," [Online]. Available: <https://developer.nvidia.com/cuquantum-sdk>

[27] NVIDIA, "NVSHMEM," [Online]. Available: <https://developer.nvidia.com/nvshmem>

[28] triton-lang, "Triton," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-lang/triton>

[29] OpenXLA Project, "XLA: Optimizing Compiler for Machine Learning," [Online]. Available: <https://openxla.org/xla>

[30] LLVM Project, "MLIR," [Online]. Available: <https://mlir.llvm.org/>

[31] Apache Software Foundation, "Apache TVM," [Online]. Available: <https://tvm.apache.org/>

[32] Exaloop, "Codon," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/exaloop/codon>

[33] PyTorch Foundation, "PyTorch," [Online]. Available: <https://pytorch.org/>

[34] Google / jax-ml, "JAX," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/jax-ml/jax>

[35] Apple / ml-explore, "MLX: An array framework for Apple silicon," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ml-explore/mlx>

[36] Google, "TensorFlow," [Online]. Available: <https://www.tensorflow.org/>

[37] NumPy Developers, "NumPy," [Online]. Available: <https://numpy.org/>

[38] SciPy Developers, "SciPy," [Online]. Available: <https://scipy.org/>

[39] Preferred Networks / CuPy Developers, "CuPy," [Online]. Available: <https://cupy.dev/>

[40] Julia Project, "The Julia Programming Language," [Online]. Available: <https://julialang.org/>

[41] scikit-learn Developers, "scikit-learn," [Online]. Available: <https://scikit-learn.org/>

[42] DMLC, "XGBoost Documentation," [Online]. Available: <https://xgboost.readthedocs.io/>

[43] Microsoft, "LightGBM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/microsoft/LightGBM>

[44] Microsoft / DeepSpeed AI, "DeepSpeed," [Online]. Available: <https://www.deepspeed.ai/>

[45] NVIDIA, "Megatron-LM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/Megatron-LM>

[46] PyTorch, "FullyShardedDataParallel (FSDP)," [Online]. Available: <https://docs.pytorch.org/docs/stable/fsdp.html>

[47] NVIDIA, "NeMo Framework," [Online]. Available: <https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html>

[48] Anyscale, "Ray Train," [Online]. Available: <https://docs.ray.io/en/latest/train/train.html>

[49] MPI Forum, "Message Passing Interface (MPI)," [Online]. Available: <https://www.mpi-forum.org/>

[50] Hugging Face / HuggingFaceFW, "FineWeb," Hugging Face Dataset, 2024. [Online]. Available: <https://huggingface.co/datasets/HuggingFaceFW/fineweb>

[51] Hugging Face, "datatrove," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/datatrove>

[52] MosaicML, "Streaming," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/streaming>

[53] Open X-Embodiment Collaboration, "Open X-Embodiment: Robotic Learning Datasets and RT-X Models," 2023. [Online]. Available: <https://robotics-transformer-x.github.io/>

[54] DROID Collaboration, "DROID: A Large-Scale In-the-Wild Robot Manipulation Dataset," [Online]. Available: <https://droid-dataset.github.io/>

[55] Hugging Face, "LeRobot," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/lerobot>

[56] Hugging Face, "TRL," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/trl>

[57] Volcengine, "verl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/volcengine/verl>

[58] Unsloth AI, "Unsloth," [Online]. Available: <https://unsloth.ai/>

[59] Axolotl AI, "Axolotl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/axolotl-ai-cloud/axolotl>

[60] Stanford Robotics, "Diffusion Policy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/real-stanford/diffusion_policy>

[61] Meta AI, "Llama," [Online]. Available: <https://ai.meta.com/llama/>

[62] Anthropic, "Claude," [Online]. Available: <https://www.anthropic.com/claude>

[63] OpenAI, "OpenAI API," [Online]. Available: <https://openai.com/api/>

[64] Alibaba Cloud / Qwen Team, "Qwen," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/QwenLM/Qwen>

[65] DeepSeek AI, "DeepSeek," [Online]. Available: <https://www.deepseek.com/en/>

[66] Google DeepMind / Isomorphic Labs, "AlphaFold Server," [Online]. Available: <https://alphafoldserver.com/>

[67] Google DeepMind, "GraphCast," [Online]. Available: <https://deepmind.google/technologies/graphcast/>

[68] Microsoft Research, "MatterGen," 2024. [Online]. Available: <https://www.microsoft.com/en-us/research/blog/mattergen-a-new-paradigm-of-materials-design-with-generative-ai/>

[69] Bo Wang Lab, "scGPT," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/bowang-lab/scGPT>

[70] Arc Institute, "Evo 2," 2025. [Online]. Available: <https://arcinstitute.org/news/blog/evo2>

[71] NVIDIA, "Isaac GR00T," [Online]. Available: <https://developer.nvidia.com/isaac/gr00t>

[72] Physical Intelligence, "Physical Intelligence (π)," [Online]. Available: <https://www.physicalintelligence.company/>

[73] Google DeepMind, "RT-2: Vision-Language-Action Models," 2023. [Online]. Available: <https://robotics-transformer2.github.io/>

[74] Stanford / UC Berkeley, "OpenVLA: An Open-Source Vision-Language-Action Model," [Online]. Available: <https://openvla.github.io/>

[75] Tsinghua University, "RDT-1B: A Diffusion Foundation Model for Bimanual Manipulation," [Online]. Available: <https://rdt-robotics.github.io/rdt-robotics/>

[76] Tesla, "Autopilot and Full Self-Driving Capability," [Online]. Available: <https://www.tesla.com/support/autopilot>

[77] Waymo, "Waymo Driver," [Online]. Available: <https://waymo.com/>

[78] Wayve, "LINGO: Natural language for autonomous driving," [Online]. Available: <https://wayve.ai/thinking/lingo-natural-language-autonomous-driving/>

[79] Google DeepMind, "Genie 3: A new frontier for world models," 2025. [Online]. Available: <https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/>

[80] World Labs, "Marble," [Online]. Available: <https://www.worldlabs.ai/>

[81] NVIDIA, "Cosmos World Foundation Models," [Online]. Available: <https://www.nvidia.com/en-us/ai/cosmos/>

[82] Ultralytics, "YOLO11," [Online]. Available: <https://docs.ultralytics.com/models/yolo11/>

[83] Meta AI, "Segment Anything Model 2 (SAM 2)," [Online]. Available: <https://ai.meta.com/sam2/>

[84] Microsoft, "Florence-2," Hugging Face Model, 2024. [Online]. Available: <https://huggingface.co/microsoft/Florence-2-large>

[85] Baidu, "RT-DETR," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/lyuwenyu/RT-DETR>

[86] Bloomberg, "BloombergGPT," 2023. [Online]. Available: <https://www.bloomberg.com/company/press/bloomberggpt-50-billion-parameter-llm-tuned-finance/>

[87] AI4Finance Foundation, "FinGPT," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/AI4Finance-Foundation/FinGPT>

[88] Nixtla, "TimeGPT," [Online]. Available: <https://www.nixtla.io/>

[89] Amazon Science, "Chronos: Pretrained Models for Time Series Forecasting," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/amazon-science/chronos-forecasting>

[90] D. Hendrycks et al., "Measuring Massive Multitask Language Understanding," *arXiv preprint*, arXiv:2009.03300, 2020. [Online]. Available: <https://arxiv.org/abs/2009.03300>

[91] Princeton NLP, "SWE-bench," [Online]. Available: <https://www.swebench.com/>

[92] Embeddings Benchmark, "MTEB: Massive Text Embedding Benchmark," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/embeddings-benchmark/mteb/>

[93] METR, "Task-Completion Time Horizons of Frontier AI Models," [Online]. Available: <https://metr.org/time-horizons/>

[94] Protein Structure Prediction Center, "CASP," [Online]. Available: <https://predictioncenter.org/>

[95] Pangeo, "WeatherBench," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pangeo-data/WeatherBench>

[96] Materials Project, "Matbench Discovery," [Online]. Available: <https://matbench-discovery.materialsproject.org/>

[97] Imperial College London, "RLBench," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stepjam/RLBench>

[98] Motional, "nuScenes," [Online]. Available: <https://www.nuscenes.org/>

[99] Microsoft, "Common Objects in Context (COCO)," [Online]. Available: <https://cocodataset.org/>

[100] Stanford Vision Lab, "ImageNet," [Online]. Available: <https://www.image-net.org/>

[101] Weights & Biases, "Weights & Biases," [Online]. Available: <https://wandb.ai/site/>

[102] MLflow Project, "MLflow," [Online]. Available: <https://mlflow.org/>

[103] Neptune AI, "Neptune," [Online]. Available: <https://neptune.ai/>

[104] vLLM Project, "vLLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/vllm-project/vllm>

[105] NVIDIA, "TensorRT-LLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/TensorRT-LLM>

[106] sgl-project, "SGLang," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/sgl-project/sglang>

[107] Georgi Gerganov, "llama.cpp," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ggerganov/llama.cpp>

[108] NVIDIA, "BioNeMo," [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[109] NVIDIA, "Isaac ROS," [Online]. Available: <https://developer.nvidia.com/isaac/ros>

[110] NVIDIA, "DRIVE OS," [Online]. Available: <https://developer.nvidia.com/drive/drive-os>

[111] Mobileye, "EyeQ Chip," [Online]. Available: <https://www.mobileye.com/technology/eyeq-chip/>

[112] Comma.ai, "openpilot," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/commaai/openpilot>

[113] Inria, "3D Gaussian Splatting for Real-Time Radiance Field Rendering," SIGGRAPH 2023. [Online]. Available: <https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/>

[114] NVIDIA NVlabs, "Instant-NGP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVlabs/instant-ngp>

[115] NVIDIA, "DeepStream SDK," [Online]. Available: <https://developer.nvidia.com/deepstream-sdk>

[116] Intel, "OpenVINO Documentation," [Online]. Available: <https://docs.openvino.ai/>

[117] Apple, "Core ML," [Online]. Available: <https://developer.apple.com/machine-learning/core-ml/>

[118] NVIDIA, "Triton Inference Server," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-inference-server/server>

[119] Anyscale, "Ray Serve," [Online]. Available: <https://docs.ray.io/en/latest/serve/index.html>

[120] BentoML, "BentoML," [Online]. Available: <https://www.bentoml.com/>

[121] NVIDIA, "BioNeMo NIM Microservices," [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[122] NVIDIA, "Earth-2," [Online]. Available: <https://www.nvidia.com/en-us/high-performance-computing/earth-2/>

[123] PickNik Robotics, "MoveIt," [Online]. Available: <https://moveit.ai/>

[124] NVIDIA, "Omniverse Kit SDK," [Online]. Available: <https://developer.nvidia.com/omniverse/kit-sdk>

[125] CoreWeave, "CoreWeave," [Online]. Available: <https://www.coreweave.com/>

[126] Lambda, "Lambda," [Online]. Available: <https://lambda.ai/>

[127] Crusoe, "Crusoe," [Online]. Available: <https://www.crusoe.ai/>

[128] Nebius, "Nebius," [Online]. Available: <https://nebius.com/>

[129] Rescale, "Rescale," [Online]. Available: <https://rescale.com/>

[130] Amazon Web Services, "AWS HPC," [Online]. Available: <https://aws.amazon.com/hpc/>

[131] Microsoft Azure, "Azure CycleCloud," [Online]. Available: <https://azure.microsoft.com/en-us/products/cyclecloud>

[132] Tesla, "Tesla AI," [Online]. Available: <https://www.tesla.com/AI>

[133] RunPod, "RunPod," [Online]. Available: <https://www.runpod.io/>

[134] fal.ai, "fal.ai," [Online]. Available: <https://fal.ai/>

[135] Amazon Web Services, "AWS Panorama," [Online]. Available: <https://aws.amazon.com/panorama/>

[136] OpenRouter, "OpenRouter," [Online]. Available: <https://openrouter.ai/>

[137] Together AI, "Together AI," [Online]. Available: <https://www.together.ai/>

[138] Fireworks AI, "Fireworks AI," [Online]. Available: <https://fireworks.ai/>

[139] Groq, "Groq," [Online]. Available: <https://groq.com/>

[140] Replicate, "Replicate," [Online]. Available: <https://replicate.com/>

[141] Anthropic, "Build on the Claude Platform," [Online]. Available: <https://www.anthropic.com/api>

[142] OpenAI, "OpenAI API Platform," [Online]. Available: <https://openai.com/api/>

[143] Google, "Gemini Developer API," [Online]. Available: <https://ai.google.dev/>

[144] xAI, "xAI," [Online]. Available: <https://x.ai/>

[145] LangChain, "LangChain," [Online]. Available: <https://www.langchain.com/>

[146] LlamaIndex, "LlamaIndex," [Online]. Available: <https://www.llamaindex.ai/>

[147] Stanford NLP, "DSPy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stanfordnlp/dspy>

[148] Vercel, "AI SDK," [Online]. Available: <https://ai-sdk.dev/>

[149] OpenAI, "Vector Embeddings," [Online]. Available: <https://platform.openai.com/docs/guides/embeddings>

[150] Cohere, "Embed," [Online]. Available: <https://cohere.com/embed>

[151] BAAI / FlagOpen, "FlagEmbedding (BGE)," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/FlagOpen/FlagEmbedding>

[152] Pinecone, "Pinecone," [Online]. Available: <https://www.pinecone.io/>

[153] Weaviate, "Weaviate," [Online]. Available: <https://weaviate.io/>

[154] Qdrant, "Qdrant," [Online]. Available: <https://qdrant.tech/>

[155] Zilliz / Milvus, "Milvus," [Online]. Available: <https://milvus.io/>

[156] Meta AI Research, "FAISS," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/facebookresearch/faiss>

[157] Roboflow, "Roboflow Universe," [Online]. Available: <https://universe.roboflow.com/>

[158] Mem0 AI, "Mem0," [Online]. Available: <https://mem0.ai/>

[159] Zep AI, "Zep," [Online]. Available: <https://www.getzep.com/>

[160] Letta AI, "Letta," [Online]. Available: <https://www.letta.com/>

[161] BerriAI, "LiteLLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/BerriAI/litellm>

[162] Portkey AI, "Portkey," [Online]. Available: <https://portkey.ai/>

[163] Cloudflare, "Cloudflare AI Gateway," [Online]. Available: <https://developers.cloudflare.com/ai-gateway/>

[164] PromptLayer, "PromptLayer," [Online]. Available: <https://www.promptlayer.com/>

[165] Langfuse, "Langfuse," [Online]. Available: <https://langfuse.com/>

[166] Braintrust, "Braintrust," [Online]. Available: <https://www.braintrust.dev/>

[167] LangChain, "LangGraph," [Online]. Available: <https://www.langchain.com/langgraph>

[168] Microsoft, "AutoGen," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/microsoft/autogen>

[169] Anthropic, "Claude Agent SDK," [Online]. Available: <https://docs.anthropic.com/en/docs/agents-and-tools>

[170] Anthropic / Model Context Protocol, "Model Context Protocol," [Online]. Available: <https://modelcontextprotocol.io/>

[171] Composio, "Composio," [Online]. Available: <https://composio.dev/>

[172] Arcade.dev, "Arcade," [Online]. Available: <https://www.arcade.dev/>

[173] Browserbase, "Browserbase," [Online]. Available: <https://www.browserbase.com/>

[174] OpenAI, "Introducing Operator," [Online]. Available: <https://openai.com/index/introducing-operator/>

[175] browser-use, "browser-use," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/browser-use/browser-use>

[176] E2B, "E2B," [Online]. Available: <https://e2b.dev/>

[177] Modal Labs, "Modal," [Online]. Available: <https://modal.com/>

[178] Daytona, "Daytona," [Online]. Available: <https://www.daytona.io/>

[179] Arize AI, "Arize," [Online]. Available: <https://arize.com/>

[180] LangChain, "LangSmith," [Online]. Available: <https://www.langchain.com/langsmith-platform>

[181] Foxglove, "Foxglove," [Online]. Available: <https://foxglove.dev/>

[182] Prometheus, "Prometheus," [Online]. Available: <https://prometheus.io/>

[183] Grafana Labs, "Grafana," [Online]. Available: <https://grafana.com/>

[184] Guardrails AI, "Guardrails," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/guardrails-ai/guardrails>

[185] NVIDIA, "NeMo Guardrails," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA-NeMo/Guardrails>

[186] Lakera, "Lakera," [Online]. Available: <https://www.lakera.ai/>

[187] ISO, "ISO 13482:2014 Robots and robotic devices — Safety requirements for personal care robots," [Online]. Available: <https://www.iso.org/standard/53820.html>

[188] ISO, "ISO 26262 Road vehicles — Functional safety," [Online]. Available: <https://www.iso.org/standard/68383.html>

[189] UNECE, "UN Regulation No. 157 — Automated Lane Keeping Systems (ALKS)," [Online]. Available: <https://unece.org/transport/documents/2021/03/standards/un-regulation-no-157-automated-lane-keeping-systems-alks>

[190] Promptfoo, "Promptfoo," [Online]. Available: <https://www.promptfoo.dev/>

[191] Confident AI, "DeepEval," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/confident-ai/deepeval>

[192] Exploding Gradients, "Ragas," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/explodinggradients/ragas>

[193] ElevenLabs, "ElevenLabs," [Online]. Available: <https://elevenlabs.io/>

[194] OpenAI, "Whisper," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/whisper>

[195] Cartesia AI, "Cartesia," [Online]. Available: <https://cartesia.ai/>

[196] Deepgram, "Deepgram," [Online]. Available: <https://deepgram.com/>

[197] NVIDIA, "Riva," [Online]. Available: <https://developer.nvidia.com/riva>

[198] Cerence, "Cerence," [Online]. Available: <https://www.cerence.com/>

[199] Midjourney, "Midjourney," [Online]. Available: <https://www.midjourney.com/>

[200] OpenAI, "Sora," [Online]. Available: <https://openai.com/sora/>

[201] Black Forest Labs, "FLUX," [Online]. Available: <https://bfl.ai/>

[202] Runway, "Runway," [Online]. Available: <https://runwayml.com/>

[203] Anthropic, "Claude.ai," [Online]. Available: <https://claude.ai/>

[204] Microsoft, "Microsoft 365 Copilot," [Online]. Available: <https://www.microsoft.com/en-us/microsoft-365-copilot>

[205] SAP, "Joule," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/ai-assistant.html>

[206] Salesforce, "Agentforce," [Online]. Available: <https://www.salesforce.com/agentforce/>

[207] Altair, "PBS Professional," [Online]. Available: <https://www.altair.com/pbs-professional/>

[208] Spack Project, "Spack," [Online]. Available: <https://spack.io/>

[209] NVIDIA, "Holoscan SDK," [Online]. Available: <https://developer.nvidia.com/holoscan-sdk>

[210] NVIDIA, "DriveWorks SDK," [Online]. Available: <https://developer.nvidia.com/drive/driveworks>

[211] AUTOSAR, "AUTOSAR," [Online]. Available: <https://www.autosar.org/>

[212] OpenMM Project, "OpenMM," [Online]. Available: <https://openmm.org/>

[213] NVIDIA, "Isaac Sim," [Online]. Available: <https://developer.nvidia.com/isaac/sim>

[214] NVIDIA, "DRIVE Sim," [Online]. Available: <https://developer.nvidia.com/drive/simulation>

[215] CARLA Simulator, "CARLA," [Online]. Available: <https://carla.org/>

[216] NVIDIA, "NVIDIA Omniverse," [Online]. Available: <https://www.nvidia.com/en-us/omniverse/>

[217] HERE Technologies, "HERE," [Online]. Available: <https://www.here.com/>

[218] TomTom, "TomTom," [Online]. Available: <https://www.tomtom.com/>

[219] Mapbox, "Mapbox," [Online]. Available: <https://www.mapbox.com/>

[220] NVIDIA, "Open GPU Kernel Modules," GitHub. [Online]. Available: <https://github.com/NVIDIA/open-gpu-kernel-modules>

[221] NVIDIA, "NVIDIA Container Toolkit," [Online]. Available: <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html>

[222] AMD, "ROCm Documentation (amdgpu / amdkfd)," [Online]. Available: <https://rocm.docs.amd.com/>

[223] AMD, "AMD GPU Operator," [Online]. Available: <https://instinct.docs.amd.com/projects/gpu-operator/en/latest/>

[224] Intel / Linux Kernel, "i915 Driver," [Online]. Available: <https://docs.kernel.org/gpu/i915.html>

[225] Intel Habana, "Gaudi Driver Installation," [Online]. Available: <https://docs.habana.ai/en/latest/Installation_Guide/Driver_Installation.html>

[226] Huawei, "Ascend Firmware and Driver," [Online]. Available: <https://www.hiascend.com/en/hardware/firmware-drivers/community>

[227] Apple, "Metal," Apple Developer. [Online]. Available: <https://developer.apple.com/metal/>

[228] AWS, "Neuron Driver," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html>

[229] AWS, "Neuron Runtime," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html>

[230] AMD, "AMD Infinity Architecture," [Online]. Available: <https://www.amd.com/en/technologies/infinity-architecture>

[231] Intel, "Intel Data Center GPU Max Series," [Online]. Available: <https://www.intel.com/content/www/us/en/products/docs/processors/max-series/overview.html>

[232] Huawei, "Atlas Cluster," [Online]. Available: <https://www.hiascend.com/en/hardware/cluster>

[233] Apple, "Apple unveils M1 Ultra with UltraFusion," [Online]. Available: <https://www.apple.com/newsroom/2022/03/apple-unveils-m1-ultra-the-worlds-most-powerful-chip-for-a-personal-computer/>

[234] AWS, "Trainium2 Architecture (NeuronLink)," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html>

[235] NVIDIA, "Quantum-2 InfiniBand," [Online]. Available: <https://www.nvidia.com/en-us/networking/quantum2/>

[236] AWS, "Elastic Fabric Adapter (EFA)," [Online]. Available: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html>

[237] Ultra Ethernet Consortium, "Ultra Ethernet," [Online]. Available: <https://ultraethernet.org/>

[238] UALink Consortium, "UALink," [Online]. Available: <https://ualinkconsortium.org/>

[239] AMD ROCm, "RCCL," GitHub. [Online]. Available: <https://github.com/ROCm/rccl>

[240] Intel, "oneCCL," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/oneccl.html>

[241] Huawei, "HCCL: Huawei Collective Communication Library," [Online]. Available: <https://www.hiascend.com/cann/hccl>

[242] AWS, "Neuron Collective Communication," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/about/collectives.html>

[243] Microsoft, "MSCCL++," GitHub. [Online]. Available: <https://github.com/microsoft/mscclpp>

[244] AMD ROCm, "HIP," [Online]. Available: <https://rocm.docs.amd.com/projects/HIP/en/latest/>

[245] Intel, "oneAPI DPC++/C++ Compiler," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html>

[246] Intel Habana, "Gaudi Software Suite (SynapseAI)," [Online]. Available: <https://docs.habana.ai/en/latest/Gaudi_Overview/Intel_Gaudi_Software_Suite.html>

[247] Huawei, "CANN," [Online]. Available: <https://www.hiascend.com/en/cann>

[248] Huawei, "AscendC," CANN Operator Development Guide. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html>

[249] Huawei, "AscendCL," CANN API Reference. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/>

[250] AWS, "Neuron SDK," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html>

[251] AWS, "Neuron Kernel Interface (NKI)," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/>

[252] Khronos Group, "OpenCL," [Online]. Available: <https://www.khronos.org/opencl/>

[253] Khronos Group, "Vulkan," [Online]. Available: <https://www.khronos.org/vulkan/>

[254] W3C, "WebGPU," [Online]. Available: <https://www.w3.org/TR/webgpu/>

[255] AMD ROCm, "rocBLAS," [Online]. Available: <https://rocm.docs.amd.com/projects/rocBLAS/en/latest/>

[256] Intel, "oneMKL," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html>

[257] Huawei, "CANN — Ascend Operator Library (AOL)," [Online]. Available: <https://www.hiascend.com/en/cann>

[258] Apple, "Accelerate Framework," [Online]. Available: <https://developer.apple.com/documentation/accelerate>

[259] Apple, "Metal Performance Shaders," [Online]. Available: <https://developer.apple.com/documentation/metalperformanceshaders>

[260] AMD ROCm, "MIOpen," [Online]. Available: <https://rocm.docs.amd.com/projects/MIOpen/en/latest/>

[261] Intel, "oneDNN," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/onednn.html>

[262] Huawei, "ACLNN: Ascend Neural Network Operator Library," CANN API Reference. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/>

[263] Apple, "BNNS — Basic Neural Network Subroutines," [Online]. Available: <https://developer.apple.com/documentation/accelerate/bnns>

[264] AMD ROCm, "Composable Kernel," GitHub. [Online]. Available: <https://github.com/ROCm/composable_kernel>

[265] Intel, "XeTLA," GitHub. [Online]. Available: <https://github.com/intel/xetla>

[266] AMD ROCm, "rocFFT," [Online]. Available: <https://rocm.docs.amd.com/projects/rocFFT/en/latest/>

[267] Meta, "xFormers," GitHub. [Online]. Available: <https://github.com/facebookresearch/xformers>

[268] NVIDIA, "CUDA Compiler Driver NVCC," NVIDIA Documentation. [Online]. Available: <https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/>

[269] AMD ROCm, "HIPCC: HIP compiler driver," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ROCm/HIPCC>

[270] Intel, "Intel oneAPI DPC++/C++ Compiler," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html>

[271] Intel Habana, "Intel Gaudi Software Suite (SynapseAI)," [Online]. Available: <https://docs.habana.ai/en/latest/Gaudi_Overview/SynapseAI_Software_Suite.html>

[272] Huawei, "CANN — Compute Architecture for Neural Networks," Ascend Community. [Online]. Available: <https://www.hiascend.com/en/cann>

[273] Huawei / MindSpore, "MindSpore," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-ai/mindspore>

[274] Apple, "Metal libraries," Apple Developer. [Online]. Available: <https://developer.apple.com/documentation/metal/metal-libraries>

[275] Apple, "Core ML," Apple Developer. [Online]. Available: <https://developer.apple.com/documentation/coreml>

[276] Apple ML Research, "MLX," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ml-explore/mlx>

[277] AWS, "AWS Neuron Documentation," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/>

[278] triton-lang, "Triton," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-lang/triton>

[279] PyTorch, "Introduction to torch.compile," PyTorch Tutorials. [Online]. Available: <https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html>

[280] OpenXLA Project, "XLA," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openxla/xla>

[281] Apache Software Foundation, "Apache TVM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/apache/tvm>

[282] IREE contributors, "IREE," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/iree-org/iree>

[283] Modular, "Mojo," [Online]. Available: <https://www.modular.com/open-source/mojo>

[284] Google DeepMind, "Flax," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/google/flax>

[285] Keras contributors, "Keras," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/keras-team/keras>

[286] Huawei / MindSpore, "MindSpore," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-ai/mindspore>

[287] Baidu / PaddlePaddle, "Paddle," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/PaddlePaddle/Paddle>

[288] tinygrad contributors, "tinygrad," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/tinygrad/tinygrad>

[289] NVIDIA, "NeMo," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/NeMo>

[290] HPC-AI Tech, "ColossalAI," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/hpcaitech/ColossalAI>

[291] MosaicML / Databricks, "Composer," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/composer>

[292] MosaicML / Databricks, "LLM Foundry," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/llm-foundry>

[293] PyTorch, "TorchTitan," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pytorch/torchtitan>

[294] Huawei / MindSpore Lab, "MindFormers," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-lab/mindformers>

[295] Huawei Ascend, "ModelLink," Gitee repository, accessed 2026. [Online]. Available: <https://gitee.com/ascend/ModelLink>

[296] Apple ML Research, "Distributed Communication — MLX Documentation," [Online]. Available: <https://ml-explore.github.io/mlx/build/html/usage/distributed.html>

[297] AWS, "Amazon SageMaker HyperPod," [Online]. Available: <https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html>

[298] WebDataset contributors, "webdataset," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/webdataset/webdataset>

[299] NVIDIA NeMo, "Curator," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA-NeMo/Curator>

[300] Allen Institute for AI, "dolma," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/allenai/dolma>

[301] Together AI, "RedPajama-Data," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/togethercomputer/RedPajama-Data>

[302] Allen Institute for AI, "allenai/dolma," Hugging Face Dataset, [Online]. Available: <https://huggingface.co/datasets/allenai/dolma>

[303] BigCode Project, "bigcode/the-stack-v2," Hugging Face Dataset. [Online]. Available: <https://huggingface.co/datasets/bigcode/the-stack-v2>

[304] Common Crawl Foundation, "Common Crawl," [Online]. Available: <https://commoncrawl.org/>

[305] hiyouga et al., "LLaMA-Factory: Unified Efficient Fine-Tuning of 100+ LLMs & VLMs," GitHub repository, ACL 2024. [Online]. Available: <https://github.com/hiyouga/LLaMA-Factory>

[306] OpenRLHF contributors, "OpenRLHF," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/OpenRLHF/OpenRLHF>

[307] NVIDIA, "NeMo-Aligner," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/NeMo-Aligner>

[308] Mistral AI, "Mistral AI," [Online]. Available: <https://mistral.ai/>

[309] Google DeepMind, "Gemma open models," [Online]. Available: <https://ai.google.dev/gemma>

[310] Moonshot AI, "Kimi-K2," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/MoonshotAI/Kimi-K2>

[311] Zhipu AI / THUDM, "GLM-4," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/THUDM/GLM-4>

[312] Microsoft, "microsoft/phi-4," Hugging Face. [Online]. Available: <https://huggingface.co/microsoft/phi-4>

[313] Allen Institute for AI, "OLMo," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/allenai/OLMo>

[314] Hugging Face, "Hugging Face," [Online]. Available: <https://huggingface.co/>

[315] Alibaba / ModelScope, "ModelScope," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/modelscope/modelscope>

[316] Ollama, "Ollama Library," [Online]. Available: <https://ollama.com/library>

[317] Civitai, "Civitai," [Online]. Available: <https://civitai.com/models>

[318] EleutherAI, "lm-evaluation-harness," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/EleutherAI/lm-evaluation-harness>

[319] Stanford CRFM, "HELM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stanford-crfm/helm>

[320] Shanghai AI Lab, "OpenCompass," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/open-compass/opencompass>

[321] K. Cobbe et al., "Training Verifiers to Solve Math Word Problems," arXiv:2110.14168, Oct 2021. [Online]. Available: <https://arxiv.org/abs/2110.14168>

[322] M. Chen et al., "Evaluating Large Language Models Trained on Code," arXiv:2107.03374, Jul 2021. [Online]. Available: <https://arxiv.org/abs/2107.03374>

[323] D. Rein et al., "GPQA: A Graduate-Level Google-Proof Q&A Benchmark," arXiv:2311.12022, Nov 2023. [Online]. Available: <https://arxiv.org/abs/2311.12022>

[324] ARC Prize Foundation, "ARC-AGI," [Online]. Available: <https://arcprize.org/arc-agi>

[325] Center for AI Safety / Scale AI, "HLE: Humanity's Last Exam," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/centerforaisafety/hle>

[326] Sierra Research, "tau-bench," GitHub repository, 2024. [Online]. Available: <https://github.com/sierra-research/tau-bench>

[327] web-arena-x, "WebArena," GitHub repository, 2023. [Online]. Available: <https://github.com/web-arena-x/webarena>

[328] XLANG-AI, "OSWorld," GitHub repository, NeurIPS 2024. [Online]. Available: <https://github.com/xlang-ai/OSWorld>

[329] THUDM, "AgentBench," GitHub repository, ICLR 2024. [Online]. Available: <https://github.com/THUDM/AgentBench>

[330] beir-cellar, "BEIR," GitHub repository, NeurIPS 2021. [Online]. Available: <https://github.com/beir-cellar/beir>

[331] LMArena / LMSYS, "Chatbot Arena," [Online]. Available: <https://lmarena.ai/>

[332] Scale AI, "SEAL LLM Leaderboards," [Online]. Available: <https://scale.com/leaderboard>

[333] UK AI Security Institute, "Inspect," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/UKGovernmentBEIS/inspect_ai>

[334] OpenAI, "Evals," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/evals>

[335] ClearML, "ClearML," [Online]. Available: <https://clear.ml/>

[336] Comet, "Comet," [Online]. Available: <https://www.comet.com/site/>

[337] TensorFlow, "TensorBoard," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/tensorflow/tensorboard>

[338] Iterative, "DVC," [Online]. Available: <https://dvc.org/>

[339] Hugging Face, "Text Generation Inference (TGI)," GitHub. [Online]. Available: <https://github.com/huggingface/text-generation-inference>

[340] Georgi Gerganov, "GGUF Specification," GitHub. [Online]. Available: <https://github.com/ggerganov/ggml/blob/master/docs/gguf.md>

[341] MLC AI, "MLC-LLM," GitHub. [Online]. Available: <https://github.com/mlc-ai/mlc-llm>

[342] Microsoft DeepSpeed AI, "DeepSpeed-MII," GitHub. [Online]. Available: <https://github.com/deepspeedai/DeepSpeed-MII>

[343] InternLM, "LMDeploy," GitHub. [Online]. Available: <https://github.com/InternLM/lmdeploy>

[344] Ollama, "Ollama," [Online]. Available: <https://ollama.com/>

[345] AMD ROCm, "AITER," GitHub. [Online]. Available: <https://github.com/ROCm/aiter>

[346] Intel, "OpenVINO," GitHub. [Online]. Available: <https://github.com/openvinotoolkit/openvino>

[347] Intel, "IPEX-LLM," GitHub. [Online]. Available: <https://github.com/intel/ipex-llm>

[348] Huawei, "MindIE," [Online]. Available: <https://www.hiascend.com/en/developer/software/mindie>

[349] Huawei, "MindSpore Lite," [Online]. Available: <https://www.mindspore.cn/lite/en>

[350] Apple, "Metal Performance Shaders Graph," [Online]. Available: <https://developer.apple.com/documentation/metalperformanceshadersgraph>

[351] AWS, "Neuron SDK (Transformers-Neuronx)," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/neuron/>

[352] DeepJavaLibrary, "DJL Serving," GitHub. [Online]. Available: <https://github.com/deepjavalibrary/djl-serving>

[353] KServe Project, "KServe," GitHub. [Online]. Available: <https://github.com/kserve/kserve>

[354] Beam, "Beam," [Online]. Available: <https://www.beam.cloud/>

[355] Replicate, "Cog," GitHub. [Online]. Available: <https://github.com/replicate/cog>

[356] Seldon, "Seldon Core," GitHub. [Online]. Available: <https://github.com/SeldonIO/seldon-core>

[357] NVIDIA, "NIM Microservices," [Online]. Available: <https://developer.nvidia.com/nim>

[358] AMD / Xilinx, "Inference Server," GitHub. [Online]. Available: <https://github.com/Xilinx/inference-server>

[359] Intel, "OpenVINO Model Server (OVMS)," GitHub. [Online]. Available: <https://github.com/openvinotoolkit/model_server>

[360] Huawei, "MindCluster (Atlas)," [Online]. Available: <https://www.hiascend.com/en>

[361] Huawei Cloud, "ModelArts," [Online]. Available: <https://www.huaweicloud.com/intl/en-us/product/modelarts.html>

[362] Apple, "Private Cloud Compute," [Online]. Available: <https://security.apple.com/documentation/private-cloud-compute>

[363] AWS, "Amazon SageMaker," [Online]. Available: <https://aws.amazon.com/sagemaker/>

[364] AWS, "Amazon Bedrock," [Online]. Available: <https://aws.amazon.com/bedrock/>

[365] Voltage Park, "Voltage Park," [Online]. Available: <https://www.voltagepark.com/>

[366] Applied Digital, "Applied Digital," [Online]. Available: <https://www.applieddigital.com/>

[367] Vast.ai, "Vast.ai," [Online]. Available: <https://vast.ai/>

[368] TensorDock, "TensorDock," [Online]. Available: <https://www.tensordock.com/>

[369] Salad, "Salad," [Online]. Available: <https://salad.com/>

[370] Hyperstack, "Hyperstack," [Online]. Available: <https://www.hyperstack.cloud/>

[371] Lepton AI (NVIDIA), "Lepton AI," [Online]. Available: <https://www.lepton.ai/>

[372] TensorWave, "TensorWave," [Online]. Available: <https://tensorwave.com/>

[373] Hot Aisle, "Hot Aisle," [Online]. Available: <https://hotaisle.xyz/>

[374] Vultr, "Cloud GPU," [Online]. Available: <https://www.vultr.com/products/cloud-gpu/>

[375] Intel, "Intel Tiber AI Cloud," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html>

[376] Huawei Cloud, "ModelArts," [Online]. Available: <https://www.huaweicloud.com/intl/en-us/product/modelarts.html>

[377] Huawei, "Atlas 900 Cluster," [Online]. Available: <https://www.hiascend.com/en/hardware/cluster>

[378] AWS, "Trainium," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/trainium/>

[379] AWS, "Inferentia," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/inferentia/>

[380] Cerebras, "Cerebras Inference," [Online]. Available: <https://www.cerebras.ai/inference>

[381] SambaNova, "SambaCloud," [Online]. Available: <https://sambanova.ai/products/sambacloud>

[382] DeepInfra, "DeepInfra," [Online]. Available: <https://deepinfra.com/>

[383] Anyscale, "Anyscale Endpoints," [Online]. Available: <https://www.anyscale.com/>

[384] Hyperbolic, "Hyperbolic," [Online]. Available: <https://www.hyperbolic.ai/>

[385] Google Cloud, "Vertex AI," [Online]. Available: <https://cloud.google.com/vertex-ai>

[386] xAI, "xAI API," [Online]. Available: <https://x.ai/api>

[387] DeepSeek, "DeepSeek API Documentation," [Online]. Available: <https://api-docs.deepseek.com/>

[388] Microsoft Azure, "Azure OpenAI Service," [Online]. Available: <https://azure.microsoft.com/en-us/products/ai-foundry/models/openai/>

[389] IBM, "watsonx," [Online]. Available: <https://www.ibm.com/products/watsonx>

[390] Databricks, "Foundation Model APIs," [Online]. Available: <https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/>

[391] SAP, "Generative AI Hub on BTP," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/generative-ai-hub.html>

[392] Oracle, "Generative AI Service," [Online]. Available: <https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/>

[393] deepset, "Haystack," [Online]. Available: <https://haystack.deepset.ai/>

[394] Microsoft, "Semantic Kernel," [Online]. Available: <https://learn.microsoft.com/en-us/semantic-kernel/>

[395] Mastra, "Mastra," [Online]. Available: <https://mastra.ai/>

[396] VMware (Broadcom), "Spring AI," [Online]. Available: <https://spring.io/projects/spring-ai/>

[397] OpenAI, "Embeddings," [Online]. Available: <https://platform.openai.com/docs/guides/embeddings>

[398] Cohere, "Rerank," [Online]. Available: <https://cohere.com/rerank>

[399] Google Cloud, "Vertex AI Embeddings," [Online]. Available: <https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings>

[400] Voyage AI, "Voyage AI," [Online]. Available: <https://www.voyageai.com/>

[401] Jina AI, "Jina Embeddings," [Online]. Available: <https://jina.ai/embeddings/>

[402] Nomic AI, "Nomic," [Online]. Available: <https://www.nomic.ai/>

[403] Microsoft Research, "E5: Text Embeddings," GitHub. [Online]. Available: <https://github.com/microsoft/unilm/tree/master/e5>

[404] Alibaba NLP, "GTE Models," Hugging Face. [Online]. Available: <https://huggingface.co/collections/Alibaba-NLP/gte-models>

[405] NovaSearch, "stella_en_1.5B_v5," Hugging Face. [Online]. Available: <https://huggingface.co/NovaSearch/stella_en_1.5B_v5>

[406] Mixedbread AI, "Mixedbread," [Online]. Available: <https://www.mixedbread.com/>

[407] OpenAI, "CLIP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/CLIP>

[408] ML Foundations, "OpenCLIP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mlfoundations/open_clip>

[409] Google / Hugging Face, "SigLIP," [Online]. Available: <https://huggingface.co/docs/transformers/model_doc/siglip>

[410] Jina AI, "jina-clip-v2," [Online]. Available: <https://jina.ai/models/jina-clip-v2/>

[411] Chroma, "Chroma," [Online]. Available: <https://www.trychroma.com/>

[412] LanceDB, "LanceDB," [Online]. Available: <https://www.lancedb.com/>

[413] Spotify, "Annoy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/spotify/annoy>

[414] Google Research, "ScaNN," GitHub. [Online]. Available: <https://github.com/google-research/google-research/tree/master/scann>

[415] pgvector contributors, "pgvector," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pgvector/pgvector>

[416] Supabase, "Supabase Vector," [Online]. Available: <https://supabase.com/modules/vector>

[417] Neon (Databricks), "Neon Serverless Postgres," [Online]. Available: <https://neon.com/>

[418] Elastic, "Elasticsearch," [Online]. Available: <https://www.elastic.co/elasticsearch>

[419] OpenSearch Project, "OpenSearch," [Online]. Available: <https://opensearch.org/>

[420] Vespa.ai, "Vespa," [Online]. Available: <https://vespa.ai/>

[421] Typesense, "Typesense," [Online]. Available: <https://typesense.org/>

[422] Meili SAS, "Meilisearch," [Online]. Available: <https://www.meilisearch.com/>

[423] Turbopuffer, "Turbopuffer," [Online]. Available: <https://turbopuffer.com/>

[424] Redis, "Vector Database," [Online]. Available: <https://redis.io/solutions/vector-database/>

[425] Alex Garcia, "sqlite-vec," GitHub. [Online]. Available: <https://github.com/asg017/sqlite-vec>

[426] LangChain AI, "LangMem," GitHub. [Online]. Available: <https://github.com/langchain-ai/langmem>

[427] Cognee, "Cognee," [Online]. Available: <https://www.cognee.ai/>

[428] Anthropic, "Memory tool," Claude API Docs. [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/memory-tool>

[429] Kong, "Kong AI Gateway," [Online]. Available: <https://konghq.com/products/kong-ai-gateway>

[430] Martian, "Martian," [Online]. Available: <https://withmartian.com/>

[431] SAP, "Joule," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/ai-assistant.html>

[432] Langfuse, "Prompt Management," [Online]. Available: <https://langfuse.com/docs/prompts>

[433] Helicone, "Helicone," [Online]. Available: <https://www.helicone.ai/>

[434] Latitude, "Latitude," [Online]. Available: <https://latitude.so/>

[435] Agenta, "Agenta," [Online]. Available: <https://agenta.ai/>

[436] Anthropic, "Prompt Caching," [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>

[437] OpenAI, "Prompt Caching," [Online]. Available: <https://platform.openai.com/docs/guides/prompt-caching>

[438] Google, "Gemini Context Caching," [Online]. Available: <https://ai.google.dev/gemini-api/docs/caching>

[439] OpenAI, "Agents SDK," [Online]. Available: <https://openai.github.io/openai-agents-python/>

[440] OpenAI, "Swarm," GitHub. [Online]. Available: <https://github.com/openai/swarm>

[441] CrewAI, "CrewAI," [Online]. Available: <https://crewai.com/>

[442] Pydantic, "PydanticAI," [Online]. Available: <https://ai.pydantic.dev/>

[443] Hugging Face, "smolagents," GitHub. [Online]. Available: <https://github.com/huggingface/smolagents>

[444] Inngest, "AgentKit," [Online]. Available: <https://agentkit.inngest.com/>

[445] Microsoft, "TaskWeaver," GitHub. [Online]. Available: <https://github.com/microsoft/TaskWeaver>

[446] Microsoft Azure, "AI Foundry," [Online]. Available: <https://azure.microsoft.com/en-us/products/ai-foundry/>

[447] AWS, "Amazon Bedrock Agents," [Online]. Available: <https://aws.amazon.com/bedrock/agents/>

[448] Google Cloud, "Vertex AI Agent Builder," [Online]. Available: <https://cloud.google.com/products/agent-builder>

[449] Databricks, "Mosaic AI Agent Framework," [Online]. Available: <https://www.databricks.com/product/machine-learning/retrieval-augmented-generation>

[450] SAP, "Joule Studio," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/joule-studio.html>

[451] ServiceNow, "AI Agents," [Online]. Available: <https://www.servicenow.com/products/ai-agents.html>

[452] Toolhouse, "Toolhouse," [Online]. Available: <https://toolhouse.ai/>

[453] Pipedream, "Pipedream Connect," [Online]. Available: <https://pipedream.com/connect>

[454] Zapier, "Zapier MCP," [Online]. Available: <https://zapier.com/mcp>

[455] Stripe, "Stripe Agent Toolkit," GitHub. [Online]. Available: <https://github.com/stripe/agent-toolkit>

[456] Cloudflare, "Cloudflare Agents," [Online]. Available: <https://developers.cloudflare.com/agents/>

[457] Cloudflare, "Model Context Protocol on Cloudflare," [Online]. Available: <https://developers.cloudflare.com/agents/model-context-protocol/>

[458] Cloudflare, "Introducing pay-per-crawl: enabling content owners to charge a price of their choice," [Online]. Available: <https://blog.cloudflare.com/introducing-pay-per-crawl/>

[459] Anthropic, "Agent Skills," [Online]. Available: <https://www.anthropic.com/news/agent-skills>

[460] Atlassian, "Remote MCP Server," [Online]. Available: <https://www.atlassian.com/platform/remote-mcp-server>

[461] Spectre Console, "OpenCLI Specification," [Online]. Available: <https://opencli.org/>

[462] HKUDS, "CLI-Anything," GitHub. [Online]. Available: <https://github.com/HKUDS/CLI-Anything>

[463] Smithery, "Smithery," [Online]. Available: <https://smithery.ai/>

[464] PulseMCP, "PulseMCP," [Online]. Available: <https://www.pulsemcp.com/>

[465] Glama, "MCP Registry," [Online]. Available: <https://glama.ai/mcp>

[466] Anthropic, "Computer Use Tool," [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/computer-use>

[467] Google DeepMind, "Project Mariner," [Online]. Available: <https://deepmind.google/models/project-mariner/>

[468] Hyperbrowser, "Hyperbrowser," [Online]. Available: <https://www.hyperbrowser.ai/>

[469] Steel, "Steel," [Online]. Available: <https://steel.dev/>

[470] Anchor Browser, "Anchor Browser," [Online]. Available: <https://anchorbrowser.io/>

[471] TinyFish, "AgentQL," [Online]. Available: <https://www.agentql.com/>

[472] Browserless, "Browserless," [Online]. Available: <https://www.browserless.io/>

[473] Skyvern AI, "Skyvern," [Online]. Available: <https://www.skyvern.com/>

[474] Browserbase, "Stagehand," GitHub. [Online]. Available: <https://github.com/browserbase/stagehand>

[475] nut-tree, "nut.js," [Online]. Available: <https://nutjs.dev/>

[476] Open Interpreter, "Open Interpreter," [Online]. Available: <https://www.openinterpreter.com/>

[477] Microsoft, "Playwright MCP," GitHub. [Online]. Available: <https://github.com/microsoft/playwright-mcp>

[478] Vercel Labs, "agent-browser," GitHub. [Online]. Available: <https://github.com/vercel-labs/agent-browser>

[479] Manus, "Manus," [Online]. Available: <https://manus.im/>

[480] Reworkd, "Reworkd," [Online]. Available: <https://www.reworkd.ai/>

[481] MultiOn, "MultiOn," [Online]. Available: <https://multion.ai/>

[482] CodeSandbox, "CodeSandbox SDK," [Online]. Available: <https://codesandbox.io/sdk>

[483] Cloudflare, "Cloudflare Containers," [Online]. Available: <https://developers.cloudflare.com/containers/>

[484] Replit, "Replit Agent," [Online]. Available: <https://replit.com/products/agent>

[485] Arize AI, "Phoenix," [Online]. Available: <https://phoenix.arize.com/>

[486] Arize AI, "Arize AX," [Online]. Available: <https://arize.com/>

[487] Helicone, "Helicone," [Online]. Available: <https://www.helicone.ai/>

[488] Pydantic, "Pydantic Logfire," [Online]. Available: <https://logfire.pydantic.dev/>

[489] Weights & Biases, "W&B Weave," [Online]. Available: <https://wandb.ai/site/weave/>

[490] Datadog, "LLM Observability," [Online]. Available: <https://www.datadoghq.com/product/ai/llm-observability/>

[491] New Relic, "AI Monitoring," [Online]. Available: <https://newrelic.com/platform/ai-monitoring>

[492] Splunk, "Observability Cloud," [Online]. Available: <https://www.splunk.com/en_us/products/observability-cloud.html>

[493] Lakera, "Lakera Guard," [Online]. Available: <https://www.lakera.ai/lakera-guard>

[494] Protect AI (Palo Alto Networks), "Protect AI," [Online]. Available: <https://protectai.com/>

[495] Protect AI, "NB Defense," GitHub. [Online]. Available: <https://github.com/protectai/nbdefense>

[496] Robust Intelligence (Cisco), "Robust Intelligence," [Online]. Available: <https://www.robustintelligence.com/>

[497] Prompt Security, "Prompt Security," [Online]. Available: <https://prompt.security/>

[498] HiddenLayer, "HiddenLayer," [Online]. Available: <https://www.hiddenlayer.com/>

[499] CalypsoAI (F5), "CalypsoAI," [Online]. Available: <https://calypsoai.com/>

[500] Meta, "Prompt Guard," [Online]. Available: <https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/>

[501] Patronus AI, "Patronus AI," [Online]. Available: <https://www.patronus.ai/>

[502] TruEra (Snowflake), "TruLens," [Online]. Available: <https://www.trulens.org/>

[503] Galileo, "Galileo AI," [Online]. Available: <https://galileo.ai/>

[504] PlayHT, "PlayHT," [Online]. Available: <https://play.ht/>

[505] Hume AI, "Hume AI," [Online]. Available: <https://www.hume.ai/>

[506] Resemble AI, "Resemble AI," [Online]. Available: <https://www.resemble.ai/>

[507] OpenAI, "Text to speech," [Online]. Available: <https://platform.openai.com/docs/guides/text-to-speech>

[508] Google, "Chirp 3," [Online]. Available: <https://cloud.google.com/text-to-speech/docs/chirp3-hd>

[509] Alibaba / FunAudioLLM, "CosyVoice," GitHub. [Online]. Available: <https://github.com/FunAudioLLM/CosyVoice>

[510] AssemblyAI, "AssemblyAI," [Online]. Available: <https://www.assemblyai.com/>

[511] Speechmatics, "Speechmatics," [Online]. Available: <https://www.speechmatics.com/>

[512] Rev AI, "Rev AI," [Online]. Available: <https://www.rev.ai/>

[513] NVIDIA, "NeMo Parakeet ASR Models," [Online]. Available: <https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/>

[514] Google, "Chirp Transcription Models," [Online]. Available: <https://cloud.google.com/speech-to-text/docs/models/chirp-3>

[515] OpenAI, "Realtime API," [Online]. Available: <https://platform.openai.com/docs/guides/realtime>

[516] Google, "Gemini Live API," [Online]. Available: <https://ai.google.dev/gemini-api/docs/live-api>

[517] Sesame AI, "Sesame AI," [Online]. Available: <https://www.sesame.com/>

[518] Kyutai, "Kyutai," [Online]. Available: <https://kyutai.org/>

[519] LiveKit, "LiveKit," [Online]. Available: <https://livekit.io/>

[520] Daily.co, "Pipecat," [Online]. Available: <https://www.pipecat.ai/>

[521] Vapi, "Vapi," [Online]. Available: <https://vapi.ai/>

[522] Retell AI, "Retell AI," [Online]. Available: <https://www.retellai.com/>

[523] Ideogram, "Ideogram," [Online]. Available: <https://ideogram.ai/>

[524] Adobe, "Adobe Firefly," [Online]. Available: <https://firefly.adobe.com/>

[525] Google DeepMind, "Imagen 3," [Online]. Available: <https://deepmind.google/technologies/imagen-3/>

[526] OpenAI, "DALL-E 3," [Online]. Available: <https://openai.com/index/dall-e-3/>

[527] Recraft, "Recraft," [Online]. Available: <https://www.recraft.ai/>

[528] Stability AI, "Stability AI," [Online]. Available: <https://stability.ai/>

[529] PixArt-alpha, "PixArt-Σ," GitHub. [Online]. Available: <https://github.com/PixArt-alpha/PixArt-sigma>

[530] Tencent, "HunyuanImage-3.0," GitHub. [Online]. Available: <https://github.com/Tencent-Hunyuan/HunyuanImage-3.0>

[531] Comfy Org, "ComfyUI," GitHub. [Online]. Available: <https://github.com/Comfy-Org/ComfyUI>

[532] AUTOMATIC1111, "stable-diffusion-webui," GitHub. [Online]. Available: <https://github.com/AUTOMATIC1111/stable-diffusion-webui>

[533] lllyasviel, "Fooocus," GitHub. [Online]. Available: <https://github.com/lllyasviel/Fooocus>

[534] Pika Labs, "Pika," [Online]. Available: <https://pika.art/>

[535] Luma AI, "Dream Machine," [Online]. Available: <https://lumalabs.ai/dream-machine>

[536] Kuaishou, "Kling AI," [Online]. Available: <https://app.klingai.com/global>

[537] MiniMax, "Hailuo AI," [Online]. Available: <https://hailuoai.video/>

[538] Google DeepMind, "Veo," [Online]. Available: <https://deepmind.google/technologies/veo/>

[539] Tencent, "HunyuanVideo," GitHub. [Online]. Available: <https://github.com/Tencent-Hunyuan/HunyuanVideo>

[540] Alibaba / Wan-Video, "Wan2.2," GitHub. [Online]. Available: <https://github.com/Wan-Video/Wan2.2>

[541] Luma AI, "Luma," [Online]. Available: <https://lumalabs.ai/>

[542] Meshy, "Meshy AI," [Online]. Available: <https://www.meshy.ai/>

[543] Tripo AI, "Tripo," [Online]. Available: <https://www.tripo3d.ai/>

[544] DeemosTech, "Rodin," [Online]. Available: <https://hyper3d.ai/>

[545] World Labs, "World Labs," [Online]. Available: <https://www.worldlabs.ai/>

[546] Common Sense Machines, "CSM," [Online]. Available: <https://www.csm.ai/>

[547] Google, "Gemini," [Online]. Available: <https://gemini.google.com/>

[548] xAI, "Grok," [Online]. Available: <https://grok.com/>

[549] DeepSeek, "DeepSeek Chat," [Online]. Available: <https://chat.deepseek.com/>

[550] Moonshot AI, "Kimi," [Online]. Available: <https://kimi.moonshot.cn/>

[551] Alibaba Cloud, "通义千问," [Online]. Available: <https://tongyi.aliyun.com/>

[552] ByteDance, "豆包," [Online]. Available: <https://www.doubao.com/>

[553] Perplexity AI, "Perplexity," [Online]. Available: <https://www.perplexity.ai/>

[554] You.com, "You.com," [Online]. Available: <https://you.com/>

[555] Brave Software, "Brave Leo AI," [Online]. Available: <https://brave.com/leo/>

[556] The Browser Company, "Arc Search," [Online]. Available: <https://arc.net/search>

[557] Komo, "Komo AI," [Online]. Available: <https://komo.ai/>

[558] Quora, "Poe," [Online]. Available: <https://poe.com/>

[559] Mistral AI, "Le Chat," [Online]. Available: <https://mistral.ai/products/le-chat>

[560] Hugging Face, "HuggingChat," [Online]. Available: <https://huggingface.co/chat/>

[561] Msty AI, "Msty," [Online]. Available: <https://msty.ai/>

[562] LM Studio, "LM Studio," [Online]. Available: <https://lmstudio.ai/>

[563] Google, "AI Tools for Business," Google Workspace. [Online]. Available: <https://workspace.google.com/solutions/ai/>

[564] Slack (Salesforce), "Slack AI," [Online]. Available: <https://slack.com/features/ai>

[565] Notion Labs, "Notion," [Online]. Available: <https://www.notion.com/>

[566] Glean, "Glean," [Online]. Available: <https://www.glean.com/>

[567] Anthropic, "Claude Code," [Online]. Available: <https://claude.ai/code>

[568] Codeium / OpenAI, "Windsurf," [Online]. Available: <https://windsurf.com/>

[569] Replit, "Replit Agent," [Online]. Available: <https://replit.com/products/agent>

[570] OpenAI, "Codex," GitHub. [Online]. Available: <https://github.com/openai/codex>

[571] Aider AI, "Aider," [Online]. Available: <https://aider.chat/>

[572] GitHub (Microsoft), "Copilot Workspace," GitHub Next. [Online]. Available: <https://githubnext.com/projects/copilot-workspace/>

[573] Augment Code, "Augment Code," [Online]. Available: <https://www.augmentcode.com/>

[574] Sourcegraph, "Amp," [Online]. Available: <https://ampcode.com/>

[575] Lovable, "Lovable," [Online]. Available: <https://lovable.dev/>

[576] StackBlitz, "Bolt," [Online]. Available: <https://bolt.new/>

[577] Vercel, "v0," [Online]. Available: <https://v0.app/>

[578] Figma, "Figma AI," [Online]. Available: <https://www.figma.com/ai/>

[579] Figma, "Figma Make," [Online]. Available: <https://www.figma.com/make/>

[580] Google (formerly Galileo AI), "Figma Make," [Online]. Available: <https://www.figma.com/make/>

[581] Framer, "Framer AI," [Online]. Available: <https://www.framer.com/ai/>

[582] Canva, "Canva AI," [Online]. Available: <https://www.canva.com/canva-ai/>

[583] Jasper AI, "Jasper," [Online]. Available: <https://www.jasper.ai/>

[584] Copy.ai, "Copy.ai," [Online]. Available: <https://www.copy.ai/>

[585] Decagon AI, "Decagon," [Online]. Available: <https://decagon.ai/>

[586] Sierra AI, "Sierra," [Online]. Available: <https://sierra.ai/>

[587] Ada Support, "Ada," [Online]. Available: <https://www.ada.cx/>

[588] Intercom, "Fin," [Online]. Available: <https://fin.ai/>

[589] Cresta AI, "Cresta," [Online]. Available: <https://cresta.com/>

[590] Clay Labs, "Clay," [Online]. Available: <https://www.clay.com/>

[591] 11x, "11x," [Online]. Available: <https://www.11x.ai/>

[592] AirOps, "AirOps," [Online]. Available: <https://www.airops.com/>

[593] Glean, "Glean," [Online]. Available: <https://www.glean.com/>

[594] Moveworks (ServiceNow), "Moveworks," [Online]. Available: <https://www.moveworks.com/>

[595] Hebbia, "Hebbia," [Online]. Available: <https://www.hebbia.com/>

[596] Counsel AI, "Harvey," [Online]. Available: <https://www.harvey.ai/>

[597] Thomson Reuters, "CoCounsel," [Online]. Available: <https://cocounsel.thomsonreuters.com/>

[598] Oracle, "AI Agents for Fusion Applications," [Online]. Available: <https://www.oracle.com/applications/fusion-ai/ai-agents/>

[599] Workday, "AI Solutions," [Online]. Available: <https://www.workday.com/en-us/artificial-intelligence.html>

[600] ServiceNow, "Now Assist," [Online]. Available: <https://www.servicenow.com/platform/now-assist.html>

[601] Microsoft, "Dynamics 365 Copilot," [Online]. Available: <https://www.microsoft.com/en-us/dynamics-365/>

[602] CodeRabbit, "CodeRabbit," [Online]. Available: <https://www.coderabbit.ai/>

[603] Greptile, "Greptile," [Online]. Available: <https://www.greptile.com/>

[604] Qodo, "Qodo," [Online]. Available: <https://www.qodo.ai/>

[605] Meticulous AI, "Meticulous," [Online]. Available: <https://www.meticulous.ai/>

[606] Snyk, "DeepCode AI," [Online]. Available: <https://snyk.io/platform/deepcode-ai/>

[607] Abridge, "Abridge," [Online]. Available: <https://www.abridge.com/>

[608] Hippocratic AI, "Hippocratic AI," [Online]. Available: <https://hippocraticai.com/>

[609] Ambience Healthcare, "Ambience," [Online]. Available: <https://www.ambiencehealthcare.com/>

[610] FutureHouse, "FutureHouse," [Online]. Available: <https://www.futurehouse.org/>

[611] Scite (Research Solutions), "Scite," [Online]. Available: <https://scite.ai/>

[612] OpenMP Architecture Review Board, "OpenMP," *openmp.org*, 2025. [Online]. Available: <https://www.openmp.org/>

[613] Open MPI Project, "Open MPI: Open Source High Performance Computing," *open-mpi.org*, 2025. [Online]. Available: <https://www.open-mpi.org/>

[614] Argonne National Laboratory, "MPICH High-Performance Portable MPI," *mpich.org*, 2025. [Online]. Available: <https://www.mpich.org/>

[615] NVIDIA, "NVIDIA HPC-X Software Toolkit," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/networking/hpc-x>

[616] UCX Consortium, "Unified Communication X (UCX)," *openucx.org*, 2025. [Online]. Available: <https://openucx.org/>

[617] Altair, "PBS Professional – HPC Workload Management," *altair.com*, 2025. [Online]. Available: <https://altair.com/pbs-professional>

[618] IBM, "IBM Spectrum LSF – HPC Workload Management," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/products/hpc-workload-management>

[619] EasyBuild Community, "EasyBuild: Building Software with Ease," *easybuild.io*, 2025. [Online]. Available: <https://easybuild.io/>

[620] Sandia National Laboratories, "LAMMPS Molecular Dynamics Simulator," *lammps.org*, 2025. [Online]. Available: <https://lammps.org/>

[621] Theoretical and Computational Biophysics Group, UIUC, "NAMD Scalable Molecular Dynamics," *ks.uiuc.edu*, 2025. [Online]. Available: <https://www.ks.uiuc.edu/Research/namd/>

[622] AMBER Developers, "AMBER Molecular Dynamics Package," *ambermd.org*, 2025. [Online]. Available: <https://ambermd.org/>

[623] Schrödinger, Inc., "Schrödinger Computational Chemistry Suite," *schrodinger.com*, 2025. [Online]. Available: <https://www.schrodinger.com/>

[624] NVIDIA, "CUDA-Q: A Platform for Hybrid Quantum-Classical Computing," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/cuda-q>

[625] IBM, "Qiskit: Open-Source Quantum Development," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/quantum/qiskit>

[626] Google, "Cirq: A Python Framework for Creating, Editing, and Invoking Noisy Intermediate Scale Quantum (NISQ) Circuits," *quantumai.google*, 2025. [Online]. Available: <https://quantumai.google/cirq>

[627] Xanadu, "PennyLane: A Cross-Platform Python Library for Differentiable Programming of Quantum Computers," *pennylane.ai*, 2025. [Online]. Available: <https://pennylane.ai/>

[628] Quantinuum, "TKET Quantum Computing Toolkit," *quantinuum.com*, 2025. [Online]. Available: <https://www.quantinuum.com/products-solutions/developer-tools>

[629] NVIDIA, "cuOpt: GPU-Accelerated Route Optimization," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/ai-data-science/products/cuopt/>

[630] Gurobi Optimization, "Gurobi Optimizer," *gurobi.com*, 2025. [Online]. Available: <https://www.gurobi.com/>

[631] IBM, "IBM ILOG CPLEX Optimization Studio," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/products/ilog-cplex-optimization-studio>

[632] Google, "OR-Tools: Open Source Software for Combinatorial Optimization," *developers.google.com*, 2025. [Online]. Available: <https://developers.google.com/optimization>

[633] COIN-OR Foundation, "Computational Infrastructure for Operations Research," *coin-or.org*, 2025. [Online]. Available: <https://www.coin-or.org/>

[634] Ansys, "Ansys Fluent – Fluid Simulation Software," *ansys.com*, 2025. [Online]. Available: <https://www.ansys.com/products/fluids/ansys-fluent>

[635] Siemens, "Simcenter STAR-CCM+: Multiphysics CFD Software," *siemens.com*, 2025. [Online]. Available: <https://www.siemens.com/en-us/products/simcenter/fluids-thermal-simulation/star-ccm/>

[636] NVIDIA, "PhysicsNeMo (formerly Modulus): Physics-Informed Neural Operator Framework," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/physicsnemo>

[637] TU Munich Physics-based Simulation Group, "PhiFlow: A Research-Oriented Differentiable Fluid Simulation Framework," *GitHub*, 2025. [Online]. Available: <https://github.com/tum-pbs/PhiFlow>

[638] Google Research, "JAX-CFD: Computational Fluid Dynamics in JAX," *GitHub*, 2025. [Online]. Available: <https://github.com/google/jax-cfd>

[639] Baker Lab, University of Washington, "RoseTTAFold All-Atom," *GitHub*, 2024. [Online]. Available: <https://github.com/baker-laboratory/RoseTTAFold-All-Atom>

[640] EvolutionaryScale, "ESM-3: Simulating 500 Million Years of Evolution with a Language Model," *evolutionaryscale.ai*, 2024. [Online]. Available: <https://www.evolutionaryscale.ai/>

[641] MIT, "Boltz-1: Democratizing Biomolecular Structure Prediction," *GitHub*, 2024. [Online]. Available: <https://github.com/jwohlwend/boltz>

[642] Chai Discovery, "Chai-1: A Multi-Modal Foundation Model for Molecular Structure Prediction," *chaidiscovery.com*, 2024. [Online]. Available: <https://www.chaidiscovery.com/>

[643] NVIDIA, "BioNeMo MolMIM: Molecular Generation NIM," *NVIDIA Docs*, 2025. [Online]. Available: <https://docs.nvidia.com/nim/bionemo/molmim/latest/overview.html>

[644] Columbia University & other contributors, "OpenFold: A Trainable, Open-Source Implementation of AlphaFold2," *openfold.io*, 2024. [Online]. Available: <https://openfold.io/>

[645] G. Corso et al., "DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking," *GitHub*, 2023. [Online]. Available: <https://github.com/gcorso/DiffDock>

[646] Insilico Medicine, "Pharma.AI: AI Drug Discovery Platform," *pharma.ai*, 2025. [Online]. Available: <https://pharma.ai/>

[647] Google DeepMind, "GenCast: Predicts Weather and the Risks of Extreme Conditions," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/>

[648] Huawei, "Pangu-Weather: Accurate Medium-Range Global Weather Forecasting (Nature 2023)," *GitHub*, 2023. [Online]. Available: <https://github.com/198808xc/Pangu-Weather>

[649] NVIDIA, "FourCastNet: Fourier Forecasting Neural Network for Global Weather Prediction," *GitHub*, 2023. [Online]. Available: <https://github.com/NVlabs/FourCastNet>

[650] Microsoft Research, "Aurora: A Foundation Model of the Atmosphere," *Microsoft Research*, 2024. [Online]. Available: <https://www.microsoft.com/en-us/research/project/aurora-forecasting/>

[651] Fudan University, "FuXi: A Cascade Machine Learning Forecasting System for 15-Day Global Weather Forecast," *GitHub*, 2023. [Online]. Available: <https://github.com/tpys/FuXi>

[652] ECMWF, "AIFS – New ECMWF AI Forecasting System," *ecmwf.int*, 2024. [Online]. Available: <https://www.ecmwf.int/en/newsletter/178/news/aifs-new-ecmwf-forecasting-system>

[653] University of Cambridge, "MACE: Fast and Accurate Machine Learning Interatomic Potentials," *GitHub*, 2024. [Online]. Available: <https://github.com/ACEsuit/mace>

[654] MIT & Harvard, "NequIP: E(3)-equivariant Neural Network Interatomic Potentials," *GitHub*, 2023. [Online]. Available: <https://github.com/mir-group/nequip>

[655] MIT, "Allegro: Scalable and Transferable Interatomic Potentials," *GitHub*, 2023. [Online]. Available: <https://github.com/mir-group/allegro>

[656] Google DeepMind, "GNoME: Millions of New Materials Discovered with Deep Learning," *deepmind.google*, 2023. [Online]. Available: <https://deepmind.google/blog/millions-of-new-materials-discovered-with-deep-learning/>

[657] Orbital Materials, "Orb: Fast and Accurate Machine Learning Potentials," *orbitalindustries.com*, 2024. [Online]. Available: <https://www.orbitalindustries.com/>

[658] Google DeepMind, "AI Solves IMO Problems at Silver Medal Level (AlphaProof + AlphaGeometry 2)," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/>

[659] Google DeepMind, "FunSearch: Making New Discoveries in Mathematical Sciences Using Large Language Models," *GitHub*, 2024. [Online]. Available: <https://github.com/google-deepmind/funsearch>

[660] Lean Prover Community, "Lean: A Functional Programming Language and Theorem Prover," *leanprover-community.github.io*, 2025. [Online]. Available: <https://leanprover-community.github.io/>

[661] DeepSeek AI, "DeepSeek-Prover-V2," *GitHub*, 2025. [Online]. Available: <https://github.com/deepseek-ai/DeepSeek-Prover-V2>

[662] C. Theodoris et al., "Geneformer: Transfer Learning with Context-Aware Gene Network Foundations," *Hugging Face*, 2023. [Online]. Available: <https://huggingface.co/ctheodoris/Geneformer>

[663] Tsinghua University & BioMap, "scFoundation: Large-Scale Foundation Model on Single-Cell Transcriptomics," *GitHub*, 2024. [Online]. Available: <https://github.com/biomap-research/scFoundation>

[664] xCompass AI, "GeneCompass: Deciphering Universal Gene Regulatory Networks with Knowledge-Informed Cross-Species Foundation Model," *GitHub*, 2024. [Online]. Available: <https://github.com/xCompass-AI/GeneCompass>

[665] MONAI Consortium, "MONAI: Medical Open Network for AI," *monai.io*, 2025. [Online]. Available: <https://monai.io/>

[666] Wang Lab, "MedSAM: Segment Anything in Medical Images," *GitHub*, 2024. [Online]. Available: <https://github.com/bowang-lab/MedSAM>

[667] J. Wasserthal et al., "TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images," *GitHub*, 2024. [Online]. Available: <https://github.com/wasserth/TotalSegmentator>

[668] Google, "Advancing Medical AI with Med-Gemini," *Google Research*, 2024. [Online]. Available: <https://research.google/blog/advancing-medical-ai-with-med-gemini/>

[669] Microsoft, "RAD-DINO: Exploring Scalable Medical Image Encoders Beyond Text Supervision," *Hugging Face*, 2024. [Online]. Available: <https://huggingface.co/microsoft/rad-dino>

[670] NVIDIA, "BioNeMo: Generative AI Platform for Drug Discovery," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[671] NVIDIA, "Earth-2: An AI Supercomputer to Predict Climate Change," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/omniverse/>

[672] NVIDIA, "CUDA-Q Cloud: Hybrid Quantum-Classical Computing Platform," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/cuda-q>

[673] Isomorphic Labs / Google DeepMind, "AlphaFold Server," *alphafoldserver.com*, 2024. [Online]. Available: <https://alphafoldserver.com/>

[674] Schrödinger, "LiveDesign: Collaborative Drug Discovery Platform," *schrodinger.com*, 2025. [Online]. Available: <https://www.schrodinger.com/platform/products/livedesign/>

[675] Recursion Pharmaceuticals, "BioHive-2: Life Science AI Supercomputer," *recursion.com*, 2024. [Online]. Available: <https://www.recursion.com/>

[676] Cradle, "Cradle.bio: AI-Powered Protein Design," *cradle.bio*, 2025. [Online]. Available: <https://www.cradle.bio/>

[677] Profluent Bio, "Profluent: AI-Designed Proteins and Gene Editors," *profluent.bio*, 2025. [Online]. Available: <https://www.profluent.bio/>

[678] Google Cloud, "Cluster Toolkit: Deploy HPC Workloads on Google Cloud," *cloud.google.com*, 2025. [Online]. Available: <https://docs.cloud.google.com/cluster-toolkit/docs/overview>

[679] Posit PBC, "Quarto: An Open-Source Scientific and Technical Publishing System," *quarto.org*, 2025. [Online]. Available: <https://quarto.org/>

[680] Project Jupyter, "JupyterHub: Multi-User Jupyter Notebooks," *jupyter.org*, 2025. [Online]. Available: <https://jupyter.org/hub>

[681] Anaconda, Inc., "Anaconda: The World's Most Popular Python/R Data Science Platform," *anaconda.com*, 2025. [Online]. Available: <https://www.anaconda.com/>

[682] micro-ROS, "micro-ROS: ROS 2 for Microcontrollers," *micro.ros.org*, 2025. [Online]. Available: <https://micro.ros.org/>

[683] ArduPilot Dev Team, "ArduPilot: Versatile, Trusted, Open Autonomous Vehicle Software," *ardupilot.org*, 2025. [Online]. Available: <https://ardupilot.org/>

[684] Dronecode Foundation, "PX4 Open Source Autopilot," *px4.io*, 2025. [Online]. Available: <https://px4.io/>

[685] BlackBerry QNX, "QNX Real-Time Operating System," *blackberry.qnx.com*, 2025. [Online]. Available: <https://blackberry.qnx.com/en>

[686] Wind River, "VxWorks: Industry-Leading Real-Time Operating System," *windriver.com*, 2025. [Online]. Available: <https://www.windriver.com/products/vxworks>

[687] Xenomai Project, "Xenomai: Real-Time Framework for Linux," *xenomai.org*, 2025. [Online]. Available: <https://xenomai.org/>

[688] NVIDIA, "Isaac Lab: GPU-Accelerated Robot Learning Framework," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/isaac/lab>

[689] NVIDIA, "Cosmos: World Foundation Models for Physical AI," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/ai/cosmos/>

[690] Genesis Team, "Genesis: A Generative and Universal Physics Engine for Robotics and Embodied AI," *genesis-embodied-ai.github.io*, 2024. [Online]. Available: <https://genesis-embodied-ai.github.io/>

[691] Toyota Research Institute, "Drake: Model-Based Design and Verification for Robotics," *drake.mit.edu*, 2025. [Online]. Available: <https://drake.mit.edu/>

[692] Meta AI Research, "Habitat: A Platform for Embodied AI Research," *aihabitat.org*, 2024. [Online]. Available: <https://aihabitat.org/>

[693] Allen Institute for AI, "AI2-THOR: An Interactive 3D Environment for Visual AI," *ai2thor.allenai.org*, 2025. [Online]. Available: <https://ai2thor.allenai.org/>

[694] Unity Technologies, "ML-Agents: Unity Machine Learning Agents Toolkit," *GitHub*, 2024. [Online]. Available: <https://github.com/unity-technologies/ml-agents>

[695] NVIDIA, "Isaac GR00T N1: Open Humanoid Robot Foundation Model," *NVIDIA Newsroom*, 2025. [Online]. Available: <https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks>

[696] Physical Intelligence, "π0: A Vision-Language-Action Flow Model for General Robot Control," *pi.website*, 2024. [Online]. Available: <https://www.pi.website/blog/pi0>

[697] Google DeepMind, "Gemini Robotics: Bringing AI into the Physical World," *deepmind.google*, 2025. [Online]. Available: <https://deepmind.google/models/gemini-robotics/>

[698] Skild AI, "Skild Brain: General-Purpose Robot Intelligence," *skild.ai*, 2025. [Online]. Available: <https://www.skild.ai/>

[699] Figure AI, "Helix: A Vision-Language-Action Model for Generalist Robot Control," *figure.ai*, 2025. [Online]. Available: <https://www.figure.ai/helix>

[700] 1X Technologies, "1X World Model," *1x.tech*, 2025. [Online]. Available: <https://www.1x.tech/discover/1x-world-model>

[701] UC Berkeley, "Octo: An Open-Source Generalist Robot Policy," *octo-models.github.io*, 2024. [Online]. Available: <https://octo-models.github.io/>

[702] T. Zhao et al., "ACT: Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware," *GitHub*, 2023. [Online]. Available: <https://github.com/tonyzhaozh/act>

[703] Tesla, "Optimus: AI Humanoid Robot," *tesla.com*, 2025. [Online]. Available: <https://www.tesla.com/AI>

[704] Figure AI, "Figure Humanoid Robots," *figure.ai*, 2025. [Online]. Available: <https://www.figure.ai/>

[705] 1X Technologies, "Neo Beta: Humanoid Robot," *1x.tech*, 2025. [Online]. Available: <https://www.1x.tech/neo>

[706] Apptronik, "Apollo: Humanoid Robot for Logistics and Manufacturing," *apptronik.com*, 2025. [Online]. Available: <https://apptronik.com/apollo>

[707] Unitree Robotics, "Unitree H1: Humanoid Robot," *unitree.com*, 2025. [Online]. Available: <https://www.unitree.com/h1/>

[708] Boston Dynamics, "Spot: The Agile Mobile Robot," *bostondynamics.com*, 2025. [Online]. Available: <https://bostondynamics.com/products/spot/>

[709] ANYbotics, "ANYmal: Autonomous Legged Robot for Inspection," *anybotics.com*, 2025. [Online]. Available: <https://www.anybotics.com/robotics/anymal/>

[710] Unitree Robotics, "Unitree Go2: Quadruped Robot," *unitree.com*, 2025. [Online]. Available: <https://www.unitree.com/go2/>

[711] Agility Robotics, "Digit: Bipedal Robot for Warehouse Logistics," *agilityrobotics.com*, 2025. [Online]. Available: <https://www.agilityrobotics.com/>

[712] Intuitive, "da Vinci 5: Surgical System," *intuitive.com*, 2024. [Online]. Available: <https://www.intuitive.com/en-us/products-and-services/da-vinci/5>

[713] Mobileye, "SuperVision: Hands-Free Driving Technology," *mobileye.com*, 2025. [Online]. Available: <https://www.mobileye.com/solutions/super-vision/>

[714] Wayve, "AI-First Approach to Autonomous Driving," *wayve.ai*, 2025. [Online]. Available: <https://wayve.ai/>

[715] NVIDIA, "DRIVE Thor: Centralized Car Computer," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/drive/agx>

[716] Mobileye, "EyeQ6 / EyeQ Ultra: Automotive-Grade Vision SoC," *mobileye.com*, 2025. [Online]. Available: <https://www.mobileye.com/solutions/super-vision/>

[717] Qualcomm, "Snapdragon Ride: Automotive Driving Platform," *qualcomm.com*, 2025. [Online]. Available: <https://www.qualcomm.com/automotive/solutions/snapdragon-ride>

[718] Horizon Robotics, "Journey 6: Automotive Intelligent Driving SoC," *horizon.auto*, 2025. [Online]. Available: <https://en.horizon.auto/>

[719] Baidu, "Apollo: Open Autonomous Driving Platform," *apollo.auto*, 2025. [Online]. Available: <https://www.apollo.auto/en/>

[720] Autoware Foundation, "Autoware: The World's Leading Open-Source Software for Autonomous Driving," *autoware.org*, 2025. [Online]. Available: <https://autoware.org/>

[721] Applied Intuition, "Simulation and Data Platform for Autonomous Systems," *appliedintuition.com*, 2025. [Online]. Available: <https://www.appliedintuition.com/>

[722] Foretellix, "Autonomous Vehicle Verification and Validation Platform," *foretellix.com*, 2025. [Online]. Available: <https://www.foretellix.com/>

[723] Bosch, "Bosch acquires Atlatec to expand HD mapping capabilities," *bosch.com*, Feb 2022. [Online]. Available: <https://www.bosch.com/>

[724] Google DeepMind, "Genie 2: A Large-Scale Foundation World Model," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/>

[725] World Labs, "Marble: Spatial Intelligence World Model," *worldlabs.ai*, 2025. [Online]. Available: <https://www.worldlabs.ai/>

[726] Wayve, "GAIA-2: Generative World Model for Autonomous Driving," *wayve.ai*, 2025. [Online]. Available: <https://wayve.ai/science/gaia/>

[727] Z. Yu et al., "Mip-Splatting: Alias-Free 3D Gaussian Splatting," *GitHub*, CVPR 2024 Best Student Paper. [Online]. Available: <https://github.com/autonomousvision/mip-splatting>

[728] Polycam, "Polycam: 3D Capture App for iPhone and iPad," *poly.cam*, 2025. [Online]. Available: <https://poly.cam/>

[729] KIRI Innovation, "KIRI Engine: Photogrammetry 3D Scanning App," *kiriengine.app*, 2025. [Online]. Available: <https://www.kiriengine.app/>

[730] DeemosTech, "Rodin: AI-Powered 3D Avatar and Asset Generation," *hyperhuman.deemos.com*, 2025. [Online]. Available: <https://hyperhuman.deemos.com/>

[731] Tencent, "Hunyuan3D 2.5: High-Resolution 3D Asset Generation," *GitHub*, 2025. [Online]. Available: <https://github.com/Tencent-Hunyuan/Hunyuan3D-2>

[732] Microsoft, "TRELLIS: Structured 3D Latents for Scalable and Versatile 3D Generation," *GitHub*, 2024. [Online]. Available: <https://github.com/microsoft/TRELLIS>

[733] Spline, "Spline: 3D Design Tool with AI Capabilities," *spline.design*, 2025. [Online]. Available: <https://spline.design/>

[734] NVIDIA, "ACE: Avatar Cloud Engine for Digital Humans," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/ace-for-games>

[735] Inworld AI, "AI-Powered NPCs and Character Simulation," *inworld.ai*, 2025. [Online]. Available: <https://inworld.ai/>

[736] Convai Technologies, "Convai: Conversational AI for Game Characters," *convai.com*, 2025. [Online]. Available: <https://convai.com/>

[737] Charisma Entertainment, "Charisma.ai: AI-Powered Storytelling and Character Platform," *charisma.ai*, 2025. [Online]. Available: <https://charisma.ai/>

[738] Unity Technologies, "Sentis: In-App Neural Network Inference," *unity.com*, 2025. [Online]. Available: <https://unity.com/products/sentis>

[739] Pixar Animation Studios, "OpenUSD: Universal Scene Description," *openusd.org*, 2025. [Online]. Available: <https://openusd.org/>

[740] SideFX, "Houdini Copernicus: GPU-Accelerated Material Computation," *sidefx.com*, 2025. [Online]. Available: <https://www.sidefx.com/products/whats-new-in-h205/copernicus/>

[741] Ultralytics, "YOLO: Real-Time Object Detection," *ultralytics.com*, 2025. [Online]. Available: <https://www.ultralytics.com/>

[742] Meta AI Research, "Detectron2: A PyTorch-Based Modular Object Detection Library," *GitHub*, 2024. [Online]. Available: <https://github.com/facebookresearch/detectron2>

[743] OpenMMLab, "OpenMMLab: Open-Source Computer Vision Toolkits," *GitHub*, 2025. [Online]. Available: <https://github.com/open-mmlab>

[744] IDEA Research, "Grounding DINO: Open-Set Object Detection," *GitHub*, ECCV 2024. [Online]. Available: <https://github.com/IDEA-Research/GroundingDINO>

[745] Baidu, "PaddleOCR: Rich, Leading and Practical OCR Tools," *GitHub*, 2025. [Online]. Available: <https://github.com/PaddlePaddle/PaddleOCR>

[746] Google (originally HP), "Tesseract Open Source OCR Engine," *GitHub*, 2025. [Online]. Available: <https://github.com/tesseract-ocr/tesseract>

[747] V. Paruchuri, "Surya: OCR, Layout Analysis, Reading Order, Table Recognition in 90+ Languages," *GitHub*, 2024. [Online]. Available: <https://github.com/VikParuchuri/surya>

[748] OpenDataLab, "DocLayout-YOLO: Enhancing Document Layout Analysis," *GitHub*, 2024. [Online]. Available: <https://github.com/opendatalab/DocLayout-YOLO>

[749] Meta AI, "Nougat: Neural Optical Understanding for Academic Documents," *GitHub*, 2023. [Online]. Available: <https://github.com/facebookresearch/nougat>

[750] Shanghai AI Laboratory, "MinerU: High-Quality Document Parsing Tool," *GitHub*, 2025. [Online]. Available: <https://github.com/opendatalab/MinerU>

[751] Mistral AI, "Mistral OCR: State-of-the-Art Document Understanding," *mistral.ai*, 2025. [Online]. Available: <https://mistral.ai/news/mistral-ocr>

[752] Reducto, "Reducto: AI Document Parsing and Extraction," *reducto.ai*, 2025. [Online]. Available: <https://reducto.ai/>

[753] Unstructured, "Unstructured: ETL Solution for Transforming Complex Documents for LLMs," *unstructured.io*, 2025. [Online]. Available: <https://unstructured.io/>

[754] OpenGVLab, "InternVideo: Video Foundation Models for Multimodal Understanding," *GitHub*, ECCV 2024. [Online]. Available: <https://github.com/OpenGVLab/InternVideo>

[755] DAMO-NLP-SG, Alibaba, "VideoLLaMA 3: Frontier Multimodal Foundation Models for Image and Video Understanding," *GitHub*, 2025. [Online]. Available: <https://github.com/DAMO-NLP-SG/VideoLLaMA3>

[756] Alibaba Cloud Qwen Team, "Qwen-VL: Multimodal Large Language Models," *GitHub*, 2025. [Online]. Available: <https://github.com/QwenLM/Qwen-VL>

[757] TwelveLabs, "Marengo: Video Foundation Model for Multimodal Understanding," *twelvelabs.io*, 2025. [Online]. Available: <https://www.twelvelabs.io/product/models-overview>

[758] TencentQQ Multimedia Research Team, "Video-CCAM: Enhancing Video-Language Understanding with Causal Cross-Attention Masks," *GitHub*, 2024. [Online]. Available: <https://github.com/QQ-MM/Video-CCAM>

[759] Qualcomm, "Qualcomm AI Engine Direct SDK (QNN)," *qualcomm.com*, 2025. [Online]. Available: <https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk>

[760] Arm, "Arm NN: ML Inference Engine for Arm CPUs, GPUs, and NPUs," *arm.com*, 2025. [Online]. Available: <https://www.arm.com/products/silicon-ip-cpu/ethos/arm-nn>

[761] Google, "MediaPipe: Cross-Platform, Customizable ML Solutions for Live and Streaming Media," *developers.google.com*, 2025. [Online]. Available: <https://developers.google.com/mediapipe>

[762] Hailo, "Hailo AI Software Suite including Dataflow Compiler," *hailo.ai*, 2025. [Online]. Available: <https://hailo.ai/products/hailo-software/hailo-ai-software-suite/>

[763] Roboflow, "Roboflow: Computer Vision Tools for Developers and Enterprises," *roboflow.com*, 2025. [Online]. Available: <https://roboflow.com/>

[764] Encord, "Encord: Multimodal Data Layer for Physical AI," *encord.com*, 2025. [Online]. Available: <https://encord.com/>

[765] Labelbox, "Labelbox: Data Factory for AI Teams," *labelbox.com*, 2025. [Online]. Available: <https://labelbox.com/>

[766] Voxel51, "FiftyOne: Open-Source Tool for Building High-Quality Datasets and Computer Vision Models," *voxel51.com*, 2025. [Online]. Available: <https://voxel51.com/fiftyone>

[767] CVAT.ai, "CVAT: Computer Vision Annotation Tool," *cvat.ai*, 2025. [Online]. Available: <https://www.cvat.ai/>

[768] Supervisely, "Supervisely: Computer Vision Platform for AI," *supervisely.com*, 2025. [Online]. Available: <https://supervisely.com/>

[769] Cognex, "VisionPro Software: Machine Vision for Industrial Inspection," *cognex.com*, 2025. [Online]. Available: <https://www.cognex.com/en/products/machine-vision-software/visionpro-software>

[770] Keyence, "Machine Vision Systems," *keyence.com*, 2025. [Online]. Available: <https://www.keyence.com/products/vision/>

[771] Landing AI, "LandingLens: Visual Inspection AI Platform," *landing.ai*, 2025. [Online]. Available: <https://landing.ai/>

[772] Hikvision, "Hikvision: Global Leader in Innovative Security Products and Solutions," *hikvision.com*, 2025. [Online]. Available: <https://www.hikvision.com/en/>

[773] Dahua Technology, "Dahua: World Leading Video-Centric AIoT Solution & Service Provider," *dahuasecurity.com*, 2025. [Online]. Available: <https://www.dahuasecurity.com/>

[774] Aidoc, "Aidoc: Clinical AI Solutions for Healthcare Providers," *aidoc.com*, 2025. [Online]. Available: <https://www.aidoc.com/>

[775] Harrison.ai (formerly Annalise.ai), "Annalise.ai: AI-Powered Radiology Solutions," *annalise.ai*, 2025. [Online]. Available: <https://annalise.ai/>

[776] Viz.ai, "Viz.ai: AI-Powered Care Coordination Platform," *viz.ai*, 2025. [Online]. Available: <https://www.viz.ai/>

[777] Standard AI, "Standard AI: AI-Powered Retail Intelligence Platform," *standard.ai*, 2025. [Online]. Available: <https://standard.ai/>

[778] Trigo, "Trigo: Autonomous Retail Technology with Computer Vision," *trigoretail.com*, 2025. [Online]. Available: <https://www.trigoretail.com/>

[779] Yandex, "CatBoost: Fast, Scalable, High Performance Gradient Boosting on Decision Trees," *catboost.ai*, 2025. [Online]. Available: <https://catboost.ai/>

[780] NVIDIA, "RAPIDS cuML: GPU-Accelerated Machine Learning Algorithms," *rapids.ai*, 2025. [Online]. Available: <https://rapids.ai/>

[781] H2O.ai, "H2O: Open-Source Machine Learning Platform," *h2o.ai*, 2025. [Online]. Available: <https://h2o.ai/>

[782] Meta, "Prophet: Forecasting at Scale," *facebook.github.io*, 2024. [Online]. Available: <https://facebook.github.io/prophet/>

[783] NeuralProphet Team, "NeuralProphet: A Simple Forecasting Package," *neuralprophet.com*, 2024. [Online]. Available: <https://neuralprophet.com/>

[784] Nixtla, "Nixtla: Time Series Forecasting and Anomaly Detection Platform," *nixtla.io*, 2025. [Online]. Available: <https://www.nixtla.io/>

[785] Salesforce, "Merlion: A Machine Learning Framework for Time Series Intelligence," *GitHub*, 2024. [Online]. Available: <https://github.com/salesforce/Merlion>

[786] Amazon, "Chronos: Pretrained Models for Time Series Forecasting," *GitHub*, 2024. [Online]. Available: <https://github.com/amazon-science/chronos-forecasting>

[787] QuantConnect, "QuantConnect: Open-Source Algorithmic Trading Platform," *quantconnect.com*, 2025. [Online]. Available: <https://www.quantconnect.com/>

[788] Backtrader, "Backtrader: Python Backtesting Library for Trading Strategies," *backtrader.com*, 2024. [Online]. Available: <https://www.backtrader.com/>

[789] vectorbt, "vectorbt: The Backtesting Engine for Quantitative Finance," *vectorbt.dev*, 2025. [Online]. Available: <https://vectorbt.dev/>

[790] S. Jansen, "Zipline-reloaded: Zipline, a Pythonic Algorithmic Trading Library," *GitHub*, 2024. [Online]. Available: <https://github.com/stefan-jansen/zipline-reloaded>

[791] QuantLib Project, "QuantLib: A Free/Open-Source Library for Quantitative Finance," *quantlib.org*, 2025. [Online]. Available: <https://www.quantlib.org/>

[792] Y. Yang et al., "FinBERT: A Pretrained Language Model for Financial Communications," *GitHub*, arXiv:2006.08097, 2020. [Online]. Available: <https://github.com/yya518/FinBERT>

[793] The FinAI, "PIXIU: A Large Language Model, Instruction Data and Evaluation Benchmark for Finance," *GitHub*, NeurIPS 2023. [Online]. Available: <https://github.com/The-FinAI/PIXIU>

[794] Bloomberg LP, "Bloomberg Terminal: Financial Data and Analytics Platform," *professional.bloomberg.com*, 2025. [Online]. Available: <https://professional.bloomberg.com/products/bloomberg-terminal/>

[795] FactSet, "FactSet Mercury: AI-Powered Financial Research Assistant," *factset.com*, 2025. [Online]. Available: <https://www.factset.com/ai>

[796] Two Sigma, "Venn: Investment Portfolio Analytics Platform," *venn.twosigma.com*, 2025. [Online]. Available: <https://www.venn.twosigma.com/>

[797] AlphaSense, "AlphaSense: AI-Powered Market Intelligence and Search Platform," *alpha-sense.com*, 2025. [Online]. Available: <https://www.alpha-sense.com/>
