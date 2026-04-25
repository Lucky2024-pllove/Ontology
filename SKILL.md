---
name: Ontology
version: 1.0.0
description: "领域本体六类模型（对象、行为、规则、场景/流程、主体、领域事件、异常与补偿）及对象分析、事件驱动扩展；输出 Markdown、JSON 与可选 YAML；内置模板与分章说明；支持将成果归档到飞书知识库并以画板形式呈现 Mermaid。当用户需要领域建模、业务架构、本体层对接下游应用或向飞书交付领域文档时使用。"
metadata:
  requires:
    bins: ["python3"]
  optional_for_feishu:
    bins: ["lark-cli"]
    notes: "飞书归档与画板需 lark-cli；复杂画板可配合 npx @larksuite/whiteboard-cli"
---

# 本体层构建技能（Ontology）

**默认交付**：仅生成本地 **`{basename}.md` / `{basename}.json`（及可选 `.yaml`）**，**不要求**飞书知识库信息。  
**可选路径**：用户若需要**一并归档到飞书知识库**，再执行步骤 14；步骤与命令见 [references/feishu-delivery.md](references/feishu-delivery.md)。

- **未**要求飞书归档、或**未提供** `space_id` / `parent_node_token`（等定位信息）时：**跳过飞书**，完成文件交付即可，不视为任务未完成。  
- **仅当**用户明确要求飞书归档时，才向用户索要并确认（不可推断、不可臆造）：**知识空间 `space_id`**、**父知识库节点 `parent_node_token`**、**节点/文档标题**（可与 `basename` 一致）。若只给 URL，按 [references/feishu-delivery.md](references/feishu-delivery.md) **第 2 节**解析或请用户补全。

> 本包提供的是**方法论、模板、校验脚本与示例**（`references/`、`assets/`、`scripts/`、`examples/`）。`lark-cli`、可选的 `npx @larksuite/whiteboard-cli` 等需在使用环境自行安装。

## 术语对照（强制）

| 规范/业务用语 | 技能落点 |
|--------------|----------|
| 场景 | 与 JSON 根字段 `processes` 对应；文档标题可用「场景/流程」 |
| 流程 | 与 `Process` 对象一致，即 `processes[]` 中的一项 |
| 领域事件 / 事件链 | `events` + 行为上 `publishesEventIds` / `subscribesToEventIds` |
| 主体 | `subjects`（人、组织、系统角色、外部系统） |
| 异常与补偿 | `compensations`（**业务**失败与 Saga/回滚；非 `signature.exceptions` 技术项） |

---

## 一、触发条件

**当用户需要…**
- 从需求文档、业务流程、技术说明中抽取领域本体
- 生成可被 API 或下游系统消费的机器可读本体（**JSON 为主，可选 YAML**）
- 构建知识图谱、事件驱动、规则 / 流程引擎所需的全部分层模型

**当任务需要…**
- 对象、行为、规则、**场景（流程）**、**主体**、**领域事件**、**异常与补偿** 的统一建模
- 双格式或三格式：Markdown + JSON +（**可选**）YAML
- 与规则引擎、流程引擎、**消息/事件** 总线及各类集成场景对接
- 将领域模型**归档到飞书知识库**某空间、某父节点下，并把文档中的 Mermaid 以**飞书画板**呈现

**当 Agent 无法…**
- 从零推导领域结构时：按本技能的 SOP 从源材料中抽取线索
- 判断输出是否完整时：按能力边界的验证策略检查

---

## 二、作业流程

### SOP 步骤概览

| 步骤 | 活动 | 输出 |
|-----|------|------|
| 1 | 源材料分析 | 六类要素线索清单（+ EDA/事件线） |
| 2 | 对象模型建模 | 实体表 + classDiagram |
| 3 | 行为模型建模 | 行为表 + 调用与 **事件发布/消费** 关系 |
| 4 | 规则模型建模 | 规则表 + 依赖图 |
| 5 | **主体模型建模** | 主体表 + 与行为/流程的参与关系 |
| 6 | **领域事件建模** | 事件表 + **行为 → 事件 → 行为/规则** 链图 |
| 7 | **异常与补偿建模** | 补偿表 + 与流程失败路径/行为的对应 |
| 8 | 流程/场景建模 | 流程表 + flowchart/sequenceDiagram |
| 9 | 分层架构与全景图 | Mermaid 分层图、知识图谱（**含事件、主体、补偿节点样式**见 output-format） |
| 10 | 领域模型文档 | `{basename}.md` |
| 11 | 机器可读 JSON | `{basename}.json` |
| 12 | **可选 YAML** | `{basename}.yaml`（与 JSON **语义等价**） |
| 13 | 输出与验证 | 交付 + 自检 |
| 14 | （可选）飞书归档 | 知识库节点 + 文档，Mermaid → 画板，见 [references/feishu-delivery.md](references/feishu-delivery.md) |

### 输出文件命名（强制）

交付物 **不得** 默认使用固定名 `domain-model`，须从**用户资料与任务表述**抽取**文件基名** `basename`：

- **必备**：`{basename}.md`、`{basename}.json`（**同基名**）
- **推荐**：`{basename}.yaml`（与 JSON 为同一领域对象，便于配置管理与多环境交付）

在交付说明首段列出**已交付**的完整文件名；`metadata.source` 注明来源；注意本地路径与基名**一致、可解析**（勿含非法文件名字符）。

### 各步骤要点

- **步骤 1**：在原有四类线索上，增加**责任主体**、**跨步骤领域事件**、**失败/冲正** 等线索。  
- **步骤 2～4、8**：见 [references/ontology-methodology.md](references/ontology-methodology.md)、[references/behavior-modeling.md](references/behavior-modeling.md)、[references/rule-modeling.md](references/rule-modeling.md)、[references/process-modeling.md](references/process-modeling.md)。行为须考虑 **publishesEventIds** / **subscribesToEventIds**。  
- **步骤 5～7**：见 [references/eda-subject-compensation.md](references/eda-subject-compensation.md) 与 [references/machine-readable-format.md](references/machine-readable-format.md) 中 `subjects`、`events`、`compensations`。  
- **步骤 9～12**：见 [references/output-format.md](references/output-format.md)、[assets/domain-model-template.md](assets/domain-model-template.md)、[references/machine-readable-format.md](references/machine-readable-format.md)。  
- **步骤 14（飞书，可选）**：仅当用户**需要**飞书归档**且**已提供或可解析出 `space_id`、`parent_node_token` 等时执行；**不得臆造**定位信息。按 [references/feishu-delivery.md](references/feishu-delivery.md) 使用 `lark-cli wiki +node-create` 与 `lark-cli docs +update`；Mermaid 转 `<whiteboard type="mermaid">` 或走复杂画板流程。用户未要求或未提供定位信息时**不执行**本步。

### 基于脚本

- 校验 JSON：在含 `SKILL.md` 的目录下执行 `python scripts/validate.py <你的文件>.json`（或写绝对路径）  
- YAML 可由同一对象序列化得到，不单独强制脚本。

---

## 三、能力边界

### 预期输出

- **`{basename}.md`**：领域概览、**六类/扩展**模型章节、可视化、附录
- **`{basename}.json`**：根级含 `entities`、`behaviors`、`rules`、**`subjects`、`events`、`compensations`**、`processes`（**可为空数组**）
- **可选** **`{basename}.yaml`**：与 JSON 同构
- **Mermaid**：含事件链、主体参与、补偿路径时须在图或表中体现

### 验证策略

- [ ] 文档中 **对象、行为、规则、场景/流程、主体、领域事件、异常与补偿** 均有章节或明确声明「本领域为空/不适用」
- [ ] 实体、行为、规则、流程（场景） 字段与 [references/machine-readable-format.md](references/machine-readable-format.md) 一致
- [ ] `subjects` / `events` / `compensations` 中 ID 与行为、流程、规则间引用**可解析**（无悬空 ID，除非 metadata 说明外部系统）
- [ ] 行为上 **事件** 与 `events[]` 中 `publishedByBehaviorId` / 消费方一致（或注明待对账）
- [ ] 补偿与 **长流程/多步** 的关联清楚（`relatedProcessId` / `fromStepId` 等，可为空但需有说明）
- [ ] JSON 与 Markdown 的 id/名称映射一致
- [ ] 关系引用使用 `targetId` 或规范中的 ID 字段，非仅名称

### 终止条件

- **成功**：验证通过，用户确认交付
- **部分成功**：源材料不足时，完成可建部分并注明「待补充」
- **终止**：源材料不可读或与建模无关

### 备选方案

- 源材料过于抽象：先建**对象**与**主流程/场景**，主体/事件/补偿标为待细化
- 消费方只收 JSON 或只收 YAML：以 **JSON 为准** 做单向转换
- 无法确定主事件/补偿：保留结构占位并在文档中列「需业务确认」
- 未要求飞书、或未提供知识库定位信息、或未安装 `lark-cli`：只交付本地 **md/json/yaml**，不执行飞书步骤

---

## 资源索引

| 用途 | 文件 |
|-----|------|
| 对象分析+事件驱动、主体/事件/补偿 | [references/eda-subject-compensation.md](references/eda-subject-compensation.md) |
| 对象建模 | [references/ontology-methodology.md](references/ontology-methodology.md) |
| 行为建模 | [references/behavior-modeling.md](references/behavior-modeling.md) |
| 规则建模 | [references/rule-modeling.md](references/rule-modeling.md) |
| 流程/场景 | [references/process-modeling.md](references/process-modeling.md) |
| 人读版式与 Mermaid | [references/output-format.md](references/output-format.md) |
| JSON 结构、代码消费与集成 | [references/machine-readable-format.md](references/machine-readable-format.md)（唯一详述） |
| 文档模板 | [assets/domain-model-template.md](assets/domain-model-template.md) |
| 飞书知识库 + Mermaid/画板交付 | [references/feishu-delivery.md](references/feishu-delivery.md) |

---

## 机器可读与消费

**单一详述来源**：根字段、各对象 Schema、示例 JSON、**集成与运行时关注点**与**机器消费指南**（含引用一致性思路）见 [references/machine-readable-format.md](references/machine-readable-format.md)。人读 Markdown 章节结构、Mermaid 图例与版式见 [references/output-format.md](references/output-format.md)（`output-format` **不**重复 JSON 与代码消费细节）。
