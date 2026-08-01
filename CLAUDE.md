# CLAUDE.md — 美妆零售知识库与客服协作系统

## 项目定位

FDE 共学营大作业。为美妆零售企业搭建"知识检索 + 回答生成 + 风险分级 + 转人工"的客服协作系统。本期 Demo 阶段：知识库只读检索、回答绑定依据、风险分级建议转人工、两级转人工、会话标记留档。

## 当前状态（2026-08-02）

- **知识库**：`知识库/*.md`，5 篇产品条目（α-熊果苷、烟酰胺、宝拉2%BHA、珀莱雅防晒、CATHERINEY卸妆膏），持续扩充
- **回答 Skill**：`.claude/skills/beauty-retail-answer/`（检索→定级→模板输出→转人工）。检索已接入飞书云端：优先查飞书云文档+多维表格，本地 `知识库/` 作离线兜底
- **Mock 素材 Skill**：`.claude/skills/fde-mock-knowledge-base/`（生成 5 篇企业流程 Mock 文档并导入飞书）
- **飞书企业系统模拟**：5 篇产品云文档 + 多维表格「美妆零售企业系统数据库」（商品信息/库存效期/会话标记 3 表）。token 见 memory `feishu-enterprise-system`
- **设计 skill（用户级）**：api-and-interface-design、mcp-builder、postgres-patterns、backend-patterns、security-and-hardening
- **交付文档**：飞书云文档 `W5B8d7bkWoELpwxEduuchW6enOd`（数据流图+系统接入+运行证据），已设为链接任何人可查看
- **GitHub**：https://github.com/wushaohengsir/PDE-beauty-makeup

## 架构要点

6 方角色：用户 → Agent(beauty-retail-answer) → 企业接入层(lark-cli) → 飞书(云文档+多维表格)；另两级转人工：初级客服 → 资深员工 → 会话标记库。Agent 不直连飞书，只调接入层。本地 `知识库/` 作离线兜底。

接入方式：本期用 **CLI（lark-cli）**——能力覆盖全部需求且 token 开销比 MCP 小。MCP/API 暂不引入。

## 迭代指引

### 新增产品知识条目
1. 抓取商品页（opencli 浏览器或用户粘贴），按 `知识库/` 现有模板写 .md（含品牌/规格/全成分 INCI/功效/用法/禁忌/适用肤质/客服要点）
2. INCI 必须有来源；页面未公布就标注"未公开"，不编造
3. 同步：导入飞书云文档（`lark-cli drive +import --type docx`），在多维表格·商品信息表加一条记录
4. git commit 推 GitHub

### 端到端 Demo 待实现（下一步）
- beauty-retail-answer skill 已接入飞书检索（`lark-cli docs +fetch` 读云文档 + `lark-cli base +record-search` 查多维表格），本地 `知识库/` 兜底
- 待做：封装 CLI 入口 `python agent.py ask "..."`，串起"理解问题→飞书检索→定级→模板输出"完整链路
- 待做：高风险/无覆盖时自动写入会话标记表（`lark-cli base +record-batch-create` 写 tblpRpbprhZIzlqp）
- 验收：`python agent.py ask "珀莱雅防晒孕期可以用吗"` → 检索飞书 → 定级(高) → 答案+依据+建议转人工

### 飞书操作约定
- 身份：user 身份（吴绍恒），已授 base 全套 scope
- 知识库只读；仅会话标记表可写
- 修改飞书云文档内容：`lark-cli docs +update --command overwrite --doc-format markdown --doc <token> --content @file`
- 设置链接公开：`lark-cli drive permission.public patch --link-share-entity anyone_readable ...`

## 知识库条目规范

- 高风险问题（孕期/过敏/医美/药物/儿童）：回答必须建议转人工，不确定按高风险处理
- 每条答案绑定 citations 原文出处，不编造成分/浓度/用法
- 诚实 > 讨好：知识库没有的说"不知道"+建议转人工
- 详细风险规则：`.claude/skills/beauty-retail-answer/references/risk_rules.md`

## 文档结构

- `解决方案框架.md` / `需求说明清单.md` / `业务流程图.md` / `项目执行计划.md` — 方案设计
- `数据流图与系统接入说明.md` — 作业4 交付内容本地副本（飞书为权威版本）
- `知识库/` — 产品知识条目
- `beauty-retail-answer-workspace/` — Skill 评测
