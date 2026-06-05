# 素材归档：从 GB10「双胞胎」看 Windows / Linux / 鸿蒙的固件分家

**素材性质**：一篇中文科技媒体／论坛风格的解读文，主题是「同一颗 GB10 芯片，为什么 RTX Spark 能跑 Windows on ARM、而 DGX Spark 只能跑 Linux」。核心论点落在 **UEFI + ACPI vs 设备树（Device Tree）** 两套硬件描述体系的分家上。

**收藏理由（用户备注）**：用户要求把原文存档，并在此基础上**对比 Windows、Linux、鸿蒙三家在 ARM 平台上的固件 / 硬件描述 / 驱动路线**。

**事实核对结论**：原文骨架经交叉核对**基本属实**（RTX Spark 确为真实产品、GB10 规格、DGX Spark 预装 Ubuntu 系 DGX OS、WoA 强制 ACPI 等均可核实）。**一处需更正**：原文称「设备树是 Linux 专属」是过度简化——Linux on ARM64 **同时支持 ACPI 和设备树**，只有 Windows on ARM 才是「只认 ACPI」。详见下方注解与对比表。核对依据见文末信源。

---

## 一、素材原文（保留原貌）

> 本周一，NVIDIA重磅发布的RTX Spark超级芯片，凭借原生支持Windows on ARM（WoA）系统的特性，给广大开发者与PC用户带来了极大惊喜。这款搭载GB10超算芯片的产品，成功在ARM架构下实现了完整的Windows桌面体验与成熟的CUDA生态，打破了以往ARM平台Windows算力不足的局限。
>
> 不少人随之产生疑问，同款搭载GB10处理器的DGX Spark，是否也可以安装使用Windows系统？答案是可能不行！核心不在于芯片算力，而是固件架构、硬件描述规范与驱动生态的底层差异，关键卡在UEFI+ACPI两套硬性标准上。
>
> 两款产品虽共享Grace+Blackwell组成的GB10 SoC，CPU与GPU硬件规格基本一致，但产品定位从源头决定固件设计路线。RTX Spark面向消费级AI PC，从研发阶段就对标微软WoA规范，固件搭载完整UEFI启动框架与标准化ACPI硬件描述表单，是微软认证的ARM桌面硬件；而DGX Spark主打科研与AI推理，出厂预装基于Ubuntu定制的DGX OS，固件原生适配Linux生态，默认依靠设备树（DT）完成硬件枚举。
>
> ACPI与设备树是两套互不兼容的硬件描述体系，也是Windows与Linux在ARM平台分家的关键。Windows on ARM硬性规定：系统只能通过UEFI调取ACPI表格，完成硬件识别、中断分配、电源管控，没有ACPI，Windows内核无法识别CPU、显卡、内存等硬件资源；设备树则是Linux专属配置方案，以独立DTB文件在开机阶段传递硬件参数，结构精简、适配嵌入式与服务器Linux，但这套描述格式完全不被Windows内核识别，仅靠设备树的DGX Spark原生固件无法引导WoA系统。
>
> 除此之外，全套适配驱动是第二道门槛。RTX Spark由英伟达联合微软深度优化，提前完成ARM64版显卡、网卡、统一内存全套Windows驱动；DGX Spark的NVLink-C2C互联、ConnectX-7网卡、专属电源管理芯片仅有Linux驱动，暂无官方Windows驱动适配方案。
>
> 若想让DGX Spark支持Windows，需要英伟达重构固件，删掉原生设备树配置、重新开发全量ACPI表单，再从零移植整套Windows驱动，改造工作量极大，因此现阶段同芯的DGX Spark，只能稳定运行Linux，很难原生适配Windows on ARM。
>
> 而DGX Spark深耕Linux生态，对专业AI开发者而言有着不可替代的核心价值。Linux系统开源开放、轻量化、高稳定性的特性，完美适配大模型训练、AI推理、高性能算力调度等专业场景。主流AI框架、深度学习库、算力调度工具均优先适配Linux，开发者可无缝搭建开发、训练、部署全流程环境。同时，DGX Spark的NVLink高速互联、超算级统一内存、硬件算力调度等核心特性，仅能在Linux系统下满血释放，充分发挥GB10芯片的极致算力。此外，Linux系统支持精细化权限管控、自定义内核优化、批量任务调度，能有效降低大规模AI研发的运行延迟与资源损耗，是科研机构、企业开展高端AI算力研发的最优系统选择，这也是英伟达坚持让DGX Spark深耕Linux生态的核心原因。

---

## 二、最小化注解（核对结果，逐条标在原文论点上）

- **「本周一发布 RTX Spark」** — 属实。NVIDIA 与 Microsoft 于 2026-05-31 公布 RTX Spark，6 月 1 日（周一）起媒体集中报道 [[1]](https://www.theregister.com/systems/2026/06/01/nvidia-recasts-gb10-superchip-in-bid-for-high-end-pc-market/), [[2]](https://www.tomshardware.com/laptops/nvidia-enters-the-windows-pc-market-with-rtx-spark)。整机（Asus / Dell / HP / Lenovo / Microsoft Surface / MSI 等）计划 2026 秋季出货 [[3]](https://en.wikipedia.org/wiki/Nvidia_RTX_Spark)。
- **「GB10 = Grace + Blackwell」** — 属实。20 核 Arm Grace CPU + Blackwell RTX GPU（6,144 CUDA 核），128GB 统一 LPDDR5X，NVLink-C2C 互联。补一个原文没提的细节：GB10 的 Arm CPU 复合体由**联发科（MediaTek）代工**，TSMC 3nm 级工艺 [[2]](https://www.tomshardware.com/laptops/nvidia-enters-the-windows-pc-market-with-rtx-spark)。
- **「DGX Spark 预装 Ubuntu 系 DGX OS」** — 属实。出厂为 NVIDIA 定制的 Ubuntu 24.04 LTS（DGX OS），面向 AI 开发／推理 [[4]](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)。
- **「DGX Spark 能不能装 Windows」这个问题本身** — 属实，是真实社区疑问：NVIDIA 开发者论坛有一个标题几乎一致的提问帖「DGX Spark: Could Windows on ARM Support Be Possible, Like RTX Spark, N1X?」[[5]](https://forums.developer.nvidia.com/t/dgx-spark-could-windows-on-arm-support-be-possible-like-rtx-spark-n1x/371870)。
- **「WoA 只认 UEFI + ACPI」** — 属实。Windows on ARM 强制 UEFI 启动、且只能经 UEFI 系统配置表读取 ACPI 表格；不支持设备树。这一要求源于微软（早在 Windows RT 时代就强制 UEFI+ACPI），目的是复用 x86 时代成熟的启动与驱动栈，而非重写内核去支持 DT [[6]](https://mjg59.dreamwidth.org/26535.html), [[7]](https://docs.kernel.org/arch/arm64/arm-acpi.html)。
- **⚠ 需更正：「设备树是 Linux 专属」** — 过度简化。Linux on ARM64 **两套都支持**：内核启动时若有 DT 就优先用 DT 做设备枚举，没有 DT 才回退到 ACPI（若存在）；服务器级 ARM Linux 普遍走 ACPI/SBBR 路线，嵌入式才以 DT 为主 [[7]](https://docs.kernel.org/arch/arm64/arm-acpi.html)。所以真正「单线程只认一种」的是 **Windows（只认 ACPI）**，不是 Linux。原文「DGX Spark 默认靠设备树枚举」对 DGX 这台具体机器可能成立，但不能反推「设备树=Linux 专属」。
- **「DGX Spark 改装 Windows 工作量极大」** — 方向属实。固件层要补全 ACPI 表、驱动层要把 NVLink-C2C / ConnectX-7 / 电源管理等从零移植 ARM64 Windows 驱动，确无官方方案。这部分属合理推断，非官方承诺。

---

## 三、对比加工：Windows / Linux / 鸿蒙在 ARM 上的固件与硬件描述路线

> 以下为本人在原文基础上的对比整理（**解读**，非原文内容）。原文只对比了 Windows 与 Linux 两家；用户要求并入鸿蒙作三方对照。

三家在 ARM 平台上「机器开机后怎么把硬件告诉操作系统」走的是三条不同的路：

| 维度 | Windows on ARM | Linux on ARM64 | 鸿蒙 HarmonyOS（ARM） | 苹果 Apple Silicon |
|---|---|---|---|---|
| 代表硬件 | RTX Spark、Surface、骁龙 X 系列笔记本 | DGX Spark、各类 ARM 服务器 / 嵌入式 | 鸿蒙电脑（麒麟 X90）、手机、车机、IoT | M 系列 Mac、iPhone / iPad |
| 启动固件 | **强制 UEFI** | UEFI（服务器）或 U-Boot 等（嵌入式），灵活 | 华为自有引导链（非标准 UEFI+ACPI；细节未公开 ⚠） | **iBoot**（私有，非 UEFI）[[16]](https://asahilinux.org/docs/fw/adt/) |
| 硬件描述体系 | **只认 ACPI**（经 UEFI 传表） | **ACPI 与设备树（DT）二者皆可** | **HDF + HCS**（自有，HCS 为树状配置，概念近 DT 但格式不同）[[8]](https://github.com/openharmony/drivers_framework) | **Apple Device Tree（ADT）**：device tree 谱系，但私有二进制格式（非 Linux FDT、非 ACPI），XNU 经 SecureDTLookup 直接解析 [[16]](https://asahilinux.org/docs/fw/adt/) |
| 内核 | Windows NT 内核 | Linux 内核 | 鸿蒙内核（HarmonyOS NEXT / 鸿蒙 5）；OpenHarmony 另有 LiteOS 等 | XNU（Darwin） |
| 驱动模型 | WDM / WDF | Linux 设备驱动模型 | HDF（Hardware Driver Foundation），可跨内核复用驱动 [[8]](https://github.com/openharmony/drivers_framework) | IOKit |
| 跨体系兼容 | 封闭、最严格（缺 ACPI 直接起不来） | 最宽松（两套都吃） | 自成一套，靠 HDF 抽象屏蔽底层差异 | 极致封闭、全栈自有；Linux 靠逆向工程（Asahi + m1n1 转标准 DT），Windows 仅虚拟化、不可原生 [[17]](https://asahilinux.org/docs/platform/introduction/) |

几个关键判断：

1. **「分家」的真正分界线是 Windows，不是 Linux。** Linux 是三家里最「不挑」的——ACPI、DT 都能引导，所以它能装进 DGX Spark，理论上也能（在补齐驱动的前提下）装进对标 ACPI 的硬件。Windows 是唯一把自己钉死在 ACPI 上的。鸿蒙则干脆**两套主流标准都不用**，自起炉灶用 HDF+HCS。

2. **鸿蒙走的是「第三条路」，而非选边站。** HCS（HarmonyOS Configuration Source）是树状的硬件配置描述，直觉上和 Linux 的设备树最像，但它是华为自有格式、由 HDF 驱动框架在初始化阶段解析，不和 ACPI 也不和标准 DTB 互通。HDF 的设计目标之一是**让同一份驱动能在不同内核（LiteOS / Linux / 鸿蒙内核）上复用** [[8]](https://github.com/openharmony/drivers_framework)——这是和 Windows「绑死单一内核+ACPI」相反的取向。

3. **桌面落地的现实对照。** 三家都已经把 ARM 推到了桌面：RTX Spark（Windows on ARM，2026 秋）、DGX Spark（Linux，已售）、鸿蒙电脑 MateBook Pro / Fold（HarmonyOS 5 + 麒麟 X90，2025-05-19 发售，从内核重构、不支持侧载）[[9]](https://www.stcn.com/article/detail/1821418.html)。但三者的「同芯换系统」可能性完全不同：Windows ↔ Linux 卡在 ACPI/DT + 驱动两道门槛（如原文 DGX Spark 案例）；鸿蒙电脑则**软硬一体、垂直封闭**，麒麟 + 鸿蒙内核 + HDF 自成闭环，换系统的命题在它这里基本不成立。

4. **「封闭度」排序**：Linux（最开放，两套标准通吃）< Windows on ARM（认证封闭，但走 UEFI+ACPI 业界标准）< 苹果 ≈ 鸿蒙（标准与生态都自有，垂直整合最深）。但同是「垂直封闭」，苹果与鸿蒙选了**不同的硬件描述谱系**：苹果的 ADT 属 **device tree 系**（XNU 直接吃私有二进制 DT），鸿蒙则**另起 HDF + HCS 框架**。可见「自立门户」不等于「必须自创描述格式」——苹果证明封闭垂直栈也能架在 device tree 谱系上，只是换成自家私有二进制格式 [[16]](https://asahilinux.org/docs/fw/adt/)。

5. **封闭硬件上「换系统」的难度阶梯**：DGX Spark 装 Windows 卡在补 ACPI 表 + 移植驱动（原文案例）；**Apple Silicon 更狠**——Windows 无法原生 dual-boot（Boot Camp 只限 Intel Mac），只能靠 Parallels 虚拟化（微软唯一授权方案）[[18]](https://www.parallels.com/products/desktop/microsoft-authorized-solution-windows-11-arm/)；Linux 则靠 Asahi 项目**逆向工程**无公开文档的 SoC，用 m1n1 把 Apple 的 XNU 启动协议桥接成标准 ARM64 + device tree 启动 [[17]](https://asahilinux.org/docs/platform/introduction/)。苹果、鸿蒙这类全栈自有平台，「同芯换系统」的成本比 Windows/Linux 互换高一个量级。

6. **四方归位**：把矛盾从原文的「Windows vs Linux」补全，更准确的图景是按**两个轴**铺开——一轴是硬件描述谱系（**ACPI 系**：Windows；**device tree 系**：Linux、苹果 ADT；**自有框架**：鸿蒙 HDF/HCS；Linux 跨 ACPI 与 DT 两栏），另一轴是开放度（**开放业界标准**：Windows、Linux；**垂直封闭自有**：苹果、鸿蒙）。Linux 是唯一同时落在「两套标准都吃」且「开放」的格子，这正是它成为 AI 算力底座通用选择的结构性原因。

⚠ **声明**：鸿蒙电脑底层固件（是否用类 UEFI 引导、引导阶段如何向鸿蒙内核传递硬件信息）华为未公开技术文档，表中「启动固件」一栏与第 3 点的闭环判断为据公开报道与 OpenHarmony 框架资料的**推断**，非官方确认。

---

## 四、追问：鸿蒙能否复用 NVIDIA 资产？华为昇腾的平行栈对照

> 本节为对原文的延伸追问与对比整理（**解读**），不是原文内容。

### 4.1 鸿蒙能否直接复用 Linux 上的 NVLink-C2C / ConnectX-7 / 电源管理驱动？

基本不能，三层卡死，一层比一层根本：

1. **硬件压根不在鸿蒙设备上。** NVLink-C2C 是 NVIDIA 私有 die-to-die 一致性互联，ConnectX-7 是 NVIDIA/Mellanox 网卡，都是 NVIDIA 自家硬件。鸿蒙电脑跑的是麒麟 X90，没有这两样东西——「鸿蒙复用这些资产」在物理上是伪命题，除非假设拿鸿蒙去驱动一台 NVIDIA 机器。

2. **鸿蒙内核确有 Linux 驱动复用机制，但对 NVIDIA 这套用不上。** 反直觉的事实：HongMeng 鸿蒙内核（2023.8 起自研、用于 HarmonyOS NEXT）内建了 Linux 驱动复用能力——在内核空间放 Linux ABI 兼容 shim，再用 **driver container（驱动容器）** 装载 Linux 驱动，与原生鸿蒙驱动共存 [[10]](https://www.usenix.org/system/files/osdi24-chen-haibo.pdf)。但这套机制是为**手机端迁移 HarmonyOS 4.x 设备、复用第三方未适配外设**设计的，前提是拿得到那份 Linux 驱动。NVIDIA 的 NVLink-C2C / ConnectX-7 驱动是**闭源专有**（ConnectX 走 MLNX_OFED，含闭源固件与组件）[[11]](https://network.nvidia.com/products/ethernet-drivers/linux/mlnx_en/)，鸿蒙生态既拿不到源码、也不在 NVIDIA 适配名单内——容器复用的前提不成立。

3. **许可证污染。** 鸿蒙内核是自研微内核（非 GPL），Linux 驱动是 GPL。OSDI'24 论文明说，正是为避免 license contamination（许可证污染）才用驱动容器隔离，代价是性能开销；驱动关键路径还要做控制面/数据面分离、造「孪生驱动」 [[10]](https://www.usenix.org/system/files/osdi24-chen-haibo.pdf)。即便技术上能塞进去，GPL × 自研内核的法律边界也是独立一道坎。

一句话：**鸿蒙复用 Linux 驱动的「机制」存在，但 NVIDIA 这套闭源专有互联/网卡资产恰好踩中「硬件没有 + 闭源拿不到 + 许可证不通」三连，复用路径全断。**

### 4.2 华为昇腾的对应方案：自建平行栈，但底座 OS 仍是 Linux（欧拉）

昇腾不是去复用 NVIDIA，而是自建了一整套平行栈逐项对标：

| NVIDIA（DGX / GB10 那套） | 华为昇腾（Ascend / Atlas 那套） |
|---|---|
| NVLink / NVLink-C2C（片间一致性互联） | **HCCS** 华为自研高速互联（910B：每 NPU 7 条双向、各 56GB/s，单板 8 卡共 392GB/s，对标 A800 NVLink 400GB/s）[[12]](https://www.scensmart.com/news/one-article-explains-common-high-speed-interconnect-solutions-for-ai-chips/) |
| NVLink + NVSwitch + InfiniBand（超节点 scale-up/out） | **灵衢 UnifiedBus（UB）** 超节点互联协议，用于 Atlas 950/960 等 [[13]](https://www.qbitai.com/2025/09/335890.html) |
| NCCL（集合通信库） | **HCCL** [[14]](https://zhuanlan.zhihu.com/p/1907189956348220034) |
| CUDA（计算架构 / 软件栈） | **CANN**（Compute Architecture for Neural Networks）[[15]](https://support.huawei.com/enterprise/zh/doc/EDOC1100258040/fc9f82a1) |
| DGX OS（定制 Ubuntu 24.04 / Linux） | **openEuler 欧拉**（Atlas 服务器官方推荐 openEuler 22.03 LTS ARM64，昇腾驱动官方仅支持 Euler 系列）[[15]](https://support.huawei.com/enterprise/zh/doc/EDOC1100258040/fc9f82a1) |

关键判断：

1. **连华为自己的 AI 算力底座（昇腾 Atlas）跑的都是 openEuler（Linux），不是鸿蒙。** NVIDIA DGX 用 Ubuntu、华为 Atlas 用 openEuler——同一个逻辑：AI 训练/推理这种高性能算力调度场景是 Linux 的天下，谁都不例外。

2. **「昇腾对应鸿蒙的方案」这个问法要拆开。** 昇腾对应的操作系统是 **openEuler，不是鸿蒙**；昇腾对应 CUDA 生态的，是 **CANN + HCCS + 灵衢** 这一整套国产平行宇宙。鸿蒙在算力栈里是**缺席**的——它是终端/消费侧 OS（手机、PC、车机、IoT），与数据中心算力 OS 是两条平行线。

3. **原文「DGX Spark 坚持 Linux」的逻辑在华为身上完全镜像。** 自家芯片 + 自家互联 + 自家通信库 + 自家计算栈，但操作系统底座照样押 Linux（欧拉）。把三方分家的图景补完整，更准确的概括是：**消费端是 Windows / 鸿蒙 / Linux 的 OS 之争，算力端则是 Linux 一统（NVIDIA→Ubuntu，华为→openEuler）。**

---

## 信源

[1] T. Claburn, "Nvidia's Grace Blackwell superchips are officially coming to the PC with RTX Spark notebooks," *The Register*, Jun. 1, 2026. [Online]. Available: <https://www.theregister.com/systems/2026/06/01/nvidia-recasts-gb10-superchip-in-bid-for-high-end-pc-market/>

[2] "Nvidia's RTX Spark could capitalize where Qualcomm's Arm-based efforts have not," *Tom's Hardware*, 2026. (GB10 Arm CPU 由联发科代工，TSMC 3nm 级；20 核 Grace + Blackwell RTX、128GB LPDDR5X。) [Online]. Available: <https://www.tomshardware.com/laptops/nvidia-enters-the-windows-pc-market-with-rtx-spark>

[3] "Nvidia RTX Spark," *Wikipedia*, 2026. (2026-05-31 与微软联合发布；整机 2026 秋季由 Asus/Dell/HP/Lenovo/Surface/MSI 出货。) [Online]. Available: <https://en.wikipedia.org/wiki/Nvidia_RTX_Spark>

[4] NVIDIA, "Personal AI Supercomputer Powered by Blackwell — NVIDIA DGX Spark," *NVIDIA.com*. (预装 DGX OS，基于 Ubuntu 24.04 LTS。) [Online]. Available: <https://www.nvidia.com/en-us/products/workstations/dgx-spark/>

[5] "DGX Spark: Could Windows on ARM Support Be Possible, Like RTX Spark, N1X?," *NVIDIA Developer Forums*, 2026. [Online]. Available: <https://forums.developer.nvidia.com/t/dgx-spark-could-windows-on-arm-support-be-possible-like-rtx-spark-n1x/371870>

[6] M. Garrett, "ARM and firmware specifications," *mjg59 dreamwidth*. (微软自 Windows RT 起强制 ARM 设备实现 UEFI+ACPI，以复用既有启动/驱动栈。) [Online]. Available: <https://mjg59.dreamwidth.org/26535.html>

[7] "ACPI on Arm systems," *The Linux Kernel documentation*. (ACPI 仅在 UEFI 启动平台支持；ARM 启动时可有 DT、ACPI 或二者；无命令行参数时内核优先用 DT，无 DT 才尝试 ACPI。) [Online]. Available: <https://docs.kernel.org/arch/arm64/arm-acpi.html>

[8] OpenHarmony, "Framework of the Hardware Driver Foundation (HDF) | HDF 驱动框架," *GitHub*. (HDF 解析 HCS 配置完成设备发现；驱动可跨内核复用。) [Online]. Available: <https://github.com/openharmony/drivers_framework>

[9] "华为，最新发布！鸿蒙电脑首度亮相," *证券时报网*, 2025-05-19. (MateBook Pro 7999 元起 / MateBook Fold 23999 元起；HarmonyOS 5 + 麒麟 X90，从内核重构。) [Online]. Available: <https://www.stcn.com/article/detail/1821418.html>

[10] H. Chen et al., "Microkernel Goes General: Performance and Compatibility in the HongMeng Production Microkernel," *USENIX OSDI*, 2024. (鸿蒙内核经 ABI shim + driver container 复用 Linux 驱动；为避免许可证污染做容器隔离与孪生驱动。) [Online]. Available: <https://www.usenix.org/system/files/osdi24-chen-haibo.pdf>

[11] NVIDIA, "Linux Ethernet Drivers — MLNX_EN," *NVIDIA Networking*. (ConnectX 系列 Linux 驱动经 MLNX_OFED/MLNX_EN 分发，含闭源固件与组件。) [Online]. Available: <https://network.nvidia.com/products/ethernet-drivers/linux/mlnx_en/>

[12] "一篇文章说明常见的 AI 芯片高速互连方案," *ScenSmart*. (昇腾 910B：每 NPU 7 条双向 HCCS、各 56GB/s，单板 8 卡共 392GB/s，对标 A800 NVLink 400GB/s。) [Online]. Available: <https://www.scensmart.com/news/one-article-explains-common-high-speed-interconnect-solutions-for-ai-chips/>

[13] "中国 AI 高速路，华为给出开源开放方案," *量子位*, 2025-09. (灵衢 UnifiedBus 超节点互联协议，用于 Atlas 950/960 等大带宽低时延互联。) [Online]. Available: <https://www.qbitai.com/2025/09/335890.html>

[14] "NVLink、HCCL 及传统 PCIe 传输对比分析报告," *知乎*. (HCCL 为昇腾集合通信库，对标 NVIDIA NCCL。) [Online]. Available: <https://zhuanlan.zhihu.com/p/1907189956348220034>

[15] 华为, "Atlas 服务器 openEuler 22.03 LTS 操作系统安装指导书（Arm）," *华为企业技术支持*. (Atlas 服务器官方推荐 openEuler 22.03 LTS ARM64；昇腾驱动官方仅支持 Euler 系列；CANN 为 NPU 驱动与工具链。) [Online]. Available: <https://support.huawei.com/enterprise/zh/doc/EDOC1100258040/fc9f82a1>

[16] "Apple Device Tree (ADT)," *Asahi Linux Documentation*. (ADT 由 iBoot2 构建，私有二进制格式，区别于 Linux 的 Flattened Device Tree；XNU 经 SecureDTLookup API 直接消费；Apple Silicon 不用 UEFI/ACPI。) [Online]. Available: <https://asahilinux.org/docs/fw/adt/>

[17] "Introduction to Apple Silicon," *Asahi Linux Documentation*. (m1n1 为 first-stage bootstrap，桥接 XNU 启动协议与 Device Tree / ARM64 Linux 启动协议；SoC 无公开文档，靠逆向工程。) [Online]. Available: <https://asahilinux.org/docs/platform/introduction/>

[18] Parallels, "Microsoft-authorized Windows 11 on Mac," *Parallels Desktop*. (Parallels 为微软唯一授权在 Apple Silicon 上运行 Windows 11 ARM 的虚拟化方案；M 系列无原生 Boot Camp 双启动。) [Online]. Available: <https://www.parallels.com/products/desktop/microsoft-authorized-solution-windows-11-arm/>
