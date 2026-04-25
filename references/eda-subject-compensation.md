# 本体论视角：OOA + EDA 与 主体 / 事件 / 异常补偿

本说明阐述 **面向对象分析（OOA）** 与 **事件驱动（EDA）** 如何与六类模型中的**主体、领域事件、异常与补偿**相衔接，与主技能 `SKILL.md` 中的 SOP 与 JSON 结构配合使用，**不**替代 `machine-readable-format.md` 的字段级定义。

## 1. 为何融合 OOA 与 EDA

- **面向对象分析（OOA）** 解决「**对象**是什么、**行为**如何归属对象、**规则**如何约束状态」。
- **事件驱动（EDA）** 解决纯**流程驱动**时易出现的行为紧耦、**长周期事务**难以拆分的问题：用**领域事件**在行为与规则之间解耦，以**事件链**串联业务流程。
- 链式结构：**行为 → 领域事件 → 行为**（可叠加规则消费事件）。有利于后续 **数据/状态变化反向触发业务**（如状态机、补偿、再编排）。

## 2. 与六类模型的关系

| 常见表述 | 本技能中的落点 |
|---------|----------------|
| 对象、行为、规则、**场景** | 对象/行为/规则层不变；**场景** 在交付物中对应 **「场景/流程」** 章节与 JSON 的 `processes`（见 SKILL 术语对照） |
| **主体** | 独立 **主体** 层，JSON 根节点 `subjects` |
| **异常补偿** | 独立 **异常与补偿** 层，JSON 根节点 `compensations`（业务向 Saga/回滚，区别于行为签名里的技术 `exceptions`） |
| 领域事件 | 一阶 `events`；**行为** 可声明 `publishesEventIds` / `subscribesToEventIds` 勾连事件链 |

## 3. 建模时的最小 EDA 自检

- [ ] 关键业务完成后是否有**可命名的领域事件**（可被下游行为或规则消费）？
- [ ] 与「长流程/多步」强相关的失败路径，是否在 **compensations** 中给出**补偿行为序列或顺序**？
- [ ] 承担行为的角色/系统是否在 **subjects** 中显式标出，并与 `processes.participants` / 步骤 `participant` 可对应（允许一方为从属描述）？

## 4. 与机器可读 JSON 的对应

详见 [machine-readable-format.md](machine-readable-format.md) 中 **Subject / Event / Compensation** 各节，以及 `Behavior` 的 `publishesEventIds`、`subscribesToEventIds`。

---

## YAML 与 JSON 的关系

- **JSON** 为权威、完整结构（`{basename}.json`）。
- **YAML** 为**等价交换格式**（`{basename}.yaml`），内容应与 JSON 表示的**同一领域对象**一致，便于下游系统或配置管线消费；**不得**在 YAML 中引入 JSON 不存在的根字段（除非已同步规范）。
