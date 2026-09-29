# ARTi — NVIDIA 供应链与合作关系研究服务

基于合法公开资料构建的**可复现**供应链与合作关系研究服务。研究对象为 **NVIDIA Corporation（NASDAQ: NVDA）**。

> 免责声明：本项目仅为技术研究演示，区分已确认事实、合理推断与未知信息，**不构成任何投资建议**。

## 覆盖范围

- 关系类型：supplier / customer / partner / investor_or_investee / peer
- 覆盖：GPU/数据中心供应链、主要客户（云厂商）、合作伙伴、投资/被投对象、可比公司（AMD、Intel 等）
- 不覆盖：实时行情、非上市公司财务细节、需登录/付费墙后的数据
- 研究时间截点：待数据冻结后在此注明

## 架构

离线研究管道（采集快照 → LLM 结构化抽取 → 实体消歧 → 人工复核 → 入库）+ PostgreSQL + FastAPI REST API + Typer CLI + React/Vite 前端。详见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 快速开始

```bash
cp .env.example .env   # 填入 LLM_API_KEY（仓库不含真实凭据）
docker compose up --build
```

本地开发：

```bash
make setup    # 创建 venv 并安装依赖
make api      # FastAPI (localhost:8000)
make web      # 前端 (Vite dev server)
make test     # pytest
```

## 复现研究数据

```bash
make ingest extract resolve score
```

采集快照存于 `pipeline/snapshots/`，复核无需重新抓取受限数据。

## 环境变量

见 [.env.example](.env.example)，所有变量均有说明；仓库不包含真实凭据。

## AI 使用声明

LLM 用于公开文本的关系结构化抽取与实体消歧辅助，所有 LLM 产出经 schema 校验与人工复核后方可入库；评分、查询、证据定位不使用 LLM。未向任何工具输入密钥、个人数据、客户机密或未授权资料。

## 数据源

- SEC EDGAR（10-K 等公开申报文件）
- NVIDIA 官方新闻稿与年报
- 各关联公司公开披露

## 已知限制与改进方向

（随开发补充：覆盖盲区、新闻共振误判处理、数据质量改进路线）

## 文档

- [docs/PRD.md](docs/PRD.md) — 需求与验收清单
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 技术架构
- [docs/TASKS.md](docs/TASKS.md) — 开发任务规划
