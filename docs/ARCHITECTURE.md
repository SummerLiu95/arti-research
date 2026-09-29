# ARCHITECTURE — ARTi 供应链与合作关系研究服务

日期：2026-09-29
状态：Draft

## 1. 总览

```
┌─────────────── 离线研究管道（Python，可重跑） ───────────────┐
│ 数据源(SEC/年报/公告/新闻)                                    │
│   → ingest 采集(快照) → extract LLM结构化抽取 → resolve 消歧  │
│   → review 人工复核队列 → 入库                                │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
                 ┌──────────────────┐        ┌───────────────┐
                 │ PostgreSQL        │◄───────│ scoring 评分引擎│
                 │ (实体/关系/证据)  │        │ (公式可复算)   │
                 └────────┬─────────┘        └───────────────┘
                          ▼
              ┌───────────────────────┐      ┌──────────────┐
              │ FastAPI REST API      │      │ CLI (Typer)  │
              │ 筛选/分页/校验/错误    │      │ 等价入口      │
              └──────────┬────────────┘      └──────────────┘
                         ▼
              ┌───────────────────────┐
              │ React + Vite + TS 前端 │
              │ 关系图/列表/证据抽屉   │
              └───────────────────────┘
```

部署：docker-compose 一键起全栈（db + api + web）。

## 2. 技术选型

| 层 | 选型 | 理由 |
|---|---|---|
| 语言 | Python 3.12（管道+API+CLI） | 一体化，生态最全 |
| 采集 | httpx / Playwright；SEC EDGAR 等免费接口 | 仅用公开资料，快照存证 |
| LLM 抽取 | 官方 SDK + Pydantic structured output | 流程固定，用确定性管道而非自主 agent |
| 编排 | 纯 Python 脚本 + Makefile | 可复现优先；需要框架时考虑 LangGraph |
| 数据库 | PostgreSQL（docker-compose 服务） | 关系查询 + JSONB 存证据快照 |
| 评分 | 纯 Python 公式：时效衰减 × 证据独立性 × 关系类型权重 | 透明可复算，不用 LLM |
| API | FastAPI + Pydantic | 自动 OpenAPI 文档，校验天然 |
| CLI | Typer | 与 API 共享 service 层 |
| 前端 | React 19 + Vite + TypeScript + npm（webapp-building skill 脚手架） | 40+ shadcn/ui 组件预装 |
| 前端 UI | shadcn/ui + Tailwind CSS | 快速出专业界面 |
| 关系图 | Cytoscape.js（或 React Flow） | 节点/边交互成熟 |
| 测试 | pytest（后端）+ Vitest（前端关键组件） | 关键路径 + 边界用例 |
| 部署 | docker-compose：db / api / web 三服务 | reviewer 一条命令复现 |

## 3. 仓库结构（monorepo）

```text
arti-research/
├── docker-compose.yml       # db + api + web
├── Makefile                 # setup / ingest / test / run 一键命令
├── README.md
├── docs/                    # PRD / ARCHITECTURE / TASKS / RULESBOOK / exec-plans
├── pipeline/                # 离线研究管道
│   ├── ingest/              # 采集 + 快照
│   ├── extract/             # LLM 结构化抽取
│   ├── resolve/             # 实体消歧
│   ├── scoring/             # 评分引擎
│   └── snapshots/           # fixture/snapshot（复现依据）
├── api/                     # FastAPI 服务
│   └── Dockerfile
├── cli/                     # Typer CLI（共享 api service 层）
├── web/                     # React + Vite 前端
│   └── Dockerfile
└── data/                    # 导出的数据集（JSON/CSV 交付物）
```

## 4. 核心设计原则

1. **证据不可变**：每条关系指向快照原文 + locator，结论可回溯
2. **LLM 被关在上游**：LLM 产出均为草稿，经 schema 校验 + 去重 + 人工复核后才入库；评分、查询、证据定位不用 LLM
3. **可复现**：snapshot + fixture 落库，reviewer 无需联网抓取即可重放全流程
4. **评分透明**：公式写在代码和 README 里，任何人可复算
5. **前后端分离**：API 是唯一数据出口，前端与 CLI 都只是 API 的消费者

## 5. 数据模型（初版）

- **entity**：公司实体（名称、别名、证券标识、是否上市）
- **relationship**：实体间关系（类型、方向、状态[confirmed/inferred/unknown]、相关度评分、时效）
- **evidence**：证据（source URL、publisher、发布时间、获取时间、locator、快照引用、访问限制）
- relationship 1─N evidence

## 6. 已决策项

- [x] 研究对象：**NVIDIA**（英文公开资料充分，供应链披露完整，证据链好做）
- [x] 关系图库：**Cytoscape.js**（只读展示 + 点击查看证据场景，自动布局开箱即用）
- [x] 不需要可选的 agent 研究助手模式（核心管道为确定性脚本）
