"""评分公式定义（T3.1）。

score = 100 × 类型权重 × 状态系数 × 证据数量系数 × 证据独立性系数 × 时效衰减

设计原则：所有因子可解释、可复算；不使用 LLM。
因子取值与理由写在注释里，reviewer 可对单条关系的 score_breakdown 逐项复算。
"""
import math
from datetime import datetime, timezone

# 关系类型权重：供应链核心关系最高，可比公司仅作参照
TYPE_WEIGHT = {
    "supplier": 1.0,
    "customer": 1.0,
    "partner": 0.85,
    "investor_or_investee": 0.8,
    "peer": 0.6,
}

# 事实状态系数：已确认事实 > 合理推断 > 未知
STATUS_FACTOR = {"confirmed": 1.0, "inferred": 0.7, "unknown": 0.3}

# 时效衰减：以最新证据发布/获取时间为基准，半衰期 2 年
RECENCY_HALF_LIFE_DAYS = 730


def evidence_count_factor(n: int) -> float:
    """证据数量：1 条 0.7，每条 +0.1，封顶 1.0。"""
    return min(1.0, 0.6 + 0.1 * n)


def independence_factor(publishers: list[str]) -> float:
    """证据独立性：独立来源占比越高越好，避免同一来源重复刷屏（新闻共振误判）。"""
    if not publishers:
        return 0.5
    distinct = len(set(publishers))
    return 0.5 + 0.5 * distinct / len(publishers)


def recency_factor(latest_at: datetime | None, now: datetime | None = None) -> float:
    """时效衰减：指数衰减，半衰期 730 天。无时间信息按 0.7 计。"""
    if latest_at is None:
        return 0.7
    now = now or datetime.now(timezone.utc)
    if latest_at.tzinfo is None:
        latest_at = latest_at.replace(tzinfo=timezone.utc)
    days = max(0, (now - latest_at).days)
    return 0.5 ** (days / RECENCY_HALF_LIFE_DAYS)


def compute_score(rel_type: str, status: str, publishers: list[str], latest_at: datetime | None,
                  now: datetime | None = None) -> tuple[float, dict]:
    """返回 (0–100 评分, 因子明细)。"""
    factors = {
        "type_weight": TYPE_WEIGHT.get(rel_type, 0.5),
        "status_factor": STATUS_FACTOR.get(status, 0.3),
        "evidence_count_factor": evidence_count_factor(len(publishers)),
        "independence_factor": independence_factor(publishers),
        "recency_factor": recency_factor(latest_at, now),
    }
    score = 100.0
    for v in factors.values():
        score *= v
    return round(min(100.0, max(0.0, score)), 1), factors
