.PHONY: setup ingest extract resolve score seed api cli web test compose-up compose-down

PY ?= python3

setup: ## 安装后端/管道依赖
	$(PY) -m venv .venv && .venv/bin/pip install -r requirements.txt

ingest: ## 采集公开数据源并落快照
	.venv/bin/python -m pipeline.ingest.run

extract: ## LLM 结构化抽取（产草稿）
	.venv/bin/python -m pipeline.extract.run

resolve: ## 实体消歧
	.venv/bin/python -m pipeline.resolve.run

review: ## 人工复核并入库（批量：make review ARGS="--approve-all"）
	.venv/bin/python -m pipeline.review.run $(ARGS)

score: ## 评分引擎（可复算）
	.venv/bin/python -m pipeline.scoring.run

seed: ## 写入种子数据
	.venv/bin/python -m pipeline.seed

export: ## 导出交付数据集（data/）
	.venv/bin/python -m pipeline.export

api: ## 本地启动 FastAPI
	.venv/bin/uvicorn api.main:app --reload --port 8000

cli: ## CLI 入口（示例：make cli ARGS="relationships --type supplier"）
	.venv/bin/python -m cli.main $(ARGS)

web: ## 前端开发服务器
	cd web && pnpm dev

test: ## 后端测试
	.venv/bin/pytest -q

compose-up: ## docker-compose 一键起全栈
	docker compose up --build

compose-down:
	docker compose down
