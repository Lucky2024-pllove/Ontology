#!/usr/bin/env python3
"""校验领域模型 JSON 是否符合本体六类模型（含主体、领域事件、异常补偿）。

用法: python scripts/validate.py <basename.json>

须显式传入待校验文件路径（与交付物同基名）。示例：在技能包根目录执行
  python scripts/validate.py examples/contract-management/contract-management.json
"""
import json
import sys
from pathlib import Path

REQUIRED_TOP = [
    "domain",
    "entities",
    "behaviors",
    "rules",
    "subjects",
    "events",
    "compensations",
    "processes",
]
ENTITY_REQUIRED = ["id", "name", "type", "properties"]
BEHAVIOR_REQUIRED = ["id", "name", "entityId"]
RULE_REQUIRED = ["id", "name", "type"]
SUBJECT_REQUIRED = ["id", "name", "type"]
EVENT_REQUIRED = ["id", "name"]
COMPENSATION_REQUIRED = ["id", "name"]
PROCESS_REQUIRED = ["id", "name", "steps"]


def validate(json_path: str) -> list[str]:
    errors: list[str] = []
    path = Path(json_path)
    if not path.exists():
        return [f"文件不存在: {json_path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON 解析失败: {e}"]
    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"缺少顶层字段: {key}")
    if "entities" in data:
        for i, e in enumerate(data["entities"]):
            for k in ENTITY_REQUIRED:
                if k not in e:
                    errors.append(f"实体[{i}] 缺少字段: {k}")
    if "behaviors" in data:
        for i, b in enumerate(data["behaviors"]):
            for k in BEHAVIOR_REQUIRED:
                if k not in b:
                    errors.append(f"行为[{i}] 缺少字段: {k}")
    if "rules" in data:
        for i, r in enumerate(data["rules"]):
            for k in RULE_REQUIRED:
                if k not in r:
                    errors.append(f"规则[{i}] 缺少字段: {k}")
    if "subjects" in data:
        for i, s in enumerate(data["subjects"]):
            for k in SUBJECT_REQUIRED:
                if k not in s:
                    errors.append(f"主体[{i}] 缺少字段: {k}")
    if "events" in data:
        for i, ev in enumerate(data["events"]):
            for k in EVENT_REQUIRED:
                if k not in ev:
                    errors.append(f"领域事件[{i}] 缺少字段: {k}")
    if "compensations" in data:
        for i, c in enumerate(data["compensations"]):
            for k in COMPENSATION_REQUIRED:
                if k not in c:
                    errors.append(f"异常补偿[{i}] 缺少字段: {k}")
    if "processes" in data:
        for i, p in enumerate(data["processes"]):
            for k in PROCESS_REQUIRED:
                if k not in p:
                    errors.append(f"流程/场景[{i}] 缺少字段: {k}")
    return errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/validate.py <basename.json>", file=sys.stderr)
        print("示例: python scripts/validate.py examples/contract-management/contract-management.json", file=sys.stderr)
        sys.exit(2)
    target = sys.argv[1]
    errs = validate(target)
    if errs:
        print("校验失败:")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("OK")
