#!/bin/sh
# API 容器启动引导：迁移 → 空库时从快照重放研究管道 → 评分 → 起服务
# 复现哲学：reviewer 无需凭据、无需联网抓取，compose up 即得完整数据
set -e

alembic upgrade head

if python -c "
from api.db import get_session_factory
from api.models import Relationship
s = get_session_factory()()
n = s.query(Relationship).count()
s.close()
import sys; sys.exit(0 if n > 0 else 1)
"; then
  echo "[bootstrap] 数据库已有数据，跳过重放"
else
  echo "[bootstrap] 空库，从快照重放管道（fixture 模式，无需 LLM 凭据）"
  python -m pipeline.extract.run
  python -m pipeline.resolve.run
  python -m pipeline.review.run --approve-all
  python -m pipeline.scoring.run
fi

exec uvicorn api.main:app --host 0.0.0.0 --port 8000
