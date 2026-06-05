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

| 维度 | Windows on ARM | Linux on ARM64 | 鸿蒙 HarmonyOS（ARM） |
|---|---|---|---|
| 代表硬件 | RTX Spark、Surface、骁龙 X 系列笔记本 | DGX Spark、各类 ARM 服务器 / 嵌入式 | 鸿蒙电脑（麒麟 X90）、手机、车机、IoT |
| 启动固件 | **强制 UEFI** | UEFI（服务器）或 U-Boot 等（嵌入式），灵活 | 华为自有引导链（非标准 UEFI+ACPI；细节未公开 ⚠） |
| 硬件描述体系 | **只认 ACPI**（经 UEFI 传表） | **ACPI 与设备树（DT）二者皆可** | **HDF + HCS**（自有，HCS 为树状配置，概念近 DT 但格式不同）[[8]](https://github.com/openharmony/drivers_framework) |
| 内核 | Windows NT 内核 | Linux 内核 | 鸿蒙内核（HarmonyOS NEXT / 鸿蒙 5）；OpenHarmony 另有 LiteOS 等 |
| 驱动模型 | WDM / WDF | Linux 设备驱动模型 | HDF（Hardware Driver Foundation），可跨内核复用驱动 [[8]](https://github.com/openharmony/drivers_framework) |
| 跨体系兼容 | 封闭、最严格（缺 ACPI 直接起不来） | 最宽松（两套都吃） | 自成一套，靠 HDF 抽象屏蔽底层差异 |

几个关键判断：

1. **「分家」的真正分界线是 Windows，不是 Linux。** Linux 是三家里最「不挑」的——ACPI、DT 都能引导，所以它能装进 DGX Spark，理论上也能（在补齐驱动的前提下）装进对标 ACPI 的硬件。Windows 是唯一把自己钉死在 ACPI 上的。鸿蒙则干脆**两套主流标准都不用**，自起炉灶用 HDF+HCS。

2. **鸿蒙走的是「第三条路」，而非选边站。** HCS（HarmonyOS Configuration Source）是树状的硬件配置描述，直觉上和 Linux 的设备树最像，但它是华为自有格式、由 HDF 驱动框架在初始化阶段解析，不和 ACPI 也不和标准 DTB 互通。HDF 的设计目标之一是**让同一份驱动能在不同内核（LiteOS / Linux / 鸿蒙内核）上复用** [[8]](https://github.com/openharmony/drivers_framework)——这是和 Windows「绑死单一内核+ACPI」相反的取向。

3. **桌面落地的现实对照。** 三家都已经把 ARM 推到了桌面：RTX Spark（Windows on ARM，2026 秋）、DGX Spark（Linux，已售）、鸿蒙电脑 MateBook Pro / Fold（HarmonyOS 5 + 麒麟 X90，2025-05-19 发售，从内核重构、不支持侧载）[[9]](https://www.stcn.com/article/detail/1821418.html)。但三者的「同芯换系统」可能性完全不同：Windows ↔ Linux 卡在 ACPI/DT + 驱动两道门槛（如原文 DGX Spark 案例）；鸿蒙电脑则**软硬一体、垂直封闭**，麒麟 + 鸿蒙内核 + HDF 自成闭环，换系统的命题在它这里基本不成立。

4. **「封闭度」排序**：Linux（最开放，两套标准通吃）< Windows on ARM（认证封闭，但走 UEFI+ACPI 业界标准）< 鸿蒙（标准与生态都自有，垂直整合最深）。原文把矛盾框成「Windows vs Linux」，加入鸿蒙后更准确的图景是：**一边是 ACPI/DT 这套开放业界标准内部的 Windows/Linux 之争，另一边是鸿蒙另立标准的国产化垂直路线。**

⚠ **声明**：鸿蒙电脑底层固件（是否用类 UEFI 引导、引导阶段如何向鸿蒙内核传递硬件信息）华为未公开技术文档，表中「启动固件」一栏与第 3 点的闭环判断为据公开报道与 OpenHarmony 框架资料的**推断**，非官方确认。

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
