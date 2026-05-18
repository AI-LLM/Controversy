## L 层 × 分支 总表

横轴 10 列对应 **A–J 共 10 条领域分支**。纵轴每一行是一个 L 层，每个条目**严格归属**到当行 L，不跨层。规则：

- `同 A`：该层在该分支与 A 列基本沿用同款（驱动 / 内核 / 编译器 / 实验追踪多数如此）。
- `—`：该层在该分支不存在或可忽略。
- **L35–L38** 是 A 没有、仅部分领域分支必需的扩展层；A 列保持空。
  - L35 HPC 作业调度 / 工作流（B 专属：Slurm[[4]](https://slurm.schedmd.com/) / PBS / Spack 这一段在 LLM 训练里被 K8s[[5]](https://kubernetes.io/) + Ray[[6]](https://docs.ray.io/en/latest/index.html) 取代）
  - L36 机器人 / 实时中间件（C / D 共用：ROS 2[[7]](https://www.ros.org/) / DriveWorks / AUTOSAR / Holoscan）
  - L37 物理仿真 / 数字孪生引擎（B / C / D / E 共用：Isaac Sim / MuJoCo[[8]](https://mujoco.org/) / GROMACS[[9]](https://www.gromacs.org/) / CARLA / Omniverse）
  - L38 高精地图 / 定位（D 专属）

---OUTRO---
---
