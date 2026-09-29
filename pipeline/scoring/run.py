"""评分引擎（T3.1/T3.2）：遍历关系，按公式计算 0–100 评分并写回数据库。

score_breakdown 存因子明细（JSONB），前端详情抽屉据此展示评分构成。
可复算：同一份数据重跑结果一致（时间敏感因子以证据时间为基准）。

运行：make score
"""
from datetime import datetime

from api.db import get_session_factory
from api.models import Relationship
from pipeline.scoring.formula import compute_score


def score_relationship(rel: Relationship, now: datetime | None = None) -> tuple[float, dict]:
    publishers = [ev.publisher for ev in rel.evidences]
    times = [ev.published_at or ev.retrieved_at for ev in rel.evidences]
    latest_at = max(times) if times else None
    rel_type = rel.type.value if hasattr(rel.type, "value") else str(rel.type)
    status = rel.status.value if hasattr(rel.status, "value") else str(rel.status)
    score, factors = compute_score(rel_type, status, publishers, latest_at, now)
    factors["evidence_count"] = len(rel.evidences)
    factors["latest_evidence_at"] = latest_at.isoformat() if latest_at else None
    return score, factors


def main() -> None:
    session = get_session_factory()()
    try:
        rels = session.query(Relationship).all()
        for rel in rels:
            score, breakdown = score_relationship(rel)
            rel.relevance_score = score
            rel.score_breakdown = breakdown
            print(f"{rel.from_entity.name} --{rel.type}--> {rel.to_entity.name}: {score}")
        session.commit()
        print(f"score 完成：{len(rels)} 条关系已评分")
    finally:
        session.close()


if __name__ == "__main__":
    main()
