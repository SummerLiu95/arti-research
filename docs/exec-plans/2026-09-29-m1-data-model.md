# M1 数据模型与数据库

日期：2026-09-29
状态：Completed

## 背景

完成 TASKS M1：核心数据模型、Alembic 迁移、种子数据，打通"数据库 → 模型 → 数据"链路。

## 完成内容

- `api/models.py`：Entity（名称/别名/证券标识/是否上市）、Relationship（类型/方向/状态/0–100 评分/评分因子 JSONB/时效区间/notes）、Evidence（source URL、publisher、发布与获取时间、locator、摘录、快照引用、访问限制）。约束：关系三元组唯一 + 评分 0–100 CHECK
- `api/db.py`：引擎与会话工厂，连接串统一读 `DATABASE_URL`
- `alembic.ini` + `migrations/env.py` + `migrations/versions/0001_initial.py`：连接串从环境变量读取，不写死凭据
- `pipeline/seed.py`：开发用种子数据（NVIDIA + TSMC/SK Hynix/Microsoft/Amazon/AMD/Intel，6 条关系带占位证据），幂等可重跑

## 验证

- `docker compose up -d db` → `alembic upgrade head` 成功建表
- `python -m pipeline.seed` 输出 entity=7 relationship=6 evidence=6
- psql 实查：6 条关系方向与类型正确（TSMC→NVIDIA supplier 等），枚举以值形式存储
- 未验证：API 层读取（M4 进行）

## 经验与后续

- 枚举列用 `String + str-Enum` 存储为值（如 "supplier"），psql 可读性好；注意模型声明与迁移 DDL 保持同步（本次手写迁移，未用 autogenerate）
- 后续：M2 管道产出真实数据后替换种子数据；评分字段（relevance_score/score_breakdown）由 M3 评分引擎回填
