"""FastAPI 入口：关系查询、关系图、证据查询。

运行：make api 或 docker compose up
文档：/docs（OpenAPI 自动生成）
"""
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api import service
from api.db import get_session_factory
from api.models import RelationStatus, RelationType
from api.schemas import (
    EntityOut,
    GraphEdge,
    GraphNode,
    GraphOut,
    RelationshipDetailOut,
    RelationshipPage,
)

app = FastAPI(title="ARTi NVIDIA Supply Chain Research API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_session():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/entities", response_model=list[EntityOut])
def list_entities(session: SessionDep, name: str | None = None):
    return service.list_entities(session, name)


@app.get("/relationships", response_model=RelationshipPage)
def list_relationships(
    session: SessionDep,
    type: RelationType | None = None,
    status: RelationStatus | None = None,
    company: str | None = None,
    min_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    max_score: Annotated[float | None, Query(ge=0, le=100)] = None,
    valid_at: datetime | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    if min_score is not None and max_score is not None and min_score > max_score:
        raise HTTPException(422, "min_score 不能大于 max_score")
    total, items = service.query_relationships(
        session, type, status, company, min_score, max_score, valid_at, page, page_size
    )
    return RelationshipPage(total=total, page=page, page_size=page_size, items=items)


@app.get("/relationships/{rel_id}", response_model=RelationshipDetailOut)
def get_relationship(rel_id: int, session: SessionDep):
    rel = service.get_relationship_detail(session, rel_id)
    if rel is None:
        raise HTTPException(404, f"关系不存在: id={rel_id}")
    return rel


@app.get("/graph", response_model=GraphOut)
def get_graph(session: SessionDep, center: str | None = None):
    entities, rels = service.build_graph(session, center)
    if center and not rels:
        raise HTTPException(404, f"未找到实体或其关系: {center}")
    return GraphOut(
        nodes=[GraphNode(id=str(e.id), label=e.name, ticker=e.ticker, is_listed=e.is_listed) for e in entities],
        edges=[
            GraphEdge(
                id=str(r.id),
                source=str(r.from_entity_id),
                target=str(r.to_entity_id),
                type=r.type,
                status=r.status,
                relevance_score=r.relevance_score,
            )
            for r in rels
        ],
    )
