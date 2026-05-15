# AI 软件栈分层索引：从设备驱动到终端用户应用

从最底层的设备驱动 / 固件（GPU、NPU、加速卡），一直到最终用户接触的应用，完整一根栈。每层至少列 3 个代表性软件 / 项目 / 厂商；同层多个候选时尽量覆盖闭源前沿、开源主流、新兴挑战者三类。

文件分两大段：

- **A. LLM / Agent 主干（L01–L34）**：当前舆论焦点，从设备驱动到 ChatGPT[[1]](https://chatgpt.com/) / Cursor[[2]](https://cursor.com/) / Devin[[3]](https://devin.ai/) 一根通。
- **B–I. 并列应用分支**：**B** 科学计算 / AI4Science、**C** 机器人、**D** 自动驾驶、**E** 世界模型 / 3D、**F** 经典视觉、**G** 量化金融、**H** 游戏、**I** 影视娱乐——共享 **L01–L09** 的硬件 / 内核 / 框架底座，但从 L10 起走自己的领域模型 + 部署路径。

## L 层 × 分支 总表

横轴 9 列对应 **A 主干 + B–I 8 条并列分支**。纵轴每一行是一个 L 层，每个条目**严格归属**到当行 L，不跨层。规则：

- `同 A`：该层在该分支与主干基本沿用同款（驱动 / 内核 / 编译器 / 实验追踪多数如此）。
- `—`：该层在该分支不存在或可忽略。
- **L35–L38** 是 A 主干没有、但 B–G 必需的新增层；A 列保持空。
  - L35 HPC 作业调度 / 工作流（B 专属：Slurm[[4]](https://slurm.schedmd.com/) / PBS / Spack 这一段在 LLM 训练里被 K8s[[5]](https://kubernetes.io/) + Ray[[6]](https://docs.ray.io/en/latest/index.html) 取代）
  - L36 机器人 / 实时中间件（C / D 共用：ROS 2[[7]](https://www.ros.org/) / DriveWorks / AUTOSAR / Holoscan）
  - L37 物理仿真 / 数字孪生引擎（B / C / D / E 共用：Isaac Sim / MuJoCo[[8]](https://mujoco.org/) / GROMACS[[9]](https://www.gromacs.org/) / CARLA / Omniverse）
  - L38 高精地图 / 定位（D 专属）

| L | A. LLM / Agent | B. 科学计算 | C. 机器人 | D. 自动驾驶 | E. 世界模型 / 3D | F. 经典 CV | G. 量化金融 | H. 游戏 | I. 影视娱乐 |
|---|---|---|---|---|---|---|--- | --- | --- |
| L01 GPU 驱动 / 固件 | NVIDIA / ROCm / Metal / Gaudi driver | 同 A | 同 A | 同 A + NVIDIA DRIVE OS driver | 同 A | 同 A + Hailo / Qualcomm QNN driver | 同 A | 同 A | 同 A |
| L02 互连 / 集合通信 | NVLink[[10]](https://www.nvidia.com/en-us/data-center/nvlink/), NCCL[[11]](https://developer.nvidia.com/nccl), InfiniBand[[12]](https://www.nvidia.com/en-us/networking/products/infiniband/) | 同 A，重 MPI + InfiniBand | NVLink for AGI rig；车端 PCIe | NVLink-C2C 整车 + 仿真集群 IB | 同 A | 边缘多无互连 | 同 A | 同 A（单节点为主） | 同 A（渲染农场用 10–100 GbE / IB） |
| L03 GPU 编程模型 | CUDA[[13]](https://developer.nvidia.com/cuda), ROCm[[14]](https://www.amd.com/en/products/software/rocm.html), Metal[[15]](https://developer.apple.com/metal/), SYCL[[16]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html), DirectML[[17]](https://learn.microsoft.com/en-us/windows/ai/directml/dml) | 同 A + Julia CUDA.jl[[18]](https://github.com/JuliaGPU/CUDA.jl) | 同 A | 同 A | 同 A | 同 A + Apple Metal + DirectML | 同 A + RAPIDS[[19]](https://rapids.ai/) | 同 A + DirectX 12（PC / Xbox）, Metal（Mac / iOS） | 同 A + Metal（Mac DCC） |
| L04 GPU 内核库 | cuBLAS[[20]](https://developer.nvidia.com/cublas), cuDNN[[21]](https://developer.nvidia.com/cudnn), FlashAttention[[22]](https://github.com/dao-ailab/flash-attention), NCCL, CUTLASS[[23]](https://github.com/NVIDIA/cutlass) | cuFFT[[24]](https://developer.nvidia.com/cufft), cuSolver[[25]](https://developer.nvidia.com/cusolver), cuSPARSE[[26]](https://developer.nvidia.com/cusparse), cuQuantum[[27]](https://developer.nvidia.com/cuquantum-sdk), NVSHMEM[[28]](https://developer.nvidia.com/nvshmem) | cuDNN + Isaac CUDA kernels | cuDNN + TensorRT plugins | 3DGS rasterizer, NeRF CUDA kernels | cuDNN + TensorRT INT8 | cuDF, cuML, cuOpt | cuDNN（DLSS / NPC inference）+ DirectML kernels | cuDNN + OptiX denoise kernels |
| L05 编译器 / IR | Triton[[29]](https://github.com/triton-lang/triton), XLA[[30]](https://openxla.org/xla), MLIR[[31]](https://mlir.llvm.org/), TVM[[32]](https://tvm.apache.org/), torch.compile | 同 A + Codon[[33]](https://github.com/exaloop/codon) | 同 A | TensorRT, NVIDIA DLA, TVM | 同 A | TensorRT, OpenVINO, Apple Core ML compiler | 同 A | 同 A + HLSL / shader compilers | 同 A |
| L06 张量 / 训练框架 | PyTorch[[34]](https://pytorch.org/), JAX[[35]](https://github.com/jax-ml/jax), MLX[[36]](https://github.com/ml-explore/mlx), TensorFlow[[37]](https://www.tensorflow.org/) | NumPy[[38]](https://numpy.org/), SciPy[[39]](https://scipy.org/), CuPy[[40]](https://cupy.dev/), JAX, PyTorch, Julia[[41]](https://julialang.org/) | PyTorch + ROS DDS | PyTorch + DriveWorks | PyTorch, JAX, threestudio | PyTorch + OpenMMLab | scikit-learn[[42]](https://scikit-learn.org/), XGBoost[[43]](https://xgboost.readthedocs.io/), LightGBM[[44]](https://github.com/microsoft/LightGBM), PyTorch | PyTorch（NPC AI 训练）+ ONNX | PyTorch（generative VFX） |
| L07 分布式训练 | DeepSpeed[[45]](https://www.deepspeed.ai/), Megatron[[46]](https://github.com/NVIDIA/Megatron-LM), FSDP[[47]](https://docs.pytorch.org/docs/stable/fsdp.html), NeMo[[48]](https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html), Ray Train[[49]](https://docs.ray.io/en/latest/train/train.html) | MPI[[50]](https://www.mpi-forum.org/) + NCCL（HPC 风格而非 ZeRO） | 多在单 / 几卡 | 同 A（仿真 + 路采联训） | 同 A（video diffusion 训练） | 同 A | 多单卡 | 多在单卡 | 多在单卡 |
| L08 训练数据 pipeline | FineWeb[[51]](https://huggingface.co/datasets/HuggingFaceFW/fineweb), datatrove[[52]](https://github.com/huggingface/datatrove), Mosaic Streaming[[53]](https://github.com/mosaicml/streaming) | 实验数据 + 仿真合成 | Open X-Embodiment[[54]](https://robotics-transformer-x.github.io/), DROID[[55]](https://droid-dataset.github.io/), LeRobot[[56]](https://github.com/huggingface/lerobot) dataset | 路采 + 影子模式 + Auto-labeling | 多视角视频 / 3D scan | Roboflow, Encord, Labelbox, FiftyOne | 时间序列 + 因子库 | 游戏 telemetry / 玩家行为日志 | 镜头库 / 母带 / 标注 |
| L09 后训练 / 微调 | TRL[[57]](https://github.com/huggingface/trl), verl[[58]](https://github.com/volcengine/verl), Unsloth[[59]](https://unsloth.ai/), Axolotl[[60]](https://github.com/axolotl-ai-cloud/axolotl) | 极少（预训练即终态） | LeRobot, Diffusion Policy[[61]](https://github.com/real-stanford/diffusion_policy), ACT | RLHF on driving sims | 极少 | YOLO finetune + 蒸馏 | sklearn 训练即生产 | NPC behavior tuning, 反作弊模型微调 | LoRA / Dreambooth 风格化 |
| L10 基础模型权重 | Llama[[62]](https://ai.meta.com/llama/), Claude[[63]](https://www.anthropic.com/claude), GPT[[64]](https://openai.com/api/), Qwen[[65]](https://github.com/QwenLM/Qwen), DeepSeek[[66]](https://www.deepseek.com/en/) | AlphaFold 3[[67]](https://alphafoldserver.com/), GraphCast[[68]](https://deepmind.google/technologies/graphcast/), MatterGen[[69]](https://www.microsoft.com/en-us/research/blog/mattergen-a-new-paradigm-of-materials-design-with-generative-ai/), scGPT[[70]](https://github.com/bowang-lab/scGPT), Evo 2[[71]](https://arcinstitute.org/news/blog/evo2) | GR00T[[72]](https://developer.nvidia.com/isaac/gr00t) N1, π0[[73]](https://www.physicalintelligence.company/) / π0.5, RT-2[[74]](https://robotics-transformer2.github.io/), OpenVLA[[75]](https://openvla.github.io/), RDT-1B[[76]](https://rdt-robotics.github.io/rdt-robotics/) | Tesla FSD[[77]](https://www.tesla.com/support/autopilot) V13/14, Waymo Driver[[78]](https://waymo.com/), Wayve LINGO[[79]](https://wayve.ai/thinking/lingo-natural-language-autonomous-driving/) | Genie 3[[80]](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/), Marble[[81]](https://www.worldlabs.ai/), Cosmos[[82]](https://www.nvidia.com/en-us/ai/cosmos/) | YOLOv11[[83]](https://docs.ultralytics.com/models/yolo11/), SAM 2[[84]](https://ai.meta.com/sam2/), Florence-2[[85]](https://huggingface.co/microsoft/Florence-2-large), RT-DETR[[86]](https://github.com/lyuwenyu/RT-DETR) | BloombergGPT[[87]](https://www.bloomberg.com/company/press/bloomberggpt-50-billion-parameter-llm-tuned-finance/), FinGPT[[88]](https://github.com/AI4Finance-Foundation/FinGPT), TimeGPT[[89]](https://www.nixtla.io/), Chronos[[90]](https://github.com/amazon-science/chronos-forecasting) | NVIDIA ACE[[91]](https://developer.nvidia.com/ace), Inworld[[92]](https://inworld.ai/), Convai[[92]](https://inworld.ai/) NPC LLM | 与 E / L32 共用：Sora, Veo 3, Kling, Runway |
| L11 评测 / 基准 | MMLU[[93]](https://arxiv.org/abs/2009.03300), SWE-bench[[94]](https://www.swebench.com/), MTEB[[95]](https://github.com/embeddings-benchmark/mteb/), METR Time Horizons[[96]](https://metr.org/time-horizons/) | CASP[[97]](https://predictioncenter.org/), WeatherBench[[98]](https://github.com/pangeo-data/WeatherBench), Matbench Discovery[[99]](https://matbench-discovery.materialsproject.org/) | RLBench[[100]](https://github.com/stepjam/RLBench), CALVIN, LIBERO | nuScenes[[101]](https://www.nuscenes.org/), KITTI, Argoverse, CARLA Leaderboard | VBench, 3D-FUTURE | COCO[[102]](https://cocodataset.org/), ImageNet[[103]](https://www.image-net.org/), Open Images | Sharpe / Sortino / IR | NPC dialogue 评估（少公开基准） | 人工评审 + 内部 A/B |
| L12 实验追踪 / MLOps | W&B[[104]](https://wandb.ai/site/), MLflow[[105]](https://mlflow.org/), Neptune[[106]](https://neptune.ai/) | 同 A | 同 A | 同 A + 闭源整车数据平台 | 同 A | 同 A | 同 A | 同 A | 同 A |
| L13 推理引擎 | vLLM[[107]](https://github.com/vllm-project/vllm), TensorRT-LLM[[108]](https://github.com/NVIDIA/TensorRT-LLM), SGLang[[109]](https://github.com/sgl-project/sglang), llama.cpp[[110]](https://github.com/ggerganov/llama.cpp), ONNX Runtime[[111]](https://onnxruntime.ai/) | BioNeMo NIM[[112]](https://www.nvidia.com/en-us/clara/bionemo/) 引擎, Modulus runtime | Isaac ROS[[113]](https://developer.nvidia.com/isaac/ros) GEMs runtime | NVIDIA DRIVE OS[[114]](https://developer.nvidia.com/drive/drive-os), Mobileye EyeQ[[115]](https://www.mobileye.com/technology/eyeq-chip/) runtime, openpilot[[116]](https://github.com/commaai/openpilot) | 3DGS[[117]](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) renderer, Instant-NGP[[118]](https://github.com/NVlabs/instant-ngp) runtime | NVIDIA DeepStream[[119]](https://developer.nvidia.com/deepstream-sdk), Intel OpenVINO[[120]](https://docs.openvino.ai/), Apple Core ML[[121]](https://developer.apple.com/machine-learning/core-ml/), ONNX Runtime + DirectML EP | 通常无独立引擎 | ONNX Runtime + DirectML（游戏内推理）+ NVIDIA TensorRT | 与 L32 共用 diffusion runtime |
| L14 模型服务 / 编排 | Triton Inference[[122]](https://github.com/triton-inference-server/server), Ray Serve[[123]](https://docs.ray.io/en/latest/serve/index.html), BentoML[[124]](https://www.bentoml.com/) | BioNeMo NIM Microservices[[125]](https://www.nvidia.com/en-us/clara/bionemo/), Earth-2 Studio[[126]](https://www.nvidia.com/en-us/high-performance-computing/earth-2/) | Isaac Manipulator, MoveIt 2[[127]](https://moveit.ai/) servers | Tesla inference fleet, Mobileye OTA | NVIDIA Omniverse Kit[[128]](https://developer.nvidia.com/omniverse/kit-sdk) | DeepStream pipeline, VMS 平台 | 自建 Python / QuantConnect cloud | 游戏后端：PlayFab[[129]](https://playfab.com/), GameLift[[130]](https://aws.amazon.com/gamelift/) | 渲染农场 + AI 服务集群 |
| L15 GPU 云 / 算力市场 | CoreWeave[[131]](https://www.coreweave.com/), Lambda[[132]](https://lambda.ai/), Crusoe[[133]](https://www.crusoe.ai/), Nebius[[134]](https://nebius.com/) | Rescale[[135]](https://rescale.com/), AWS HPC[[136]](https://aws.amazon.com/hpc/), Azure CycleCloud[[137]](https://azure.microsoft.com/en-us/products/cyclecloud) | Tesla 自建, Figure GPU farm | Tesla Dojo[[138]](https://www.tesla.com/AI), Mobileye 自建 | RunPod[[139]](https://www.runpod.io/), fal.ai[[140]](https://fal.ai/) | AWS Panorama[[141]](https://aws.amazon.com/panorama/) 边缘 | 通用 AWS / GCP | Tencent / NetEase / Sony 自建 GPU farms | 渲染云：Conductor[[142]](https://www.conductortech.com/), AWS Thinkbox Deadline[[143]](https://aws.amazon.com/thinkbox-deadline/) |
| L16 模型 API 聚合 | OpenRouter[[144]](https://openrouter.ai/), Together[[145]](https://www.together.ai/), Fireworks[[146]](https://fireworks.ai/), Groq[[147]](https://groq.com/) | — | — | — | fal.ai 3D 模型托管 | Replicate[[148]](https://replicate.com/)（YOLO / SAM 托管） | — | — | — |
| L17 前沿模型 API | Anthropic[[149]](https://www.anthropic.com/api), OpenAI[[150]](https://openai.com/api/), Gemini[[151]](https://ai.google.dev/), xAI[[152]](https://x.ai/), DeepSeek | Isomorphic AlphaFold Server, Schrödinger LiveDesign API | Skild Brain API, π API（内部） | — | World Labs Marble API, Decart Mirage | — | Bloomberg API | — | — |
| L18 LLM 应用框架 | LangChain[[153]](https://www.langchain.com/), LlamaIndex[[154]](https://www.llamaindex.ai/), DSPy[[155]](https://github.com/stanfordnlp/dspy), Vercel AI SDK[[156]](https://ai-sdk.dev/) | — | — | — | — | — | — | — | — |
| L19 Embedding / 重排序 | OpenAI text-embedding-3[[157]](https://platform.openai.com/docs/guides/embeddings), Cohere Embed[[158]](https://cohere.com/embed), BGE[[159]](https://github.com/FlagOpen/FlagEmbedding) | ESM-2 / 3（蛋白）, MolE（分子） | — | — | OpenCLIP, SigLIP | CLIP, SigLIP, DINOv2 | FinBERT embedding | — | — |
| L20 向量数据库 / 检索 | Pinecone[[160]](https://www.pinecone.io/), Weaviate[[161]](https://weaviate.io/), Qdrant[[162]](https://qdrant.tech/), Milvus[[163]](https://milvus.io/) | FAISS[[164]](https://github.com/facebookresearch/faiss)（蛋白 / 分子搜索） | — | — | 3D scene 索引（少） | Roboflow Universe[[165]](https://universe.roboflow.com/) | — | — | — |
| L21 长期记忆 | Mem0[[166]](https://mem0.ai/), Zep[[167]](https://www.getzep.com/), Letta[[168]](https://www.letta.com/) | — | （仅 in-context） | — | — | — | — | NPC long-term memory：Charisma[[169]](https://charisma.ai/) | — |
| L22 LLM 网关 / 路由 | LiteLLM[[170]](https://github.com/BerriAI/litellm), Portkey[[171]](https://portkey.ai/), Cloudflare AI Gateway[[172]](https://developers.cloudflare.com/ai-gateway/) | — | — | — | — | — | — | — | — |
| L23 Prompt 管理 / 缓存 | PromptLayer[[173]](https://www.promptlayer.com/), Langfuse[[174]](https://langfuse.com/) Prompts, Braintrust[[175]](https://www.braintrust.dev/) | — | — | — | — | — | — | — | — |
| L24 Agent 框架 | LangGraph[[176]](https://www.langchain.com/langgraph), AutoGen[[177]](https://github.com/microsoft/autogen), Claude Agent SDK[[178]](https://docs.anthropic.com/en/docs/agents-and-tools) | — | VLA 控制循环（**非 Agent 概念**） | 端到端策略（**非 Agent**） | — | — | — | —（NPC 走专用 dialogue 循环，非 Agent） | — |
| L25 工具协议 / MCP | Anthropic MCP[[179]](https://modelcontextprotocol.io/), Composio[[180]](https://composio.dev/), Arcade[[181]](https://www.arcade.dev/) | — | — | — | — | — | — | — | — |
| L26 浏览器 / Computer Use | Browserbase[[182]](https://www.browserbase.com/), Operator[[183]](https://openai.com/index/introducing-operator/), browser-use[[184]](https://github.com/browser-use/browser-use) | — | — | — | — | — | — | — | — |
| L27 代码 / Agent 沙箱 | E2B[[185]](https://e2b.dev/), Modal Sandbox[[186]](https://modal.com/), Daytona[[187]](https://www.daytona.io/) | — | — | — | — | — | — | — | — |
| L28 LLM 观测 / 追踪 | Langfuse, Arize[[188]](https://arize.com/), LangSmith[[189]](https://www.langchain.com/langsmith-platform) | — | Foxglove[[190]](https://foxglove.dev/), Datadog | 自动驾驶闭源遥测平台 | — | Prometheus[[191]](https://prometheus.io/) + Grafana[[192]](https://grafana.com/) | — | Unity Analytics, GameAnalytics[[193]](https://gameanalytics.com/) | ShotGrid[[194]](https://www.autodesk.com/products/flow-production-tracking)（生产管线追踪） |
| L29 Guardrails / 安全 | Guardrails AI[[195]](https://github.com/guardrails-ai/guardrails), NeMo Guardrails[[196]](https://github.com/NVIDIA-NeMo/Guardrails), Lakera[[197]](https://www.lakera.ai/) | — | ISO 13482[[198]](https://www.iso.org/standard/53820.html) 服务机器人安全 | ISO 26262[[199]](https://www.iso.org/standard/68383.html) + 21448 SOTIF + UNECE R157[[200]](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-157-automated-lane-keeping-systems-alks) | — | — | — | 反作弊：BattlEye[[201]](https://www.battleye.com/), Easy Anti-Cheat[[202]](https://www.easy.ac/), VAC[[203]](https://help.steampowered.com/en/faqs/view/571A-97DA-70E9-FF74) | C2PA[[204]](https://c2pa.org/) 内容来源 + watermarking |
| L30 LLM 评测 / 测试 | Promptfoo[[205]](https://www.promptfoo.dev/), DeepEval[[206]](https://github.com/confident-ai/deepeval), Ragas[[207]](https://github.com/explodinggradients/ragas) | — | — | — | — | — | — | — | — |
| L31 语音 (TTS / ASR) | ElevenLabs[[208]](https://elevenlabs.io/), Whisper[[209]](https://github.com/openai/whisper), Cartesia[[210]](https://cartesia.ai/), Deepgram[[211]](https://deepgram.com/) | — | Figure 接 ElevenLabs; NVIDIA Riva[[212]](https://developer.nvidia.com/riva) | Cerence[[213]](https://www.cerence.com/) 车载语音 | — | — | — | 与 A 共用 ElevenLabs / Riva 做 NPC 配音 | ElevenLabs, Descript[[214]](https://www.descript.com/), Adobe Podcast[[215]](https://podcast.adobe.com/) |
| L32 图像 / 视频 / 3D 生成 | Midjourney[[216]](https://www.midjourney.com/), Sora[[217]](https://openai.com/sora/), FLUX[[218]](https://bfl.ai/), Runway[[219]](https://runwayml.com/) | — | — | — | 与 E 段相互渗透 | — | — | MetaHuman[[220]](https://www.unrealengine.com/en-US/metahuman), Reallusion[[221]](https://www.reallusion.com/) | 与 A 共用 + Topaz Video AI[[222]](https://www.topazlabs.com/topaz-video-ai), Wonder Dynamics[[223]](https://wonderdynamics.com/) Wonder Studio |
| L33 通用对话 / 搜索 Agent | ChatGPT, Claude.ai[[224]](https://claude.ai/), Gemini, M365 Copilot[[225]](https://www.microsoft.com/en-us/microsoft-365-copilot), SAP Joule[[226]](https://www.sap.com/products/artificial-intelligence/ai-assistant.html) | — | — | — | — | — | — | — | — |
| L34 垂直 Agent 应用 | Cursor, Devin, Salesforce Agentforce[[227]](https://www.salesforce.com/agentforce/), SAP Joule | AlphaFold Server, Schrödinger LiveDesign client | Tesla Optimus, Figure 02, 1X Neo, Unitree GD01 | Tesla FSD, Waymo One, Mobileye Chauffeur | World Labs Marble app, Genie 3 playground | Hikvision, Cognex, Aidoc, Standard AI | Bloomberg Terminal, FactSet Mercury, AlphaSense, Hebbia | Inworld 集成游戏, Replica Studios[[228]](https://replicastudios.com/), Skybox AI[[229]](https://skybox.blockadelabs.com/) | Cuebric[[230]](https://www.cuebric.com/), Captions[[231]](https://www.captions.ai/), Adobe Firefly Video[[232]](https://firefly.adobe.com/), ILM StageCraft[[233]](https://www.ilm.com/sandbox/stagecraft/) |
| L35 HPC 作业调度 / 工作流 | — | Slurm, PBS[[234]](https://www.altair.com/pbs-professional/), LSF, Spack[[235]](https://spack.io/), EasyBuild | — | — | — | — | — | — | — |
| L36 机器人 / 实时中间件 | — | — | ROS 2, micro-ROS, MoveIt 2, NVIDIA Holoscan[[236]](https://developer.nvidia.com/holoscan-sdk), PX4, QNX | NVIDIA DriveWorks[[237]](https://developer.nvidia.com/drive/driveworks), AUTOSAR[[238]](https://www.autosar.org/) Classic / Adaptive | — | — | — | — | — |
| L37 物理仿真 / 数字孪生引擎 | — | GROMACS, OpenMM[[239]](https://openmm.org/), LAMMPS, NAMD, JAX-CFD, PhiFlow | Isaac Sim[[240]](https://developer.nvidia.com/isaac/sim), MuJoCo, Gazebo, Genesis, Drake, Habitat | NVIDIA DRIVE Sim[[241]](https://developer.nvidia.com/drive/simulation), Applied Intuition, CARLA[[242]](https://carla.org/), AirSim | NVIDIA Omniverse[[243]](https://www.nvidia.com/en-us/omniverse/) + USD, Unity ML-Agents | — | — | Unity ML-Agents（与 E 共用） | V-Ray[[244]](https://www.chaos.com/vray), RenderMan[[245]](https://renderman.pixar.com/), Arnold[[246]](https://arnoldrenderer.com/) 渲染器；Houdini[[247]](https://www.sidefx.com/) 物理 |
| L38 高精地图 / 定位 | — | — | — | HERE[[248]](https://www.here.com/), TomTom[[249]](https://www.tomtom.com/), 四维图新, Mapbox[[250]](https://www.mapbox.com/) | — | — | — | — | — |

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
- Display / Compute Driver[[251]](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html)（`nvidia.ko` 内核模块、GSP 固件、`nvidia-smi`、MIG / vGPU）
- Open GPU Kernel Modules[[252]](https://github.com/NVIDIA/open-gpu-kernel-modules)（2022 起开源的 R515+ 内核侧驱动，仅支持 Turing 及更新架构）
- NVIDIA Container Toolkit[[251]](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html) / `nvidia-container-runtime`（K8s / Docker 接入事实标准）

**AMD**：
- `amdgpu` DRM driver[[253]](https://rocm.docs.amd.com/) + `amdkfd` KFD 计算子系统
- ROCm[[14]](https://www.amd.com/en/products/software/rocm.html) runtime + `rocm-smi`
- AMD GPU Operator[[254]](https://instinct.docs.amd.com/projects/gpu-operator/en/latest/)（K8s 接入）

**Intel**：
- `i915` / `xe` driver[[255]](https://docs.kernel.org/gpu/i915.html)（消费 / 数据中心 Xe / Ponte Vecchio / Falcon Shores）
- `habanalabs`[[256]](https://docs.habana.ai/en/latest/Installation_Guide/Driver_Installation.html) 内核驱动（Habana Gaudi 2 / 3）
- Intel GPU Tools (`igt`)[[255]](https://docs.kernel.org/gpu/i915.html) + `xpu-smi`

**华为昇腾（Ascend）**：
- `davinci_manager`[[257]](https://www.hiascend.com/en/hardware/firmware-drivers/community) + `devmm_svm` + `drv_npu` 内核驱动（Atlas / Ascend 910B / 910C）
- HCCN driver[[257]](https://www.hiascend.com/en/hardware/firmware-drivers/community)（互连专用）
- `npu-smi`[[257]](https://www.hiascend.com/en/hardware/firmware-drivers/community)（对位 `nvidia-smi`）
- Ascend Docker Runtime[[257]](https://www.hiascend.com/en/hardware/firmware-drivers/community)

**Apple**：
- Apple Silicon GPU / ANE driver[[258]](https://developer.apple.com/metal/)（macOS / iOS 内置，与 Metal 紧绑定，闭源）
- AGX / DCP（Display Controller Processor）固件[[258]](https://developer.apple.com/metal/)
- AMX co-processor（M 系列 CPU 内置矩阵单元）通过私有 ABI 暴露给 Accelerate[[259]](https://developer.apple.com/documentation/accelerate)
- `powermetrics` / `sysdiagnose`[[258]](https://developer.apple.com/metal/)（对位 `nvidia-smi` 的功耗 / 利用率读取入口）

**AWS（Annapurna / Trainium 阵营）**：
- Neuron driver[[260]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html)（Trainium / Trainium2 / Inferentia2 的内核驱动 `neuron-driver`）
- Neuron Runtime[[261]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html)（用户态运行时；负责 NEFF 加载、DMA、collective）
- `neuron-ls` / `neuron-top`[[261]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html)（对位 `nvidia-smi`）
- AWS Neuron Container Toolkit[[260]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html)（EKS / ECS 接入）

**高通（Qualcomm）**：
- Adreno GPU driver[[873]](https://developer.qualcomm.com/software/adreno-gpu-sdk)（Android / Windows on Snapdragon，KGSL 内核侧 + 用户态 OpenCL / Vulkan / OpenGL ES）
- Hexagon DSP / NPU driver（FastRPC + ADSP/CDSP/NSP 固件，SoC 内置 Hexagon Tensor Processor）
- Qualcomm Cloud AI 100[[872]](https://www.qualcomm.com/products/technology/processors/cloud-artificial-intelligence/cloud-ai-100) PCIe driver（QAic 数据中心推理卡的内核驱动 + Platform SDK）
- Snapdragon Ride[[753]](https://www.qualcomm.com/automotive/solutions/snapdragon-ride) Vision SDK driver stack（车载 SA8775P / SA8295P）

**联发科（MediaTek）**：
- Mali GPU / Imagination GPU driver（Dimensity / Genio / Kompanio SoC 多用 Arm Mali，少数用 Imagination IMG）
- MediaTek APU (AI Processing Unit) driver[[874]](https://neuropilot.mediatek.com/)（NeuroPilot driver + APU firmware，Android Neural Networks HAL 后端）
- Dimensity Auto[[875]](https://www.mediatek.com/products/automotive) 平台驱动（车机 MT2731 / Dimensity Auto Cockpit）

**瑞芯微（Rockchip）**：
- Mali GPU driver（RK3588 / RK3576 / RK3568 多用 Arm Mali-G610 / G52，社区 Panfrost 替代驱动渐熟）
- RKNPU driver[[879]](https://github.com/rockchip-linux/rknpu2)（`rknpu_ko` 内核模块；RK3588 6 TOPS、RK3576 6 TOPS、RV1106 / RV1109 边缘视觉子系列）
- RKNN Runtime[[879]](https://github.com/rockchip-linux/rknpu2)（用户态 `librknnrt.so`，对位 NVIDIA `libnvidia-ml` + TensorRT runtime）

## L02 GPU 互连 / 集合通信

多卡 / 多机之间的物理与协议层；性能瓶颈往往不在 FLOPS 而在这层。

**节点内互连（芯片 ↔ 芯片）**：
- NVIDIA：NVLink[[10]](https://www.nvidia.com/en-us/data-center/nvlink/) / NVSwitch（H100 900 GB/s、B200 1.8 TB/s、GB200 NVL72 全互连域）
- AMD：Infinity Fabric / xGMI[[262]](https://www.amd.com/en/technologies/infinity-architecture)（MI300X 7 路全互连）
- Intel：Xe Link[[263]](https://www.intel.com/content/www/us/en/products/docs/processors/max-series/overview.html)（Ponte Vecchio）
- 华为：HCCS[[264]](https://www.hiascend.com/en/hardware/cluster)（HyperLink；Ascend 910B 内 8 卡 fullmesh，节点内 392 GB/s）
- Apple：UltraFusion[[265]](https://www.apple.com/newsroom/2022/03/apple-unveils-m1-ultra-the-worlds-most-powerful-chip-for-a-personal-computer/)（M Ultra 把两颗 M Max 缝合为单一逻辑芯片，2.5 TB/s）；M 系列内部 fabric 闭源
- AWS：NeuronLink-v3[[266]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)（Trainium2 内 16 芯片 fullmesh）+ Trn2 UltraServer 64 芯片域

**节点间网络**：
- NVIDIA / Mellanox Quantum-2[[267]](https://www.nvidia.com/en-us/networking/quantum2/) / Quantum-X800 InfiniBand + OFED
- AWS EFA[[268]](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html)（Elastic Fabric Adapter）+ SRD 协议（EFA v2 / v3，Trn2 UltraServer 用 EFAv3）
- Ultra Ethernet[[269]](https://ultraethernet.org/)（UEC 1.0，2024）；RoCE v2
- UALink[[270]](https://ualinkconsortium.org/) 1.0（AMD / Intel / Google / Meta 联盟，对位 NVLink 跨节点版）
- 华为：200 GE RoCE（CloudEngine 8800 / 16800 系列；Atlas 900[[271]](https://www.hiascend.com/en/hardware/cluster) 集群）
- Apple：无（Apple 不卖训练集群，节点间网络不在产品线内）

**集合通信库（NCCL 对应面）**：
- NVIDIA NCCL[[11]](https://developer.nvidia.com/nccl)
- AMD RCCL[[272]](https://github.com/ROCm/rccl)（NCCL API 兼容 fork）
- Intel oneCCL[[273]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/oneccl.html)
- 华为 HCCL[[274]](https://www.hiascend.com/cann/hccl)（Huawei Collective Communication Library）
- Apple：MLX[[36]](https://github.com/ml-explore/mlx) Distributed `mlx.distributed`（基于 MPI 或 ring；规模偏研究）
- AWS：Neuron Collective Communication[[275]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/about/collectives.html)（NCCL-style API，跑在 NeuronLink + EFA 上）
- 微软 MSCCL[[276]](https://github.com/microsoft/mscclpp) / MSCCL++（在 NCCL 之上的可编程调度层）

## L03 GPU 编程模型 / 计算 API

让开发者写并行 kernel；下层各家硬件的统一抽象。

**厂商专有 GPU / 加速器计算栈**：
- NVIDIA：CUDA[[13]](https://developer.nvidia.com/cuda)（`nvcc` 编译器、PTX 中间码、CUDA Runtime / Driver API、NVRTC、CUDA Graphs）
- AMD：ROCm / HIP[[277]](https://rocm.docs.amd.com/projects/HIP/en/latest/)（HIP 提供 CUDA 源码级近似兼容，`hipify` 自动迁移）+ HIPCC
- Intel：oneAPI / SYCL / DPC++[[278]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html)（`icpx`）；Habana SynapseAI[[279]](https://docs.habana.ai/en/latest/Gaudi_Overview/Intel_Gaudi_Software_Suite.html)（Gaudi 专用，Python + C++ 接口）
- 华为：CANN[[280]](https://www.hiascend.com/en/cann)（Compute Architecture for Neural Networks）+ AscendC[[281]](https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html)L[[282]](https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/)（runtime C API，对位 CUDA Runtime）+ AscendC（C++ kernel DSL，对位 CUDA C++）
- Apple：Metal[[15]](https://developer.apple.com/metal/) + Metal Performance Shaders（MPS）+ Metal Shading Language（MSL）+ MetalFX；ANE（Apple Neural Engine）通过 Core ML / BNNS 间接暴露，无公开 kernel-level API
- AWS：AWS Neuron SDK[[283]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html) + NKI[[284]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/)（Neuron Kernel Interface，Python DSL，对位 CUDA C++ + Triton）+ Neuron PyTorch / JAX 适配层
- Microsoft（Windows-only 跨厂商加速线）：DirectX 12 / Direct3D 12 Compute[[285]](https://learn.microsoft.com/en-us/windows/win32/direct3d12/direct3d-12-graphics) + HLSL（着色器与计算 kernel 写法）+ DirectML[[286]](https://learn.microsoft.com/en-us/windows/ai/directml/dml)（基于 D3D12 的硬件无关 ML 计算 API，NVIDIA / AMD / Intel / Qualcomm Windows 端通吃）+ DirectStorage[[287]](https://devblogs.microsoft.com/directx/directstorage-api-available-on-pc/)（高速 IO，GPU 直读）
- 高通（Qualcomm）：Qualcomm AI Engine Direct (QNN)[[793]](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk)（Hexagon NPU + Adreno GPU + Kryo CPU 统一编程接口，C / C++ + Python 适配）+ Hexagon SDK[[868]](https://developer.qualcomm.com/software/hexagon-dsp-sdk)（HVX 向量 / HMX 矩阵指令、scalar / vector / tensor 三种 kernel 写法）+ SNPE[[869]](https://www.qualcomm.com/developer/software/neural-processing-sdk-for-ai)（Snapdragon Neural Processing Engine，传统 model-loading runtime）+ Adreno SDK[[873]](https://developer.qualcomm.com/software/adreno-gpu-sdk)（OpenCL / Vulkan / OpenGL ES）
- 联发科（MediaTek）：NeuroPilot SDK[[874]](https://neuropilot.mediatek.com/)（统一 APU / GPU / DSP / CPU 编程接口，对位 QNN；含 NeuroPilot Compiler、NeuroPilot Runtime、NN-Tools）+ Android NNAPI 后端 + ArmNN / TFLite delegate
- 瑞芯微（Rockchip）：RKNN-Toolkit2[[878]](https://github.com/airockchip/rknn-toolkit2)（Python 模型转换 + 量化 + 仿真，对位 TensorRT 前端）+ RKNN C/C++ API（用户态 kernel 调度）+ RKNPU2 runtime[[879]](https://github.com/rockchip-linux/rknpu2)（设备侧执行器）

**跨厂商 / 便携后端**：
- OpenCL 3.0[[288]](https://www.khronos.org/opencl/)（跨厂商，地位下滑但仍在嵌入式 / Android）
- Vulkan Compute[[289]](https://www.khronos.org/vulkan/)（图形 + 计算合一；llama.cpp 用作便携后端）
- WebGPU[[290]](https://www.w3.org/TR/webgpu/) / wgpu（浏览器内 GPU 计算；Chrome 113 起默认开启）
- Codeplay oneAPI for CUDA[[13]](https://developer.nvidia.com/cuda) / for ROCm（SYCL 跨硬件适配层）

## L04 GPU 内核库（DNN / BLAS / 通信 / Attention）

预编译好的高性能算子，框架直接调用。四大硬件厂商各自一套，再叠加跨厂商的 Attention / fused kernel。

**GEMM / BLAS**：
- NVIDIA：cuBLAS[[20]](https://developer.nvidia.com/cublas) / cuBLASLt
- AMD：rocBLAS[[291]](https://rocm.docs.amd.com/projects/rocBLAS/en/latest/) / hipBLASLt
- Intel：oneMKL[[292]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html)（含 BLAS / LAPACK / FFT / Sparse）
- 华为：CANN AOL[[293]](https://www.hiascend.com/en/cann)（Ascend Operator Library；含 BLAS / Vector kernels）
- Apple：Accelerate / vecLib BLAS[[259]](https://developer.apple.com/documentation/accelerate) + AMX 内置加速；Metal Performance Shaders MPSMatrixMultiplication[[294]](https://developer.apple.com/documentation/metalperformanceshaders)
- AWS：Neuron BLAS kernels（Trainium / Inferentia2[[295]](https://aws.amazon.com/ai/machine-learning/inferentia/) 上的 matmul / GEMM 算子）

**深度学习 primitive（卷积 / RNN / Attention / Norm）**：
- NVIDIA：cuDNN[[21]](https://developer.nvidia.com/cudnn)
- AMD：MIOpen[[296]](https://rocm.docs.amd.com/projects/MIOpen/en/latest/)
- Intel：oneDNN[[297]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onednn.html)（原 MKL-DNN / DNNL）
- 华为：CANN ACLNN[[298]](https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/)（Ascend Neural Network Operator Library）
- Apple：BNNS / BNNSGraph[[299]](https://developer.apple.com/documentation/accelerate/bnns)（Accelerate 内 Basic Neural Network Subroutines）+ MPS Graph + Core ML kernel library
- AWS：Neuron Custom Operators 库 + AWS Neuron[[283]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html) `libnrt` 算子集
- 高通：QNN op packages（HTP / GPU / DSP backend 各自一套预编译算子集）+ Hexagon NN library（HVX / HMX fused conv / matmul / attention）+ AIMET[[871]](https://github.com/quic/aimet) 量化感知 op set
- 联发科：NeuroPilot SDK 内置 APU op library + TFLite GPU delegate（Mali / Imagination）
- 瑞芯微：RKNN op set（卷积 / Transformer / Attention 已支持 Llama / Qwen / Whisper / YOLO 主流结构）+ MatMul / Softmax INT4 / INT8 fused kernels（RK3588 / RK3576 NPU 上）

**GEMM 模板 / kernel 编写库**：
- NVIDIA：CUTLASS（FlashAttention[[22]](https://github.com/dao-ailab/flash-attention) / vLLM 大量复用）
- AMD：Composable Kernel[[300]](https://github.com/ROCm/composable_kernel) (CK)
- Intel：XeTLA[[301]](https://github.com/intel/xetla)、TileLang
- 华为：AscendC[[281]](https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html) kernel 套件（含 TBE / Tensor Boost Engine 老接口）
- Apple：MLX kernel DSL（C++ + Metal 后端，对位 CUTLASS[[23]](https://github.com/NVIDIA/cutlass) 但远更轻量）
- AWS：NKI[[284]](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/)（Neuron Kernel Interface，Trainium 上写 fused kernel 的 Python DSL）

**集合通信**：
- NVIDIA NCCL / AMD RCCL / Intel oneCCL / 华为 HCCL / Apple MLX Distributed[[302]](https://ml-explore.github.io/mlx/build/html/usage/distributed.html) / AWS Neuron Collective Communication（见 L02 集合通信库一节）

**FFT / Sparse / Solver / 量子**：
- NVIDIA：cuFFT、cuSPARSE、cuSolver、cuQuantum[[27]](https://developer.nvidia.com/cuquantum-sdk)、NVSHMEM
- AMD：rocFFT[[303]](https://rocm.docs.amd.com/projects/rocFFT/en/latest/)、rocSPARSE、rocSOLVER
- Intel：oneMKL[[292]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html) DFT / Sparse / Solver
- 华为：CANN AOL[[293]](https://www.hiascend.com/en/cann) 内置 FFT / Sparse / Solver 子集
- Apple：Accelerate vDSP（FFT / DSP）+ Sparse Solvers + LAPACK；Metal[[15]](https://developer.apple.com/metal/) Performance Shaders MPSMatrixDecomposition
- AWS：通过 Neuron 调用上层 JAX / PyTorch[[34]](https://pytorch.org/) 走 XLA → Neuron Compiler；专用 FFT / Solver 库未独立公开

**跨厂商 / 高层 attention 与 fused kernel**：
- FlashAttention[[22]](https://github.com/dao-ailab/flash-attention) 1 / 2 / 3（Tri Dao；FA3 针对 Hopper Tensor Core + TMA；AMD 有 `flash-attention` ROCm fork；Intel Habana 自研 FusedSDPA）
- xFormers[[304]](https://github.com/facebookresearch/xformers)（Meta；memory-efficient attention 集合）
- Triton[[29]](https://github.com/triton-lang/triton) kernels（OpenAI；社区贡献的 fused MoE / RMSNorm / SwiGLU；AMD Triton 与 Intel Triton 在各自硬件上接后端）
- MSCCL / MSCCL++（微软在 NCCL[[11]](https://developer.nvidia.com/nccl) 之上的可编程调度层）

## L05 编译器 / IR

把模型图或 Python 代码编译成 GPU 可执行体；过去十年从单一图编译器演化为多层 IR + JIT 混合。

**厂商专有图编译器 / 设备编译器**：
- NVIDIA：NVCC[[305]](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/) + NVRTC + PTX → SASS（ptxas）
- AMD：HIPCC[[306]](https://github.com/ROCm/HIPCC) + LLVM AMDGPU backend；ROCm Compute Profile (RCP)
- Intel：oneAPI DPC++ compiler[[307]](https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html)（`icpx`）；Habana SynapseAI Graph Compiler[[308]](https://docs.habana.ai/en/latest/Gaudi_Overview/SynapseAI_Software_Suite.html)
- 华为：CANN Graph Engine[[309]](https://www.hiascend.com/en/cann)（GE）+ TBE / AscendC 算子编译器；MindSpore Graph Engine[[310]](https://github.com/mindspore-ai/mindspore)（MindSpore IR / MindIR）
- Apple：Metal Compiler[[311]](https://developer.apple.com/documentation/metal/metal-libraries)（`metal` + `metallib`）+ Core ML Compiler[[312]](https://developer.apple.com/documentation/coreml)（`coremlcompiler`，把 `.mlmodel` / `.mlpackage` 编成 ANE / GPU / CPU 多目标 program）+ MLX JIT[[313]](https://github.com/ml-explore/mlx)
- AWS：Neuron Compiler[[314]](https://awsdocs-neuron.readthedocs-hosted.com/)（接 PyTorch / JAX / XLA HLO → NEFF 二进制格式）+ XLA-Neuron 后端
- 高通：QNN Converter / QNN Model Compiler（ONNX / TFLite / PyTorch → QNN context binary `.bin`，可分派到 HTP / GPU / CPU）+ Hexagon LLVM toolchain（`hexagon-clang`，HVX / HMX 自动向量化）+ AI Hub[[870]](https://aihub.qualcomm.com/) 云端模型编译流水线（用户上传 PyTorch / ONNX，平台自动编译并跑真机 benchmark）
- 联发科：NeuroPilot Compiler[[874]](https://neuropilot.mediatek.com/)（DLA / TFLite → APU 可执行格式）+ MDLA backend（MediaTek Deep Learning Accelerator IR）
- 瑞芯微：RKNN-Toolkit2 Converter[[878]](https://github.com/airockchip/rknn-toolkit2)（ONNX / PyTorch / TensorFlow / Caffe → `.rknn` 模型；含 PTQ 量化、混合精度、graph fusion；事实上的国产边缘转换器主流）

**跨厂商 / 上层 IR 与 JIT**：
- OpenAI Triton[[315]](https://github.com/triton-lang/triton)（Python 嵌入式 DSL，事实上的 GPU kernel 写法新标准；NVIDIA / AMD / Intel 各自维护后端）
- PyTorch torch.compile[[316]](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) / TorchInductor + TorchDynamo（PT 2.x 默认编译路径，下接 Triton / C++ / Halide）
- XLA / OpenXLA[[317]](https://github.com/openxla/xla)（JAX 与 TF 默认；Google + AWS + NVIDIA + Meta + Intel + AMD 共治）
- MLIR[[31]](https://mlir.llvm.org/)（LLVM 项目；TPU、IREE、Mojo、torch-mlir、CANN 共享的中间表示）
- TVM / Apache TVM[[318]](https://github.com/apache/tvm) + Unity（陈天奇主导的端到端深度学习编译栈；MLC-LLM 后端）
- IREE[[319]](https://github.com/iree-org/iree)（Google；MLIR-based，定位移动 / 边缘）
- Mojo / MAX[[320]](https://www.modular.com/open-source/mojo)（Modular；Chris Lattner，Python 超集 + MLIR 后端）

## L06 张量 / 训练框架

定义计算图、autograd、optimizer；用户写 `nn.Module` 的那一层。

- **PyTorch[[34]](https://pytorch.org/)**（Meta；2025 LLM 训练事实标准，份额 >70%）
- **JAX + Flax[[321]](https://github.com/google/flax) / NNX / Equinox**（Google；Gemini / Anthropic 训练栈核心）
- **TensorFlow + Keras 3[[322]](https://github.com/keras-team/keras)**（Google；Keras 3 后端可切 JAX / PyTorch / TF）
- **MLX[[36]](https://github.com/ml-explore/mlx)**（Apple；Apple Silicon 原生）
- **MindSpore[[323]](https://github.com/mindspore-ai/mindspore)**（华为）
- **PaddlePaddle[[324]](https://github.com/PaddlePaddle/Paddle)**（百度）
- **tinygrad[[325]](https://github.com/tinygrad/tinygrad)**（George Hotz；研究 / 教学）

## L07 分布式训练框架

把模型与数据切到上千 / 上万卡上，并管 checkpoint / 容错 / 恢复。

- **DeepSpeed[[45]](https://www.deepspeed.ai/)**（Microsoft；ZeRO-1/2/3、ZeRO-Infinity、MoE）
- **Megatron[[46]](https://github.com/NVIDIA/Megatron-LM)-LM / Megatron-Core**（NVIDIA；3D 并行：TP / PP / DP）
- **PyTorch[[34]](https://pytorch.org/) FSDP / FSDP2**（PyTorch 官方；FSDP2 2024 GA）
- **NVIDIA NeMo[[326]](https://github.com/NVIDIA/NeMo)**（Megatron-Core 上的端到端训练 + 数据 + 评测套件）
- **Colossal-AI[[327]](https://github.com/hpcaitech/ColossalAI)**（HPC-AI Tech）
- **Ray Train[[49]](https://docs.ray.io/en/latest/train/train.html)**（Anyscale；调度层在 Ray 上）
- **MosaicML Composer[[328]](https://github.com/mosaicml/composer) / LLM Foundry[[329]](https://github.com/mosaicml/llm-foundry)**（被 Databricks 收购）
- **TorchTitan[[330]](https://github.com/pytorch/torchtitan)**（PyTorch 官方 2024 推出的 LLM 训练参考实现）
- **厂商专有训练栈**：AMD ROCm Megatron-LM fork + ROCm DeepSpeed；Intel Habana Gaudi 上的 Optimum-Habana + DeepSpeed-Habana 集成；华为 MindFormers[[331]](https://github.com/mindspore-lab/mindformers) / MindSpore Distributed（基于 MindSpore 的大模型并行套件，对位 Megatron + DeepSpeed）+ ModelLink[[332]](https://gitee.com/ascend/ModelLink)（昇腾 PyTorch 适配大模型训练套件）；Apple MLX Distributed[[302]](https://ml-explore.github.io/mlx/build/html/usage/distributed.html)（`mlx.distributed`，定位研究 / 小集群）；AWS Neuron Distributed Training + SageMaker HyperPod[[333]](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html)（Trainium2 + EFAv3，支持 FSDP / 张量并行）

## L08 训练数据 pipeline

数据集构建、清洗、去重、tokenize、streaming。这一层 2023 后被独立看待。

- **datatrove[[52]](https://github.com/huggingface/datatrove)**（HuggingFace；FineWeb 的生产工具）
- **MosaicML Streaming**[[53]](https://github.com/mosaicml/streaming)（云对象存储到训练机的流式 dataset）
- **WebDataset[[334]](https://github.com/webdataset/webdataset)**（POSIX tar 流，PyTorch 生态早期事实标准）
- **Nemo Curator[[335]](https://github.com/NVIDIA-NeMo/Curator)**（NVIDIA；GPU 加速去重 / 分类）
- **Dolma toolkit[[336]](https://github.com/allenai/dolma)**（AI2；OLMo 数据集工具）
- **llm-foundry**[[329]](https://github.com/mosaicml/llm-foundry)（Mosaic / Databricks）
- **数据集本体**：FineWeb / FineWeb-Edu（HF）、RedPajama-V2[[337]](https://github.com/togethercomputer/RedPajama-Data)（Together）、Dolma[[338]](https://huggingface.co/datasets/allenai/dolma)（AI2）、The Stack v2[[339]](https://huggingface.co/datasets/bigcode/the-stack-v2)（BigCode）、Common Crawl[[340]](https://commoncrawl.org/)

## L09 后训练 / 微调框架

SFT、RLHF / DPO / IPO / GRPO / RLVR、reward modeling、合成数据。这一层 2024-2025 爆发。

- **TRL[[57]](https://github.com/huggingface/trl)**（HuggingFace；SFT / DPO / GRPO / PPO trainer，事实标准）
- **Unsloth[[59]](https://unsloth.ai/)**（QLoRA 极致优化，单卡微调首选）
- **Axolotl[[60]](https://github.com/axolotl-ai-cloud/axolotl)**（OpenAccess AI Collective；config-driven 微调）
- **LLaMA-Factory[[341]](https://github.com/hiyouga/LLaMA-Factory)**（北航；中文社区主流）
- **OpenRLHF[[342]](https://github.com/OpenRLHF/OpenRLHF)**（OpenLLMAI；分布式 RLHF，Ray 调度）
- **verl**（字节；HybridFlow，veRL，DeepSeek[[66]](https://www.deepseek.com/en/)-R1 风格 RLVR）
- **NeMo-Aligner[[343]](https://github.com/NVIDIA/NeMo-Aligner)**（NVIDIA）

## L10 基础模型权重

可下载（开源 / 开放权重）或可 API 调用的模型本体。这一层 2025 已分裂为开放权重与闭源前沿两轨。

- **开放权重 / 开源**：Llama 3 / 4（Meta）、Qwen 3（阿里）、DeepSeek-V3 / R1、Mistral / Mixtral[[344]](https://mistral.ai/)、Gemma 3[[345]](https://ai.google.dev/gemma)（Google）、Kimi K2[[346]](https://github.com/MoonshotAI/Kimi-K2)（Moonshot）、GLM-4.6[[347]](https://github.com/THUDM/GLM-4)（智谱）、Phi-4[[348]](https://huggingface.co/microsoft/phi-4)（Microsoft）、OLMo 2[[349]](https://github.com/allenai/OLMo)（AI2，真·全开源）
- **闭源前沿**：GPT-5 / GPT-5.1（OpenAI）、Claude[[63]](https://www.anthropic.com/claude) Opus / Sonnet / Haiku 4.x（Anthropic）、Gemini 2.5 / 3（Google DeepMind）、Grok 4（xAI）
- **模型枢纽 / 发现**：HuggingFace Hub[[350]](https://huggingface.co/)、ModelScope[[351]](https://github.com/modelscope/modelscope)（阿里）、Replicate models、Ollama Library[[352]](https://ollama.com/library)、Civitai[[353]](https://civitai.com/models)（图像 / Stable Diffusion 衍生）

## L11 评测 / 基准

公开打分系统；越来越多被用作 RL reward 的代理。

- **lm-evaluation-harness[[354]](https://github.com/EleutherAI/lm-evaluation-harness)**（EleutherAI；HF Open LLM Leaderboard 后端）
- **HELM[[355]](https://github.com/stanford-crfm/helm)**（Stanford CRFM）
- **OpenCompass[[356]](https://github.com/open-compass/opencompass)**（上海 AI Lab）
- **任务类**：MMLU / MMLU-Pro、GSM8K[[357]](https://arxiv.org/abs/2110.14168) / MATH、HumanEval[[358]](https://arxiv.org/abs/2107.03374) / MBPP、SWE-bench / SWE-bench Verified、GPQA[[359]](https://arxiv.org/abs/2311.12022)、ARC-AGI[[360]](https://arcprize.org/arc-agi)、HLE[[361]](https://github.com/centerforaisafety/hle)（Humanity's Last Exam）
- **Agent / 长 horizon**：METR Time Horizons、TAU-bench[[362]](https://github.com/sierra-research/tau-bench)、WebArena[[363]](https://github.com/web-arena-x/webarena)、OSWorld[[364]](https://github.com/xlang-ai/OSWorld)、AgentBench[[365]](https://github.com/THUDM/AgentBench)
- **Embedding / 检索**：MTEB、BEIR[[366]](https://github.com/beir-cellar/beir)
- **对战 / 人类偏好**：LMSYS Chatbot Arena[[367]](https://lmarena.ai/)、SEAL[[368]](https://scale.com/leaderboard)（Scale）
- **代码定制平台**：Inspect AI[[369]](https://github.com/UKGovernmentBEIS/inspect_ai)（UK AISI）、OpenAI Evals[[370]](https://github.com/openai/evals)、DeepEval（参 L30）

## L12 实验追踪 / MLOps

run、metric、artifact、sweep、模型 registry。

- **Weights & Biases (W&B[[104]](https://wandb.ai/site/))**
- **MLflow[[105]](https://mlflow.org/)**（Databricks 开源）
- **Neptune[[106]](https://neptune.ai/).ai**
- **ClearML[[371]](https://clear.ml/)**
- **Comet ML[[372]](https://www.comet.com/site/)**
- **TensorBoard[[373]](https://github.com/tensorflow/tensorboard)**（仍是免费默认）
- **DVC[[374]](https://dvc.org/) / DVC Studio**（Iterative；偏数据版本）

## L13 推理引擎

负责 KV cache、continuous batching、speculative decoding、量化、PagedAttention 等推理侧硬核优化。

**跨厂商 / 通用**：
- vLLM（UC Berkeley → 公司化；PagedAttention 发起者，开源吞吐量基准；CUDA[[13]](https://developer.nvidia.com/cuda) 主线 + ROCm / Intel / Ascend 后端）
- SGLang[[109]](https://github.com/sgl-project/sglang)（LMSYS / xAI；RadixAttention，结构化输出强）
- HuggingFace TGI[[375]](https://github.com/huggingface/text-generation-inference)（Text Generation Inference）
- llama.cpp / GGUF[[376]](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)（Georgi Gerganov；CPU / Apple Silicon / CUDA / ROCm / Vulkan / SYCL 任意后端）
- MLC-LLM[[377]](https://github.com/mlc-ai/mlc-llm)（陈天奇团队；TVM Unity 后端，Web / 移动 / 任意硬件）
- DeepSpeed-FastGen / DeepSpeed-MII[[378]](https://github.com/deepspeedai/DeepSpeed-MII)
- LMDeploy[[379]](https://github.com/InternLM/lmdeploy)（上海 AI Lab；InternLM 配套，NVIDIA + Ascend 双后端）
- Ollama[[380]](https://ollama.com/)（llama.cpp 之上的本地一键运行）

**厂商专有推理栈**：
- NVIDIA：TensorRT-LLM（CUDA[[13]](https://developer.nvidia.com/cuda) Graph + FP8 / FP4，Hopper / Blackwell 专属优化）+ TensorRT 通用
- AMD：AITER[[381]](https://github.com/ROCm/aiter)（AMD Inference Throughput Engine for ROCm）+ vLLM-ROCm 官方分支 + Composable Kernel attention
- Intel：OpenVINO[[382]](https://github.com/openvinotoolkit/openvino)（Xe / Habana / CPU 通吃）+ IPEX-LLM[[383]](https://github.com/intel/ipex-llm)（Intel Extension for PyTorch LLM 分支，原 BigDL-LLM）+ Habana TGI / vLLM-fork
- 华为：MindIE[[384]](https://www.hiascend.com/en/developer/software/mindie)（Mind Inference Engine，对位 TensorRT-LLM）+ MindSpore Lite[[385]](https://www.mindspore.cn/lite/en)（端边一体）+ Ascend vLLM 适配层
- Apple：Core ML（端侧默认推理路径，自动分派 ANE / GPU / CPU）+ MLX（M 系列 GPU 上的 PyTorch-like 框架，含 mlx-lm）+ MPSGraph[[386]](https://developer.apple.com/documentation/metalperformanceshadersgraph) + llama.cpp Metal 后端
- AWS：AWS Neuron + Transformers-Neuronx[[387]](https://aws.amazon.com/ai/machine-learning/neuron/)（Trainium / Inferentia2 上 LLM 推理库）+ vLLM Neuron 后端 + DJLServing[[388]](https://github.com/deepjavalibrary/djl-serving) Neuron
- 高通（端侧 / 数据中心两线）：Qualcomm AI Engine Direct (QNN)[[793]](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk) runtime（手机 / Copilot+ PC / 车机）+ Qualcomm Genie[[882]](https://www.qualcomm.com/developer/software/genie-sdk)（On-Device 生成式 AI SDK，2024-10 发布；Llama 3 / Phi-3 在 Snapdragon 8 Gen 3 / 8 Elite 上跑 20+ tokens/s）+ AI Hub Models（Qualcomm 维护 100+ 优化模型）+ Cloud AI 100[[872]](https://www.qualcomm.com/products/technology/processors/cloud-artificial-intelligence/cloud-ai-100) Apps SDK（数据中心 PCIe 卡，vLLM 后端）；llama.cpp + MLC-LLM 通过 QNN backend 接入
- 联发科：NeuroPilot SDK runtime[[874]](https://neuropilot.mediatek.com/) + Dimensity 9400 / 9500 上的端侧 LLM 推理（Llama 3 8B 4-bit @ 20+ tokens/s）+ Genio Model Library[[876]](https://www.mediatek.com/products/iot)（IoT / Edge AI）+ Kompanio[[877]](https://www.mediatek.com/products/chromebooks-tablets) ChromeOS ML stack；llama.cpp + MLC-LLM 也支持 Mali GPU OpenCL / Vulkan 后端
- 瑞芯微：RKNN Runtime[[879]](https://github.com/rockchip-linux/rknpu2)（C / Python API；RK3588[[881]](https://www.rock-chips.com/a/en/products/RK35_Series/2022/0926/1660.html) 6 TOPS、RK3576 6 TOPS、RV1106 0.5 TOPS）+ **RKLLM**[[880]](https://github.com/airockchip/rknn-llm)（瑞芯微大模型推理框架，对位 llama.cpp；支持 Llama 3、Qwen 2.5、ChatGLM、MiniCPM、Phi-3、InternLM 等，在 RK3588 上跑 Qwen 2.5 7B INT4 @ 4-5 tokens/s）+ MLC-LLM + llama.cpp Mali GPU 路径
- Microsoft（Windows / Azure 端推理栈）：ONNX Runtime[[389]](https://onnxruntime.ai/)（跨平台事实标准，含 CUDA / TensorRT / DirectML / CoreML / OpenVINO / WebGPU 多 EP）+ DirectML EP for ONNX Runtime[[286]](https://learn.microsoft.com/en-us/windows/ai/directml/dml)（Windows 端 GPU 厂商无关推理）+ Windows ML[[390]](https://learn.microsoft.com/en-us/windows/ai/windows-ml/overview)（Windows 11 内置 ML 推理 API，Copilot+ PC 上分派至 NPU / GPU / CPU）+ Olive[[391]](https://github.com/microsoft/Olive)（端到端模型优化工具链：量化 + 图优化 + EP 适配）+ DeepSpeed-Inference

## L14 模型服务 / 编排（GPU orchestration）

把推理引擎封装成 service：自动伸缩、多模型、A/B、批处理。

**跨厂商 / 通用**：
- Ray Serve[[123]](https://docs.ray.io/en/latest/serve/index.html)（Anyscale）
- KServe[[392]](https://github.com/kserve/kserve)（K8s 原生，原 KFServing）
- BentoML[[124]](https://www.bentoml.com/) / Yatai
- Modal（serverless GPU[[393]](https://lammps.org/) 函数）
- Beam[[394]](https://www.beam.cloud/) / Beam Cloud
- Replicate Cog[[395]](https://github.com/replicate/cog)（容器规范 + Replicate 平台）
- Seldon Core[[396]](https://github.com/SeldonIO/seldon-core)

**厂商专有 model server**：
- NVIDIA：Triton Inference Server（事实标准；多框架 / 多模型并行）+ NIM Microservices[[397]](https://developer.nvidia.com/nim)（OpenAI-API 兼容容器）
- AMD：AMD Inference Server[[398]](https://github.com/Xilinx/inference-server)（原 ZenDNN serving，CPU + GPU）+ ROCm Triton Inference 后端
- Intel：OpenVINO Model Server[[399]](https://github.com/openvinotoolkit/model_server)（OVMS，对位 Triton）+ Habana SynapseAI Model Server
- 华为：MindCluster[[400]](https://www.hiascend.com/en)（推理集群管理）+ MindX（昇腾推理参考方案，电力 / 制造 / 金融分行业 SDK）+ ModelArts[[401]](https://www.huaweicloud.com/intl/en-us/product/modelarts.html) 推理服务
- Apple：Core ML 仅端侧，无独立 model server 产品；服务侧 Apple 自家用 Apple Private Cloud Compute[[402]](https://security.apple.com/documentation/private-cloud-compute)（Apple Silicon Server 集群 + Swift on Server，私有不外销）
- AWS：Amazon SageMaker Inference[[403]](https://aws.amazon.com/sagemaker/) + SageMaker MMS（Multi-Model Server）+ Amazon Bedrock[[404]](https://aws.amazon.com/bedrock/)（托管前沿模型，含 Anthropic / Meta / Mistral / Amazon Nova）+ DJL Serving

## L15 GPU 云 / 算力市场

物理 GPU 容量提供方；neocloud 与超大云共存。

- **超大云 GPU**：AWS (P5 / P5e / Trainium2[[405]](https://aws.amazon.com/ai/machine-learning/trainium/) Ultra)、Azure (ND H100 / ND GB200 v6)、Google Cloud (A3 Ultra / TPU v5p / v6e Trillium)、Oracle Cloud (OCI GPU bare-metal)
- **GPU neocloud**：CoreWeave、Lambda Labs、Crusoe、Nebius（前 Yandex 海外）、Voltage Park[[406]](https://www.voltagepark.com/)、Applied Digital[[407]](https://www.applieddigital.com/)
- **市场 / 撮合 / 长尾**：RunPod、Vast.ai[[408]](https://vast.ai/)、TensorDock[[409]](https://www.tensordock.com/)、Salad[[410]](https://salad.com/)、Hyperstack[[411]](https://www.hyperstack.cloud/)
- **训练 + 推理一体**：Together AI、Lepton AI[[412]](https://www.lepton.ai/)（被 NVIDIA 收购）
- **AMD 算力供给**：TensorWave[[413]](https://tensorwave.com/)（北美首家 MI300X 专营 neocloud）、Hot Aisle[[414]](https://hotaisle.xyz/)、Vultr MI300X[[415]](https://www.vultr.com/products/cloud-gpu/)、Oracle OCI MI300X、Microsoft Azure ND MI300X v5
- **Intel Gaudi 算力**：Intel Tiber AI Cloud[[416]](https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html)（原 Intel Developer Cloud）、IBM Cloud Gaudi 3
- **华为昇腾算力**：华为云 ModelArts[[417]](https://www.huaweicloud.com/intl/en-us/product/modelarts.html) + Atlas 900[[271]](https://www.hiascend.com/en/hardware/cluster)（910B / 910C 集群）、运营商云（移动 / 联通 / 电信）昇腾 AI 算力、地方智算中心（如武汉昇腾、济南昇腾）
- **AWS 自研芯片算力**：Trn2 / Trn2 UltraServer（Trainium2[[405]](https://aws.amazon.com/ai/machine-learning/trainium/)，64 芯片 NeuronLink 域）、Inf2（Inferentia2[[295]](https://aws.amazon.com/ai/machine-learning/inferentia/)）；SageMaker HyperPod（训练）、Bedrock（推理 API 直供）
- **Apple 算力供给**：无对外 GPU / NPU 云租赁；服务端仅 Apple Private Cloud Compute[[402]](https://security.apple.com/documentation/private-cloud-compute) 自用，外部不可访问（Apple Intelligence 后端）

## L16 模型 API 聚合 / 路由（推理服务市场）

不直接持有最前沿模型，但把开源 / 半开源模型托管成 OpenAI 兼容 endpoint，并互相竞价。

- **OpenRouter[[144]](https://openrouter.ai/)**（按 token 转售，覆盖 100+ 模型）
- **Together[[145]](https://www.together.ai/) AI**（开源模型托管 + 训练 + 推理引擎自研）
- **Fireworks[[146]](https://fireworks.ai/) AI**（自研 FireAttention 引擎）
- **Groq Cloud**（自家 LPU；Llama[[62]](https://ai.meta.com/llama/) 系超低延迟）
- **Cerebras Inference[[418]](https://www.cerebras.ai/inference)**（WSE-3；超长上下文 + 高速）
- **SambaNova Cloud[[419]](https://sambanova.ai/products/sambacloud)**（SN40L Reconfigurable Dataflow）
- **Replicate[[148]](https://replicate.com/)**（按秒计费，模型即容器）
- **DeepInfra[[420]](https://deepinfra.com/)**、**Anyscale Endpoints[[421]](https://www.anyscale.com/)**、**Hyperbolic[[422]](https://www.hyperbolic.ai/)**

## L17 前沿模型 API（闭源 / 半闭源）

直接调用模型厂商自营 endpoint；当前 90%+ 高端 token 流量在这层。

- **Anthropic[[149]](https://www.anthropic.com/api) API**（Claude Opus / Sonnet / Haiku，含 Tool Use、Computer Use、Skills、Prompt Caching、Files、Batch、Citations、Memory、MCP connector）
- **OpenAI[[150]](https://openai.com/api/) API**（GPT-5.x、o-series、Realtime、Assistants → Responses API、Agents SDK、Files、Batch）
- **Google Gemini API / Vertex AI[[423]](https://cloud.google.com/vertex-ai)**（Gemini 2.5 / 3 Pro / Flash / Nano）
- **xAI API[[424]](https://x.ai/api)**（Grok 4）
- **DeepSeek API[[425]](https://api-docs.deepseek.com/)**（V3 / R1，价格屠夫）
- **企业转售层**：Azure OpenAI Service[[426]](https://azure.microsoft.com/en-us/products/ai-foundry/models/openai/)、AWS Bedrock、Google Vertex AI Model Garden、IBM watsonx[[427]](https://www.ibm.com/products/watsonx)、Databricks Foundation Model APIs[[428]](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)、**SAP BTP GenAI Hub[[429]](https://www.sap.com/products/artificial-intelligence/generative-ai-hub.html)**（SAP 客户在 BTP 内调用 Anthropic / OpenAI / 自家 SAP-AI 的统一入口）、Oracle Cloud Generative AI Service[[430]](https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/)

## L18 LLM 应用框架

prompt 链、工作流、retriever、tool calling 的高层抽象。

- **LangChain[[153]](https://www.langchain.com/) / LangChain Expression Language (LCEL)**
- **LlamaIndex[[154]](https://www.llamaindex.ai/)**（原 GPT-Index；偏 RAG-first）
- **DSPy[[155]](https://github.com/stanfordnlp/dspy)**（Stanford；prompt-as-program、optimizer 驱动）
- **Haystack[[431]](https://haystack.deepset.ai/)**（deepset）
- **Vercel AI SDK[[156]](https://ai-sdk.dev/)**（TypeScript / React 生态最常见）
- **Semantic Kernel[[432]](https://learn.microsoft.com/en-us/semantic-kernel/)**（Microsoft）
- **Mastra[[433]](https://mastra.ai/)**（TS，新兴）
- **Spring AI[[434]](https://spring.io/projects/spring-ai/)**（Java）

## L19 Embedding / 重排序模型与服务

把文本 / 图像变成向量；Reranker 给检索结果二次排序。

- **闭源**：OpenAI text-embedding-3[[435]](https://platform.openai.com/docs/guides/embeddings)、Cohere Embed v3 / Rerank[[436]](https://cohere.com/rerank)、Google Vertex text-embedding-005[[437]](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings)、Voyage AI[[438]](https://www.voyageai.com/)（被 MongoDB 收购）
- **开源**：BGE / BGE-M3（北京智源）、Jina Embeddings v3[[439]](https://jina.ai/embeddings/)、Nomic Embed[[440]](https://www.nomic.ai/)、E5[[441]](https://github.com/microsoft/unilm/tree/master/e5)（Microsoft）、GTE[[442]](https://huggingface.co/collections/Alibaba-NLP/gte-models)（阿里）、Stella[[443]](https://huggingface.co/NovaSearch/stella_en_1.5B_v5)、mxbai-embed[[444]](https://www.mixedbread.com/)
- **多模态**：CLIP[[445]](https://github.com/openai/CLIP) / OpenCLIP[[446]](https://github.com/mlfoundations/open_clip)、SigLIP[[447]](https://huggingface.co/docs/transformers/model_doc/siglip)、Jina-CLIP[[448]](https://jina.ai/models/jina-clip-v2/)

## L20 向量数据库 / 检索引擎

- **专用向量库（SaaS-first）**：Pinecone[[160]](https://www.pinecone.io/)、Weaviate、Qdrant、Milvus / Zilliz
- **开源 / 嵌入式**：Chroma[[449]](https://www.trychroma.com/)、LanceDB[[450]](https://www.lancedb.com/)、FAISS（Meta；库不是服务）、Annoy[[451]](https://github.com/spotify/annoy)、ScaNN[[452]](https://github.com/google-research/google-research/tree/master/scann)
- **关系数据库扩展**：pgvector[[453]](https://github.com/pgvector/pgvector)、pg_vectorize、Supabase Vector[[454]](https://supabase.com/modules/vector)、Neon + pgvector[[455]](https://neon.com/)
- **搜索引擎类**：Elasticsearch dense vector[[456]](https://www.elastic.co/elasticsearch)、OpenSearch k-NN[[457]](https://opensearch.org/)、Vespa[[458]](https://vespa.ai/)、Typesense[[459]](https://typesense.org/)、Meilisearch[[460]](https://www.meilisearch.com/)、Turbopuffer[[461]](https://turbopuffer.com/)
- **嵌入式 + KV**：Redis Vector Search[[462]](https://redis.io/solutions/vector-database/)、SQLite-vec[[463]](https://github.com/asg017/sqlite-vec)

## L21 长期记忆系统

跨会话 / 跨 Agent 的状态层；从 RAG-of-chat 演化到结构化记忆图。

- **Mem0[[166]](https://mem0.ai/)**（开源 + SaaS，事实图 + 向量混合）
- **Zep[[167]](https://www.getzep.com/) / Zep Cloud**（temporal knowledge graph）
- **Letta[[168]](https://www.letta.com/)**（原 MemGPT；研究项目公司化）
- **LangMem[[464]](https://github.com/langchain-ai/langmem)**（LangChain 旗下记忆 SDK）
- **Cognee[[465]](https://www.cognee.ai/)**
- **Anthropic Memory tool[[466]](https://docs.anthropic.com/en/docs/build-with-claude/memory-tool)**（2025 推出，平台内置）

## L22 LLM 网关 / 路由

应用与 L17 / L16 之间的代理层：限流、配额、密钥、fallback、cost guard、A/B。

- **LiteLLM[[170]](https://github.com/BerriAI/litellm)**（BerriAI；100+ provider 适配器，自部署最常用）
- **Portkey[[171]](https://portkey.ai/)**
- **Cloudflare AI Gateway[[172]](https://developers.cloudflare.com/ai-gateway/)**（缓存 + WAF + 计费）
- **Kong AI Gateway[[467]](https://konghq.com/products/kong-ai-gateway)**
- **Helicone[[468]](https://www.helicone.ai/) Gateway**
- **Martian Router[[469]](https://withmartian.com/)**（按 prompt 动态路由）
- **OpenRouter[[144]](https://openrouter.ai/)**（兼有 L16 与 L22 双重身份）
- **企业 / 系统记录层 gateway**：SAP Joule MCP Gateway[[470]](https://www.sap.com/products/artificial-intelligence/ai-assistant.html)（强制非 SAP Agent 经 Joule / BTP 路由到 S/4HANA 才"合规"）、Oracle AI Apps Gateway、Workday AGI Gateway——把"通行权"做到 ERP / HCM 入口

## L23 Prompt 管理 / 提示缓存

prompt 版本化、A/B、提示模板、prompt 级缓存命中分析。

- **PromptLayer[[173]](https://www.promptlayer.com/)**
- **Langfuse Prompt Management[[471]](https://langfuse.com/docs/prompts)**
- **Helicone Prompts[[472]](https://www.helicone.ai/)**
- **Braintrust[[175]](https://www.braintrust.dev/) prompt registry**
- **Latitude[[473]](https://latitude.so/)**（YC W24，prompt-as-code）
- **Agenta[[474]](https://agenta.ai/)**
- **平台原生**：Anthropic Prompt Caching[[475]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)、OpenAI Prompt Caching[[476]](https://platform.openai.com/docs/guides/prompt-caching)、Gemini Context Caching[[477]](https://ai.google.dev/gemini-api/docs/caching)

## L24 Agent 框架

tool-loop、规划、子任务分解、多 agent 协作。2025 这一层从"链式工作流"快速向"事件循环 + 控制平面"迁移。

- **LangGraph**（LangChain[[153]](https://www.langchain.com/)；graph + 持久化 state，企业部署最多）
- **OpenAI Agents SDK[[478]](https://openai.github.io/openai-agents-python/)**（原 Swarm 演化[[479]](https://github.com/openai/swarm)；Responses API 配套）
- **Anthropic Claude Agent SDK[[178]](https://docs.anthropic.com/en/docs/agents-and-tools) / claude-agent-sdk**（Claude Code 同源）
- **AutoGen[[177]](https://github.com/microsoft/autogen) / AutoGen v0.4**（Microsoft Research；多 agent 对话）
- **CrewAI[[480]](https://crewai.com/)**
- **Pydantic AI[[481]](https://ai.pydantic.dev/)**（type-safe，FastAPI 风格）
- **smolagents[[482]](https://github.com/huggingface/smolagents)**（HuggingFace；code-as-action）
- **Mastra**、**Inngest Agent Kit[[483]](https://agentkit.inngest.com/)**、**TaskWeaver[[484]](https://github.com/microsoft/TaskWeaver)**（Microsoft）
- **企业 / 云厂商一体化平台**：Azure AI Foundry[[485]](https://azure.microsoft.com/en-us/products/ai-foundry/)（原 Azure AI Studio，含 Agent Service）、AWS Bedrock Agents[[486]](https://aws.amazon.com/bedrock/agents/)、Google Vertex AI Agent Builder[[487]](https://cloud.google.com/products/agent-builder)、Databricks Mosaic AI Agent Framework[[488]](https://www.databricks.com/product/machine-learning/retrieval-augmented-generation)、SAP Joule Studio[[489]](https://www.sap.com/products/artificial-intelligence/joule-studio.html)（企业级 Agent 构建器，35 解决方案集成、30+ 专属 Agent）、ServiceNow AI Agent Studio[[490]](https://www.servicenow.com/products/ai-agents.html)

## L25 工具协议 / MCP / 集成市场

Agent 怎么调外部世界——文件、API、SaaS、数据库。

- **Anthropic MCP[[179]](https://modelcontextprotocol.io/)（Model Context Protocol）**（2024-11 开源；2025 已被 OpenAI / Google / 主流框架普遍接入；事实标准）
- **Composio[[180]](https://composio.dev/)**（500+ SaaS 集成，认证 + 工具一站式）
- **Arcade[[181]](https://www.arcade.dev/).dev**（auth-first 的 tool runtime）
- **Toolhouse[[491]](https://toolhouse.ai/)**
- **Pipedream Connect[[492]](https://pipedream.com/connect)**
- **Zapier MCP[[493]](https://zapier.com/mcp) / Zapier AI Actions**
- **厂商自营 MCP / Agent 工具（Vendor-side）**：Stripe Agent Toolkit[[494]](https://github.com/stripe/agent-toolkit)、Cloudflare Agents SDK[[495]](https://developers.cloudflare.com/agents/) + Cloudflare MCP[[496]](https://developers.cloudflare.com/agents/model-context-protocol/) + **HTTP 402 pay-per-crawl[[497]](https://blog.cloudflare.com/introducing-pay-per-crawl/)**（把反 Bot 从成本中心变收入中心）、Anthropic Agent Skills[[498]](https://www.anthropic.com/news/agent-skills)（2025-10 公布；与 SAP Joule Skills 同类抽象）、SAP Joule MCP Gateway + Joule Skills（2 500+）、Atlassian Remote MCP[[499]](https://www.atlassian.com/platform/remote-mcp-server)、Notion MCP、Slack MCP、Figma MCP、GitHub MCP、Salesforce MCP for Agentforce
- **CLI 强 wrap 路径**：OpenCLI[[500]](https://opencli.org/)（开放规范，把任意 CLI 描述为 agent-callable tool）、CLI-Anything[[501]](https://github.com/HKUDS/CLI-Anything)（GitHub 21K stars，社区驱动地把已有 CLI 包成 LLM 工具）——与厂商主动出 MCP 形成"第三方强 wrap"对照
- **服务器目录**：Smithery[[502]](https://smithery.ai/)、MCP Hub、PulseMCP[[503]](https://www.pulsemcp.com/)、Glama MCP Registry[[504]](https://glama.ai/mcp)

## L26 浏览器 / Computer Use Agent

让 Agent 操作 GUI / 浏览器 / 桌面。

- **闭源平台**：Anthropic Computer Use[[505]](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)（API 内置）、OpenAI Operator（ChatGPT 内）、Google Project Mariner[[506]](https://deepmind.google/models/project-mariner/) / Gemini browser
- **托管浏览器基础设施**：Browserbase、Hyperbrowser[[507]](https://www.hyperbrowser.ai/)、Steel.dev[[508]](https://steel.dev/)、Anchor Browser[[509]](https://anchorbrowser.io/)、AgentQL[[510]](https://www.agentql.com/)、Browserless[[511]](https://www.browserless.io/)
- **开源 agent 控制器**：browser-use、Skyvern[[512]](https://www.skyvern.com/)、Stagehand[[513]](https://github.com/browserbase/stagehand)（Browserbase）、Nut.js[[514]](https://nutjs.dev/)、Open Interpreter[[515]](https://www.openinterpreter.com/)、Playwright MCP[[516]](https://github.com/microsoft/playwright-mcp)（Microsoft）、Vercel agent-browser[[517]](https://github.com/vercel-labs/agent-browser)（v0 / Vercel AI SDK 配套，把浏览器封装为 agent 可直调的 tool）
- **垂直自动化**：Manus[[518]](https://manus.im/)（端侧通用 agent）、Reworkd[[519]](https://www.reworkd.ai/)、MultiOn[[520]](https://multion.ai/)

## L27 代码 / Agent 沙箱

Agent 跑代码 / 跑命令的隔离环境；MicroVM + 快照成为新基线。

- **E2B[[185]](https://e2b.dev/)**（Firecracker microVM，开源 SDK）
- **Modal Sandboxes**（serverless GPU[[393]](https://lammps.org/) + sandbox 一体）
- **Daytona[[187]](https://www.daytona.io/)**（开源 dev environment manager，被 Agent 平台普遍用作 runner）
- **CodeSandbox SDK[[521]](https://codesandbox.io/sdk) / CodeSandbox Containers**
- **Cloudflare Containers[[522]](https://developers.cloudflare.com/containers/) / Workers Sandbox**
- **Replit Agent runtime[[523]](https://replit.com/products/agent)**（含 Nix-based 沙箱）
- **Devin VM**[[3]](https://devin.ai/)（Cognition 自营）

## L28 LLM 观测 / 追踪（LLM Observability）

trace、span、token / 成本、prompt / completion 日志，是 agent 时代的新 APM。

- **Langfuse[[174]](https://langfuse.com/)**（开源 + cloud，主流之一）
- **Arize Phoenix[[524]](https://phoenix.arize.com/) / Arize AX[[525]](https://arize.com/)**（OpenTelemetry GenAI 推手）
- **LangSmith**（LangChain[[153]](https://www.langchain.com/) 官方）
- **Helicone[[468]](https://www.helicone.ai/)**（proxy-based，零代码接入）
- **Braintrust[[175]](https://www.braintrust.dev/)**（eval + observability 一体）
- **Logfire[[526]](https://logfire.pydantic.dev/)**（Pydantic 团队，OTel-native）
- **W&B Weave[[527]](https://wandb.ai/site/weave/)**
- **Datadog LLM Observability[[528]](https://www.datadoghq.com/product/ai/llm-observability/)**、**New Relic AI Monitoring[[529]](https://newrelic.com/platform/ai-monitoring)**、**Splunk AI Observability[[530]](https://www.splunk.com/en_us/products/observability-cloud.html)**（传统 APM 厂商扩展）

## L29 Guardrails / 安全 / 红队

提示注入防御、PII / 越狱检测、输出过滤、内容策略。

- **Guardrails AI[[195]](https://github.com/guardrails-ai/guardrails)**（开源 validator 框架）
- **NVIDIA NeMo Guardrails[[196]](https://github.com/NVIDIA-NeMo/Guardrails)**（Colang DSL）
- **Lakera Guard / Lakera Red[[531]](https://www.lakera.ai/lakera-guard)**
- **Protect AI[[532]](https://protectai.com/)（含 NB Defense[[533]](https://github.com/protectai/nbdefense)、Guardian、Recon）**
- **Robust Intelligence[[534]](https://www.robustintelligence.com/)**（被 Cisco 收购）
- **Prompt Security[[535]](https://prompt.security/)**、**HiddenLayer[[536]](https://www.hiddenlayer.com/)**、**CalypsoAI[[537]](https://calypsoai.com/)**
- **Llama Guard 3 / Prompt Guard[[538]](https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/)**（Meta 开源策略模型）
- **Promptfoo[[205]](https://www.promptfoo.dev/) red team**（开源越狱测试套件，参 L30）

## L30 LLM 评测 / 测试（CI 中的 prompt 测试）

把 prompt / agent 当作软件来跑回归测试。

- **Promptfoo[[205]](https://www.promptfoo.dev/)**（YAML + CLI，开源主流）
- **DeepEval[[206]](https://github.com/confident-ai/deepeval)**（Confident AI；pytest 风格）
- **Ragas[[207]](https://github.com/explodinggradients/ragas)**（RAG-specific 指标）
- **Braintrust[[175]](https://www.braintrust.dev/) Evals**
- **Patronus AI[[539]](https://www.patronus.ai/)**（合规向）
- **TruLens[[540]](https://www.trulens.org/)**（TruEra；被 Snowflake 收购）
- **OpenAI Evals[[370]](https://github.com/openai/evals)**、**Inspect AI**（UK AISI；安全评测主流）
- **Galileo Evaluate[[541]](https://galileo.ai/)**

## L31 语音（TTS / ASR / 实时对话）

- **TTS**：ElevenLabs、Cartesia、PlayHT[[542]](https://play.ht/)、Hume AI[[543]](https://www.hume.ai/)、Resemble[[544]](https://www.resemble.ai/)、OpenAI tts[[545]](https://platform.openai.com/docs/guides/text-to-speech)、Google Chirp 3[[546]](https://cloud.google.com/text-to-speech/docs/chirp3-hd)、阿里 CosyVoice[[547]](https://github.com/FunAudioLLM/CosyVoice)
- **ASR**：OpenAI Whisper / Whisper Large v3、Deepgram、AssemblyAI[[548]](https://www.assemblyai.com/)、Speechmatics[[549]](https://www.speechmatics.com/)、Rev AI[[550]](https://www.rev.ai/)、NVIDIA Parakeet[[551]](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/)、Google Chirp 2[[552]](https://cloud.google.com/speech-to-text/docs/models/chirp-3)
- **实时语音 / 端到端**：OpenAI Realtime API[[553]](https://platform.openai.com/docs/guides/realtime)、Google Gemini Live[[554]](https://ai.google.dev/gemini-api/docs/live-api)、Anthropic（暂无原生 voice，多用 Cartesia / ElevenLabs 拼接）、Sesame[[555]](https://www.sesame.com/)、Kyutai Moshi[[556]](https://kyutai.org/)、LiveKit Agents[[557]](https://livekit.io/)、Pipecat[[558]](https://www.pipecat.ai/)（编排框架）、Vapi[[559]](https://vapi.ai/)、Retell AI[[560]](https://www.retellai.com/)

## L32 图像 / 视频 / 3D 生成

- **图像（闭源 / SaaS）**：Midjourney、Ideogram[[561]](https://ideogram.ai/)、Adobe Firefly[[232]](https://firefly.adobe.com/)、Google Imagen 3[[562]](https://deepmind.google/technologies/imagen-3/)、OpenAI DALL-E 3[[563]](https://openai.com/index/dall-e-3/) / GPT-4o image、Recraft[[564]](https://www.recraft.ai/)
- **图像（开源 / 工作流）**：Black Forest Labs FLUX.1 / FLUX.2、Stable Diffusion 3[[565]](https://stability.ai/) / SD 3.5 / SDXL（Stability AI）、PixArt-Σ[[566]](https://github.com/PixArt-alpha/PixArt-sigma)、HunyuanImage[[567]](https://github.com/Tencent-Hunyuan/HunyuanImage-3.0)（腾讯）、ComfyUI[[568]](https://github.com/Comfy-Org/ComfyUI)（工作流编辑器）、Automatic1111 WebUI[[569]](https://github.com/AUTOMATIC1111/stable-diffusion-webui)、Fooocus[[570]](https://github.com/lllyasviel/Fooocus)
- **视频**：Runway Gen-4、Pika 2.x[[571]](https://pika.art/)、Luma Dream Machine[[572]](https://lumalabs.ai/dream-machine) / Ray2、Kling[[573]](https://app.klingai.com/global)（快手）、Hailuo MiniMax[[574]](https://hailuoai.video/)、OpenAI Sora、Google Veo 3[[575]](https://deepmind.google/technologies/veo/)、HunyuanVideo[[576]](https://github.com/Tencent-Hunyuan/HunyuanVideo)（腾讯开源）、Wan 2.x[[577]](https://github.com/Wan-Video/Wan2.2)（阿里开源）
- **3D / 场景**：Luma Genie[[578]](https://lumalabs.ai/)、Meshy[[579]](https://www.meshy.ai/)、Tripo3D[[580]](https://www.tripo3d.ai/)、Rodin[[581]](https://hyper3d.ai/)、World Labs[[582]](https://www.worldlabs.ai/)（Fei-Fei Li）、CSM[[583]](https://www.csm.ai/)
- **托管 / 推理市场**：fal.ai、Replicate[[148]](https://replicate.com/)、RunPod Serverless（这一层与 L16 重合，但更偏 diffusion 工作负载）

## L33 通用对话 / 搜索 Agent（终端用户）

直接给非开发者用户用的"AI 助手"。

- **ChatGPT**（OpenAI；含 Tasks、Operator[[183]](https://openai.com/index/introducing-operator/)、Codex、Connectors）
- **Claude.ai**（Anthropic[[149]](https://www.anthropic.com/api)；含 Projects、Artifacts、Computer Use、Skills、Claude Memory、Claude Desktop）
- **Gemini app[[584]](https://gemini.google.com/) / Gemini Advanced**（Google）
- **Grok[[585]](https://grok.com/)**（xAI；X 内嵌 + grok.com）
- **DeepSeek Chat[[586]](https://chat.deepseek.com/)**、**Kimi[[587]](https://kimi.moonshot.cn/)**（Moonshot）、**通义千问[[588]](https://tongyi.aliyun.com/)**、**豆包[[589]](https://www.doubao.com/)**（字节）
- **搜索类**：Perplexity[[590]](https://www.perplexity.ai/)、You.com[[591]](https://you.com/)、Brave Leo[[592]](https://brave.com/leo/)、Arc Search[[593]](https://arc.net/search)（Browser Company）、Komo[[594]](https://komo.ai/)
- **多模型聚合 / 隐私**：Poe[[595]](https://poe.com/)（Quora）、Le Chat[[596]](https://mistral.ai/products/le-chat)（Mistral）、HuggingChat[[597]](https://huggingface.co/chat/)、Msty[[598]](https://msty.ai/)（本地）、LM Studio[[599]](https://lmstudio.ai/)（本地）
- **企业内 Copilot / 默认入口**：Microsoft 365 Copilot（$30/seat，企业 AI 默认入口；CIO 把它当 SAP / Workday / Slack 的统一抢前端）、Google Gemini for Workspace[[600]](https://workspace.google.com/solutions/ai/)、Slack AI[[601]](https://slack.com/features/ai)、Notion AI[[602]](https://www.notion.com/)、Glean Assistant[[603]](https://www.glean.com/)、SAP Joule（SAP 客户内嵌 Agent UI，生产采用率仅 3% 但是 SAP 战略中枢）

## L34 垂直 Agent 应用（终端用户）

按行业 / 角色划分的 Agent；2025 在编码、设计、营销、客服、医疗、法律均跑出独立公司。

- **编码 Agent**：Cursor、Claude Code[[604]](https://claude.ai/code)（Anthropic）、Devin（Cognition）、Windsurf[[605]](https://windsurf.com/)（被 OpenAI 收购）、Replit Agent[[606]](https://replit.com/products/agent)、Codex CLI[[607]](https://github.com/openai/codex)（OpenAI）、Aider[[608]](https://aider.chat/)、GitHub Copilot Workspace[[609]](https://githubnext.com/projects/copilot-workspace/)、Augment[[610]](https://www.augmentcode.com/)、Amp[[611]](https://ampcode.com/)（Sourcegraph）、Lovable[[612]](https://lovable.dev/)、Bolt.new[[613]](https://bolt.new/)、v0[[614]](https://v0.app/)（Vercel）、Manus
- **设计 / 内容**：Figma AI[[615]](https://www.figma.com/ai/) / Make[[616]](https://www.figma.com/make/)、Galileo AI[[617]](https://www.figma.com/make/)、Framer AI[[618]](https://www.framer.com/ai/)、Canva Magic Studio[[619]](https://www.canva.com/canva-ai/)、Jasper[[620]](https://www.jasper.ai/)、Copy.ai[[621]](https://www.copy.ai/)、Notion AI
- **销售 / 营销 / 客服**：Decagon[[622]](https://decagon.ai/)、Sierra[[623]](https://sierra.ai/)、Ada[[624]](https://www.ada.cx/)、Intercom Fin[[625]](https://fin.ai/)、Cresta[[626]](https://cresta.com/)、Clay[[627]](https://www.clay.com/)、11x.ai[[628]](https://www.11x.ai/)、AirOps[[629]](https://www.airops.com/)、**Salesforce Agentforce**（CRM 数据上的 Agent 平台，per-conversation $2 定价）
- **企业知识 / 内部 IT**：Glean[[630]](https://www.glean.com/)、Moveworks[[631]](https://www.moveworks.com/)、Hebbia[[632]](https://www.hebbia.com/)、Harvey[[633]](https://www.harvey.ai/)（法律）、Casetext CoCounsel[[634]](https://cocounsel.thomsonreuters.com/)（被 Thomson Reuters 收购）
- **ERP / HCM / ITSM 内嵌 Agent（系统记录层自营）**：SAP Joule（覆盖 S/4HANA、SuccessFactors、Ariba、Concur、Fieldglass；30+ 专属 Agent，FY25 BTP 收入是 SAP "Agent toll booth" 押注核心）、Oracle AI Apps[[635]](https://www.oracle.com/applications/fusion-ai/ai-agents/) / Oracle Fusion AI Agents、Workday AGI / Workday Illuminate[[636]](https://www.workday.com/en-us/artificial-intelligence.html)、ServiceNow Now Assist[[637]](https://www.servicenow.com/platform/now-assist.html) + AI Agents（ITSM / HRSD / CSM）、Microsoft Dynamics 365 Copilot[[638]](https://www.microsoft.com/en-us/dynamics-365/)
- **代码评审 / 测试 / 安全 Agent**：CodeRabbit[[639]](https://www.coderabbit.ai/)、Greptile[[640]](https://www.greptile.com/)、Qodo[[641]](https://www.qodo.ai/)、Meticulous[[642]](https://www.meticulous.ai/)、Snyk DeepCode AI[[643]](https://snyk.io/platform/deepcode-ai/)（这一层与 SDLC 栈高度重合，详见 [`../SDLC-stack/README.md`](../SDLC-stack/README.md)）
- **医疗 / 科研**：Abridge[[644]](https://www.abridge.com/)、Hippocratic AI[[645]](https://hippocraticai.com/)、Ambience[[646]](https://www.ambiencehealthcare.com/)、Future House[[647]](https://www.futurehouse.org/)、Scite[[648]](https://scite.ai/)

---

## 并列应用分支（共享 L01–L09，从 L10 起分叉）

LLM 不是 GPU 的唯一负载。下面 6 条分支（**B** 科学计算 / **C** 机器人 / **D** 自动驾驶 / **E** 世界模型 / 3D / **F** 经典 CV / **G** 量化金融）与 L10–L34 并列存在，物理上跑在同一批 GPU 上，逻辑上各自独立。B 因为最早成形而拆出 B1 / B2 / B3 三个子层；C–G 用字母 + 小写后缀（Ca / Cb / …）继续切。

### B1 科学计算 / HPC 通用底座（与 L06–L09 并行）

数值仿真、PDE 求解、分子动力学、量子模拟、线性 / 整数规划——这一段比深度学习古老 30 年，但 2023 后被 GPU 与 AI 重新激活。

- **数值 / 张量底座（与深度学习共享）**：NumPy、SciPy、CuPy、JAX、PyTorch[[34]](https://pytorch.org/)（autograd 也用作物理仿真）、Julia + CUDA.jl
- **经典 HPC 运行时**：OpenMP[[649]](https://www.openmp.org/)I[[650]](https://www.open-mpi.org/)、MPICH[[651]](https://www.mpich.org/)、NVIDIA HPC-X[[652]](https://developer.nvidia.com/networking/hpc-x)、UCX[[653]](https://openucx.org/)；OpenMP；Slurm、PBS[[654]](https://altair.com/pbs-professional)、LSF[[655]](https://www.ibm.com/products/hpc-workload-management)；Spack、EasyBuild[[656]](https://easybuild.io/)（HPC 包管理）
- **分子 / 化学 / 生物仿真**：GROMACS（CUDA / SYCL）、OpenMM、LAMMPS-GPU[[393]](https://lammps.org/)、NAMD-CUDA[[657]](https://www.ks.uiuc.edu/Research/namd/)、AMBER[[658]](https://ambermd.org/)、Schrödinger Suite（商业）[[659]](https://www.schrodinger.com/)
- **量子模拟 / 编程**：NVIDIA cuQuantum + CUDA-Q[[660]](https://developer.nvidia.com/cuda-q)、IBM Qiskit[[661]](https://www.ibm.com/quantum/qiskit)、Google Cirq[[662]](https://quantumai.google/cirq)、Xanadu PennyLane[[663]](https://pennylane.ai/)、Quantinuum TKET[[664]](https://www.quantinuum.com/products-solutions/developer-tools)
- **优化 / 运筹**：NVIDIA cuOpt（GPU 路径规划）[[665]](https://www.nvidia.com/en-us/ai-data-science/products/cuopt/)、Gurobi[[666]](https://www.gurobi.com/)、IBM CPLEX[[667]](https://www.ibm.com/products/ilog-cplex-optimization-studio)、Google OR-Tools[[668]](https://developers.google.com/optimization)、COIN-OR[[669]](https://www.coin-or.org/)
- **CFD / 工程仿真**：Ansys Fluent (GPU)[[670]](https://www.ansys.com/products/fluids/ansys-fluent)、Siemens Simcenter STAR-CCM+[[671]](https://www.siemens.com/en-us/products/simcenter/fluids-thermal-simulation/star-ccm/)、NVIDIA Modulus（物理信息 NN）[[672]](https://developer.nvidia.com/physicsnemo)、PhiFlow[[673]](https://github.com/tum-pbs/PhiFlow)、JAX-CFD[[674]](https://github.com/google/jax-cfd)

### B2 AI4Science 领域基础模型（与 L10 并行）

把"基础模型"的范式从语言迁到分子、天气、材料、基因、数学。2024–2025 是 AlphaFold 3 + GraphCast + MatterGen 三个里程碑同年发生的一年。

- **蛋白质 / 抗体 / 复合物**：AlphaFold 3（Google DeepMind / Isomorphic Labs，2024-05；2024-11 开放权重学术非商用）、RoseTTAFold All-Atom（Baker Lab）[[675]](https://github.com/baker-laboratory/RoseTTAFold-All-Atom)、ESM-3（EvolutionaryScale）[[676]](https://www.evolutionaryscale.ai/)、Boltz-1 / Boltz-2（MIT，2024–2025；Boltz-2 含亲和力预测）[[677]](https://github.com/jwohlwend/boltz)、Chai-1（Chai Discovery）[[678]](https://www.chaidiscovery.com/)
- **小分子 / 药物 / 反应**：NVIDIA BioNeMo MolMIM[[679]](https://docs.nvidia.com/nim/bionemo/molmim/latest/overview.html)、OpenFold[[680]](https://openfold.io/)、DiffDock（Gabriele Corso）[[681]](https://github.com/gcorso/DiffDock)、AlphaFold-Multimer、Insilico Medicine Pharma.AI[[682]](https://pharma.ai/)
- **天气 / 气候**：GraphCast、GenCast（DeepMind）[[683]](https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/)、Pangu-Weather（华为，2023 Nature）[[684]](https://github.com/198808xc/Pangu-Weather)、FourCastNet（NVIDIA）[[685]](https://github.com/NVlabs/FourCastNet)、Aurora（Microsoft，2024）[[686]](https://www.microsoft.com/en-us/research/project/aurora-forecasting/)、Fuxi（复旦）[[687]](https://github.com/tpys/FuXi)、ECMWF AIFS[[688]](https://www.ecmwf.int/en/newsletter/178/news/aifs-new-ecmwf-forecasting-system)
- **材料 / 凝聚态**：MatterGen（Microsoft Research，2024）、MACE（Cambridge）[[689]](https://github.com/ACEsuit/mace)、NequIP[[690]](https://github.com/mir-group/nequip)、Allegro（MIT）[[691]](https://github.com/mir-group/allegro)、GNoME（DeepMind，220 万新晶体）[[692]](https://deepmind.google/blog/millions-of-new-materials-discovered-with-deep-learning/)、Orb（Orbital Materials）[[693]](https://www.orbitalindustries.com/)
- **数学 / 形式化推理**：AlphaProof + AlphaGeometry 2（DeepMind，2024 IMO 银牌）[[694]](https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/)、FunSearch[[695]](https://github.com/google-deepmind/funsearch)、Lean + Lean Copilot[[696]](https://leanprover-community.github.io/)、DeepSeek-Prover-V2[[697]](https://github.com/deepseek-ai/DeepSeek-Prover-V2)
- **单细胞 / 基因组**：scGPT（Wang Bo）、Geneformer（Christina Theodoris）[[698]](https://huggingface.co/ctheodoris/Geneformer)、scFoundation（清华 + 百图生科）[[699]](https://github.com/biomap-research/scFoundation)、GeneCompass[[700]](https://github.com/xCompass-AI/GeneCompass)、Evo 2（Arc Institute，1.7T 核苷酸训练）
- **医学影像**：MONAI（NVIDIA + KCL）[[701]](https://monai.io/)、MedSAM[[702]](https://github.com/bowang-lab/MedSAM)、TotalSegmentator[[703]](https://github.com/wasserth/TotalSegmentator)、Google MedGemini[[704]](https://research.google/blog/advancing-medical-ai-with-med-gemini/)、Microsoft RAD-DINO[[705]](https://huggingface.co/microsoft/rad-dino)

### B3 科学 / 工程平台与服务（与 L13–L17 并行）

把 B2 的模型工程化、API 化、SaaS 化。

- **NVIDIA 自研栈**：BioNeMo Framework + BioNeMo NIM Microservices[[706]](https://www.nvidia.com/en-us/clara/bionemo/)、Earth-2 + Earth-2 Studio[[707]](https://www.nvidia.com/en-us/omniverse/)、Modulus（PINN / Neural Operator）、CUDA-Q Cloud[[708]](https://developer.nvidia.com/cuda-q)
- **闭源 / 公司化研发平台**：Isomorphic Labs AlphaFold Server[[709]](https://alphafoldserver.com/)、Schrödinger LiveDesign（药物发现 SaaS）[[710]](https://www.schrodinger.com/platform/products/livedesign/)、Recursion Pharmaceuticals BioHive-2（自营超算 + 模型）[[711]](https://www.recursion.com/)、Cradle.bio[[712]](https://www.cradle.bio/)、Profluent[[713]](https://www.profluent.bio/)
- **科学计算云**：Rescale、CoreWeave Mission Control（HPC + AI 双模）、AWS HPC（ParallelCluster）、Azure CycleCloud、Google Cluster Toolkit[[714]](https://docs.cloud.google.com/cluster-toolkit/docs/overview)
- **科学数据 / Notebook**：Quarto[[715]](https://quarto.org/)、Jupyter + JupyterHub[[716]](https://jupyter.org/hub)、Anaconda[[717]](https://www.anaconda.com/)、Hugging Face Datasets for Science（PubMedQA、OpenProteinSet）

### C 机器人栈：从中间件到 VLA 模型（与 L18–L26 并行）

物理具身 AI 自己一根栈。2024–2025 关键变化是 VLA（Vision-Language-Action）取代了过去的"感知 + 规划 + 控制"三段式。

- **Ca 机器人中间件 / 实时 OS**：ROS 2（事实标准，Humble / Iron / Jazzy）、NVIDIA Isaac ROS、MoveIt 2、micro-ROS（MCU 上的 ROS）[[718]](https://micro.ros.org/)、PX4 / ArduPilot[[719]](https://ardupilot.org/)（无人机）[[720]](https://px4.io/)；实时层 NVIDIA Holoscan、QNX[[721]](https://blackberry.qnx.com/en)、VxWorks[[722]](https://www.windriver.com/products/vxworks)、Xenomai[[723]](https://xenomai.org/)
- **Cb 仿真 / 数字孪生**：NVIDIA Isaac Sim + Isaac Lab[[724]](https://developer.nvidia.com/isaac/lab)、NVIDIA Cosmos（世界基础模型，2025-01 发布）[[725]](https://www.nvidia.com/en-us/ai/cosmos/)、MuJoCo + MuJoCo-MJX（DeepMind 2021 收购后开源 + JAX 化）、Gazebo / Ignition、Genesis（CMU + 多校，2024-12，零样本物理仿真）[[726]](https://genesis-embodied-ai.github.io/)、Drake（TRI）[[727]](https://drake.mit.edu/)、Habitat 3（Meta）[[728]](https://aihabitat.org/)、AI2-THOR[[729]](https://ai2thor.allenai.org/)、Unity ML-Agents[[730]](https://github.com/unity-technologies/ml-agents)
- **Cc 机器人基础模型 / VLA**：NVIDIA GR00T N1 / GR00T-Dreams[[731]](https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks)、Physical Intelligence π0 / π0.5（2024–2025，Sergey Levine、Chelsea Finn）[[732]](https://www.pi.website/blog/pi0)、Google DeepMind RT-2 / Open X-Embodiment / Gemini Robotics（2025-03）[[733]](https://deepmind.google/models/gemini-robotics/)、Skild AI Skild Brain（$300M Series A）[[734]](https://www.skild.ai/)、Figure Helix[[735]](https://www.figure.ai/helix)、1X World Model[[736]](https://www.1x.tech/discover/1x-world-model)、OpenVLA（Stanford）、RDT-1B（清华）、Octo（UC Berkeley）[[737]](https://octo-models.github.io/)
- **Cd 数据 / 训练框架**：LeRobot（HuggingFace；社区主流）、Diffusion Policy（哥伦比亚 + TRI）、ACT（Tony Zhao）[[738]](https://github.com/tonyzhaozh/act)、Open X-Embodiment 数据集（22 机器人形态、527 任务）、DROID 数据集
- **Ce 终端机器人产品**：人形 Tesla Optimus[[739]](https://www.tesla.com/AI)、Figure 02 / 03[[740]](https://www.figure.ai/)、1X Neo Beta[[741]](https://www.1x.tech/neo)、Apptronik Apollo[[742]](https://apptronik.com/apollo)、Unitree H1 / G1 / GD01[[743]](https://www.unitree.com/h1/)；四足 Boston Dynamics Spot[[744]](https://bostondynamics.com/products/spot/)、ANYmal[[745]](https://www.anybotics.com/robotics/anymal/)、Unitree Go2[[746]](https://www.unitree.com/go2/)；服务 / 物流 Agility Robotics Digit[[747]](https://www.agilityrobotics.com/)、Covariant Brain（被 Amazon "聘走团队"）；手术 Intuitive da Vinci 5[[748]](https://www.intuitive.com/en-us/products-and-services/da-vinci/5)

### D 自动驾驶栈（与 L18–L34 并行）

闭源端到端神经网络栈已成为主流；HD 地图 + 规则栈正在被替代。

- **Da 闭源端到端 / 整车**：Tesla FSD V13 / V14（HW4 → HW5）、Waymo Driver（Multi-Modal Foundation Model 路线）、Mobileye SuperVision / Chauffeur / Drive[[749]](https://www.mobileye.com/solutions/super-vision/)、华为 ADS 3.0 / 4.0、小鹏 XNGP、理想 AD Max、Momenta、Pony.ai、Wayve（伦敦，端到端 self-driving 模型 LINGO + GAIA）[[750]](https://wayve.ai/)
- **Db 车载 AI 平台 / 芯片栈**：NVIDIA DRIVE Thor + DRIVE AV / DRIVE OS[[751]](https://developer.nvidia.com/drive/agx)、Mobileye EyeQ6 / EyeQ Ultra[[752]](https://www.mobileye.com/solutions/super-vision/)、Qualcomm Snapdragon Ride[[753]](https://www.qualcomm.com/automotive/solutions/snapdragon-ride) / Ride Flex SoC（SA8775P 智驾 + 座舱融合，2025 主流量产）+ Snapdragon Cockpit Elite、MediaTek Dimensity Auto Cockpit / Dimensity Auto Connect[[875]](https://www.mediatek.com/products/automotive)（与 NVIDIA 联合的 AI 座舱平台，CES 2024 发布 NVIDIA DRIVE OS on MTK SoC）、Horizon Robotics Journey 6（中国主流国产替代）[[754]](https://en.horizon.auto/)、地平线 SuperDrive、瑞芯微 RK3588M（座舱 / 仪表 / 流媒体后视镜，国产中低端车型大量采用）
- **Dc 开源 / 开放栈**：百度 Apollo[[755]](https://www.apollo.auto/en/)、Autoware (Foundation)[[756]](https://autoware.org/)、Comma.ai openpilot、CARLA（仿真）、AirSim（已停维但仍流行）
- **Dd 仿真 / 数据闭环**：NVIDIA DRIVE Sim + Omniverse、Applied Intuition（仿真 + 数据平台）[[757]](https://www.appliedintuition.com/)、Foretellix[[758]](https://www.foretellix.com/)、Cognata、Parallel Domain、Helm.ai
- **De 高精地图 / 定位（被端到端架构挤压但未消失）**：HERE、TomTom、四维图新、Mapbox、Atlatec[[759]](https://www.bosch.com/)（被 Bosch 收购）

### E 世界模型 / 3D 重建 / 游戏 AI（与 L32 并行但目标不同）

L32 偏"生成图像 / 视频"；这一支偏"生成可交互的 3D 世界"。

- **Ea 通用世界模型**：Google DeepMind Genie 2 / Genie 3（2025-08，从一张图生成可交互 1 分钟世界）[[760]](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)、World Labs Marble（Fei-Fei Li，2025-12 GA）[[761]](https://www.worldlabs.ai/)、Wayve GAIA-2[[762]](https://wayve.ai/science/gaia/)、NVIDIA Cosmos World Foundation Models、Decart Mirage、Odyssey
- **Eb 3D 重建 / 新视角合成**：NeRF / Instant-NGP（NVIDIA）、3D Gaussian Splatting（Inria 2023；事实标准）、Mip-Splatting[[763]](https://github.com/autonomousvision/mip-splatting)、Luma Genie、Polycam[[764]](https://poly.cam/)、KIRI Engine[[765]](https://www.kiriengine.app/)
- **Ec 文本 → 3D / Mesh**：Meshy、Tripo3D（VAST）、Rodin（DeemosTech）[[766]](https://hyperhuman.deemos.com/)、Hunyuan3D 2.5（腾讯）[[767]](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)、Trellis（Microsoft）[[768]](https://github.com/microsoft/TRELLIS)、CSM、Spline AI[[769]](https://spline.design/)
- **Ed 游戏内 NPC / 引擎 AI**：NVIDIA ACE（Audio2Face、Riva、NeMo Retriever 套件）[[770]](https://developer.nvidia.com/ace-for-games)、Inworld AI[[92]](https://inworld.ai/)、Convai[[771]](https://convai.com/)、Charisma.ai[[169]](https://charisma.ai/)
- **Ee 工业 / 编辑器**：NVIDIA Omniverse + USD、Unity Sentis（端内 ONNX 推理）[[772]](https://unity.com/products/sentis)、Unreal NNE（Neural Network Engine）、Pixar OpenUSD[[773]](https://openusd.org/)、Houdini Copernicus[[774]](https://www.sidefx.com/products/whats-new-in-h205/copernicus/)

### F 经典计算机视觉 / 边缘感知（与 L13–L14 并行，但模型不属 LLM）

工业视觉、安防、医学影像、OCR、文档智能——这一段在 LLM 大火前就有，2024–2025 又被 VLM 部分蚕食但远未消失。

- **Fa 检测 / 分割 / Pose**：YOLOv10 / v11 / v12（Ultralytics）[[775]](https://www.ultralytics.com/)、RT-DETR（百度）、Detectron2（Meta）[[776]](https://github.com/facebookresearch/detectron2)、MMDetection / MMPose / MMSegmentation（OpenMMLab）[[777]](https://github.com/open-mmlab)、SAM 2（Meta，视频分割）、Grounding DINO[[778]](https://github.com/IDEA-Research/GroundingDINO)、Florence-2（Microsoft）
- **Fb OCR / 文档智能**：PaddleOCR（百度，开源主流）[[779]](https://github.com/PaddlePaddle/PaddleOCR)、Tesseract[[780]](https://github.com/tesseract-ocr/tesseract)、Surya[[781]](https://github.com/VikParuchuri/surya)、DocLayout-YOLO[[782]](https://github.com/opendatalab/DocLayout-YOLO)、Nougat（Meta，学术 PDF）[[783]](https://github.com/facebookresearch/nougat)、MinerU（上海 AI Lab）[[784]](https://github.com/opendatalab/MinerU)、Mistral OCR[[785]](https://mistral.ai/news/mistral-ocr)、Reducto[[786]](https://reducto.ai/)、Unstructured.io[[787]](https://unstructured.io/)
- **Fc 视频理解**：InternVideo 2.5[[788]](https://github.com/OpenGVLab/InternVideo)、VideoLLaMA 3[[789]](https://github.com/DAMO-NLP-SG/VideoLLaMA3)、Qwen2.5-VL[[790]](https://github.com/QwenLM/Qwen-VL)、TwelveLabs Marengo[[791]](https://www.twelvelabs.io/product/models-overview)、Video-CCAM[[792]](https://github.com/QQ-MM/Video-CCAM)
- **Fd 边缘 / 嵌入式部署**：NVIDIA DeepStream + TensorRT、Intel OpenVINO、Qualcomm AI Engine Direct（QNN）[[793]](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk) + Qualcomm Genie[[882]](https://www.qualcomm.com/developer/software/genie-sdk) + AI Hub[[870]](https://aihub.qualcomm.com/)、MediaTek NeuroPilot[[874]](https://neuropilot.mediatek.com/) + Genio[[876]](https://www.mediatek.com/products/iot)、Rockchip RKNN-Toolkit2[[878]](https://github.com/airockchip/rknn-toolkit2) + RKNPU2[[879]](https://github.com/rockchip-linux/rknpu2) + RKLLM[[880]](https://github.com/airockchip/rknn-llm)（国产边缘视觉 / 端侧 LLM 主流，海康 / 大华 / 安霸竞品线大量基于 RK3588 / RK3576 出货）、Arm NN[[794]](https://www.arm.com/products/silicon-ip-cpu/ethos/arm-nn)、Apple Core ML、MediaPipe（Google）[[795]](https://developers.google.com/mediapipe)、Hailo Dataflow Compiler[[796]](https://hailo.ai/products/hailo-software/hailo-ai-software-suite/)、爱芯元智 AXera Pulsar SDK[[883]](https://www.axera-tech.com/)（AX650N / AX620E）、地平线 Horizon OpenExplorer（Journey / Sunrise X 系列）、寒武纪 MagicMind
- **Fe 数据 / 训练平台**：Roboflow[[797]](https://roboflow.com/)、Encord[[798]](https://encord.com/)、Labelbox[[799]](https://labelbox.com/)、Voxel51 FiftyOne[[800]](https://voxel51.com/fiftyone)、CVAT[[801]](https://www.cvat.ai/)、Supervisely[[802]](https://supervisely.com/)
- **Ff 终端应用**：工业 Cognex VisionPro Deep Learning[[803]](https://www.cognex.com/en/products/machine-vision-software/visionpro-software)、Keyence[[804]](https://www.keyence.com/products/vision/)、Landing AI（Andrew Ng）[[805]](https://landing.ai/)；安防 Hikvision[[806]](https://www.hikvision.com/en/)、Dahua[[807]](https://www.dahuasecurity.com/)；医学影像 Aidoc[[808]](https://www.aidoc.com/)、Annalise.ai[[809]](https://annalise.ai/)、Viz.ai[[810]](https://www.viz.ai/)；零售 Standard AI[[811]](https://standard.ai/)、Trigo[[812]](https://www.trigoretail.com/)

### G 量化金融 / 经典 ML 应用（轻量分支）

绝大多数金融 AI 跑在 L06 PyTorch / JAX 通用框架上，没有独立"基础模型"层；但工具链与终端用户面孔与 LLM 分支差异大。

- **Ga 经典 ML 框架**：scikit-learn、XGBoost、LightGBM、CatBoost[[813]](https://catboost.ai/)、RAPIDS cuML（GPU 加速 sklearn）[[814]](https://rapids.ai/)、H2O.ai[[815]](https://h2o.ai/)
- **Gb 时间序列 / 预测**：Prophet（Meta）[[816]](https://facebook.github.io/prophet/)、NeuralProphet[[817]](https://neuralprophet.com/)、Nixtla（StatsForecast / NeuralForecast / TimeGPT）[[818]](https://www.nixtla.io/)、Salesforce Merlion[[819]](https://github.com/salesforce/Merlion)、Amazon Chronos[[820]](https://github.com/amazon-science/chronos-forecasting)
- **Gc 量化 / 回测平台**：QuantConnect[[821]](https://www.quantconnect.com/)、Backtrader[[822]](https://www.backtrader.com/)、vectorbt / vectorbt-pro[[823]](https://vectorbt.dev/)、Zipline-reloaded[[824]](https://github.com/stefan-jansen/zipline-reloaded)、QuantLib（衍生品定价库）[[825]](https://www.quantlib.org/)、NVIDIA cuOpt + Risk Pricing
- **Gd 金融领域模型**：BloombergGPT、FinGPT、FinBERT[[826]](https://github.com/yya518/FinBERT)、PIXIU[[17]](https://github.com/The-FinAI/PIXIU)；金融具体应用大多复用 GPT / Claude，没有独立分发
- **Ge 终端 / 平台**：Bloomberg Terminal + AI[[827]](https://professional.bloomberg.com/products/bloomberg-terminal/)、FactSet Mercury[[111]](https://www.factset.com/ai)、Two Sigma Venn[[828]](https://www.venn.twosigma.com/)、AlphaSense[[829]](https://www.alpha-sense.com/)、Hebbia（这一项已在 L34 列出）

### H 游戏栈：引擎 + NPC AI + 反作弊 + 渲染（与 L13 / L21 / L29 / L32 渗透）

游戏行业 AI 应用集中在三个方向：实时性能（DLSS / FSR / XeSS 等 super-resolution）、NPC 智能（对话 + 行为）、反作弊与玩家行为监测。生成式 AI 主要进入资产生成与原型阶段，对线上玩法的影响仍较有限。

- **Ha 游戏引擎（AI 是嵌入而非主干）**：Unreal Engine[[830]](https://www.unrealengine.com/)、Unity[[831]](https://unity.com/)、Godot[[832]](https://godotengine.org/)、CryEngine[[833]](https://www.cryengine.com/)、Cocos Creator[[834]](https://www.cocos.com/en/creator)
- **Hb 实时画质提升 / 上采样**：NVIDIA DLSS[[835]](https://www.nvidia.com/en-us/geforce/technologies/dlss/)（Deep Learning Super Sampling）、AMD FSR[[836]](https://gpuopen.com/fidelityfx-super-resolution-4/)（FidelityFX Super Resolution）、Intel XeSS[[837]](https://www.intel.com/content/www/us/en/products/docs/discrete-gpus/arc/technology/xess.html)、Sony PSSR[[838]](https://blog.playstation.com/2024/09/10/playstation-5-pro-launches-november-7-priced-at-699-99/)（PlayStation Spectral Super Resolution）
- **Hc NPC / 对话 AI**：NVIDIA ACE、Inworld AI（含 Inworld Origins 演示）、Convai、Charisma.ai、Replica Studios（语音 + 角色）；游戏内 LLM 集成方向上 NetEase Naraku Dialogue 等本土探索
- **Hd 程序化生成 / 资产**：Promethean AI[[839]](https://www.prometheanai.com/)、Scenario[[840]](https://www.scenario.com/)、Rosebud AI[[841]](https://www.rosebud.ai/)、Skybox AI（360° 场景）、Houdini procedural、SideFX Solaris
- **He 反作弊 / 玩家行为**：BattlEye、Easy Anti-Cheat（Epic）、VAC（Valve）、GGWP[[842]](https://www.ggwp.com/)、Anybrain[[843]](https://www.anybrain.gg/)（行为生物特征反作弊）
- **Hf 玩家服务 / live ops 后端**：Microsoft PlayFab、AWS GameLift、Unity Gaming Services[[844]](https://unity.com/products/gaming-services)、Epic Online Services[[845]](https://dev.epicgames.com/services)、GameAnalytics、Unity Analytics
- **Hg 终端游戏 / AI-first 工作室**：Inworld 集成游戏（Status: One、Sims-style 等）、Hidden Door[[846]](https://www.hiddendoor.co/)（叙事 AI 游戏平台）、AI Dungeon[[847]](https://aidungeon.com/)、Suck Up\![[848]](https://www.proxima-enterprises.com/)（Proxima Enterprises）

### I 影视娱乐栈：VFX / 后期 / 虚拟制作 / 生成式（与 E / L32 高度渗透）

L32 已列了 Sora / Veo / Runway 等生成模型。本段重在**工业级 VFX 工具链** + **AI-first 制作工作流**——它们大多用 NVIDIA / Apple GPU、但栈在 Houdini / Nuke / DaVinci 这条传统 DCC 轴上演化。

- **Ia VFX / 合成 / 调色**：Adobe After Effects[[849]](https://www.adobe.com/products/aftereffects.html)、Foundry Nuke[[850]](https://www.foundry.com/products/nuke-family/nuke)、Blackmagic DaVinci Resolve[[851]](https://www.blackmagicdesign.com/products/davinciresolve)、Autodesk Maya[[852]](https://www.autodesk.com/products/maya/overview)、Blender[[853]](https://www.blender.org/)、Houdini、Cinema 4D[[854]](https://www.maxon.net/en/cinema-4d)
- **Ib AI VFX / 自动化制作**：Wonder Dynamics Wonder Studio（角色替换 + 自动 mocap）、Runway（视频生成与编辑）、Move.ai[[855]](https://www.move.ai/)（无标记 mocap）、Cuebric（虚拟制作 LED wall 场景）、Promise[[856]](https://www.promise.studio/)（生成式电影工作室）
- **Ic 视频生成 / 模型层**：与 L32 共用：Sora、Veo 3、Kling、Runway Gen-4、Pika、Luma Dream Machine、Hailuo MiniMax、HunyuanVideo、Wan、OpenAI Sora 2 等
- **Id 音频 / 配音 / 修复**：ElevenLabs（配音）、Resemble、Descript（视频 + 播客后期 + Overdub）、Adobe Podcast（语音增强）、Krisp[[857]](https://krisp.ai/)（降噪）、iZotope RX[[858]](https://www.izotope.com/en/products/rx.html)（音频修复）
- **Ie 影像增强 / 修复 / 上采样**：Topaz Video AI（去噪 / 上采样 / 帧插值）、Adobe Enhance / Premiere AI、NVIDIA RTX Video[[859]](https://www.nvidia.com/en-us/geforce/news/rtx-video-super-resolution/)、DaVinci Resolve Neural Engine
- **If 虚拟制作 / LED 摄影棚**：ILM StageCraft（Mandalorian 的 LED volume）、Disguise[[860]](https://www.disguise.one/)、Pixotope[[861]](https://www.pixotope.com/)、Unreal Engine + nDisplay（实时背景）
- **Ig 渲染引擎 / 渲染农场**：V-Ray、RenderMan（Pixar）、Arnold（Autodesk）、Redshift[[862]](https://www.maxon.net/en/redshift)、Octane[[863]](https://home.otoy.com/render/octane-render/)；渲染云 Conductor、AWS Thinkbox Deadline、Coresite、Foundry Athera
- **Ih 字幕 / 翻译 / 内容审核**：Captions（短视频 AI 工作室）、Submagic[[864]](https://www.submagic.co/)、CapCut[[865]](https://www.capcut.com/)（字节，AI 内嵌剪辑）、Veed.io[[866]](https://www.veed.io/)
- **Ii AI-first 影视工作室 / 终端品牌**：Adobe Firefly Video、ILM StageCraft、Marvel（已多次使用 AI 风格化）、Wonder Studios、Promise；Lightricks / LTX-Video[[867]](https://www.lightricks.com/) 模型；OpenAI Sora 自有 app

---

## 几条横切的观察

不属于具体某一层，但跨层规律值得单列。

- **MCP 是这一栈唯一在 2024–2025 通过的"工具接口标准"**：从 L25 起，向上影响 L24 / L18，向下影响 L17（模型 API 内置 MCP connector）和 L22（gateway 必须懂 MCP）。
- **L13 推理引擎 与 L14 模型服务 的边界正在合并**：vLLM、SGLang[[109]](https://github.com/sgl-project/sglang) 自带 OpenAI 兼容 HTTP server，挤压了纯 L14 厂商（KServe、BentoML）的独立性。
- **L15 GPU 云、L16 模型 API 聚合、L17 前沿模型 API 三层正在相互渗透**：CoreWeave[[131]](https://www.coreweave.com/) 推自家模型；Together / Fireworks 自研推理引擎；Anthropic / OpenAI 转售他人模型（极少，但 Bedrock / Vertex 把这种关系制度化）。
- **L9 后训练 + L11 评测 + L24 Agent 框架 形成 RL 闭环**：RLVR / GRPO 把 L11 的评测器当 reward，把 L24 的 agent rollout 当 trajectory，是 2025 训练范式的核心变化。
- **L34 垂直 Agent 与 L24 Agent 框架的耦合方式分两类**：闭源垂直 Agent（Cursor、Devin、Sierra）几乎都不用第三方 Agent 框架，自己造控制循环；而中小垂直 Agent（Clay、Lovable 的部分组件）大量复用 LangGraph / Agents SDK。
- **L18 LLM 应用框架 在 2025 出现 "去 LangChain[[153]](https://www.langchain.com/) 化"信号**：原生 SDK（OpenAI Agents SDK、Claude Agent SDK）抢占了 LangChain 早期的功能位；LangChain 通过 LangGraph + LangSmith 上移到 L24 + L28。
- **并列分支 B–G 共享 L01–L09，但向上越走越像各自孤岛**：科学计算几乎不进 L13 推理服务（用 Slurm + 直接调脚本）；机器人 VLA / 自动驾驶端到端策略**根本不是 Agent**（没有 tool-loop、没有规划），用主干"Agent 框架"的话语去套是误读；只有 E 世界模型与 L32 视频生成在底层模型上真正同源。
- **NVIDIA 是唯一在 A 主干 + B–G 全部 6 个分支都占重要席位的供应商**：CUDA + cuDNN[[21]](https://developer.nvidia.com/cudnn)（L03–L04）→ Megatron / NeMo（L07）→ Triton Inference（L14）→ BioNeMo / Earth-2 / Modulus（B3）→ Isaac / Cosmos / GR00T（C）→ DRIVE（D）→ Omniverse + ACE（E）→ DeepStream（F）。这是 2025 估值溢价相对于纯 LLM 厂商更稳的结构性原因。
- **移动 / 边缘 SoC 三巨头（高通 / 联发科 / 瑞芯微）走的是与 NVIDIA 正交的栈**：他们集中在 L01（自研 NPU 驱动）+ L03（QNN / NeuroPilot / RKNN 三套互不兼容的 SDK）+ L13（端侧 LLM 推理引擎 Genie / NeuroPilot / RKLLM），几乎不出现在 L06–L09 训练栈与 L18 以上 Agent 栈——他们卖的是"模型转出后跑在哪"的最后一公里。三家分工：高通占高端手机 / Copilot+ PC / 高端车载（Snapdragon Ride）、联发科占中高端手机 + 中端车机 + ChromeOS、瑞芯微占低成本边缘视觉 + 中低端国产车机 / IoT。共同对手是 Apple ANE + 内置 Core ML 闭环（Apple 自家硬件 / 自家 OS / 自家 SDK 不外销）。

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

[17] The FinAI, "PIXIU: A Large Language Model, Instruction Data and Evaluation Benchmark for Finance," *GitHub*, NeurIPS 2023. [Online]. Available: <https://github.com/The-FinAI/PIXIU>

[18] JuliaGPU, "CUDA.jl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/JuliaGPU/CUDA.jl>

[19] NVIDIA / RAPIDS AI, "RAPIDS: GPU Accelerated Data Science," [Online]. Available: <https://rapids.ai/>

[20] NVIDIA, "cuBLAS," [Online]. Available: <https://developer.nvidia.com/cublas>

[21] NVIDIA, "CUDA Deep Neural Network (cuDNN)," [Online]. Available: <https://developer.nvidia.com/cudnn>

[22] Dao-AILab, "FlashAttention," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/dao-ailab/flash-attention>

[23] NVIDIA, "CUTLASS," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/cutlass>

[24] NVIDIA, "cuFFT," [Online]. Available: <https://developer.nvidia.com/cufft>

[25] NVIDIA, "cuSOLVER," [Online]. Available: <https://developer.nvidia.com/cusolver>

[26] NVIDIA, "cuSPARSE," [Online]. Available: <https://developer.nvidia.com/cusparse>

[27] NVIDIA, "cuQuantum SDK," [Online]. Available: <https://developer.nvidia.com/cuquantum-sdk>

[28] NVIDIA, "NVSHMEM," [Online]. Available: <https://developer.nvidia.com/nvshmem>

[29] triton-lang, "Triton," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-lang/triton>

[30] OpenXLA Project, "XLA: Optimizing Compiler for Machine Learning," [Online]. Available: <https://openxla.org/xla>

[31] LLVM Project, "MLIR," [Online]. Available: <https://mlir.llvm.org/>

[32] Apache Software Foundation, "Apache TVM," [Online]. Available: <https://tvm.apache.org/>

[33] Exaloop, "Codon," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/exaloop/codon>

[34] PyTorch Foundation, "PyTorch," [Online]. Available: <https://pytorch.org/>

[35] Google / jax-ml, "JAX," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/jax-ml/jax>

[36] Apple / ml-explore, "MLX: An array framework for Apple silicon," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ml-explore/mlx>

[37] Google, "TensorFlow," [Online]. Available: <https://www.tensorflow.org/>

[38] NumPy Developers, "NumPy," [Online]. Available: <https://numpy.org/>

[39] SciPy Developers, "SciPy," [Online]. Available: <https://scipy.org/>

[40] Preferred Networks / CuPy Developers, "CuPy," [Online]. Available: <https://cupy.dev/>

[41] Julia Project, "The Julia Programming Language," [Online]. Available: <https://julialang.org/>

[42] scikit-learn Developers, "scikit-learn," [Online]. Available: <https://scikit-learn.org/>

[43] DMLC, "XGBoost Documentation," [Online]. Available: <https://xgboost.readthedocs.io/>

[44] Microsoft, "LightGBM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/microsoft/LightGBM>

[45] Microsoft / DeepSpeed AI, "DeepSpeed," [Online]. Available: <https://www.deepspeed.ai/>

[46] NVIDIA, "Megatron-LM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/Megatron-LM>

[47] PyTorch, "FullyShardedDataParallel (FSDP)," [Online]. Available: <https://docs.pytorch.org/docs/stable/fsdp.html>

[48] NVIDIA, "NeMo Framework," [Online]. Available: <https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html>

[49] Anyscale, "Ray Train," [Online]. Available: <https://docs.ray.io/en/latest/train/train.html>

[50] MPI Forum, "Message Passing Interface (MPI)," [Online]. Available: <https://www.mpi-forum.org/>

[51] Hugging Face / HuggingFaceFW, "FineWeb," Hugging Face Dataset, 2024. [Online]. Available: <https://huggingface.co/datasets/HuggingFaceFW/fineweb>

[52] Hugging Face, "datatrove," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/datatrove>

[53] MosaicML, "Streaming," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/streaming>

[54] Open X-Embodiment Collaboration, "Open X-Embodiment: Robotic Learning Datasets and RT-X Models," 2023. [Online]. Available: <https://robotics-transformer-x.github.io/>

[55] DROID Collaboration, "DROID: A Large-Scale In-the-Wild Robot Manipulation Dataset," [Online]. Available: <https://droid-dataset.github.io/>

[56] Hugging Face, "LeRobot," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/lerobot>

[57] Hugging Face, "TRL," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/huggingface/trl>

[58] Volcengine, "verl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/volcengine/verl>

[59] Unsloth AI, "Unsloth," [Online]. Available: <https://unsloth.ai/>

[60] Axolotl AI, "Axolotl," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/axolotl-ai-cloud/axolotl>

[61] Stanford Robotics, "Diffusion Policy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/real-stanford/diffusion_policy>

[62] Meta AI, "Llama," [Online]. Available: <https://ai.meta.com/llama/>

[63] Anthropic, "Claude," [Online]. Available: <https://www.anthropic.com/claude>

[64] OpenAI, "OpenAI API," [Online]. Available: <https://openai.com/api/>

[65] Alibaba Cloud / Qwen Team, "Qwen," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/QwenLM/Qwen>

[66] DeepSeek AI, "DeepSeek," [Online]. Available: <https://www.deepseek.com/en/>

[67] Google DeepMind / Isomorphic Labs, "AlphaFold Server," [Online]. Available: <https://alphafoldserver.com/>

[68] Google DeepMind, "GraphCast," [Online]. Available: <https://deepmind.google/technologies/graphcast/>

[69] Microsoft Research, "MatterGen," 2024. [Online]. Available: <https://www.microsoft.com/en-us/research/blog/mattergen-a-new-paradigm-of-materials-design-with-generative-ai/>

[70] Bo Wang Lab, "scGPT," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/bowang-lab/scGPT>

[71] Arc Institute, "Evo 2," 2025. [Online]. Available: <https://arcinstitute.org/news/blog/evo2>

[72] NVIDIA, "Isaac GR00T," [Online]. Available: <https://developer.nvidia.com/isaac/gr00t>

[73] Physical Intelligence, "Physical Intelligence (π)," [Online]. Available: <https://www.physicalintelligence.company/>

[74] Google DeepMind, "RT-2: Vision-Language-Action Models," 2023. [Online]. Available: <https://robotics-transformer2.github.io/>

[75] Stanford / UC Berkeley, "OpenVLA: An Open-Source Vision-Language-Action Model," [Online]. Available: <https://openvla.github.io/>

[76] Tsinghua University, "RDT-1B: A Diffusion Foundation Model for Bimanual Manipulation," [Online]. Available: <https://rdt-robotics.github.io/rdt-robotics/>

[77] Tesla, "Autopilot and Full Self-Driving Capability," [Online]. Available: <https://www.tesla.com/support/autopilot>

[78] Waymo, "Waymo Driver," [Online]. Available: <https://waymo.com/>

[79] Wayve, "LINGO: Natural language for autonomous driving," [Online]. Available: <https://wayve.ai/thinking/lingo-natural-language-autonomous-driving/>

[80] Google DeepMind, "Genie 3: A new frontier for world models," 2025. [Online]. Available: <https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/>

[81] World Labs, "Marble," [Online]. Available: <https://www.worldlabs.ai/>

[82] NVIDIA, "Cosmos World Foundation Models," [Online]. Available: <https://www.nvidia.com/en-us/ai/cosmos/>

[83] Ultralytics, "YOLO11," [Online]. Available: <https://docs.ultralytics.com/models/yolo11/>

[84] Meta AI, "Segment Anything Model 2 (SAM 2)," [Online]. Available: <https://ai.meta.com/sam2/>

[85] Microsoft, "Florence-2," Hugging Face Model, 2024. [Online]. Available: <https://huggingface.co/microsoft/Florence-2-large>

[86] Baidu, "RT-DETR," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/lyuwenyu/RT-DETR>

[87] Bloomberg, "BloombergGPT," 2023. [Online]. Available: <https://www.bloomberg.com/company/press/bloomberggpt-50-billion-parameter-llm-tuned-finance/>

[88] AI4Finance Foundation, "FinGPT," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/AI4Finance-Foundation/FinGPT>

[89] Nixtla, "TimeGPT," [Online]. Available: <https://www.nixtla.io/>

[90] Amazon Science, "Chronos: Pretrained Models for Time Series Forecasting," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/amazon-science/chronos-forecasting>

[91] NVIDIA, "NVIDIA ACE — Avatar Cloud Engine", [Online]. Available: <https://developer.nvidia.com/ace>

[92] Inworld AI, "AI-Powered NPCs and Character Simulation," *inworld.ai*, 2025. [Online]. Available: <https://inworld.ai/>

[93] D. Hendrycks et al., "Measuring Massive Multitask Language Understanding," *arXiv preprint*, arXiv:2009.03300, 2020. [Online]. Available: <https://arxiv.org/abs/2009.03300>

[94] Princeton NLP, "SWE-bench," [Online]. Available: <https://www.swebench.com/>

[95] Embeddings Benchmark, "MTEB: Massive Text Embedding Benchmark," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/embeddings-benchmark/mteb/>

[96] METR, "Task-Completion Time Horizons of Frontier AI Models," [Online]. Available: <https://metr.org/time-horizons/>

[97] Protein Structure Prediction Center, "CASP," [Online]. Available: <https://predictioncenter.org/>

[98] Pangeo, "WeatherBench," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pangeo-data/WeatherBench>

[99] Materials Project, "Matbench Discovery," [Online]. Available: <https://matbench-discovery.materialsproject.org/>

[100] Imperial College London, "RLBench," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stepjam/RLBench>

[101] Motional, "nuScenes," [Online]. Available: <https://www.nuscenes.org/>

[102] Microsoft, "Common Objects in Context (COCO)," [Online]. Available: <https://cocodataset.org/>

[103] Stanford Vision Lab, "ImageNet," [Online]. Available: <https://www.image-net.org/>

[104] Weights & Biases, "Weights & Biases," [Online]. Available: <https://wandb.ai/site/>

[105] MLflow Project, "MLflow," [Online]. Available: <https://mlflow.org/>

[106] Neptune AI, "Neptune," [Online]. Available: <https://neptune.ai/>

[107] vLLM Project, "vLLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/vllm-project/vllm>

[108] NVIDIA, "TensorRT-LLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/TensorRT-LLM>

[109] sgl-project, "SGLang," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/sgl-project/sglang>

[110] Georgi Gerganov, "llama.cpp," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ggerganov/llama.cpp>

[111] FactSet, "FactSet Mercury: AI-Powered Financial Research Assistant," *factset.com*, 2025. [Online]. Available: <https://www.factset.com/ai>

[112] NVIDIA, "BioNeMo," [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[113] NVIDIA, "Isaac ROS," [Online]. Available: <https://developer.nvidia.com/isaac/ros>

[114] NVIDIA, "DRIVE OS," [Online]. Available: <https://developer.nvidia.com/drive/drive-os>

[115] Mobileye, "EyeQ Chip," [Online]. Available: <https://www.mobileye.com/technology/eyeq-chip/>

[116] Comma.ai, "openpilot," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/commaai/openpilot>

[117] Inria, "3D Gaussian Splatting for Real-Time Radiance Field Rendering," SIGGRAPH 2023. [Online]. Available: <https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/>

[118] NVIDIA NVlabs, "Instant-NGP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVlabs/instant-ngp>

[119] NVIDIA, "DeepStream SDK," [Online]. Available: <https://developer.nvidia.com/deepstream-sdk>

[120] Intel, "OpenVINO Documentation," [Online]. Available: <https://docs.openvino.ai/>

[121] Apple, "Core ML," [Online]. Available: <https://developer.apple.com/machine-learning/core-ml/>

[122] NVIDIA, "Triton Inference Server," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-inference-server/server>

[123] Anyscale, "Ray Serve," [Online]. Available: <https://docs.ray.io/en/latest/serve/index.html>

[124] BentoML, "BentoML," [Online]. Available: <https://www.bentoml.com/>

[125] NVIDIA, "BioNeMo NIM Microservices," [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[126] NVIDIA, "Earth-2," [Online]. Available: <https://www.nvidia.com/en-us/high-performance-computing/earth-2/>

[127] PickNik Robotics, "MoveIt," [Online]. Available: <https://moveit.ai/>

[128] NVIDIA, "Omniverse Kit SDK," [Online]. Available: <https://developer.nvidia.com/omniverse/kit-sdk>

[129] Microsoft, "PlayFab — Backend services for live games", [Online]. Available: <https://playfab.com/>

[130] AWS, "Amazon GameLift", [Online]. Available: <https://aws.amazon.com/gamelift/>

[131] CoreWeave, "CoreWeave," [Online]. Available: <https://www.coreweave.com/>

[132] Lambda, "Lambda," [Online]. Available: <https://lambda.ai/>

[133] Crusoe, "Crusoe," [Online]. Available: <https://www.crusoe.ai/>

[134] Nebius, "Nebius," [Online]. Available: <https://nebius.com/>

[135] Rescale, "Rescale," [Online]. Available: <https://rescale.com/>

[136] Amazon Web Services, "AWS HPC," [Online]. Available: <https://aws.amazon.com/hpc/>

[137] Microsoft Azure, "Azure CycleCloud," [Online]. Available: <https://azure.microsoft.com/en-us/products/cyclecloud>

[138] Tesla, "Tesla AI," [Online]. Available: <https://www.tesla.com/AI>

[139] RunPod, "RunPod," [Online]. Available: <https://www.runpod.io/>

[140] fal.ai, "fal.ai," [Online]. Available: <https://fal.ai/>

[141] Amazon Web Services, "AWS Panorama," [Online]. Available: <https://aws.amazon.com/panorama/>

[142] CoreWeave / Conductor Technologies, "Conductor — Cloud rendering platform", [Online]. Available: <https://www.conductortech.com/>

[143] AWS Thinkbox, "Deadline — Render farm management", [Online]. Available: <https://aws.amazon.com/thinkbox-deadline/>

[144] OpenRouter, "OpenRouter," [Online]. Available: <https://openrouter.ai/>

[145] Together AI, "Together AI," [Online]. Available: <https://www.together.ai/>

[146] Fireworks AI, "Fireworks AI," [Online]. Available: <https://fireworks.ai/>

[147] Groq, "Groq," [Online]. Available: <https://groq.com/>

[148] Replicate, "Replicate," [Online]. Available: <https://replicate.com/>

[149] Anthropic, "Build on the Claude Platform," [Online]. Available: <https://www.anthropic.com/api>

[150] OpenAI, "OpenAI API Platform," [Online]. Available: <https://openai.com/api/>

[151] Google, "Gemini Developer API," [Online]. Available: <https://ai.google.dev/>

[152] xAI, "xAI," [Online]. Available: <https://x.ai/>

[153] LangChain, "LangChain," [Online]. Available: <https://www.langchain.com/>

[154] LlamaIndex, "LlamaIndex," [Online]. Available: <https://www.llamaindex.ai/>

[155] Stanford NLP, "DSPy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stanfordnlp/dspy>

[156] Vercel, "AI SDK," [Online]. Available: <https://ai-sdk.dev/>

[157] OpenAI, "Vector Embeddings," [Online]. Available: <https://platform.openai.com/docs/guides/embeddings>

[158] Cohere, "Embed," [Online]. Available: <https://cohere.com/embed>

[159] BAAI / FlagOpen, "FlagEmbedding (BGE)," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/FlagOpen/FlagEmbedding>

[160] Pinecone, "Pinecone," [Online]. Available: <https://www.pinecone.io/>

[161] Weaviate, "Weaviate," [Online]. Available: <https://weaviate.io/>

[162] Qdrant, "Qdrant," [Online]. Available: <https://qdrant.tech/>

[163] Zilliz / Milvus, "Milvus," [Online]. Available: <https://milvus.io/>

[164] Meta AI Research, "FAISS," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/facebookresearch/faiss>

[165] Roboflow, "Roboflow Universe," [Online]. Available: <https://universe.roboflow.com/>

[166] Mem0 AI, "Mem0," [Online]. Available: <https://mem0.ai/>

[167] Zep AI, "Zep," [Online]. Available: <https://www.getzep.com/>

[168] Letta AI, "Letta," [Online]. Available: <https://www.letta.com/>

[169] Charisma Entertainment, "Charisma.ai: AI-Powered Storytelling and Character Platform," *charisma.ai*, 2025. [Online]. Available: <https://charisma.ai/>

[170] BerriAI, "LiteLLM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/BerriAI/litellm>

[171] Portkey AI, "Portkey," [Online]. Available: <https://portkey.ai/>

[172] Cloudflare, "Cloudflare AI Gateway," [Online]. Available: <https://developers.cloudflare.com/ai-gateway/>

[173] PromptLayer, "PromptLayer," [Online]. Available: <https://www.promptlayer.com/>

[174] Langfuse, "Langfuse," [Online]. Available: <https://langfuse.com/>

[175] Braintrust, "Braintrust," [Online]. Available: <https://www.braintrust.dev/>

[176] LangChain, "LangGraph," [Online]. Available: <https://www.langchain.com/langgraph>

[177] Microsoft, "AutoGen," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/microsoft/autogen>

[178] Anthropic, "Claude Agent SDK," [Online]. Available: <https://docs.anthropic.com/en/docs/agents-and-tools>

[179] Anthropic / Model Context Protocol, "Model Context Protocol," [Online]. Available: <https://modelcontextprotocol.io/>

[180] Composio, "Composio," [Online]. Available: <https://composio.dev/>

[181] Arcade.dev, "Arcade," [Online]. Available: <https://www.arcade.dev/>

[182] Browserbase, "Browserbase," [Online]. Available: <https://www.browserbase.com/>

[183] OpenAI, "Introducing Operator," [Online]. Available: <https://openai.com/index/introducing-operator/>

[184] browser-use, "browser-use," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/browser-use/browser-use>

[185] E2B, "E2B," [Online]. Available: <https://e2b.dev/>

[186] Modal Labs, "Modal," [Online]. Available: <https://modal.com/>

[187] Daytona, "Daytona," [Online]. Available: <https://www.daytona.io/>

[188] Arize AI, "Arize," [Online]. Available: <https://arize.com/>

[189] LangChain, "LangSmith," [Online]. Available: <https://www.langchain.com/langsmith-platform>

[190] Foxglove, "Foxglove," [Online]. Available: <https://foxglove.dev/>

[191] Prometheus, "Prometheus," [Online]. Available: <https://prometheus.io/>

[192] Grafana Labs, "Grafana," [Online]. Available: <https://grafana.com/>

[193] GameAnalytics, "GameAnalytics", [Online]. Available: <https://gameanalytics.com/>

[194] Autodesk, "Flow Production Tracking (ShotGrid)", [Online]. Available: <https://www.autodesk.com/products/flow-production-tracking>

[195] Guardrails AI, "Guardrails," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/guardrails-ai/guardrails>

[196] NVIDIA, "NeMo Guardrails," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA-NeMo/Guardrails>

[197] Lakera, "Lakera," [Online]. Available: <https://www.lakera.ai/>

[198] ISO, "ISO 13482:2014 Robots and robotic devices — Safety requirements for personal care robots," [Online]. Available: <https://www.iso.org/standard/53820.html>

[199] ISO, "ISO 26262 Road vehicles — Functional safety," [Online]. Available: <https://www.iso.org/standard/68383.html>

[200] UNECE, "UN Regulation No. 157 — Automated Lane Keeping Systems (ALKS)," [Online]. Available: <https://unece.org/transport/documents/2021/03/standards/un-regulation-no-157-automated-lane-keeping-systems-alks>

[201] BattlEye, "BattlEye Anti-Cheat", [Online]. Available: <https://www.battleye.com/>

[202] Epic Games, "Easy Anti-Cheat", [Online]. Available: <https://www.easy.ac/>

[203] Valve, "Valve Anti-Cheat (VAC) System", [Online]. Available: <https://help.steampowered.com/en/faqs/view/571A-97DA-70E9-FF74>

[204] C2PA, "Coalition for Content Provenance and Authenticity", [Online]. Available: <https://c2pa.org/>

[205] Promptfoo, "Promptfoo," [Online]. Available: <https://www.promptfoo.dev/>

[206] Confident AI, "DeepEval," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/confident-ai/deepeval>

[207] Exploding Gradients, "Ragas," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/explodinggradients/ragas>

[208] ElevenLabs, "ElevenLabs," [Online]. Available: <https://elevenlabs.io/>

[209] OpenAI, "Whisper," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/whisper>

[210] Cartesia AI, "Cartesia," [Online]. Available: <https://cartesia.ai/>

[211] Deepgram, "Deepgram," [Online]. Available: <https://deepgram.com/>

[212] NVIDIA, "Riva," [Online]. Available: <https://developer.nvidia.com/riva>

[213] Cerence, "Cerence," [Online]. Available: <https://www.cerence.com/>

[214] Descript, "Descript — All-in-one video and podcast editing", [Online]. Available: <https://www.descript.com/>

[215] Adobe, "Adobe Podcast — AI audio tools", [Online]. Available: <https://podcast.adobe.com/>

[216] Midjourney, "Midjourney," [Online]. Available: <https://www.midjourney.com/>

[217] OpenAI, "Sora," [Online]. Available: <https://openai.com/sora/>

[218] Black Forest Labs, "FLUX," [Online]. Available: <https://bfl.ai/>

[219] Runway, "Runway," [Online]. Available: <https://runwayml.com/>

[220] Epic Games, "MetaHuman", [Online]. Available: <https://www.unrealengine.com/en-US/metahuman>

[221] Reallusion, "Reallusion", [Online]. Available: <https://www.reallusion.com/>

[222] Topaz Labs, "Topaz Video AI", [Online]. Available: <https://www.topazlabs.com/topaz-video-ai>

[223] Wonder Dynamics (Autodesk), "Wonder Studio", [Online]. Available: <https://wonderdynamics.com/>

[224] Anthropic, "Claude.ai," [Online]. Available: <https://claude.ai/>

[225] Microsoft, "Microsoft 365 Copilot," [Online]. Available: <https://www.microsoft.com/en-us/microsoft-365-copilot>

[226] SAP, "Joule," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/ai-assistant.html>

[227] Salesforce, "Agentforce," [Online]. Available: <https://www.salesforce.com/agentforce/>

[228] Replica Studios, "Replica Studios", [Online]. Available: <https://replicastudios.com/>

[229] Blockade Labs, "Skybox AI", [Online]. Available: <https://skybox.blockadelabs.com/>

[230] Cuebric, "Cuebric — Generative AI virtual production", [Online]. Available: <https://www.cuebric.com/>

[231] Captions, "Captions — AI creative studio", [Online]. Available: <https://www.captions.ai/>

[232] Adobe, "Adobe Firefly," [Online]. Available: <https://firefly.adobe.com/>

[233] Industrial Light & Magic, "StageCraft", [Online]. Available: <https://www.ilm.com/sandbox/stagecraft/>

[234] Altair, "PBS Professional," [Online]. Available: <https://www.altair.com/pbs-professional/>

[235] Spack Project, "Spack," [Online]. Available: <https://spack.io/>

[236] NVIDIA, "Holoscan SDK," [Online]. Available: <https://developer.nvidia.com/holoscan-sdk>

[237] NVIDIA, "DriveWorks SDK," [Online]. Available: <https://developer.nvidia.com/drive/driveworks>

[238] AUTOSAR, "AUTOSAR," [Online]. Available: <https://www.autosar.org/>

[239] OpenMM Project, "OpenMM," [Online]. Available: <https://openmm.org/>

[240] NVIDIA, "Isaac Sim," [Online]. Available: <https://developer.nvidia.com/isaac/sim>

[241] NVIDIA, "DRIVE Sim," [Online]. Available: <https://developer.nvidia.com/drive/simulation>

[242] CARLA Simulator, "CARLA," [Online]. Available: <https://carla.org/>

[243] NVIDIA, "NVIDIA Omniverse," [Online]. Available: <https://www.nvidia.com/en-us/omniverse/>

[244] Chaos, "V-Ray", [Online]. Available: <https://www.chaos.com/vray>

[245] Pixar, "RenderMan", [Online]. Available: <https://renderman.pixar.com/>

[246] Autodesk, "Arnold Renderer", [Online]. Available: <https://arnoldrenderer.com/>

[247] SideFX, "Houdini", [Online]. Available: <https://www.sidefx.com/>

[248] HERE Technologies, "HERE," [Online]. Available: <https://www.here.com/>

[249] TomTom, "TomTom," [Online]. Available: <https://www.tomtom.com/>

[250] Mapbox, "Mapbox," [Online]. Available: <https://www.mapbox.com/>

[251] NVIDIA, "NVIDIA Container Toolkit," [Online]. Available: <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html>

[252] NVIDIA, "Open GPU Kernel Modules," GitHub. [Online]. Available: <https://github.com/NVIDIA/open-gpu-kernel-modules>

[253] AMD, "ROCm Documentation (amdgpu / amdkfd)," [Online]. Available: <https://rocm.docs.amd.com/>

[254] AMD, "AMD GPU Operator," [Online]. Available: <https://instinct.docs.amd.com/projects/gpu-operator/en/latest/>

[255] Intel / Linux Kernel, "i915 Driver," [Online]. Available: <https://docs.kernel.org/gpu/i915.html>

[256] Intel Habana, "Gaudi Driver Installation," [Online]. Available: <https://docs.habana.ai/en/latest/Installation_Guide/Driver_Installation.html>

[257] Huawei, "Ascend Firmware and Driver," [Online]. Available: <https://www.hiascend.com/en/hardware/firmware-drivers/community>

[258] Apple, "Metal," Apple Developer. [Online]. Available: <https://developer.apple.com/metal/>

[259] Apple, "Accelerate Framework," [Online]. Available: <https://developer.apple.com/documentation/accelerate>

[260] AWS, "Neuron Driver," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/runtime/aws-neuronx-dkms/index.html>

[261] AWS, "Neuron Runtime," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/index.html>

[262] AMD, "AMD Infinity Architecture," [Online]. Available: <https://www.amd.com/en/technologies/infinity-architecture>

[263] Intel, "Intel Data Center GPU Max Series," [Online]. Available: <https://www.intel.com/content/www/us/en/products/docs/processors/max-series/overview.html>

[264] Huawei, "Atlas Cluster," [Online]. Available: <https://www.hiascend.com/en/hardware/cluster>

[265] Apple, "Apple unveils M1 Ultra with UltraFusion," [Online]. Available: <https://www.apple.com/newsroom/2022/03/apple-unveils-m1-ultra-the-worlds-most-powerful-chip-for-a-personal-computer/>

[266] AWS, "Trainium2 Architecture (NeuronLink)," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html>

[267] NVIDIA, "Quantum-2 InfiniBand," [Online]. Available: <https://www.nvidia.com/en-us/networking/quantum2/>

[268] AWS, "Elastic Fabric Adapter (EFA)," [Online]. Available: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html>

[269] Ultra Ethernet Consortium, "Ultra Ethernet," [Online]. Available: <https://ultraethernet.org/>

[270] UALink Consortium, "UALink," [Online]. Available: <https://ualinkconsortium.org/>

[271] Huawei, "Atlas 900 Cluster," [Online]. Available: <https://www.hiascend.com/en/hardware/cluster>

[272] AMD ROCm, "RCCL," GitHub. [Online]. Available: <https://github.com/ROCm/rccl>

[273] Intel, "oneCCL," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/oneccl.html>

[274] Huawei, "HCCL: Huawei Collective Communication Library," [Online]. Available: <https://www.hiascend.com/cann/hccl>

[275] AWS, "Neuron Collective Communication," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-runtime/about/collectives.html>

[276] Microsoft, "MSCCL++," GitHub. [Online]. Available: <https://github.com/microsoft/mscclpp>

[277] AMD ROCm, "HIP," [Online]. Available: <https://rocm.docs.amd.com/projects/HIP/en/latest/>

[278] Intel, "oneAPI DPC++/C++ Compiler," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html>

[279] Intel Habana, "Gaudi Software Suite (SynapseAI)," [Online]. Available: <https://docs.habana.ai/en/latest/Gaudi_Overview/Intel_Gaudi_Software_Suite.html>

[280] Huawei, "CANN," [Online]. Available: <https://www.hiascend.com/en/cann>

[281] Huawei, "AscendC," CANN Operator Development Guide. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/opdevg/Ascendcopdevg/atlas_ascendc_10_0036.html>

[282] Huawei, "AscendCL," CANN API Reference. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/>

[283] AWS, "Neuron SDK," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/index.html>

[284] AWS, "Neuron Kernel Interface (NKI)," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/en/latest/nki/>

[285] Microsoft, "Direct3D 12 graphics," Microsoft Learn. [Online]. Available: <https://learn.microsoft.com/en-us/windows/win32/direct3d12/direct3d-12-graphics>

[286] Microsoft, "DirectML overview," Microsoft Learn. [Online]. Available: <https://learn.microsoft.com/en-us/windows/ai/directml/dml>

[287] Microsoft, "DirectStorage API," DirectX Developer Blog. [Online]. Available: <https://devblogs.microsoft.com/directx/directstorage-api-available-on-pc/>

[288] Khronos Group, "OpenCL," [Online]. Available: <https://www.khronos.org/opencl/>

[289] Khronos Group, "Vulkan," [Online]. Available: <https://www.khronos.org/vulkan/>

[290] W3C, "WebGPU," [Online]. Available: <https://www.w3.org/TR/webgpu/>

[291] AMD ROCm, "rocBLAS," [Online]. Available: <https://rocm.docs.amd.com/projects/rocBLAS/en/latest/>

[292] Intel, "oneMKL," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html>

[293] Huawei, "CANN — Ascend Operator Library (AOL)," [Online]. Available: <https://www.hiascend.com/en/cann>

[294] Apple, "Metal Performance Shaders," [Online]. Available: <https://developer.apple.com/documentation/metalperformanceshaders>

[295] AWS, "Inferentia," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/inferentia/>

[296] AMD ROCm, "MIOpen," [Online]. Available: <https://rocm.docs.amd.com/projects/MIOpen/en/latest/>

[297] Intel, "oneDNN," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/onednn.html>

[298] Huawei, "ACLNN: Ascend Neural Network Operator Library," CANN API Reference. [Online]. Available: <https://www.hiascend.com/document/detail/en/canncommercial/800/apiref/>

[299] Apple, "BNNS — Basic Neural Network Subroutines," [Online]. Available: <https://developer.apple.com/documentation/accelerate/bnns>

[300] AMD ROCm, "Composable Kernel," GitHub. [Online]. Available: <https://github.com/ROCm/composable_kernel>

[301] Intel, "XeTLA," GitHub. [Online]. Available: <https://github.com/intel/xetla>

[302] Apple ML Research, "Distributed Communication — MLX Documentation," [Online]. Available: <https://ml-explore.github.io/mlx/build/html/usage/distributed.html>

[303] AMD ROCm, "rocFFT," [Online]. Available: <https://rocm.docs.amd.com/projects/rocFFT/en/latest/>

[304] Meta, "xFormers," GitHub. [Online]. Available: <https://github.com/facebookresearch/xformers>

[305] NVIDIA, "CUDA Compiler Driver NVCC," NVIDIA Documentation. [Online]. Available: <https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/>

[306] AMD ROCm, "HIPCC: HIP compiler driver," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ROCm/HIPCC>

[307] Intel, "Intel oneAPI DPC++/C++ Compiler," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html>

[308] Intel Habana, "Intel Gaudi Software Suite (SynapseAI)," [Online]. Available: <https://docs.habana.ai/en/latest/Gaudi_Overview/SynapseAI_Software_Suite.html>

[309] Huawei, "CANN — Compute Architecture for Neural Networks," Ascend Community. [Online]. Available: <https://www.hiascend.com/en/cann>

[310] Huawei / MindSpore, "MindSpore," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-ai/mindspore>

[311] Apple, "Metal libraries," Apple Developer. [Online]. Available: <https://developer.apple.com/documentation/metal/metal-libraries>

[312] Apple, "Core ML," Apple Developer. [Online]. Available: <https://developer.apple.com/documentation/coreml>

[313] Apple ML Research, "MLX," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/ml-explore/mlx>

[314] AWS, "AWS Neuron Documentation," [Online]. Available: <https://awsdocs-neuron.readthedocs-hosted.com/>

[315] triton-lang, "Triton," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/triton-lang/triton>

[316] PyTorch, "Introduction to torch.compile," PyTorch Tutorials. [Online]. Available: <https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html>

[317] OpenXLA Project, "XLA," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openxla/xla>

[318] Apache Software Foundation, "Apache TVM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/apache/tvm>

[319] IREE contributors, "IREE," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/iree-org/iree>

[320] Modular, "Mojo," [Online]. Available: <https://www.modular.com/open-source/mojo>

[321] Google DeepMind, "Flax," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/google/flax>

[322] Keras contributors, "Keras," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/keras-team/keras>

[323] Huawei / MindSpore, "MindSpore," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-ai/mindspore>

[324] Baidu / PaddlePaddle, "Paddle," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/PaddlePaddle/Paddle>

[325] tinygrad contributors, "tinygrad," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/tinygrad/tinygrad>

[326] NVIDIA, "NeMo," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/NeMo>

[327] HPC-AI Tech, "ColossalAI," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/hpcaitech/ColossalAI>

[328] MosaicML / Databricks, "Composer," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/composer>

[329] MosaicML / Databricks, "LLM Foundry," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mosaicml/llm-foundry>

[330] PyTorch, "TorchTitan," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pytorch/torchtitan>

[331] Huawei / MindSpore Lab, "MindFormers," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mindspore-lab/mindformers>

[332] Huawei Ascend, "ModelLink," Gitee repository, accessed 2026. [Online]. Available: <https://gitee.com/ascend/ModelLink>

[333] AWS, "Amazon SageMaker HyperPod," [Online]. Available: <https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html>

[334] WebDataset contributors, "webdataset," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/webdataset/webdataset>

[335] NVIDIA NeMo, "Curator," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA-NeMo/Curator>

[336] Allen Institute for AI, "dolma," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/allenai/dolma>

[337] Together AI, "RedPajama-Data," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/togethercomputer/RedPajama-Data>

[338] Allen Institute for AI, "allenai/dolma," Hugging Face Dataset, [Online]. Available: <https://huggingface.co/datasets/allenai/dolma>

[339] BigCode Project, "bigcode/the-stack-v2," Hugging Face Dataset. [Online]. Available: <https://huggingface.co/datasets/bigcode/the-stack-v2>

[340] Common Crawl Foundation, "Common Crawl," [Online]. Available: <https://commoncrawl.org/>

[341] hiyouga et al., "LLaMA-Factory: Unified Efficient Fine-Tuning of 100+ LLMs & VLMs," GitHub repository, ACL 2024. [Online]. Available: <https://github.com/hiyouga/LLaMA-Factory>

[342] OpenRLHF contributors, "OpenRLHF," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/OpenRLHF/OpenRLHF>

[343] NVIDIA, "NeMo-Aligner," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/NVIDIA/NeMo-Aligner>

[344] Mistral AI, "Mistral AI," [Online]. Available: <https://mistral.ai/>

[345] Google DeepMind, "Gemma open models," [Online]. Available: <https://ai.google.dev/gemma>

[346] Moonshot AI, "Kimi-K2," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/MoonshotAI/Kimi-K2>

[347] Zhipu AI / THUDM, "GLM-4," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/THUDM/GLM-4>

[348] Microsoft, "microsoft/phi-4," Hugging Face. [Online]. Available: <https://huggingface.co/microsoft/phi-4>

[349] Allen Institute for AI, "OLMo," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/allenai/OLMo>

[350] Hugging Face, "Hugging Face," [Online]. Available: <https://huggingface.co/>

[351] Alibaba / ModelScope, "ModelScope," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/modelscope/modelscope>

[352] Ollama, "Ollama Library," [Online]. Available: <https://ollama.com/library>

[353] Civitai, "Civitai," [Online]. Available: <https://civitai.com/models>

[354] EleutherAI, "lm-evaluation-harness," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/EleutherAI/lm-evaluation-harness>

[355] Stanford CRFM, "HELM," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/stanford-crfm/helm>

[356] Shanghai AI Lab, "OpenCompass," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/open-compass/opencompass>

[357] K. Cobbe et al., "Training Verifiers to Solve Math Word Problems," arXiv:2110.14168, Oct 2021. [Online]. Available: <https://arxiv.org/abs/2110.14168>

[358] M. Chen et al., "Evaluating Large Language Models Trained on Code," arXiv:2107.03374, Jul 2021. [Online]. Available: <https://arxiv.org/abs/2107.03374>

[359] D. Rein et al., "GPQA: A Graduate-Level Google-Proof Q&A Benchmark," arXiv:2311.12022, Nov 2023. [Online]. Available: <https://arxiv.org/abs/2311.12022>

[360] ARC Prize Foundation, "ARC-AGI," [Online]. Available: <https://arcprize.org/arc-agi>

[361] Center for AI Safety / Scale AI, "HLE: Humanity's Last Exam," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/centerforaisafety/hle>

[362] Sierra Research, "tau-bench," GitHub repository, 2024. [Online]. Available: <https://github.com/sierra-research/tau-bench>

[363] web-arena-x, "WebArena," GitHub repository, 2023. [Online]. Available: <https://github.com/web-arena-x/webarena>

[364] XLANG-AI, "OSWorld," GitHub repository, NeurIPS 2024. [Online]. Available: <https://github.com/xlang-ai/OSWorld>

[365] THUDM, "AgentBench," GitHub repository, ICLR 2024. [Online]. Available: <https://github.com/THUDM/AgentBench>

[366] beir-cellar, "BEIR," GitHub repository, NeurIPS 2021. [Online]. Available: <https://github.com/beir-cellar/beir>

[367] LMArena / LMSYS, "Chatbot Arena," [Online]. Available: <https://lmarena.ai/>

[368] Scale AI, "SEAL LLM Leaderboards," [Online]. Available: <https://scale.com/leaderboard>

[369] UK AI Security Institute, "Inspect," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/UKGovernmentBEIS/inspect_ai>

[370] OpenAI, "Evals," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/evals>

[371] ClearML, "ClearML," [Online]. Available: <https://clear.ml/>

[372] Comet, "Comet," [Online]. Available: <https://www.comet.com/site/>

[373] TensorFlow, "TensorBoard," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/tensorflow/tensorboard>

[374] Iterative, "DVC," [Online]. Available: <https://dvc.org/>

[375] Hugging Face, "Text Generation Inference (TGI)," GitHub. [Online]. Available: <https://github.com/huggingface/text-generation-inference>

[376] Georgi Gerganov, "GGUF Specification," GitHub. [Online]. Available: <https://github.com/ggerganov/ggml/blob/master/docs/gguf.md>

[377] MLC AI, "MLC-LLM," GitHub. [Online]. Available: <https://github.com/mlc-ai/mlc-llm>

[378] Microsoft DeepSpeed AI, "DeepSpeed-MII," GitHub. [Online]. Available: <https://github.com/deepspeedai/DeepSpeed-MII>

[379] InternLM, "LMDeploy," GitHub. [Online]. Available: <https://github.com/InternLM/lmdeploy>

[380] Ollama, "Ollama," [Online]. Available: <https://ollama.com/>

[381] AMD ROCm, "AITER," GitHub. [Online]. Available: <https://github.com/ROCm/aiter>

[382] Intel, "OpenVINO," GitHub. [Online]. Available: <https://github.com/openvinotoolkit/openvino>

[383] Intel, "IPEX-LLM," GitHub. [Online]. Available: <https://github.com/intel/ipex-llm>

[384] Huawei, "MindIE," [Online]. Available: <https://www.hiascend.com/en/developer/software/mindie>

[385] Huawei, "MindSpore Lite," [Online]. Available: <https://www.mindspore.cn/lite/en>

[386] Apple, "Metal Performance Shaders Graph," [Online]. Available: <https://developer.apple.com/documentation/metalperformanceshadersgraph>

[387] AWS, "Neuron SDK (Transformers-Neuronx)," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/neuron/>

[388] DeepJavaLibrary, "DJL Serving," GitHub. [Online]. Available: <https://github.com/deepjavalibrary/djl-serving>

[389] Microsoft / ONNX Runtime contributors, "ONNX Runtime," [Online]. Available: <https://onnxruntime.ai/>

[390] Microsoft, "Windows ML overview," Microsoft Learn. [Online]. Available: <https://learn.microsoft.com/en-us/windows/ai/windows-ml/overview>

[391] Microsoft, "Olive: Hardware-aware model optimization tool chain," GitHub. [Online]. Available: <https://github.com/microsoft/Olive>

[392] KServe Project, "KServe," GitHub. [Online]. Available: <https://github.com/kserve/kserve>

[393] Sandia National Laboratories, "LAMMPS Molecular Dynamics Simulator," *lammps.org*, 2025. [Online]. Available: <https://lammps.org/>

[394] Beam, "Beam," [Online]. Available: <https://www.beam.cloud/>

[395] Replicate, "Cog," GitHub. [Online]. Available: <https://github.com/replicate/cog>

[396] Seldon, "Seldon Core," GitHub. [Online]. Available: <https://github.com/SeldonIO/seldon-core>

[397] NVIDIA, "NIM Microservices," [Online]. Available: <https://developer.nvidia.com/nim>

[398] AMD / Xilinx, "Inference Server," GitHub. [Online]. Available: <https://github.com/Xilinx/inference-server>

[399] Intel, "OpenVINO Model Server (OVMS)," GitHub. [Online]. Available: <https://github.com/openvinotoolkit/model_server>

[400] Huawei, "MindCluster (Atlas)," [Online]. Available: <https://www.hiascend.com/en>

[401] Huawei Cloud, "ModelArts," [Online]. Available: <https://www.huaweicloud.com/intl/en-us/product/modelarts.html>

[402] Apple, "Private Cloud Compute," [Online]. Available: <https://security.apple.com/documentation/private-cloud-compute>

[403] AWS, "Amazon SageMaker," [Online]. Available: <https://aws.amazon.com/sagemaker/>

[404] AWS, "Amazon Bedrock," [Online]. Available: <https://aws.amazon.com/bedrock/>

[405] AWS, "Trainium," [Online]. Available: <https://aws.amazon.com/ai/machine-learning/trainium/>

[406] Voltage Park, "Voltage Park," [Online]. Available: <https://www.voltagepark.com/>

[407] Applied Digital, "Applied Digital," [Online]. Available: <https://www.applieddigital.com/>

[408] Vast.ai, "Vast.ai," [Online]. Available: <https://vast.ai/>

[409] TensorDock, "TensorDock," [Online]. Available: <https://www.tensordock.com/>

[410] Salad, "Salad," [Online]. Available: <https://salad.com/>

[411] Hyperstack, "Hyperstack," [Online]. Available: <https://www.hyperstack.cloud/>

[412] Lepton AI (NVIDIA), "Lepton AI," [Online]. Available: <https://www.lepton.ai/>

[413] TensorWave, "TensorWave," [Online]. Available: <https://tensorwave.com/>

[414] Hot Aisle, "Hot Aisle," [Online]. Available: <https://hotaisle.xyz/>

[415] Vultr, "Cloud GPU," [Online]. Available: <https://www.vultr.com/products/cloud-gpu/>

[416] Intel, "Intel Tiber AI Cloud," [Online]. Available: <https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html>

[417] Huawei Cloud, "ModelArts," [Online]. Available: <https://www.huaweicloud.com/intl/en-us/product/modelarts.html>

[418] Cerebras, "Cerebras Inference," [Online]. Available: <https://www.cerebras.ai/inference>

[419] SambaNova, "SambaCloud," [Online]. Available: <https://sambanova.ai/products/sambacloud>

[420] DeepInfra, "DeepInfra," [Online]. Available: <https://deepinfra.com/>

[421] Anyscale, "Anyscale Endpoints," [Online]. Available: <https://www.anyscale.com/>

[422] Hyperbolic, "Hyperbolic," [Online]. Available: <https://www.hyperbolic.ai/>

[423] Google Cloud, "Vertex AI," [Online]. Available: <https://cloud.google.com/vertex-ai>

[424] xAI, "xAI API," [Online]. Available: <https://x.ai/api>

[425] DeepSeek, "DeepSeek API Documentation," [Online]. Available: <https://api-docs.deepseek.com/>

[426] Microsoft Azure, "Azure OpenAI Service," [Online]. Available: <https://azure.microsoft.com/en-us/products/ai-foundry/models/openai/>

[427] IBM, "watsonx," [Online]. Available: <https://www.ibm.com/products/watsonx>

[428] Databricks, "Foundation Model APIs," [Online]. Available: <https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/>

[429] SAP, "Generative AI Hub on BTP," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/generative-ai-hub.html>

[430] Oracle, "Generative AI Service," [Online]. Available: <https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/>

[431] deepset, "Haystack," [Online]. Available: <https://haystack.deepset.ai/>

[432] Microsoft, "Semantic Kernel," [Online]. Available: <https://learn.microsoft.com/en-us/semantic-kernel/>

[433] Mastra, "Mastra," [Online]. Available: <https://mastra.ai/>

[434] VMware (Broadcom), "Spring AI," [Online]. Available: <https://spring.io/projects/spring-ai/>

[435] OpenAI, "Embeddings," [Online]. Available: <https://platform.openai.com/docs/guides/embeddings>

[436] Cohere, "Rerank," [Online]. Available: <https://cohere.com/rerank>

[437] Google Cloud, "Vertex AI Embeddings," [Online]. Available: <https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings>

[438] Voyage AI, "Voyage AI," [Online]. Available: <https://www.voyageai.com/>

[439] Jina AI, "Jina Embeddings," [Online]. Available: <https://jina.ai/embeddings/>

[440] Nomic AI, "Nomic," [Online]. Available: <https://www.nomic.ai/>

[441] Microsoft Research, "E5: Text Embeddings," GitHub. [Online]. Available: <https://github.com/microsoft/unilm/tree/master/e5>

[442] Alibaba NLP, "GTE Models," Hugging Face. [Online]. Available: <https://huggingface.co/collections/Alibaba-NLP/gte-models>

[443] NovaSearch, "stella_en_1.5B_v5," Hugging Face. [Online]. Available: <https://huggingface.co/NovaSearch/stella_en_1.5B_v5>

[444] Mixedbread AI, "Mixedbread," [Online]. Available: <https://www.mixedbread.com/>

[445] OpenAI, "CLIP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/openai/CLIP>

[446] ML Foundations, "OpenCLIP," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/mlfoundations/open_clip>

[447] Google / Hugging Face, "SigLIP," [Online]. Available: <https://huggingface.co/docs/transformers/model_doc/siglip>

[448] Jina AI, "jina-clip-v2," [Online]. Available: <https://jina.ai/models/jina-clip-v2/>

[449] Chroma, "Chroma," [Online]. Available: <https://www.trychroma.com/>

[450] LanceDB, "LanceDB," [Online]. Available: <https://www.lancedb.com/>

[451] Spotify, "Annoy," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/spotify/annoy>

[452] Google Research, "ScaNN," GitHub. [Online]. Available: <https://github.com/google-research/google-research/tree/master/scann>

[453] pgvector contributors, "pgvector," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/pgvector/pgvector>

[454] Supabase, "Supabase Vector," [Online]. Available: <https://supabase.com/modules/vector>

[455] Neon (Databricks), "Neon Serverless Postgres," [Online]. Available: <https://neon.com/>

[456] Elastic, "Elasticsearch," [Online]. Available: <https://www.elastic.co/elasticsearch>

[457] OpenSearch Project, "OpenSearch," [Online]. Available: <https://opensearch.org/>

[458] Vespa.ai, "Vespa," [Online]. Available: <https://vespa.ai/>

[459] Typesense, "Typesense," [Online]. Available: <https://typesense.org/>

[460] Meili SAS, "Meilisearch," [Online]. Available: <https://www.meilisearch.com/>

[461] Turbopuffer, "Turbopuffer," [Online]. Available: <https://turbopuffer.com/>

[462] Redis, "Vector Database," [Online]. Available: <https://redis.io/solutions/vector-database/>

[463] Alex Garcia, "sqlite-vec," GitHub. [Online]. Available: <https://github.com/asg017/sqlite-vec>

[464] LangChain AI, "LangMem," GitHub. [Online]. Available: <https://github.com/langchain-ai/langmem>

[465] Cognee, "Cognee," [Online]. Available: <https://www.cognee.ai/>

[466] Anthropic, "Memory tool," Claude API Docs. [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/memory-tool>

[467] Kong, "Kong AI Gateway," [Online]. Available: <https://konghq.com/products/kong-ai-gateway>

[468] Helicone, "Helicone," [Online]. Available: <https://www.helicone.ai/>

[469] Martian, "Martian," [Online]. Available: <https://withmartian.com/>

[470] SAP, "Joule," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/ai-assistant.html>

[471] Langfuse, "Prompt Management," [Online]. Available: <https://langfuse.com/docs/prompts>

[472] Helicone, "Helicone," [Online]. Available: <https://www.helicone.ai/>

[473] Latitude, "Latitude," [Online]. Available: <https://latitude.so/>

[474] Agenta, "Agenta," [Online]. Available: <https://agenta.ai/>

[475] Anthropic, "Prompt Caching," [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>

[476] OpenAI, "Prompt Caching," [Online]. Available: <https://platform.openai.com/docs/guides/prompt-caching>

[477] Google, "Gemini Context Caching," [Online]. Available: <https://ai.google.dev/gemini-api/docs/caching>

[478] OpenAI, "Agents SDK," [Online]. Available: <https://openai.github.io/openai-agents-python/>

[479] OpenAI, "Swarm," GitHub. [Online]. Available: <https://github.com/openai/swarm>

[480] CrewAI, "CrewAI," [Online]. Available: <https://crewai.com/>

[481] Pydantic, "PydanticAI," [Online]. Available: <https://ai.pydantic.dev/>

[482] Hugging Face, "smolagents," GitHub. [Online]. Available: <https://github.com/huggingface/smolagents>

[483] Inngest, "AgentKit," [Online]. Available: <https://agentkit.inngest.com/>

[484] Microsoft, "TaskWeaver," GitHub. [Online]. Available: <https://github.com/microsoft/TaskWeaver>

[485] Microsoft Azure, "AI Foundry," [Online]. Available: <https://azure.microsoft.com/en-us/products/ai-foundry/>

[486] AWS, "Amazon Bedrock Agents," [Online]. Available: <https://aws.amazon.com/bedrock/agents/>

[487] Google Cloud, "Vertex AI Agent Builder," [Online]. Available: <https://cloud.google.com/products/agent-builder>

[488] Databricks, "Mosaic AI Agent Framework," [Online]. Available: <https://www.databricks.com/product/machine-learning/retrieval-augmented-generation>

[489] SAP, "Joule Studio," [Online]. Available: <https://www.sap.com/products/artificial-intelligence/joule-studio.html>

[490] ServiceNow, "AI Agents," [Online]. Available: <https://www.servicenow.com/products/ai-agents.html>

[491] Toolhouse, "Toolhouse," [Online]. Available: <https://toolhouse.ai/>

[492] Pipedream, "Pipedream Connect," [Online]. Available: <https://pipedream.com/connect>

[493] Zapier, "Zapier MCP," [Online]. Available: <https://zapier.com/mcp>

[494] Stripe, "Stripe Agent Toolkit," GitHub. [Online]. Available: <https://github.com/stripe/agent-toolkit>

[495] Cloudflare, "Cloudflare Agents," [Online]. Available: <https://developers.cloudflare.com/agents/>

[496] Cloudflare, "Model Context Protocol on Cloudflare," [Online]. Available: <https://developers.cloudflare.com/agents/model-context-protocol/>

[497] Cloudflare, "Introducing pay-per-crawl: enabling content owners to charge a price of their choice," [Online]. Available: <https://blog.cloudflare.com/introducing-pay-per-crawl/>

[498] Anthropic, "Agent Skills," [Online]. Available: <https://www.anthropic.com/news/agent-skills>

[499] Atlassian, "Remote MCP Server," [Online]. Available: <https://www.atlassian.com/platform/remote-mcp-server>

[500] Spectre Console, "OpenCLI Specification," [Online]. Available: <https://opencli.org/>

[501] HKUDS, "CLI-Anything," GitHub. [Online]. Available: <https://github.com/HKUDS/CLI-Anything>

[502] Smithery, "Smithery," [Online]. Available: <https://smithery.ai/>

[503] PulseMCP, "PulseMCP," [Online]. Available: <https://www.pulsemcp.com/>

[504] Glama, "MCP Registry," [Online]. Available: <https://glama.ai/mcp>

[505] Anthropic, "Computer Use Tool," [Online]. Available: <https://docs.anthropic.com/en/docs/build-with-claude/computer-use>

[506] Google DeepMind, "Project Mariner," [Online]. Available: <https://deepmind.google/models/project-mariner/>

[507] Hyperbrowser, "Hyperbrowser," [Online]. Available: <https://www.hyperbrowser.ai/>

[508] Steel, "Steel," [Online]. Available: <https://steel.dev/>

[509] Anchor Browser, "Anchor Browser," [Online]. Available: <https://anchorbrowser.io/>

[510] TinyFish, "AgentQL," [Online]. Available: <https://www.agentql.com/>

[511] Browserless, "Browserless," [Online]. Available: <https://www.browserless.io/>

[512] Skyvern AI, "Skyvern," [Online]. Available: <https://www.skyvern.com/>

[513] Browserbase, "Stagehand," GitHub. [Online]. Available: <https://github.com/browserbase/stagehand>

[514] nut-tree, "nut.js," [Online]. Available: <https://nutjs.dev/>

[515] Open Interpreter, "Open Interpreter," [Online]. Available: <https://www.openinterpreter.com/>

[516] Microsoft, "Playwright MCP," GitHub. [Online]. Available: <https://github.com/microsoft/playwright-mcp>

[517] Vercel Labs, "agent-browser," GitHub. [Online]. Available: <https://github.com/vercel-labs/agent-browser>

[518] Manus, "Manus," [Online]. Available: <https://manus.im/>

[519] Reworkd, "Reworkd," [Online]. Available: <https://www.reworkd.ai/>

[520] MultiOn, "MultiOn," [Online]. Available: <https://multion.ai/>

[521] CodeSandbox, "CodeSandbox SDK," [Online]. Available: <https://codesandbox.io/sdk>

[522] Cloudflare, "Cloudflare Containers," [Online]. Available: <https://developers.cloudflare.com/containers/>

[523] Replit, "Replit Agent," [Online]. Available: <https://replit.com/products/agent>

[524] Arize AI, "Phoenix," [Online]. Available: <https://phoenix.arize.com/>

[525] Arize AI, "Arize AX," [Online]. Available: <https://arize.com/>

[526] Pydantic, "Pydantic Logfire," [Online]. Available: <https://logfire.pydantic.dev/>

[527] Weights & Biases, "W&B Weave," [Online]. Available: <https://wandb.ai/site/weave/>

[528] Datadog, "LLM Observability," [Online]. Available: <https://www.datadoghq.com/product/ai/llm-observability/>

[529] New Relic, "AI Monitoring," [Online]. Available: <https://newrelic.com/platform/ai-monitoring>

[530] Splunk, "Observability Cloud," [Online]. Available: <https://www.splunk.com/en_us/products/observability-cloud.html>

[531] Lakera, "Lakera Guard," [Online]. Available: <https://www.lakera.ai/lakera-guard>

[532] Protect AI (Palo Alto Networks), "Protect AI," [Online]. Available: <https://protectai.com/>

[533] Protect AI, "NB Defense," GitHub. [Online]. Available: <https://github.com/protectai/nbdefense>

[534] Robust Intelligence (Cisco), "Robust Intelligence," [Online]. Available: <https://www.robustintelligence.com/>

[535] Prompt Security, "Prompt Security," [Online]. Available: <https://prompt.security/>

[536] HiddenLayer, "HiddenLayer," [Online]. Available: <https://www.hiddenlayer.com/>

[537] CalypsoAI (F5), "CalypsoAI," [Online]. Available: <https://calypsoai.com/>

[538] Meta, "Prompt Guard," [Online]. Available: <https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/>

[539] Patronus AI, "Patronus AI," [Online]. Available: <https://www.patronus.ai/>

[540] TruEra (Snowflake), "TruLens," [Online]. Available: <https://www.trulens.org/>

[541] Galileo, "Galileo AI," [Online]. Available: <https://galileo.ai/>

[542] PlayHT, "PlayHT," [Online]. Available: <https://play.ht/>

[543] Hume AI, "Hume AI," [Online]. Available: <https://www.hume.ai/>

[544] Resemble AI, "Resemble AI," [Online]. Available: <https://www.resemble.ai/>

[545] OpenAI, "Text to speech," [Online]. Available: <https://platform.openai.com/docs/guides/text-to-speech>

[546] Google, "Chirp 3," [Online]. Available: <https://cloud.google.com/text-to-speech/docs/chirp3-hd>

[547] Alibaba / FunAudioLLM, "CosyVoice," GitHub. [Online]. Available: <https://github.com/FunAudioLLM/CosyVoice>

[548] AssemblyAI, "AssemblyAI," [Online]. Available: <https://www.assemblyai.com/>

[549] Speechmatics, "Speechmatics," [Online]. Available: <https://www.speechmatics.com/>

[550] Rev AI, "Rev AI," [Online]. Available: <https://www.rev.ai/>

[551] NVIDIA, "NeMo Parakeet ASR Models," [Online]. Available: <https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/>

[552] Google, "Chirp Transcription Models," [Online]. Available: <https://cloud.google.com/speech-to-text/docs/models/chirp-3>

[553] OpenAI, "Realtime API," [Online]. Available: <https://platform.openai.com/docs/guides/realtime>

[554] Google, "Gemini Live API," [Online]. Available: <https://ai.google.dev/gemini-api/docs/live-api>

[555] Sesame AI, "Sesame AI," [Online]. Available: <https://www.sesame.com/>

[556] Kyutai, "Kyutai," [Online]. Available: <https://kyutai.org/>

[557] LiveKit, "LiveKit," [Online]. Available: <https://livekit.io/>

[558] Daily.co, "Pipecat," [Online]. Available: <https://www.pipecat.ai/>

[559] Vapi, "Vapi," [Online]. Available: <https://vapi.ai/>

[560] Retell AI, "Retell AI," [Online]. Available: <https://www.retellai.com/>

[561] Ideogram, "Ideogram," [Online]. Available: <https://ideogram.ai/>

[562] Google DeepMind, "Imagen 3," [Online]. Available: <https://deepmind.google/technologies/imagen-3/>

[563] OpenAI, "DALL-E 3," [Online]. Available: <https://openai.com/index/dall-e-3/>

[564] Recraft, "Recraft," [Online]. Available: <https://www.recraft.ai/>

[565] Stability AI, "Stability AI," [Online]. Available: <https://stability.ai/>

[566] PixArt-alpha, "PixArt-Σ," GitHub. [Online]. Available: <https://github.com/PixArt-alpha/PixArt-sigma>

[567] Tencent, "HunyuanImage-3.0," GitHub. [Online]. Available: <https://github.com/Tencent-Hunyuan/HunyuanImage-3.0>

[568] Comfy Org, "ComfyUI," GitHub. [Online]. Available: <https://github.com/Comfy-Org/ComfyUI>

[569] AUTOMATIC1111, "stable-diffusion-webui," GitHub. [Online]. Available: <https://github.com/AUTOMATIC1111/stable-diffusion-webui>

[570] lllyasviel, "Fooocus," GitHub. [Online]. Available: <https://github.com/lllyasviel/Fooocus>

[571] Pika Labs, "Pika," [Online]. Available: <https://pika.art/>

[572] Luma AI, "Dream Machine," [Online]. Available: <https://lumalabs.ai/dream-machine>

[573] Kuaishou, "Kling AI," [Online]. Available: <https://app.klingai.com/global>

[574] MiniMax, "Hailuo AI," [Online]. Available: <https://hailuoai.video/>

[575] Google DeepMind, "Veo," [Online]. Available: <https://deepmind.google/technologies/veo/>

[576] Tencent, "HunyuanVideo," GitHub. [Online]. Available: <https://github.com/Tencent-Hunyuan/HunyuanVideo>

[577] Alibaba / Wan-Video, "Wan2.2," GitHub. [Online]. Available: <https://github.com/Wan-Video/Wan2.2>

[578] Luma AI, "Luma," [Online]. Available: <https://lumalabs.ai/>

[579] Meshy, "Meshy AI," [Online]. Available: <https://www.meshy.ai/>

[580] Tripo AI, "Tripo," [Online]. Available: <https://www.tripo3d.ai/>

[581] DeemosTech, "Rodin," [Online]. Available: <https://hyper3d.ai/>

[582] World Labs, "World Labs," [Online]. Available: <https://www.worldlabs.ai/>

[583] Common Sense Machines, "CSM," [Online]. Available: <https://www.csm.ai/>

[584] Google, "Gemini," [Online]. Available: <https://gemini.google.com/>

[585] xAI, "Grok," [Online]. Available: <https://grok.com/>

[586] DeepSeek, "DeepSeek Chat," [Online]. Available: <https://chat.deepseek.com/>

[587] Moonshot AI, "Kimi," [Online]. Available: <https://kimi.moonshot.cn/>

[588] Alibaba Cloud, "通义千问," [Online]. Available: <https://tongyi.aliyun.com/>

[589] ByteDance, "豆包," [Online]. Available: <https://www.doubao.com/>

[590] Perplexity AI, "Perplexity," [Online]. Available: <https://www.perplexity.ai/>

[591] You.com, "You.com," [Online]. Available: <https://you.com/>

[592] Brave Software, "Brave Leo AI," [Online]. Available: <https://brave.com/leo/>

[593] The Browser Company, "Arc Search," [Online]. Available: <https://arc.net/search>

[594] Komo, "Komo AI," [Online]. Available: <https://komo.ai/>

[595] Quora, "Poe," [Online]. Available: <https://poe.com/>

[596] Mistral AI, "Le Chat," [Online]. Available: <https://mistral.ai/products/le-chat>

[597] Hugging Face, "HuggingChat," [Online]. Available: <https://huggingface.co/chat/>

[598] Msty AI, "Msty," [Online]. Available: <https://msty.ai/>

[599] LM Studio, "LM Studio," [Online]. Available: <https://lmstudio.ai/>

[600] Google, "AI Tools for Business," Google Workspace. [Online]. Available: <https://workspace.google.com/solutions/ai/>

[601] Slack (Salesforce), "Slack AI," [Online]. Available: <https://slack.com/features/ai>

[602] Notion Labs, "Notion," [Online]. Available: <https://www.notion.com/>

[603] Glean, "Glean," [Online]. Available: <https://www.glean.com/>

[604] Anthropic, "Claude Code," [Online]. Available: <https://claude.ai/code>

[605] Codeium / OpenAI, "Windsurf," [Online]. Available: <https://windsurf.com/>

[606] Replit, "Replit Agent," [Online]. Available: <https://replit.com/products/agent>

[607] OpenAI, "Codex," GitHub. [Online]. Available: <https://github.com/openai/codex>

[608] Aider AI, "Aider," [Online]. Available: <https://aider.chat/>

[609] GitHub (Microsoft), "Copilot Workspace," GitHub Next. [Online]. Available: <https://githubnext.com/projects/copilot-workspace/>

[610] Augment Code, "Augment Code," [Online]. Available: <https://www.augmentcode.com/>

[611] Sourcegraph, "Amp," [Online]. Available: <https://ampcode.com/>

[612] Lovable, "Lovable," [Online]. Available: <https://lovable.dev/>

[613] StackBlitz, "Bolt," [Online]. Available: <https://bolt.new/>

[614] Vercel, "v0," [Online]. Available: <https://v0.app/>

[615] Figma, "Figma AI," [Online]. Available: <https://www.figma.com/ai/>

[616] Figma, "Figma Make," [Online]. Available: <https://www.figma.com/make/>

[617] Google (formerly Galileo AI), "Figma Make," [Online]. Available: <https://www.figma.com/make/>

[618] Framer, "Framer AI," [Online]. Available: <https://www.framer.com/ai/>

[619] Canva, "Canva AI," [Online]. Available: <https://www.canva.com/canva-ai/>

[620] Jasper AI, "Jasper," [Online]. Available: <https://www.jasper.ai/>

[621] Copy.ai, "Copy.ai," [Online]. Available: <https://www.copy.ai/>

[622] Decagon AI, "Decagon," [Online]. Available: <https://decagon.ai/>

[623] Sierra AI, "Sierra," [Online]. Available: <https://sierra.ai/>

[624] Ada Support, "Ada," [Online]. Available: <https://www.ada.cx/>

[625] Intercom, "Fin," [Online]. Available: <https://fin.ai/>

[626] Cresta AI, "Cresta," [Online]. Available: <https://cresta.com/>

[627] Clay Labs, "Clay," [Online]. Available: <https://www.clay.com/>

[628] 11x, "11x," [Online]. Available: <https://www.11x.ai/>

[629] AirOps, "AirOps," [Online]. Available: <https://www.airops.com/>

[630] Glean, "Glean," [Online]. Available: <https://www.glean.com/>

[631] Moveworks (ServiceNow), "Moveworks," [Online]. Available: <https://www.moveworks.com/>

[632] Hebbia, "Hebbia," [Online]. Available: <https://www.hebbia.com/>

[633] Counsel AI, "Harvey," [Online]. Available: <https://www.harvey.ai/>

[634] Thomson Reuters, "CoCounsel," [Online]. Available: <https://cocounsel.thomsonreuters.com/>

[635] Oracle, "AI Agents for Fusion Applications," [Online]. Available: <https://www.oracle.com/applications/fusion-ai/ai-agents/>

[636] Workday, "AI Solutions," [Online]. Available: <https://www.workday.com/en-us/artificial-intelligence.html>

[637] ServiceNow, "Now Assist," [Online]. Available: <https://www.servicenow.com/platform/now-assist.html>

[638] Microsoft, "Dynamics 365 Copilot," [Online]. Available: <https://www.microsoft.com/en-us/dynamics-365/>

[639] CodeRabbit, "CodeRabbit," [Online]. Available: <https://www.coderabbit.ai/>

[640] Greptile, "Greptile," [Online]. Available: <https://www.greptile.com/>

[641] Qodo, "Qodo," [Online]. Available: <https://www.qodo.ai/>

[642] Meticulous AI, "Meticulous," [Online]. Available: <https://www.meticulous.ai/>

[643] Snyk, "DeepCode AI," [Online]. Available: <https://snyk.io/platform/deepcode-ai/>

[644] Abridge, "Abridge," [Online]. Available: <https://www.abridge.com/>

[645] Hippocratic AI, "Hippocratic AI," [Online]. Available: <https://hippocraticai.com/>

[646] Ambience Healthcare, "Ambience," [Online]. Available: <https://www.ambiencehealthcare.com/>

[647] FutureHouse, "FutureHouse," [Online]. Available: <https://www.futurehouse.org/>

[648] Scite (Research Solutions), "Scite," [Online]. Available: <https://scite.ai/>

[649] OpenMP Architecture Review Board, "OpenMP," *openmp.org*, 2025. [Online]. Available: <https://www.openmp.org/>

[650] Open MPI Project, "Open MPI: Open Source High Performance Computing," *open-mpi.org*, 2025. [Online]. Available: <https://www.open-mpi.org/>

[651] Argonne National Laboratory, "MPICH High-Performance Portable MPI," *mpich.org*, 2025. [Online]. Available: <https://www.mpich.org/>

[652] NVIDIA, "NVIDIA HPC-X Software Toolkit," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/networking/hpc-x>

[653] UCX Consortium, "Unified Communication X (UCX)," *openucx.org*, 2025. [Online]. Available: <https://openucx.org/>

[654] Altair, "PBS Professional – HPC Workload Management," *altair.com*, 2025. [Online]. Available: <https://altair.com/pbs-professional>

[655] IBM, "IBM Spectrum LSF – HPC Workload Management," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/products/hpc-workload-management>

[656] EasyBuild Community, "EasyBuild: Building Software with Ease," *easybuild.io*, 2025. [Online]. Available: <https://easybuild.io/>

[657] Theoretical and Computational Biophysics Group, UIUC, "NAMD Scalable Molecular Dynamics," *ks.uiuc.edu*, 2025. [Online]. Available: <https://www.ks.uiuc.edu/Research/namd/>

[658] AMBER Developers, "AMBER Molecular Dynamics Package," *ambermd.org*, 2025. [Online]. Available: <https://ambermd.org/>

[659] Schrödinger, Inc., "Schrödinger Computational Chemistry Suite," *schrodinger.com*, 2025. [Online]. Available: <https://www.schrodinger.com/>

[660] NVIDIA, "CUDA-Q: A Platform for Hybrid Quantum-Classical Computing," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/cuda-q>

[661] IBM, "Qiskit: Open-Source Quantum Development," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/quantum/qiskit>

[662] Google, "Cirq: A Python Framework for Creating, Editing, and Invoking Noisy Intermediate Scale Quantum (NISQ) Circuits," *quantumai.google*, 2025. [Online]. Available: <https://quantumai.google/cirq>

[663] Xanadu, "PennyLane: A Cross-Platform Python Library for Differentiable Programming of Quantum Computers," *pennylane.ai*, 2025. [Online]. Available: <https://pennylane.ai/>

[664] Quantinuum, "TKET Quantum Computing Toolkit," *quantinuum.com*, 2025. [Online]. Available: <https://www.quantinuum.com/products-solutions/developer-tools>

[665] NVIDIA, "cuOpt: GPU-Accelerated Route Optimization," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/ai-data-science/products/cuopt/>

[666] Gurobi Optimization, "Gurobi Optimizer," *gurobi.com*, 2025. [Online]. Available: <https://www.gurobi.com/>

[667] IBM, "IBM ILOG CPLEX Optimization Studio," *ibm.com*, 2025. [Online]. Available: <https://www.ibm.com/products/ilog-cplex-optimization-studio>

[668] Google, "OR-Tools: Open Source Software for Combinatorial Optimization," *developers.google.com*, 2025. [Online]. Available: <https://developers.google.com/optimization>

[669] COIN-OR Foundation, "Computational Infrastructure for Operations Research," *coin-or.org*, 2025. [Online]. Available: <https://www.coin-or.org/>

[670] Ansys, "Ansys Fluent – Fluid Simulation Software," *ansys.com*, 2025. [Online]. Available: <https://www.ansys.com/products/fluids/ansys-fluent>

[671] Siemens, "Simcenter STAR-CCM+: Multiphysics CFD Software," *siemens.com*, 2025. [Online]. Available: <https://www.siemens.com/en-us/products/simcenter/fluids-thermal-simulation/star-ccm/>

[672] NVIDIA, "PhysicsNeMo (formerly Modulus): Physics-Informed Neural Operator Framework," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/physicsnemo>

[673] TU Munich Physics-based Simulation Group, "PhiFlow: A Research-Oriented Differentiable Fluid Simulation Framework," *GitHub*, 2025. [Online]. Available: <https://github.com/tum-pbs/PhiFlow>

[674] Google Research, "JAX-CFD: Computational Fluid Dynamics in JAX," *GitHub*, 2025. [Online]. Available: <https://github.com/google/jax-cfd>

[675] Baker Lab, University of Washington, "RoseTTAFold All-Atom," *GitHub*, 2024. [Online]. Available: <https://github.com/baker-laboratory/RoseTTAFold-All-Atom>

[676] EvolutionaryScale, "ESM-3: Simulating 500 Million Years of Evolution with a Language Model," *evolutionaryscale.ai*, 2024. [Online]. Available: <https://www.evolutionaryscale.ai/>

[677] MIT, "Boltz-1: Democratizing Biomolecular Structure Prediction," *GitHub*, 2024. [Online]. Available: <https://github.com/jwohlwend/boltz>

[678] Chai Discovery, "Chai-1: A Multi-Modal Foundation Model for Molecular Structure Prediction," *chaidiscovery.com*, 2024. [Online]. Available: <https://www.chaidiscovery.com/>

[679] NVIDIA, "BioNeMo MolMIM: Molecular Generation NIM," *NVIDIA Docs*, 2025. [Online]. Available: <https://docs.nvidia.com/nim/bionemo/molmim/latest/overview.html>

[680] Columbia University & other contributors, "OpenFold: A Trainable, Open-Source Implementation of AlphaFold2," *openfold.io*, 2024. [Online]. Available: <https://openfold.io/>

[681] G. Corso et al., "DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking," *GitHub*, 2023. [Online]. Available: <https://github.com/gcorso/DiffDock>

[682] Insilico Medicine, "Pharma.AI: AI Drug Discovery Platform," *pharma.ai*, 2025. [Online]. Available: <https://pharma.ai/>

[683] Google DeepMind, "GenCast: Predicts Weather and the Risks of Extreme Conditions," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/>

[684] Huawei, "Pangu-Weather: Accurate Medium-Range Global Weather Forecasting (Nature 2023)," *GitHub*, 2023. [Online]. Available: <https://github.com/198808xc/Pangu-Weather>

[685] NVIDIA, "FourCastNet: Fourier Forecasting Neural Network for Global Weather Prediction," *GitHub*, 2023. [Online]. Available: <https://github.com/NVlabs/FourCastNet>

[686] Microsoft Research, "Aurora: A Foundation Model of the Atmosphere," *Microsoft Research*, 2024. [Online]. Available: <https://www.microsoft.com/en-us/research/project/aurora-forecasting/>

[687] Fudan University, "FuXi: A Cascade Machine Learning Forecasting System for 15-Day Global Weather Forecast," *GitHub*, 2023. [Online]. Available: <https://github.com/tpys/FuXi>

[688] ECMWF, "AIFS – New ECMWF AI Forecasting System," *ecmwf.int*, 2024. [Online]. Available: <https://www.ecmwf.int/en/newsletter/178/news/aifs-new-ecmwf-forecasting-system>

[689] University of Cambridge, "MACE: Fast and Accurate Machine Learning Interatomic Potentials," *GitHub*, 2024. [Online]. Available: <https://github.com/ACEsuit/mace>

[690] MIT & Harvard, "NequIP: E(3)-equivariant Neural Network Interatomic Potentials," *GitHub*, 2023. [Online]. Available: <https://github.com/mir-group/nequip>

[691] MIT, "Allegro: Scalable and Transferable Interatomic Potentials," *GitHub*, 2023. [Online]. Available: <https://github.com/mir-group/allegro>

[692] Google DeepMind, "GNoME: Millions of New Materials Discovered with Deep Learning," *deepmind.google*, 2023. [Online]. Available: <https://deepmind.google/blog/millions-of-new-materials-discovered-with-deep-learning/>

[693] Orbital Materials, "Orb: Fast and Accurate Machine Learning Potentials," *orbitalindustries.com*, 2024. [Online]. Available: <https://www.orbitalindustries.com/>

[694] Google DeepMind, "AI Solves IMO Problems at Silver Medal Level (AlphaProof + AlphaGeometry 2)," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/>

[695] Google DeepMind, "FunSearch: Making New Discoveries in Mathematical Sciences Using Large Language Models," *GitHub*, 2024. [Online]. Available: <https://github.com/google-deepmind/funsearch>

[696] Lean Prover Community, "Lean: A Functional Programming Language and Theorem Prover," *leanprover-community.github.io*, 2025. [Online]. Available: <https://leanprover-community.github.io/>

[697] DeepSeek AI, "DeepSeek-Prover-V2," *GitHub*, 2025. [Online]. Available: <https://github.com/deepseek-ai/DeepSeek-Prover-V2>

[698] C. Theodoris et al., "Geneformer: Transfer Learning with Context-Aware Gene Network Foundations," *Hugging Face*, 2023. [Online]. Available: <https://huggingface.co/ctheodoris/Geneformer>

[699] Tsinghua University & BioMap, "scFoundation: Large-Scale Foundation Model on Single-Cell Transcriptomics," *GitHub*, 2024. [Online]. Available: <https://github.com/biomap-research/scFoundation>

[700] xCompass AI, "GeneCompass: Deciphering Universal Gene Regulatory Networks with Knowledge-Informed Cross-Species Foundation Model," *GitHub*, 2024. [Online]. Available: <https://github.com/xCompass-AI/GeneCompass>

[701] MONAI Consortium, "MONAI: Medical Open Network for AI," *monai.io*, 2025. [Online]. Available: <https://monai.io/>

[702] Wang Lab, "MedSAM: Segment Anything in Medical Images," *GitHub*, 2024. [Online]. Available: <https://github.com/bowang-lab/MedSAM>

[703] J. Wasserthal et al., "TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images," *GitHub*, 2024. [Online]. Available: <https://github.com/wasserth/TotalSegmentator>

[704] Google, "Advancing Medical AI with Med-Gemini," *Google Research*, 2024. [Online]. Available: <https://research.google/blog/advancing-medical-ai-with-med-gemini/>

[705] Microsoft, "RAD-DINO: Exploring Scalable Medical Image Encoders Beyond Text Supervision," *Hugging Face*, 2024. [Online]. Available: <https://huggingface.co/microsoft/rad-dino>

[706] NVIDIA, "BioNeMo: Generative AI Platform for Drug Discovery," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/clara/bionemo/>

[707] NVIDIA, "Earth-2: An AI Supercomputer to Predict Climate Change," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/omniverse/>

[708] NVIDIA, "CUDA-Q Cloud: Hybrid Quantum-Classical Computing Platform," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/cuda-q>

[709] Isomorphic Labs / Google DeepMind, "AlphaFold Server," *alphafoldserver.com*, 2024. [Online]. Available: <https://alphafoldserver.com/>

[710] Schrödinger, "LiveDesign: Collaborative Drug Discovery Platform," *schrodinger.com*, 2025. [Online]. Available: <https://www.schrodinger.com/platform/products/livedesign/>

[711] Recursion Pharmaceuticals, "BioHive-2: Life Science AI Supercomputer," *recursion.com*, 2024. [Online]. Available: <https://www.recursion.com/>

[712] Cradle, "Cradle.bio: AI-Powered Protein Design," *cradle.bio*, 2025. [Online]. Available: <https://www.cradle.bio/>

[713] Profluent Bio, "Profluent: AI-Designed Proteins and Gene Editors," *profluent.bio*, 2025. [Online]. Available: <https://www.profluent.bio/>

[714] Google Cloud, "Cluster Toolkit: Deploy HPC Workloads on Google Cloud," *cloud.google.com*, 2025. [Online]. Available: <https://docs.cloud.google.com/cluster-toolkit/docs/overview>

[715] Posit PBC, "Quarto: An Open-Source Scientific and Technical Publishing System," *quarto.org*, 2025. [Online]. Available: <https://quarto.org/>

[716] Project Jupyter, "JupyterHub: Multi-User Jupyter Notebooks," *jupyter.org*, 2025. [Online]. Available: <https://jupyter.org/hub>

[717] Anaconda, Inc., "Anaconda: The World's Most Popular Python/R Data Science Platform," *anaconda.com*, 2025. [Online]. Available: <https://www.anaconda.com/>

[718] micro-ROS, "micro-ROS: ROS 2 for Microcontrollers," *micro.ros.org*, 2025. [Online]. Available: <https://micro.ros.org/>

[719] ArduPilot Dev Team, "ArduPilot: Versatile, Trusted, Open Autonomous Vehicle Software," *ardupilot.org*, 2025. [Online]. Available: <https://ardupilot.org/>

[720] Dronecode Foundation, "PX4 Open Source Autopilot," *px4.io*, 2025. [Online]. Available: <https://px4.io/>

[721] BlackBerry QNX, "QNX Real-Time Operating System," *blackberry.qnx.com*, 2025. [Online]. Available: <https://blackberry.qnx.com/en>

[722] Wind River, "VxWorks: Industry-Leading Real-Time Operating System," *windriver.com*, 2025. [Online]. Available: <https://www.windriver.com/products/vxworks>

[723] Xenomai Project, "Xenomai: Real-Time Framework for Linux," *xenomai.org*, 2025. [Online]. Available: <https://xenomai.org/>

[724] NVIDIA, "Isaac Lab: GPU-Accelerated Robot Learning Framework," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/isaac/lab>

[725] NVIDIA, "Cosmos: World Foundation Models for Physical AI," *NVIDIA*, 2025. [Online]. Available: <https://www.nvidia.com/en-us/ai/cosmos/>

[726] Genesis Team, "Genesis: A Generative and Universal Physics Engine for Robotics and Embodied AI," *genesis-embodied-ai.github.io*, 2024. [Online]. Available: <https://genesis-embodied-ai.github.io/>

[727] Toyota Research Institute, "Drake: Model-Based Design and Verification for Robotics," *drake.mit.edu*, 2025. [Online]. Available: <https://drake.mit.edu/>

[728] Meta AI Research, "Habitat: A Platform for Embodied AI Research," *aihabitat.org*, 2024. [Online]. Available: <https://aihabitat.org/>

[729] Allen Institute for AI, "AI2-THOR: An Interactive 3D Environment for Visual AI," *ai2thor.allenai.org*, 2025. [Online]. Available: <https://ai2thor.allenai.org/>

[730] Unity Technologies, "ML-Agents: Unity Machine Learning Agents Toolkit," *GitHub*, 2024. [Online]. Available: <https://github.com/unity-technologies/ml-agents>

[731] NVIDIA, "Isaac GR00T N1: Open Humanoid Robot Foundation Model," *NVIDIA Newsroom*, 2025. [Online]. Available: <https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks>

[732] Physical Intelligence, "π0: A Vision-Language-Action Flow Model for General Robot Control," *pi.website*, 2024. [Online]. Available: <https://www.pi.website/blog/pi0>

[733] Google DeepMind, "Gemini Robotics: Bringing AI into the Physical World," *deepmind.google*, 2025. [Online]. Available: <https://deepmind.google/models/gemini-robotics/>

[734] Skild AI, "Skild Brain: General-Purpose Robot Intelligence," *skild.ai*, 2025. [Online]. Available: <https://www.skild.ai/>

[735] Figure AI, "Helix: A Vision-Language-Action Model for Generalist Robot Control," *figure.ai*, 2025. [Online]. Available: <https://www.figure.ai/helix>

[736] 1X Technologies, "1X World Model," *1x.tech*, 2025. [Online]. Available: <https://www.1x.tech/discover/1x-world-model>

[737] UC Berkeley, "Octo: An Open-Source Generalist Robot Policy," *octo-models.github.io*, 2024. [Online]. Available: <https://octo-models.github.io/>

[738] T. Zhao et al., "ACT: Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware," *GitHub*, 2023. [Online]. Available: <https://github.com/tonyzhaozh/act>

[739] Tesla, "Optimus: AI Humanoid Robot," *tesla.com*, 2025. [Online]. Available: <https://www.tesla.com/AI>

[740] Figure AI, "Figure Humanoid Robots," *figure.ai*, 2025. [Online]. Available: <https://www.figure.ai/>

[741] 1X Technologies, "Neo Beta: Humanoid Robot," *1x.tech*, 2025. [Online]. Available: <https://www.1x.tech/neo>

[742] Apptronik, "Apollo: Humanoid Robot for Logistics and Manufacturing," *apptronik.com*, 2025. [Online]. Available: <https://apptronik.com/apollo>

[743] Unitree Robotics, "Unitree H1: Humanoid Robot," *unitree.com*, 2025. [Online]. Available: <https://www.unitree.com/h1/>

[744] Boston Dynamics, "Spot: The Agile Mobile Robot," *bostondynamics.com*, 2025. [Online]. Available: <https://bostondynamics.com/products/spot/>

[745] ANYbotics, "ANYmal: Autonomous Legged Robot for Inspection," *anybotics.com*, 2025. [Online]. Available: <https://www.anybotics.com/robotics/anymal/>

[746] Unitree Robotics, "Unitree Go2: Quadruped Robot," *unitree.com*, 2025. [Online]. Available: <https://www.unitree.com/go2/>

[747] Agility Robotics, "Digit: Bipedal Robot for Warehouse Logistics," *agilityrobotics.com*, 2025. [Online]. Available: <https://www.agilityrobotics.com/>

[748] Intuitive, "da Vinci 5: Surgical System," *intuitive.com*, 2024. [Online]. Available: <https://www.intuitive.com/en-us/products-and-services/da-vinci/5>

[749] Mobileye, "SuperVision: Hands-Free Driving Technology," *mobileye.com*, 2025. [Online]. Available: <https://www.mobileye.com/solutions/super-vision/>

[750] Wayve, "AI-First Approach to Autonomous Driving," *wayve.ai*, 2025. [Online]. Available: <https://wayve.ai/>

[751] NVIDIA, "DRIVE Thor: Centralized Car Computer," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/drive/agx>

[752] Mobileye, "EyeQ6 / EyeQ Ultra: Automotive-Grade Vision SoC," *mobileye.com*, 2025. [Online]. Available: <https://www.mobileye.com/solutions/super-vision/>

[753] Qualcomm, "Snapdragon Ride: Automotive Driving Platform," *qualcomm.com*, 2025. [Online]. Available: <https://www.qualcomm.com/automotive/solutions/snapdragon-ride>

[754] Horizon Robotics, "Journey 6: Automotive Intelligent Driving SoC," *horizon.auto*, 2025. [Online]. Available: <https://en.horizon.auto/>

[755] Baidu, "Apollo: Open Autonomous Driving Platform," *apollo.auto*, 2025. [Online]. Available: <https://www.apollo.auto/en/>

[756] Autoware Foundation, "Autoware: The World's Leading Open-Source Software for Autonomous Driving," *autoware.org*, 2025. [Online]. Available: <https://autoware.org/>

[757] Applied Intuition, "Simulation and Data Platform for Autonomous Systems," *appliedintuition.com*, 2025. [Online]. Available: <https://www.appliedintuition.com/>

[758] Foretellix, "Autonomous Vehicle Verification and Validation Platform," *foretellix.com*, 2025. [Online]. Available: <https://www.foretellix.com/>

[759] Bosch, "Bosch acquires Atlatec to expand HD mapping capabilities," *bosch.com*, Feb 2022. [Online]. Available: <https://www.bosch.com/>

[760] Google DeepMind, "Genie 2: A Large-Scale Foundation World Model," *deepmind.google*, 2024. [Online]. Available: <https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/>

[761] World Labs, "Marble: Spatial Intelligence World Model," *worldlabs.ai*, 2025. [Online]. Available: <https://www.worldlabs.ai/>

[762] Wayve, "GAIA-2: Generative World Model for Autonomous Driving," *wayve.ai*, 2025. [Online]. Available: <https://wayve.ai/science/gaia/>

[763] Z. Yu et al., "Mip-Splatting: Alias-Free 3D Gaussian Splatting," *GitHub*, CVPR 2024 Best Student Paper. [Online]. Available: <https://github.com/autonomousvision/mip-splatting>

[764] Polycam, "Polycam: 3D Capture App for iPhone and iPad," *poly.cam*, 2025. [Online]. Available: <https://poly.cam/>

[765] KIRI Innovation, "KIRI Engine: Photogrammetry 3D Scanning App," *kiriengine.app*, 2025. [Online]. Available: <https://www.kiriengine.app/>

[766] DeemosTech, "Rodin: AI-Powered 3D Avatar and Asset Generation," *hyperhuman.deemos.com*, 2025. [Online]. Available: <https://hyperhuman.deemos.com/>

[767] Tencent, "Hunyuan3D 2.5: High-Resolution 3D Asset Generation," *GitHub*, 2025. [Online]. Available: <https://github.com/Tencent-Hunyuan/Hunyuan3D-2>

[768] Microsoft, "TRELLIS: Structured 3D Latents for Scalable and Versatile 3D Generation," *GitHub*, 2024. [Online]. Available: <https://github.com/microsoft/TRELLIS>

[769] Spline, "Spline: 3D Design Tool with AI Capabilities," *spline.design*, 2025. [Online]. Available: <https://spline.design/>

[770] NVIDIA, "ACE: Avatar Cloud Engine for Digital Humans," *NVIDIA Developer*, 2025. [Online]. Available: <https://developer.nvidia.com/ace-for-games>

[771] Convai Technologies, "Convai: Conversational AI for Game Characters," *convai.com*, 2025. [Online]. Available: <https://convai.com/>

[772] Unity Technologies, "Sentis: In-App Neural Network Inference," *unity.com*, 2025. [Online]. Available: <https://unity.com/products/sentis>

[773] Pixar Animation Studios, "OpenUSD: Universal Scene Description," *openusd.org*, 2025. [Online]. Available: <https://openusd.org/>

[774] SideFX, "Houdini Copernicus: GPU-Accelerated Material Computation," *sidefx.com*, 2025. [Online]. Available: <https://www.sidefx.com/products/whats-new-in-h205/copernicus/>

[775] Ultralytics, "YOLO: Real-Time Object Detection," *ultralytics.com*, 2025. [Online]. Available: <https://www.ultralytics.com/>

[776] Meta AI Research, "Detectron2: A PyTorch-Based Modular Object Detection Library," *GitHub*, 2024. [Online]. Available: <https://github.com/facebookresearch/detectron2>

[777] OpenMMLab, "OpenMMLab: Open-Source Computer Vision Toolkits," *GitHub*, 2025. [Online]. Available: <https://github.com/open-mmlab>

[778] IDEA Research, "Grounding DINO: Open-Set Object Detection," *GitHub*, ECCV 2024. [Online]. Available: <https://github.com/IDEA-Research/GroundingDINO>

[779] Baidu, "PaddleOCR: Rich, Leading and Practical OCR Tools," *GitHub*, 2025. [Online]. Available: <https://github.com/PaddlePaddle/PaddleOCR>

[780] Google (originally HP), "Tesseract Open Source OCR Engine," *GitHub*, 2025. [Online]. Available: <https://github.com/tesseract-ocr/tesseract>

[781] V. Paruchuri, "Surya: OCR, Layout Analysis, Reading Order, Table Recognition in 90+ Languages," *GitHub*, 2024. [Online]. Available: <https://github.com/VikParuchuri/surya>

[782] OpenDataLab, "DocLayout-YOLO: Enhancing Document Layout Analysis," *GitHub*, 2024. [Online]. Available: <https://github.com/opendatalab/DocLayout-YOLO>

[783] Meta AI, "Nougat: Neural Optical Understanding for Academic Documents," *GitHub*, 2023. [Online]. Available: <https://github.com/facebookresearch/nougat>

[784] Shanghai AI Laboratory, "MinerU: High-Quality Document Parsing Tool," *GitHub*, 2025. [Online]. Available: <https://github.com/opendatalab/MinerU>

[785] Mistral AI, "Mistral OCR: State-of-the-Art Document Understanding," *mistral.ai*, 2025. [Online]. Available: <https://mistral.ai/news/mistral-ocr>

[786] Reducto, "Reducto: AI Document Parsing and Extraction," *reducto.ai*, 2025. [Online]. Available: <https://reducto.ai/>

[787] Unstructured, "Unstructured: ETL Solution for Transforming Complex Documents for LLMs," *unstructured.io*, 2025. [Online]. Available: <https://unstructured.io/>

[788] OpenGVLab, "InternVideo: Video Foundation Models for Multimodal Understanding," *GitHub*, ECCV 2024. [Online]. Available: <https://github.com/OpenGVLab/InternVideo>

[789] DAMO-NLP-SG, Alibaba, "VideoLLaMA 3: Frontier Multimodal Foundation Models for Image and Video Understanding," *GitHub*, 2025. [Online]. Available: <https://github.com/DAMO-NLP-SG/VideoLLaMA3>

[790] Alibaba Cloud Qwen Team, "Qwen-VL: Multimodal Large Language Models," *GitHub*, 2025. [Online]. Available: <https://github.com/QwenLM/Qwen-VL>

[791] TwelveLabs, "Marengo: Video Foundation Model for Multimodal Understanding," *twelvelabs.io*, 2025. [Online]. Available: <https://www.twelvelabs.io/product/models-overview>

[792] TencentQQ Multimedia Research Team, "Video-CCAM: Enhancing Video-Language Understanding with Causal Cross-Attention Masks," *GitHub*, 2024. [Online]. Available: <https://github.com/QQ-MM/Video-CCAM>

[793] Qualcomm, "Qualcomm AI Engine Direct SDK (QNN)," *qualcomm.com*, 2025. [Online]. Available: <https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk>

[794] Arm, "Arm NN: ML Inference Engine for Arm CPUs, GPUs, and NPUs," *arm.com*, 2025. [Online]. Available: <https://www.arm.com/products/silicon-ip-cpu/ethos/arm-nn>

[795] Google, "MediaPipe: Cross-Platform, Customizable ML Solutions for Live and Streaming Media," *developers.google.com*, 2025. [Online]. Available: <https://developers.google.com/mediapipe>

[796] Hailo, "Hailo AI Software Suite including Dataflow Compiler," *hailo.ai*, 2025. [Online]. Available: <https://hailo.ai/products/hailo-software/hailo-ai-software-suite/>

[797] Roboflow, "Roboflow: Computer Vision Tools for Developers and Enterprises," *roboflow.com*, 2025. [Online]. Available: <https://roboflow.com/>

[798] Encord, "Encord: Multimodal Data Layer for Physical AI," *encord.com*, 2025. [Online]. Available: <https://encord.com/>

[799] Labelbox, "Labelbox: Data Factory for AI Teams," *labelbox.com*, 2025. [Online]. Available: <https://labelbox.com/>

[800] Voxel51, "FiftyOne: Open-Source Tool for Building High-Quality Datasets and Computer Vision Models," *voxel51.com*, 2025. [Online]. Available: <https://voxel51.com/fiftyone>

[801] CVAT.ai, "CVAT: Computer Vision Annotation Tool," *cvat.ai*, 2025. [Online]. Available: <https://www.cvat.ai/>

[802] Supervisely, "Supervisely: Computer Vision Platform for AI," *supervisely.com*, 2025. [Online]. Available: <https://supervisely.com/>

[803] Cognex, "VisionPro Software: Machine Vision for Industrial Inspection," *cognex.com*, 2025. [Online]. Available: <https://www.cognex.com/en/products/machine-vision-software/visionpro-software>

[804] Keyence, "Machine Vision Systems," *keyence.com*, 2025. [Online]. Available: <https://www.keyence.com/products/vision/>

[805] Landing AI, "LandingLens: Visual Inspection AI Platform," *landing.ai*, 2025. [Online]. Available: <https://landing.ai/>

[806] Hikvision, "Hikvision: Global Leader in Innovative Security Products and Solutions," *hikvision.com*, 2025. [Online]. Available: <https://www.hikvision.com/en/>

[807] Dahua Technology, "Dahua: World Leading Video-Centric AIoT Solution & Service Provider," *dahuasecurity.com*, 2025. [Online]. Available: <https://www.dahuasecurity.com/>

[808] Aidoc, "Aidoc: Clinical AI Solutions for Healthcare Providers," *aidoc.com*, 2025. [Online]. Available: <https://www.aidoc.com/>

[809] Harrison.ai (formerly Annalise.ai), "Annalise.ai: AI-Powered Radiology Solutions," *annalise.ai*, 2025. [Online]. Available: <https://annalise.ai/>

[810] Viz.ai, "Viz.ai: AI-Powered Care Coordination Platform," *viz.ai*, 2025. [Online]. Available: <https://www.viz.ai/>

[811] Standard AI, "Standard AI: AI-Powered Retail Intelligence Platform," *standard.ai*, 2025. [Online]. Available: <https://standard.ai/>

[812] Trigo, "Trigo: Autonomous Retail Technology with Computer Vision," *trigoretail.com*, 2025. [Online]. Available: <https://www.trigoretail.com/>

[813] Yandex, "CatBoost: Fast, Scalable, High Performance Gradient Boosting on Decision Trees," *catboost.ai*, 2025. [Online]. Available: <https://catboost.ai/>

[814] NVIDIA, "RAPIDS cuML: GPU-Accelerated Machine Learning Algorithms," *rapids.ai*, 2025. [Online]. Available: <https://rapids.ai/>

[815] H2O.ai, "H2O: Open-Source Machine Learning Platform," *h2o.ai*, 2025. [Online]. Available: <https://h2o.ai/>

[816] Meta, "Prophet: Forecasting at Scale," *facebook.github.io*, 2024. [Online]. Available: <https://facebook.github.io/prophet/>

[817] NeuralProphet Team, "NeuralProphet: A Simple Forecasting Package," *neuralprophet.com*, 2024. [Online]. Available: <https://neuralprophet.com/>

[818] Nixtla, "Nixtla: Time Series Forecasting and Anomaly Detection Platform," *nixtla.io*, 2025. [Online]. Available: <https://www.nixtla.io/>

[819] Salesforce, "Merlion: A Machine Learning Framework for Time Series Intelligence," *GitHub*, 2024. [Online]. Available: <https://github.com/salesforce/Merlion>

[820] Amazon, "Chronos: Pretrained Models for Time Series Forecasting," *GitHub*, 2024. [Online]. Available: <https://github.com/amazon-science/chronos-forecasting>

[821] QuantConnect, "QuantConnect: Open-Source Algorithmic Trading Platform," *quantconnect.com*, 2025. [Online]. Available: <https://www.quantconnect.com/>

[822] Backtrader, "Backtrader: Python Backtesting Library for Trading Strategies," *backtrader.com*, 2024. [Online]. Available: <https://www.backtrader.com/>

[823] vectorbt, "vectorbt: The Backtesting Engine for Quantitative Finance," *vectorbt.dev*, 2025. [Online]. Available: <https://vectorbt.dev/>

[824] S. Jansen, "Zipline-reloaded: Zipline, a Pythonic Algorithmic Trading Library," *GitHub*, 2024. [Online]. Available: <https://github.com/stefan-jansen/zipline-reloaded>

[825] QuantLib Project, "QuantLib: A Free/Open-Source Library for Quantitative Finance," *quantlib.org*, 2025. [Online]. Available: <https://www.quantlib.org/>

[826] Y. Yang et al., "FinBERT: A Pretrained Language Model for Financial Communications," *GitHub*, arXiv:2006.08097, 2020. [Online]. Available: <https://github.com/yya518/FinBERT>

[827] Bloomberg LP, "Bloomberg Terminal: Financial Data and Analytics Platform," *professional.bloomberg.com*, 2025. [Online]. Available: <https://professional.bloomberg.com/products/bloomberg-terminal/>

[828] Two Sigma, "Venn: Investment Portfolio Analytics Platform," *venn.twosigma.com*, 2025. [Online]. Available: <https://www.venn.twosigma.com/>

[829] AlphaSense, "AlphaSense: AI-Powered Market Intelligence and Search Platform," *alpha-sense.com*, 2025. [Online]. Available: <https://www.alpha-sense.com/>

[830] Epic Games, "Unreal Engine", [Online]. Available: <https://www.unrealengine.com/>

[831] Unity Technologies, "Unity Engine", [Online]. Available: <https://unity.com/>

[832] Godot Engine community, "Godot Engine", [Online]. Available: <https://godotengine.org/>

[833] Crytek, "CryEngine", [Online]. Available: <https://www.cryengine.com/>

[834] Cocos, "Cocos Creator", [Online]. Available: <https://www.cocos.com/en/creator>

[835] NVIDIA, "DLSS — Deep Learning Super Sampling", [Online]. Available: <https://www.nvidia.com/en-us/geforce/technologies/dlss/>

[836] AMD, "FidelityFX Super Resolution (FSR)", [Online]. Available: <https://gpuopen.com/fidelityfx-super-resolution-4/>

[837] Intel, "Intel XeSS (Xe Super Sampling)", [Online]. Available: <https://www.intel.com/content/www/us/en/products/docs/discrete-gpus/arc/technology/xess.html>

[838] Sony Interactive Entertainment, "PlayStation 5 Pro — PSSR", PlayStation.Blog, [Online]. Available: <https://blog.playstation.com/2024/09/10/playstation-5-pro-launches-november-7-priced-at-699-99/>

[839] Promethean AI, "Promethean AI", [Online]. Available: <https://www.prometheanai.com/>

[840] Scenario, "Scenario AI Generative Art", [Online]. Available: <https://www.scenario.com/>

[841] Rosebud AI, "Rosebud AI", [Online]. Available: <https://www.rosebud.ai/>

[842] GGWP, "GGWP — AI-powered player safety", [Online]. Available: <https://www.ggwp.com/>

[843] Anybrain, "Anybrain — Behaviour-based anti-cheat", [Online]. Available: <https://www.anybrain.gg/>

[844] Unity Technologies, "Unity Gaming Services", [Online]. Available: <https://unity.com/products/gaming-services>

[845] Epic Games, "Epic Online Services", [Online]. Available: <https://dev.epicgames.com/services>

[846] Hidden Door, "Hidden Door — Social roleplay platform", [Online]. Available: <https://www.hiddendoor.co/>

[847] Latitude, "AI Dungeon", [Online]. Available: <https://aidungeon.com/>

[848] Proxima Enterprises, "Suck Up! and Proxima Enterprises games", [Online]. Available: <https://www.proxima-enterprises.com/>

[849] Adobe, "Adobe After Effects", [Online]. Available: <https://www.adobe.com/products/aftereffects.html>

[850] Foundry, "Nuke Family — Compositing software", [Online]. Available: <https://www.foundry.com/products/nuke-family/nuke>

[851] Blackmagic Design, "DaVinci Resolve", [Online]. Available: <https://www.blackmagicdesign.com/products/davinciresolve>

[852] Autodesk, "Maya", [Online]. Available: <https://www.autodesk.com/products/maya/overview>

[853] Blender Foundation, "Blender", [Online]. Available: <https://www.blender.org/>

[854] Maxon, "Cinema 4D", [Online]. Available: <https://www.maxon.net/en/cinema-4d>

[855] Move.ai, "Move.ai — Markerless motion capture", [Online]. Available: <https://www.move.ai/>

[856] Promise, "Promise — Generative film studio", [Online]. Available: <https://www.promise.studio/>

[857] Krisp Technologies, "Krisp — AI voice productivity", [Online]. Available: <https://krisp.ai/>

[858] iZotope, "RX — Audio repair and enhancement", [Online]. Available: <https://www.izotope.com/en/products/rx.html>

[859] NVIDIA, "RTX Video Super Resolution", [Online]. Available: <https://www.nvidia.com/en-us/geforce/news/rtx-video-super-resolution/>

[860] Disguise, "Disguise — Virtual production platform", [Online]. Available: <https://www.disguise.one/>

[861] Pixotope, "Pixotope — Real-time virtual production", [Online]. Available: <https://www.pixotope.com/>

[862] Maxon, "Redshift Renderer", [Online]. Available: <https://www.maxon.net/en/redshift>

[863] OTOY, "Octane Render", [Online]. Available: <https://home.otoy.com/render/octane-render/>

[864] Submagic, "Submagic — AI video editor", [Online]. Available: <https://www.submagic.co/>

[865] ByteDance, "CapCut", [Online]. Available: <https://www.capcut.com/>

[866] Veed.io, "VEED — AI online video editor", [Online]. Available: <https://www.veed.io/>

[867] Lightricks, "LTX-Video — Open-source video generation", [Online]. Available: <https://www.lightricks.com/>

[868] Qualcomm, "Hexagon SDK," [Online]. Available: <https://developer.qualcomm.com/software/hexagon-dsp-sdk>

[869] Qualcomm, "Snapdragon Neural Processing SDK (SNPE)," [Online]. Available: <https://www.qualcomm.com/developer/software/neural-processing-sdk-for-ai>

[870] Qualcomm, "Qualcomm AI Hub," [Online]. Available: <https://aihub.qualcomm.com/>

[871] Qualcomm Innovation Center, "AIMET — AI Model Efficiency Toolkit," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/quic/aimet>

[872] Qualcomm, "Cloud AI 100," [Online]. Available: <https://www.qualcomm.com/products/technology/processors/cloud-artificial-intelligence/cloud-ai-100>

[873] Qualcomm, "Adreno GPU SDK," [Online]. Available: <https://developer.qualcomm.com/software/adreno-gpu-sdk>

[874] MediaTek, "NeuroPilot SDK," [Online]. Available: <https://neuropilot.mediatek.com/>

[875] MediaTek, "Automotive Solutions — Dimensity Auto," [Online]. Available: <https://www.mediatek.com/products/automotive>

[876] MediaTek, "Genio — IoT Platform," [Online]. Available: <https://www.mediatek.com/products/iot>

[877] MediaTek, "Kompanio — Chromebooks & Tablets," [Online]. Available: <https://www.mediatek.com/products/chromebooks-tablets>

[878] Rockchip / airockchip, "RKNN-Toolkit2," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/airockchip/rknn-toolkit2>

[879] Rockchip, "RKNPU2 Runtime," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/rockchip-linux/rknpu2>

[880] Rockchip / airockchip, "RKLLM — Rockchip Large Language Model SDK," GitHub repository, accessed 2026. [Online]. Available: <https://github.com/airockchip/rknn-llm>

[881] Rockchip, "RK3588 — Octa-core 64-bit AI Processor with 6 TOPS NPU," [Online]. Available: <https://www.rock-chips.com/a/en/products/RK35_Series/2022/0926/1660.html>

[882] Qualcomm, "Genie SDK — On-Device Generative AI," [Online]. Available: <https://www.qualcomm.com/developer/software/genie-sdk>

[883] AXera Tech, "Pulsar SDK — Axera AI Toolchain," [Online]. Available: <https://www.axera-tech.com/>
