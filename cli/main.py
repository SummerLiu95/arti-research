"""CLI 入口：与 REST API 等价的脚本化查询（共用 service 层）。

示例：
  make cli ARGS="relationships --type supplier --min-score 60"
  make cli ARGS="graph --center NVIDIA"
  make cli ARGS="detail 3"
"""
import json
from datetime import datetime

import typer

from api import service
from api.db import get_session_factory
from api.models import RelationStatus, RelationType

app = typer.Typer(help="ARTi NVIDIA 供应链关系查询 CLI")


def _rel_dict(r) -> dict:
    return {
        "id": r.id,
        "from": r.from_entity.name,
        "to": r.to_entity.name,
        "type": r.type,
        "status": r.status,
        "relevance_score": r.relevance_score,
        "notes": r.notes,
    }


@app.command()
def relationships(
    type: RelationType | None = typer.Option(None, help="关系类型筛选"),
    status: RelationStatus | None = typer.Option(None),
    company: str | None = typer.Option(None, help="按公司名模糊匹配（双向）"),
    min_score: float | None = typer.Option(None, "--min-score", help="最低相关度 0-100"),
    max_score: float | None = typer.Option(None, "--max-score"),
    valid_at: datetime | None = typer.Option(None, "--valid-at", help="查询某时点仍有效的关系"),
    page: int = 1,
    page_size: int = 20,
):
    """查询公司关系（筛选 + 分页，输出 JSON）。"""
    session = get_session_factory()()
    try:
        total, items = service.query_relationships(
            session, type, status, company, min_score, max_score, valid_at, page, page_size
        )
        typer.echo(json.dumps(
            {"total": total, "page": page, "page_size": page_size,
             "items": [_rel_dict(r) for r in items]},
            ensure_ascii=False, indent=2, default=str,
        ))
    finally:
        session.close()


@app.command()
def detail(rel_id: int):
    """查看单条关系详情（含证据链与评分构成）。"""
    session = get_session_factory()()
    try:
        rel = service.get_relationship_detail(session, rel_id)
        if rel is None:
            typer.echo(f"关系不存在: id={rel_id}", err=True)
            raise typer.Exit(1)
        out = _rel_dict(rel)
        out["score_breakdown"] = rel.score_breakdown
        out["evidences"] = [
            {"source_url": ev.source_url, "publisher": ev.publisher,
             "published_at": ev.published_at, "locator": ev.locator, "excerpt": ev.excerpt}
            for ev in rel.evidences
        ]
        typer.echo(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    finally:
        session.close()


@app.command()
def graph(center: str | None = typer.Option(None, help="只取该中心实体的直接关系")):
    """输出关系图（节点/边 JSON，可直接喂给可视化工具）。"""
    session = get_session_factory()()
    try:
        entities, rels = service.build_graph(session, center)
        if center and not rels:
            typer.echo(f"未找到实体或其关系: {center}", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps({
            "nodes": [{"id": e.id, "name": e.name, "ticker": e.ticker} for e in entities],
            "edges": [{"id": r.id, "from": r.from_entity.name, "to": r.to_entity.name,
                       "type": r.type, "score": r.relevance_score} for r in rels],
        }, ensure_ascii=False, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    app()
