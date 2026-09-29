# M0 项目骨架搭建

日期：2026-09-29
状态：Completed

## 背景

完成 TASKS M0：monorepo 骨架、docker-compose、README 初版，为后续 M1–M6 打基础。

## 完成内容

- 目录结构：`pipeline/`（ingest/extract/resolve/scoring + snapshots）、`api/`、`cli/`、`web/`、`data/`
- 根文件：`Makefile`（setup/ingest/extract/resolve/score/seed/api/cli/web/test/compose-up）、`.gitignore`、`.env.example`、`requirements.txt`
- `docker-compose.yml`：db(PostgreSQL 16) + api + web 三服务，db 带 healthcheck，api 依赖健康检查通过
- `api/Dockerfile`：python:3.12-slim + uvicorn
- `web/Dockerfile`：占位（node 构建 + nginx 托管），M5 脚手架后完善
- `README.md` 初版：研究对象声明（NVIDIA，NASDAQ: NVDA）、免责声明、覆盖范围、启动/复现命令、环境变量说明、AI 使用声明、数据源清单

## 验证

- `docker compose config -q` 通过
- 发现并修复：`env_file: .env` 在无 .env 时校验失败，改为 `required: false` 可选加载
- 未验证：未实际 `compose up`（api/web 尚无代码，M1/M5 后整体验证，归 T6.3）

## 经验与后续

- 经验（已同步 RULESBOOK.md）：docker-compose 的 env_file 在文件缺失时直接报错，骨架阶段应设 `required: false`
- 后续：`web/` 目前只有占位 Dockerfile；`cli/` 为空目录待 M4
