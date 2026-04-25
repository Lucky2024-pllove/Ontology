# 机器可读格式规范

## 目录
- [JSON Schema 概述](#json-schema-概述)
- [对象模型 JSON 格式](#对象模型-json-格式)
- [行为模型 JSON 格式](#行为模型-json-格式)
- [规则模型 JSON 格式](#规则模型-json-格式)
- [主体模型 JSON 格式](#主体模型-json-格式)
- [领域事件 JSON 格式](#领域事件-json-格式)
- [异常与补偿 JSON 格式](#异常与补偿-json-格式)
- [流程/场景 JSON 格式](#流程场景-json-格式)（`processes` 对应业务**场景/流程**）
- [完整 JSON 结构](#完整-json-结构)
- [集成与运行时关注点](#集成与运行时关注点)
- [机器消费指南](#机器消费指南)

> **术语**：文中「**场景**」与根字段 `processes` 一一对应；`Process` 即一条可编排的**业务场景/流程**实例。与 OOA+EDA 扩展的关系见 [eda-subject-compensation.md](eda-subject-compensation.md)。
>
> **单一详述（JSON）**：本文件为**根结构、各对象字段、机器消费示例**的**唯一**权威说明；[output-format.md](output-format.md) 仅规范人读 Markdown 与 Mermaid，不重复 JSON 与代码。

## JSON Schema 概述

### 设计原则

1. **ID 优先**：`entities` / `behaviors` / `rules` / `subjects` / `events` / `compensations` / `processes` 中**各条记录**均须有唯一 `id`（`Process.steps` 等嵌套子项亦然，按各节约定）
2. **引用明确**：关系通过 `id` 引用，而非仅名称
3. **类型明确**：每个对象都有明确的 `type` 等区分字段（按各节 Schema）
4. **可扩展**：预留 `metadata` 等用于扩展
5. **一致性**：JSON 与对应 Markdown 领域文档可互查

### 数据类型映射

| Markdown类型 | JSON类型 | 示例 |
|-------------|---------|------|
| 实体名称 | string | "Contract" |
| 数据类型 | string | "String", "Integer", "Decimal" |
| 约束条件 | object | {"min": 0, "max": 100} |
| 关系 | object | {"targetId": "Entity-002", "type": "1:N"} |
| 布尔值 | boolean | true, false |
| 数组 | array | ["item1", "item2"] |

## 对象模型 JSON 格式

### Entity Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Entity",
  "type": "object",
  "required": ["id", "name", "type", "properties"],
  "properties": {
    "id": {
      "type": "string",
      "description": "实体唯一标识，格式：Entity-{序号}"
    },
    "name": {
      "type": "string",
      "description": "实体名称（中文）"
    },
    "nameEn": {
      "type": "string",
      "description": "实体英文名称（可选）"
    },
    "type": {
      "type": "string",
      "enum": ["core", "reference"],
      "description": "实体类型：core(核心实体), reference(引用实体)"
    },
    "parentId": {
      "type": "string",
      "description": "父类实体ID（可选）"
    },
    "description": {
      "type": "string",
      "description": "实体描述"
    },
    "properties": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Property"
      }
    },
    "relations": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Relation"
      }
    },
    "metadata": {
      "type": "object",
      "description": "扩展元数据"
    }
  },
  "definitions": {
    "Property": {
      "type": "object",
      "required": ["name", "dataType"],
      "properties": {
        "name": {"type": "string"},
        "dataType": {
          "type": "string",
          "enum": ["String", "Integer", "Float", "Decimal", "Boolean", "Date", "DateTime", "Object"]
        },
        "constraints": {
          "type": "object",
          "properties": {
            "required": {"type": "boolean"},
            "unique": {"type": "boolean"},
            "min": {"type": "number"},
            "max": {"type": "number"},
            "pattern": {"type": "string"},
            "enum": {"type": "array"}
          }
        },
        "description": {"type": "string"}
      }
    },
    "Relation": {
      "type": "object",
      "required": ["targetId", "type"],
      "properties": {
        "targetId": {
          "type": "string",
          "description": "关联实体ID"
        },
        "type": {
          "type": "string",
          "enum": ["1:1", "1:N", "N:1", "N:M"]
        },
        "relationType": {
          "type": "string",
          "enum": ["inheritance", "association", "composition", "aggregation"]
        },
        "description": {"type": "string"}
      }
    }
  }
}
```

### Entity 示例

```json
{
  "id": "Entity-001",
  "name": "合同",
  "nameEn": "Contract",
  "type": "core",
  "parentId": null,
  "description": "业务合同实体，记录合同基本信息",
  "properties": [
    {
      "name": "合同编号",
      "dataType": "String",
      "constraints": {
        "required": true,
        "unique": true,
        "pattern": "^CT[0-9]{10}$"
      },
      "description": "合同唯一编号"
    },
    {
      "name": "金额",
      "dataType": "Decimal",
      "constraints": {
        "required": true,
        "min": 0
      },
      "description": "合同总金额"
    },
    {
      "name": "状态",
      "dataType": "String",
      "constraints": {
        "required": true,
        "enum": ["草稿", "待审批", "已生效", "已作废"]
      },
      "description": "合同当前状态"
    }
  ],
  "relations": [
    {
      "targetId": "Entity-002",
      "type": "N:1",
      "relationType": "association",
      "description": "合同归属客户"
    },
    {
      "targetId": "Entity-003",
      "type": "1:N",
      "relationType": "composition",
      "description": "合同包含付款条款"
    }
  ],
  "metadata": {
    "source": "需求文档v1.2",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

## 行为模型 JSON 格式

### Behavior Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Behavior",
  "type": "object",
  "required": ["id", "name", "entityId"],
  "properties": {
    "id": {
      "type": "string",
      "description": "行为唯一标识，格式：Behavior-{序号}"
    },
    "name": {
      "type": "string",
      "description": "行为名称"
    },
    "entityId": {
      "type": "string",
      "description": "所属实体ID"
    },
    "description": {
      "type": "string"
    },
    "signature": {
      "type": "object",
      "properties": {
        "inputs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "dataType": {"type": "string"},
              "required": {"type": "boolean"},
              "constraints": {"type": "object"},
              "description": {"type": "string"}
            }
          }
        },
        "outputs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "dataType": {"type": "string"},
              "description": {"type": "string"}
            }
          }
        },
        "exceptions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string"},
              "condition": {"type": "string"},
              "message": {"type": "string"}
            }
          }
        }
      }
    },
    "preconditions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "前置条件表达式列表"
    },
    "postconditions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "后置条件表达式列表"
    },
    "invokes": {
      "type": "array",
      "items": {"type": "string"},
      "description": "调用的其他行为ID列表"
    },
    "triggeredBy": {
      "type": "array",
      "items": {"type": "string"},
      "description": "触发该行为的行为/事件ID列表"
    },
    "publishesEventIds": {
      "type": "array",
      "items": {"type": "string"},
      "description": "该行为成功完成后发布的领域事件ID列表（与 Event.publishedByBehaviorId 对应）"
    },
    "subscribesToEventIds": {
      "type": "array",
      "items": {"type": "string"},
      "description": "启动或推进该行为所依赖/消费的领域事件ID列表"
    },
    "validates": {
      "type": "array",
      "items": {"type": "string"},
      "description": "该行为触发校验的规则ID列表"
    },
    "metadata": {
      "type": "object"
    }
  }
}
```

### Behavior 示例

```json
{
  "id": "Behavior-001",
  "name": "创建合同",
  "entityId": "Entity-001",
  "description": "创建新的合同记录",
  "signature": {
    "inputs": [
      {
        "name": "客户ID",
        "dataType": "String",
        "required": true,
        "constraints": {"pattern": "^CU[0-9]{8}$"},
        "description": "客户唯一标识"
      },
      {
        "name": "金额",
        "dataType": "Decimal",
        "required": true,
        "constraints": {"min": 0},
        "description": "合同金额"
      },
      {
        "name": "条款列表",
        "dataType": "Array",
        "required": true,
        "constraints": {"minItems": 1},
        "description": "付款条款列表"
      }
    ],
    "outputs": [
      {
        "name": "合同对象",
        "dataType": "Object",
        "description": "创建的合同对象"
      }
    ],
    "exceptions": [
      {
        "type": "CustomerNotFoundException",
        "condition": "客户ID不存在",
        "message": "客户不存在"
      },
      {
        "type": "InvalidAmountException",
        "condition": "金额 <= 0",
        "message": "金额必须大于0"
      }
    ]
  },
  "preconditions": [
    "客户状态 = '正常'",
    "当前用户有创建合同权限"
  ],
  "postconditions": [
    "合同状态 = '草稿'",
    "生成合同编号"
  ],
  "invokes": ["Behavior-002", "Behavior-003"],
  "triggeredBy": ["Process-001"],
  "validates": ["Rule-001", "Rule-002"],
  "publishesEventIds": ["Event-001"],
  "subscribesToEventIds": [],
  "metadata": {
    "transactional": true,
    "async": false
  }
}
```

## 规则模型 JSON 格式

### Rule Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Rule",
  "type": "object",
  "required": ["id", "name", "type"],
  "properties": {
    "id": {
      "type": "string",
      "description": "规则唯一标识，格式：Rule-{序号}"
    },
    "name": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": ["validation", "business", "state", "computation"]
    },
    "description": {
      "type": "string"
    },
    "trigger": {
      "type": "object",
      "properties": {
        "event": {"type": "string"},
        "target": {"type": "string"},
        "timing": {"type": "string"}
      }
    },
    "condition": {
      "type": "object",
      "properties": {
        "expression": {"type": "string"},
        "description": {"type": "string"}
      }
    },
    "actions": {
      "type": "object",
      "properties": {
        "onTrue": {
          "type": "array",
          "items": {"type": "string"}
        },
        "onFalse": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "priority": {
      "type": "integer",
      "description": "规则优先级，数值越大优先级越高"
    },
    "scope": {
      "type": "string",
      "description": "规则生效范围"
    },
    "dependsOn": {
      "type": "array",
      "items": {"type": "string"},
      "description": "依赖的规则ID列表"
    },
    "triggers": {
      "type": "array",
      "items": {"type": "string"},
      "description": "触发的其他规则ID列表"
    },
    "metadata": {
      "type": "object"
    }
  }
}
```

### Rule 示例

```json
{
  "id": "Rule-001",
  "name": "合同金额非空校验",
  "type": "validation",
  "description": "验证合同金额必须大于0",
  "trigger": {
    "event": "合同提交",
    "target": "Entity-001",
    "timing": "提交前"
  },
  "condition": {
    "expression": "amount > 0",
    "description": "合同金额必须大于0"
  },
  "actions": {
    "onTrue": ["继续流程"],
    "onFalse": ["抛出InvalidAmountException", "返回错误信息"]
  },
  "priority": 100,
  "scope": "全局",
  "dependsOn": [],
  "triggers": [],
  "metadata": {
    "category": "基础校验",
    "version": "1.0"
  }
}
```

## 主体模型 JSON 格式

**主体**（人、组织、系统角色、外部系统）是责任与参与边界的一阶对象；**不等同**于数据实体，但可与 `Entity` 通过 `metadata` 或 `boundEntityId` 关联。

### Subject Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Subject",
  "type": "object",
  "required": ["id", "name", "type"],
  "properties": {
    "id": {
      "type": "string",
      "description": "唯一标识，格式：Subject-{序号}"
    },
    "name": { "type": "string" },
    "nameEn": { "type": "string" },
    "type": {
      "type": "string",
      "enum": ["role", "person", "organization", "system", "external"],
      "description": "主体类型"
    },
    "description": { "type": "string" },
    "boundEntityId": {
      "type": "string",
      "description": "可选，对应的引用实体/参与方实体 ID（如“客户”在对象层有实体时）"
    },
    "performsBehaviorIds": {
      "type": "array",
      "items": { "type": "string" },
      "description": "常执行或负责的行为 ID"
    },
    "participatesInProcessIds": {
      "type": "array",
      "items": { "type": "string" },
      "description": "参与的流程/场景 ID"
    },
    "metadata": { "type": "object" }
  }
}
```

### Subject 示例

```json
{
  "id": "Subject-001",
  "name": "销售承办人",
  "type": "role",
  "description": "负责合同创建与日常维护",
  "boundEntityId": null,
  "performsBehaviorIds": ["Behavior-001", "Behavior-002"],
  "participatesInProcessIds": ["Process-001"],
  "metadata": {}
}
```

## 领域事件 JSON 格式

**领域事件**用于 **行为 → 事件 → 行为/规则** 的解耦与编排；`trigger.event` 可写自然语言名，**推荐**同时引用本处 `Event.id`。

### Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DomainEvent",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "唯一标识，格式：Event-{序号}"
    },
    "name": { "type": "string" },
    "nameEn": { "type": "string" },
    "description": { "type": "string" },
    "publishedByBehaviorId": {
      "type": "string",
      "description": "产生该事件的行为 ID；由外部系统产生时可留空并在 description 说明"
    },
    "consumedByBehaviorIds": {
      "type": "array",
      "items": { "type": "string" }
    },
    "consumedByRuleIds": {
      "type": "array",
      "items": { "type": "string" }
    },
    "relatedEntityIds": {
      "type": "array",
      "items": { "type": "string" }
    },
    "payload": {
      "type": "object",
      "description": "关键载荷/投影字段的摘要说明（可结构化）"
    },
    "metadata": { "type": "object" }
  }
}
```

### Event 示例

```json
{
  "id": "Event-001",
  "name": "合同已创建",
  "description": "合同持久化完成后的领域事件",
  "publishedByBehaviorId": "Behavior-001",
  "consumedByBehaviorIds": ["Behavior-002"],
  "consumedByRuleIds": ["Rule-001"],
  "relatedEntityIds": ["Entity-001"],
  "payload": { "summary": "合同ID, 客户ID, 金额快照" },
  "metadata": {}
}
```

## 异常与补偿 JSON 格式

与 **行为签名** 中的 `signature.exceptions`（技术/接口异常）区分：本层描述**业务失败路径**下的**逆操作、冲正、Saga 补偿顺序**，支撑长链路的可靠性与「反向驱动」设计。

### Compensation Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Compensation",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "唯一标识，格式：Compensation-{序号}"
    },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "trigger": {
      "type": "string",
      "description": "自然语言或条件说明：在何种失败/回滚下启用"
    },
    "relatedProcessId": { "type": "string" },
    "fromStepId": { "type": "string", "description": "失败起始步骤 id（同 Process.steps.id）" },
    "compensatingBehaviorIds": {
      "type": "array",
      "items": { "type": "string" },
      "description": "需执行的补偿类行为（冲销、反审、关单等）"
    },
    "executionOrder": {
      "type": "string",
      "enum": ["reverse", "sequence", "parallel"],
      "description": "补偿行为执行顺序；reverse 表示与主流程逆序"
    },
    "relatedEventId": { "type": "string" },
    "metadata": { "type": "object" }
  }
}
```

### Compensation 示例

```json
{
  "id": "Compensation-001",
  "name": "收款流程中开票失败时冲销与回退",
  "description": "按逆序或约定顺序冲销子步骤",
  "trigger": "Process-001 中开票步骤失败或 Event-xxx 未达成",
  "relatedProcessId": "Process-001",
  "fromStepId": "Step-102",
  "compensatingBehaviorIds": ["Behavior-007", "Behavior-006"],
  "executionOrder": "reverse",
  "metadata": {}
}
```

## 流程/场景 JSON 格式

> JSON 根数组名为 **`processes`**，与文档中的**场景/流程**章对应。

### Process Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Process",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "流程唯一标识，格式：Process-{序号}"
    },
    "name": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": ["business", "system"],
      "description": "流程类型：business(业务流程), system(系统流程)"
    },
    "description": {
      "type": "string"
    },
    "trigger": {
      "type": "string",
      "description": "流程触发条件"
    },
    "participants": {
      "type": "array",
      "items": {"type": "string"},
      "description": "人类可读参与者名，可与 participantSubjectIds 同时出现"
    },
    "participantSubjectIds": {
      "type": "array",
      "items": {"type": "string"},
      "description": "本场景参与主体的 Subject ID 列表，与「主体层」一致"
    },
    "scene": {
      "type": "string",
      "description": "可选：与业务文档一致的「场景」命名（同一条 Process 的别名说明）"
    },
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "type": {
            "type": "string",
            "enum": ["userTask", "serviceTask", "scriptTask", "decision", "subProcess"]
          },
          "behaviorId": {
            "type": "string",
            "description": "调用的行为ID"
          },
          "rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "触发的规则ID列表"
          },
          "participant": {"type": "string"},
          "participantSubjectId": {
            "type": "string",
            "description": "可选，执行该步的主体 Subject ID"
          },
          "transitions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "to": {"type": "string"},
                "condition": {"type": "string"},
                "type": {"type": "string", "enum": ["success", "failure", "conditional"]}
              }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object"
    }
  }
}
```

### Process 示例

```json
{
  "id": "Process-001",
  "name": "合同录入流程",
  "type": "business",
  "description": "从创建到提交的完整合同录入流程",
  "trigger": "用户点击创建合同",
  "participants": ["销售人员", "合同系统", "审批系统"],
  "steps": [
    {
      "id": "Step-001",
      "name": "填写合同信息",
      "type": "userTask",
      "behaviorId": null,
      "rules": [],
      "participant": "销售人员",
      "transitions": [
        {"to": "Step-002", "condition": "信息填写完成", "type": "success"}
      ]
    },
    {
      "id": "Step-002",
      "name": "创建合同",
      "type": "serviceTask",
      "behaviorId": "Behavior-001",
      "rules": ["Rule-001", "Rule-002"],
      "participant": "合同系统",
      "transitions": [
        {"to": "Step-003", "condition": "创建成功", "type": "success"},
        {"to": "Step-004", "condition": "创建失败", "type": "failure"}
      ]
    },
    {
      "id": "Step-003",
      "name": "提交审批",
      "type": "serviceTask",
      "behaviorId": "Behavior-005",
      "rules": ["Rule-003"],
      "participant": "审批系统",
      "transitions": [
        {"to": "End", "condition": "提交成功", "type": "success"}
      ]
    },
    {
      "id": "Step-004",
      "name": "显示错误",
      "type": "userTask",
      "behaviorId": null,
      "rules": [],
      "participant": "销售人员",
      "transitions": [
        {"to": "Step-001", "condition": "用户选择修改", "type": "conditional"}
      ]
    }
  ],
  "metadata": {
    "version": "1.0",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

## 完整 JSON 结构

### Domain Model Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Domain Model",
  "type": "object",
  "required": [
    "domain",
    "entities",
    "behaviors",
    "rules",
    "subjects",
    "events",
    "compensations",
    "processes"
  ],
  "properties": {
    "domain": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "nameEn": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "generatedAt": {"type": "string", "format": "date-time"},
        "source": {"type": "string"},
        "author": {"type": "string"}
      }
    },
    "statistics": {
      "type": "object",
      "properties": {
        "entityCount": {"type": "integer"},
        "behaviorCount": {"type": "integer"},
        "ruleCount": {"type": "integer"},
        "subjectCount": {"type": "integer"},
        "eventCount": {"type": "integer"},
        "compensationCount": {"type": "integer"},
        "processCount": {"type": "integer"}
      }
    },
    "entities": {
      "type": "array",
      "items": {"$ref": "#/definitions/Entity"}
    },
    "behaviors": {
      "type": "array",
      "items": {"$ref": "#/definitions/Behavior"}
    },
    "rules": {
      "type": "array",
      "items": {"$ref": "#/definitions/Rule"}
    },
    "subjects": {
      "type": "array",
      "items": {"$ref": "#/definitions/Subject"},
      "description": "主体层：角色/系统/组织等"
    },
    "events": {
      "type": "array",
      "items": {"$ref": "#/definitions/DomainEvent"},
      "description": "领域事件层"
    },
    "compensations": {
      "type": "array",
      "items": {"$ref": "#/definitions/Compensation"},
      "description": "异常与业务补偿"
    },
    "processes": {
      "type": "array",
      "items": {"$ref": "#/definitions/Process"}
    }
  }
}
```

> **兼容**：未包含 `subjects` / `events` / `compensations` 的历史 JSON 在迁移时补入空数组并补齐统计项即可。

### 完整示例

```json
{
  "domain": {
    "name": "合同管理系统",
    "nameEn": "Contract Management System",
    "description": "管理业务合同的全生命周期",
    "version": "1.0"
  },
  "metadata": {
    "generatedAt": "2024-01-15T10:30:00Z",
    "source": "需求文档v1.2.pdf",
    "author": "Domain Modeler"
  },
  "statistics": {
    "entityCount": 6,
    "behaviorCount": 8,
    "ruleCount": 5,
    "subjectCount": 1,
    "eventCount": 1,
    "compensationCount": 1,
    "processCount": 3
  },
  "entities": [
    {
      "id": "Entity-001",
      "name": "合同",
      "type": "core",
      "properties": [...],
      "relations": [...]
    }
    // ... 更多实体
  ],
  "behaviors": [
    {
      "id": "Behavior-001",
      "name": "创建合同",
      "entityId": "Entity-001",
      "signature": {...}
    }
    // ... 更多行为
  ],
  "rules": [
    {
      "id": "Rule-001",
      "name": "合同金额非空校验",
      "type": "validation",
      "condition": {...}
    }
    // ... 更多规则
  ],
  "subjects": [ { "id": "Subject-001", "name": "销售承办人", "type": "role" } ],
  "events": [ { "id": "Event-001", "name": "合同已创建", "publishedByBehaviorId": "Behavior-001" } ],
  "compensations": [ { "id": "Compensation-001", "name": "失败路径补偿", "compensatingBehaviorIds": [] } ],
  "processes": [
    {
      "id": "Process-001",
      "name": "合同录入流程",
      "steps": [...]
    }
    // ... 更多流程
  ]
}
```

## 集成与运行时关注点

与 [SKILL.md](../SKILL.md) 中「能力边界」一致，供**消费方**集成时对照（细节与字段以本文各 Schema 节为准）：

1. **加载**：解析 JSON（或 YAML → 与 JSON 同构对象），访问 `entities`、`behaviors`、`rules`、`subjects`、`events`、`compensations`、`processes`。
2. **查询**：按 `id` / `name` 建立索引。
3. **图与依赖**：`relations.targetId`，`invokes`，`dependsOn`，行为上 `publishesEventIds` / `subscribesToEventIds`，`compensations[].compensatingBehaviorIds` 等。
4. **规则**：`priority` + `trigger`；可与 `Event.id` 及规则内引用对齐。
5. **流程**：`processes[].steps`、`transitions`，以及步骤上 `behaviorId` / `rules`。
6. **消息/事件总线**：以 `events` 为枢纽串联发布方与消费方（行为/规则侧 ID 一致可解析为准）。
7. **可靠性**：`compensations` 与 `executionOrder`，并与流程失败路径/步骤可对应。

## 机器消费指南

以下示例为可选实现参考（语言与运行时无关，可按栈改写）。

### 1. 查询实体

```javascript
// 获取所有核心实体
const coreEntities = domainModel.entities.filter(e => e.type === 'core');

// 获取实体的所有属性
const contractProperties = domainModel.entities
  .find(e => e.id === 'Entity-001')
  .properties;

// 获取实体的关联实体
const contractRelations = domainModel.entities
  .find(e => e.id === 'Entity-001')
  .relations;
```

### 2. 遍历关系

```javascript
// 构建实体关系图
function buildEntityGraph(entities) {
  const graph = {};
  entities.forEach(entity => {
    graph[entity.id] = {
      ...entity,
      related: entity.relations.map(r => r.targetId)
    };
  });
  return graph;
}

// 查找实体的所有关联实体
function findRelatedEntities(entityId, entities) {
  const entity = entities.find(e => e.id === entityId);
  return entity.relations.map(r => ({
    relation: r,
    target: entities.find(e => e.id === r.targetId)
  }));
}
```

### 3. 分析行为调用链

```javascript
// 构建行为调用图
function buildBehaviorCallGraph(behaviors) {
  const graph = {};
  behaviors.forEach(behavior => {
    graph[behavior.id] = {
      ...behavior,
      calls: behavior.invokes || [],
      calledBy: behaviors
        .filter(b => b.invokes && b.invokes.includes(behavior.id))
        .map(b => b.id)
    };
  });
  return graph;
}

// 查找行为的前置条件中涉及的所有规则
function findRelatedRules(behaviorId, behaviors, rules) {
  const behavior = behaviors.find(b => b.id === behaviorId);
  const ruleIds = behavior.validates || [];
  return rules.filter(r => ruleIds.includes(r.id));
}
```

### 4. 规则引擎集成

```javascript
// 按优先级排序规则
function sortRulesByPriority(rules) {
  return rules.sort((a, b) => (b.priority || 0) - (a.priority || 0));
}

// 获取规则的依赖链
function getRuleDependencyChain(ruleId, rules, visited = new Set()) {
  if (visited.has(ruleId)) return [];
  visited.add(ruleId);
  
  const rule = rules.find(r => r.id === ruleId);
  const dependencies = rule.dependsOn || [];
  
  return [
    rule,
    ...dependencies.flatMap(depId => 
      getRuleDependencyChain(depId, rules, visited)
    )
  ];
}
```

### 5. 流程执行模拟

```javascript
// 模拟流程执行
function simulateProcess(processId, processes) {
  const process = processes.find(p => p.id === processId);
  let currentStep = process.steps[0];
  const executionPath = [];
  
  while (currentStep) {
    executionPath.push(currentStep);
    
    // 找到下一个步骤（默认取第一个成功transition）
    const nextTransition = currentStep.transitions
      .find(t => t.type === 'success');
    
    if (nextTransition && nextTransition.to !== 'End') {
      currentStep = process.steps.find(s => s.id === nextTransition.to);
    } else {
      currentStep = null;
    }
  }
  
  return executionPath;
}
```

### 6. 一致性验证

```javascript
// 验证所有ID引用是否有效
function validateReferences(domainModel) {
  const errors = [];
  const entityIds = domainModel.entities.map(e => e.id);
  const behaviorIds = domainModel.behaviors.map(b => b.id);
  const ruleIds = domainModel.rules.map(r => r.id);
  const processIds = domainModel.processes.map(p => p.id);
  const subjectIds = (domainModel.subjects || []).map(s => s.id);
  const eventIds = (domainModel.events || []).map(ev => ev.id);
  const compensationIds = (domainModel.compensations || []).map(c => c.id);

  // 验证行为引用的实体
  domainModel.behaviors.forEach(b => {
    if (!entityIds.includes(b.entityId)) {
      errors.push(`Behavior ${b.id} references unknown entity ${b.entityId}`);
    }
  });
  
  // 验证规则依赖
  domainModel.rules.forEach(r => {
    (r.dependsOn || []).forEach(depId => {
      if (!ruleIds.includes(depId)) {
        errors.push(`Rule ${r.id} depends on unknown rule ${depId}`);
      }
    });
  });
  
  // 验证流程步骤引用的行为和规则
  domainModel.processes.forEach(p => {
    p.steps.forEach(s => {
      if (s.behaviorId && !behaviorIds.includes(s.behaviorId)) {
        errors.push(`Process ${p.id} step ${s.id} references unknown behavior ${s.behaviorId}`);
      }
      (s.rules || []).forEach(ruleId => {
        if (!ruleIds.includes(ruleId)) {
          errors.push(`Process ${p.id} step ${s.id} references unknown rule ${ruleId}`);
        }
      });
    });
  });

  (domainModel.subjects || []).forEach(s => {
    (s.performsBehaviorIds || []).forEach(bid => {
      if (!behaviorIds.includes(bid)) {
        errors.push(`Subject ${s.id} references unknown behavior ${bid}`);
      }
    });
  });

  (domainModel.events || []).forEach(ev => {
    if (ev.publishedByBehaviorId && !behaviorIds.includes(ev.publishedByBehaviorId)) {
      errors.push(`Event ${ev.id} publishedBy unknown behavior ${ev.publishedByBehaviorId}`);
    }
    (ev.consumedByBehaviorIds || []).forEach(bid => {
      if (!behaviorIds.includes(bid)) {
        errors.push(`Event ${ev.id} consumedBy unknown behavior ${bid}`);
      }
    });
  });

  (domainModel.compensations || []).forEach(c => {
    (c.compensatingBehaviorIds || []).forEach(bid => {
      if (bid && !behaviorIds.includes(bid)) {
        errors.push(`Compensation ${c.id} references unknown behavior ${bid}`);
      }
    });
  });
  
  return errors;
}
```
