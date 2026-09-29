# TASKS — 开发任务规划

日期：2026-09-29
状态：进行中

优先级原则：可复现性 > 证据可追溯性 > 评分可解释性 > 数据覆盖量。
状态标记：`[ ]` 未开始 / `[~]` 进行中 / `[x]` 完成（完成后同步写 docs/exec-plans/）

## M0 项目骨架

- [x] T0.1 monorepo 初始化：目录结构（pipeline/api/cli/web/data）、Makefile、.gitignore、.env.example
- [x] T0.2 docker-compose.yml：db(PostgreSQL) + api + web 三服务
- [x] T0.3 README 初版：研究对象声明、启动命令、合规声明、AI 使用声明

## M1 数据模型与数据库

- [x] T1.1 SQLAlchemy 模型：entity / relationship / evidence（见 ARCHITECTURE.md §5）
- [x] T1.2 Alembic 迁移 + docker-compose 内 db 初始化
- [x] T1.3 种子数据脚本（开发用假数据，打通前后端）

## M2 采集与抽取管道（核心）

- [x] T2.1 数据源清单与合规自查（SEC EDGAR、NVIDIA 年报/10-K、官网新闻稿等公开源）
- [x] T2.2 ingest：采集脚本 + 快照落盘（pipeline/snapshots/）
- [x] T2.3 extract：LLM 结构化抽取（Pydantic schema：实体/关系类型/方向/状态/证据片段/locator；fixture/llm 双模式）
- [x] T2.4 resolve：实体消歧（别名表精确匹配，LLM 辅助留扩展点）
- [x] T2.5 review：人工复核流程（草稿 → 确认入库，幂等）+ AI 使用方式记录
- [x] T2.6 失败/边界用例：schema 校验、未注册实体、fixture 质量门（6 个测试通过）

## M3 评分引擎

- [x] T3.1 评分公式定义与实现（时效衰减 × 证据独立性 × 关系类型权重），输出 0–100
- [x] T3.2 评分构成可解释输出（每项因子明细，供 API/前端展示）
- [x] T3.3 评分可复算测试（同输入同输出）

## M4 后端服务

- [ ] T4.1 FastAPI：关系查询接口（按公司、关系图、证据）
- [ ] T4.2 筛选（关系类型/相关度/时间）+ 分页 + 输入校验 + 错误响应
- [ ] T4.3 Typer CLI：与 API 等价入口
- [ ] T4.4 pytest：关键路径 + 至少一个失败/边界用例

## M5 前端

- [ ] T5.1 `pnpm create vite` 脚手架 + TS + Tailwind + shadcn/ui
- [ ] T5.2 关系图视图：Cytoscape.js（节点=公司带评分，边=关系带类型/方向）
- [ ] T5.3 关系列表：筛选、排序、分页
- [ ] T5.4 详情抽屉：证据链展开 + 评分构成拆解
- [ ] T5.5 Vitest 关键组件测试

## M6 交付收尾

- [ ] T6.1 数据集导出（data/ 下 JSON/CSV，明确数据截点）
- [ ] T6.2 README 完善：依赖、环境变量说明（无真实凭据）、启动/测试/复现命令、限制与已知盲区、改进方向
- [ ] T6.3 docker-compose 全流程验证（干净环境一键起）
- [ ] T6.4 对照 PRD §5 验收清单逐条自查

## 里程碑依赖

M0 → M1 → M2 ⇄ M3 → M4 → M5 → M6

（M2/M3 可并行；M5 依赖 M4 的 API 契约，可用种子数据先行）
