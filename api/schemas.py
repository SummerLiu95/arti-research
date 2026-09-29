"""API 响应模型。"""
from datetime import datetime

from pydantic import BaseModel

from api.models import RelationStatus, RelationType


class EntityOut(BaseModel):
    id: int
    name: str
    aliases: list
    ticker: str | None
    is_listed: bool

    model_config = {"from_attributes": True}


class EvidenceOut(BaseModel):
    id: int
    source_url: str
    publisher: str
    published_at: datetime | None
    retrieved_at: datetime
    locator: str | None
    excerpt: str | None
    snapshot_path: str | None
    access_note: str | None

    model_config = {"from_attributes": True}


class RelationshipOut(BaseModel):
    id: int
    from_entity: EntityOut
    to_entity: EntityOut
    type: RelationType
    status: RelationStatus
    relevance_score: float | None
    valid_from: datetime | None
    valid_to: datetime | None
    notes: str | None

    model_config = {"from_attributes": True}


class RelationshipDetailOut(RelationshipOut):
    score_breakdown: dict | None
    evidences: list[EvidenceOut]


class RelationshipPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RelationshipOut]


class GraphNode(BaseModel):
    id: str
    label: str
    ticker: str | None
    is_listed: bool


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: RelationType
    status: RelationStatus
    relevance_score: float | None


class GraphOut(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
