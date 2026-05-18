{%- set ext_layers = layers | rejectattr('view') | list -%}
## L 层 × 分支 总表

横轴 {{ branches | length }} 列对应 **{{ branches[0].code }}–{{ branches[-1].code }} 共 {{ branches | length }} 条领域分支**。纵轴每一行是一个 L 层，每个条目**严格归属**到当行 L，不跨层。规则：

- `同 {{ branches[0].code }}`：该层在该分支与 {{ branches[0].code }} 列基本沿用同款（驱动 / 内核 / 编译器 / 实验追踪多数如此）。
- `—`：该层在该分支不存在或可忽略。
- **{{ ext_layers[0].code }}–{{ ext_layers[-1].code }}** 是 {{ branches[0].code }} 没有、仅部分领域分支必需的扩展层；{{ branches[0].code }} 列保持空。
  - {{ ext_layers[0].code }} {{ ext_layers[0].name }}（B 专属：Slurm[[4]](https://slurm.schedmd.com/) / PBS / Spack 这一段在 LLM 训练里被 K8s[[5]](https://kubernetes.io/) + Ray[[6]](https://docs.ray.io/en/latest/index.html) 取代）
  - {{ ext_layers[1].code }} {{ ext_layers[1].name }}（C / D 共用：ROS 2[[7]](https://www.ros.org/) / DriveWorks / AUTOSAR / Holoscan）
  - {{ ext_layers[2].code }} {{ ext_layers[2].name }}（B / C / D / E 共用：Isaac Sim / MuJoCo[[8]](https://mujoco.org/) / GROMACS[[9]](https://www.gromacs.org/) / CARLA / Omniverse）
  - {{ ext_layers[3].code }} {{ ext_layers[3].name }}（D 专属）

---OUTRO---
---
