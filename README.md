# ARTi — NVIDIA 供应链与合作关系研究服务

基于合法公开资料构建的**可复现**供应链与合作关系研究服务。

> 免责声明：本项目仅为技术研究演示，区分已确认事实（confirmed）、合理推断（inferred）与未知信息（unknown），**不构成任何投资建议**。

## 研究对象与范围

- **研究对象**：NVIDIA Corporation（NASDAQ: NVDA，SEC CIK 0001045810）
- **数据截点**：2026-09-29（快照见 `pipeline/snapshots/2026-09-29/`）
- **关系类型**：supplier / customer / partner / investor_or_investee / peer
- **覆盖范围**：GPU/数据中心供应链（TSMC、SK Hynix、Micron、Samsung）、主要客户（云厂商）、可比公司（AMD、Intel）
- **不覆盖**：实时行情、需登录/付费墙后的数据、非公开供应链细节、合作伙伴与投资的穷举（当前仅覆盖 10-K 明确披露的关系）

## 快速开始（docker-compose 一键复现）

```bash
docker compose up --build
```

- API：<http://localhost:8000>（文档 `/docs`）
- 前端：<http://localhost:5173>

空库启动时自动从已提交的快照重放研究管道（fixture 模式），**无需 LLM 凭据、无需联网抓取**即可复核交付。

## 本地开发

```bash
make setup    # 创建 venv 并安装依赖
make api      # FastAPI (localhost:8000)
make cli ARGS="relationships --type supplier"   # CLI 等价入口
make web      # 前端 (localhost:3000)
make test     # pytest（25 个用例，含失败/边界用例）
```

## 研究管道（可重跑）

```bash
make ingest    # 采集 SEC 公开数据 → 快照落盘（带 sha256 meta）
make extract   # 结构化抽取（默认 fixture 模式；EXTRACT_MODE=llm 需 LLM_API_KEY）
make resolve   # 实体消歧（别名表，未匹配进 unresolved 交人工）
make review    # 人工复核入库（幂等）
make score     # 评分（可复算）
make export    # 导出交付数据集 data/
```

## 评分方法（0–100，可复算）

```
score = 100 × 类型权重 × 状态系数 × 证据数量系数 × 证据独立性系数 × 时效衰减
```

| 因子 | 取值逻辑 |
|---|---|
| 类型权重 | supplier/customer 1.0，partner 0.85，investor 0.8，peer 0.6 |
| 状态系数 | confirmed 1.0 / inferred 0.7 / unknown 0.3 |
| 证据数量 | 0.6 + 0.1×n，封顶 1.0 |
| 证据独立性 | 0.5 + 0.5×(独立来源数/总条数)，抑制新闻共振 |
| 时效衰减 | 以最新证据时间为基准指数衰减，半衰期 730 天 |

常量与理由见 `pipeline/scoring/formula.py` 注释；每条关系的因子明细存于 `score_breakdown`，API `/relationships/{id}` 与前端详情抽屉可直接查看、逐项复算。**这些权重是工程判断，可按需调整。**

## 数据源与合规

仅使用合法公开资料：SEC EDGAR（submissions JSON + 10-K 全文），遵守 SEC User-Agent 政策与限速；不绕过 robots/登录/付费墙/验证码/限流；不含密钥、个人数据、客户机密。详见 [pipeline/ingest/SOURCES.md](pipeline/ingest/SOURCES.md)。

## AI 使用声明

LLM 仅用于公开文本的关系结构化抽取与实体消歧辅助；所有 LLM 产出经 Pydantic schema 校验与**人工复核**后方可入库。评分、查询、证据定位不使用 LLM。未向任何工具输入密钥、个人数据或未授权资料。本次交付默认走 fixture 模式（预置的、经人工整理的抽取结果），保证无凭据复现。

## 已知限制与盲区

1. **覆盖量有限**：当前仅覆盖 NVIDIA 最新 10-K 明确披露的关系（8 条），未覆盖 partner 与 investor_or_investee 类型——10-K 未系统披露此类信息，需引入新闻稿数据源扩充
2. **客户关系多为 inferred**：10-K 通常不点名具体云厂商客户，故 Microsoft/Amazon 标记为推断并相应降分
3. **时效依赖证据时间**：部分证据仅有获取时间（published_at 缺失），时效因子可能偏乐观
4. **评分权重为人工设定**：类型权重与半衰期是工程判断而非统计拟合
5. **fixture 摘录为人工整理**：LLM 模式未经真实 API key 端到端验证

## 未来改进方向

- 接入 NVIDIA/TSMC 官方新闻稿，扩充 partner/investor 关系覆盖
- 来源冲突自动降级规则代码化（官方申报 > 新闻）
- evidence locator 升级为精确章节锚点
- 评分因子基于历史数据校准

## 测试

```bash
make test          # 25 用例：管道边界、评分可复算、API 关键路径与失败用例
cd web && npm test # 前端 4 用例
```

## 文档

- [docs/PRD.md](docs/PRD.md) — 需求与验收清单（含逐条自查）
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 技术架构
- [docs/TASKS.md](docs/TASKS.md) — 开发任务规划
- [docs/exec-plans/](docs/exec-plans/) — 各里程碑实现记录
