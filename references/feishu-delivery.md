# 飞书知识库归档与 Mermaid → 画板

> 以下为本技能在飞书侧的操作摘要。**执行**需本机已安装 `lark-cli`；复杂画板可配合 `npx -y @larksuite/whiteboard-cli@^0.2.10`。命令行为以你本地的 `lark-cli` 版本与[飞书开放平台](https://open.feishu.cn/)文档为准。

## 1. 依赖与认证

| 能力 | 依赖 |
|------|------|
| 知识库建节点、写文档、白板嵌入 | `lark-cli`（[安装与登录](https://open.feishu.cn/) 以官方为准） |
| 复杂图渲染后写入「空白画板」块 | `npx -y @larksuite/whiteboard-cli@^0.2.10` + `lark-cli whiteboard` |

**认证（最小步骤）：**

```bash
lark-cli auth login
# 若租户有独立域名，按 lark-cli 提示使用 --domain
```

- 写知识库/文档/画板时通常以 **`--as user`**；应用身份见官方「bot 权限与成员」说明。
- 遇 `Permission denied` 时按飞书应用 scope 在开发者后台为当前应用补全：`wiki:node:*`、`wiki:space:*`（以实际报错为准）、文档与画板相关读写 scope。

## 2. 用户须提供的定位信息

> 本节的索要项**仅在使用飞书知识库归档时**需要。若任务只需要本地 `md`/`json`/`yaml`，**不必**问用户要下列信息。

执行归档**前**，请用户**明确给出**（或从知识库 URL 解析）：

| 项 | 说明 |
|----|------|
| `space_id` | 知识空间 ID（非 URL 时直接提供；若只给 `.../wiki/<token>` 的 URL，用 `lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}' --format json` 取 `data.node.space_id`） |
| `parent_node_token` | 父**知识库节点** token（在目标「文件夹」下挂新文档时，挂在该节点下） |
| `title` | 新文档/节点标题（建议与领域基名相关，如 `{basename} 领域本体`） |

> **不要**用 Drive 的「我的空间」路径代替知识库；知识库与云空间目录在 CLI 中语义不同。

## 3. 在目标节点下创建云文档（知识库挂接）

在**已知的** `space_id` 与 `parent_node_token` 下创建 `docx` 节点（自动解析空间）：

```bash
lark-cli wiki +node-create \
  --space-id "<SPACE_ID>" \
  --parent-node-token "<PARENT_NODE_TOKEN>" \
  --title "<title>"
```

从返回 JSON 读取：

- `obj_token`：即后续 `docs` 子命令使用的**文档 id / token**（以 CLI 实际字段名为准，常见为 `obj_token` 或 `data` 内文档标识）。
- 若需确认：再执行 `lark-cli docs +fetch --api-version v2 --doc "<obj_token>" --as user` 校验可读。

> 与「只在个人知识库根创建」等变体，以 `lark-cli wiki +node-create --help` 为准；本技能以**用户指定知识库+父节点**为主路径。

## 4. 将 `{basename}.md` 推送到飞书：Mermaid → 画板

飞书云文档**不**直接渲染 Markdown 里的 ` ```mermaid ` 代码块为图；需改为 **画板块** 或 **内嵌 mermaid 画板资源**。

### 4.1 简单图（推荐）：DocxXML 中的内嵌 mermaid 画板

在写入文档的 **XML 内容**中，用扩展标签（与飞书 HTML 子集一致）：

```xml
<whiteboard type="mermaid">flowchart LR
  A --> B
</whiteboard>
```

- 支持 `mermaid` / `plantuml`。
- 将本地 `{basename}.md` 中每个 ` ```mermaid ... ``` ` 块**去掉围栏**，把正文粘贴到 `<whiteboard type="mermaid">` 与 `</whiteboard>` 之间；其余标题、段落、列表可转为对应 XML（`<h1>`…`<p>`…`<ul><li>`）或使用 Markdown 整篇导入（见下）。

**整篇写入**（在拿到 `--doc` 的文档 token 后，注意高危指令）：

```bash
lark-cli docs +update --api-version v2 --doc "<obj_token>" --command append \
  --content '<h1>领域模型</h1><p>...</p><whiteboard type="mermaid">flowchart TD
  I[输入] --> P[处理] --> O[输出]
</whiteboard>' 
```

- 大文档可分段 `block_insert_after`，避免单次字符串过长。

### 4.2 Markdown 格式导入

若使用 `--doc-format markdown`，正文中仍可直接写**未转义**的：

```html
<whiteboard type="mermaid">
flowchart LR
  A --> B
</whiteboard>
```

### 4.3 复杂图：空白画板 + `whiteboard +update`

当图元过多、需 DSL/SVG 路线或内嵌 mermaid 不足以表达时：

1. 用 `docs +update --command append` 插入：`<whiteboard type="blank"></whiteboard>`。
2. 从响应的 `data.document.new_blocks` 中取 `block_type == "whiteboard"` 的 `block_token` 作为**画板 token**。
3. 使用 `lark-cli whiteboard +update` 写入（具体 `--input_format mermaid` / `raw` 等）与 **dry-run** 要求：

```bash
# 写入前对已有内容务必先 dry-run（见 lark-cli whiteboard 子命令帮助）
lark-cli whiteboard +query "<board_token>" --output_as code --as user
# 再按 whiteboard +update 的 --overwrite --dry-run 流程操作…
npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd --to openapi --format json \
  | lark-cli whiteboard +update --whiteboard-token "<board_token>" \
    --source - --input_format raw --idempotent-token "<唯一串10字以上>" \
    --overwrite --dry-run --as user
```

- **规则**：`docs +update` **不能**改已有画板内容，只能**新增**画板块；**改**已有图必须走 `whiteboard +query` / `+update`。

### 4.4 与本体交付物的对应关系

| 本地产物 | 飞书侧 |
|----------|--------|
| `{basename}.md` 中 Mermaid 图 | 转为 `<whiteboard type="mermaid">` 或经复杂流程写入独立画板 |
| 分层/全景等非 mermaid 图 | 若仍用 mermaid 表达，同上；否则走「空白画板 + whiteboard」 |

## 5. 推荐编排顺序（端到端）

1. 用户确认 `space_id`、`parent_node_token`、展示用标题。  
2. `wiki +node-create` → 得 `obj_token`。  
3. 转换 `{basename}.md`：抽取 Mermaid → 画板块；补全 `title` 与章节结构。  
4. `docs +update` 分段写入（优先 `append` / `block_insert_after`，避免误用 `overwrite` 清稿）。  
5. 对复杂图按第 4.3 节补画板。  
6. 将飞书文档 URL 回写给用户。

## 6. 子节点/列表（可选）

- 在知识库下**列出**子节点、确认父节点：使用 `lark-cli wiki nodes list`（先 `lark-cli schema wiki.nodes.list` 查参数）。  
- **移动**节点、快捷方式等：以官方 `lark-cli wiki` 子命令为准。

---

`lark-cli` 子命令以 `lark-cli <service> --help` 与飞书开放文档为准。
