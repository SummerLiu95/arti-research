"""评分引擎测试（T3.3）：可复算、范围约束、因子单调性。"""
from datetime import datetime, timedelta, timezone

from pipeline.scoring.formula import (
    compute_score,
    evidence_count_factor,
    independence_factor,
    recency_factor,
)

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def test_score_deterministic():
    """可复算：同输入同输出。"""
    args = ("supplier", "confirmed", ["SEC EDGAR", "SEC EDGAR"], NOW)
    assert compute_score(*args, now=NOW) == compute_score(*args, now=NOW)


def test_score_within_0_100():
    for t in ("supplier", "customer", "partner", "investor_or_investee", "peer"):
        score, _ = compute_score(t, "confirmed", ["A"], NOW, now=NOW)
        assert 0 <= score <= 100


def test_confirmed_beats_inferred():
    s1, _ = compute_score("supplier", "confirmed", ["A"], NOW, now=NOW)
    s2, _ = compute_score("supplier", "inferred", ["A"], NOW, now=NOW)
    assert s1 > s2


def test_more_independent_evidence_scores_higher():
    """独立性：3 个不同来源 > 同一来源 3 条（新闻共振抑制）。"""
    s1, _ = compute_score("supplier", "confirmed", ["A", "B", "C"], NOW, now=NOW)
    s2, _ = compute_score("supplier", "confirmed", ["A", "A", "A"], NOW, now=NOW)
    assert s1 > s2


def test_recency_decays():
    recent = recency_factor(NOW, NOW)
    old = recency_factor(NOW - timedelta(days=730), NOW)  # 一个半衰期
    assert recent > old
    assert abs(old - 0.5) < 1e-6


def test_factor_bounds():
    assert evidence_count_factor(0) == 0.6
    assert evidence_count_factor(100) == 1.0
    assert independence_factor([]) == 0.5
    assert independence_factor(["A", "A"]) == 0.75
    assert independence_factor(["A", "B"]) == 1.0
