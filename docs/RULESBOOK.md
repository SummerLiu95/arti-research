# RULESBOOK — 可复用经验

本文件记录开发过程中沉淀的可复用经验、约定与坑。条目化、保持简短。
新经验随时追加；来自 exec-plans 归档的教训同步至此。

## 约定

- 文档用中文，代码与标识符用英文
- 文档目录与使用规则见 AGENTS.md

## 经验

- docker-compose 的 `env_file` 指向不存在的文件时整个配置校验失败；骨架/开源仓库场景应写 `env_file: [{path: .env, required: false}]`
- SEC EDGAR：`www.sec.gov/Archives` 严格校验 User-Agent（需带可联系身份信息，否则 403），且路径中 CIK 必须去前导零（否则 301）；`data.sec.gov` 的 JSON API 相对宽松
- 管道入库必须先按唯一约束查再插（get-or-create + 证据去重），保证可重跑幂等
- pytest 找不到项目包时，用 pyproject.toml 的 `[tool.pytest.ini_options] pythonpath = ["."]` 解决
- SQLAlchemy 用 String 列存 str-Enum 时读出是纯字符串，消费 `.value` 前需判断类型
- ORM 双向公司匹配不能用 union 拼 Query，应双别名 join + or_
- FastAPI 测试要用 SQLite 时，JSONB 列写成 `JSON().with_variant(JSONB, "postgresql")`，生产 PG、测试 SQLite 两不误
- Vitest 配置写进 vite.config.ts 时，`defineConfig` 必须从 `vitest/config` 导入，否则 TS 报 `test` 属性不存在
- Dockerfile 里的包管理器必须与实际 lock 文件一致（package-lock.json ↔ npm ci）
