"""查询 service 层：API 与 CLI 共用。"""
from datetime import datetime

from sqlalchemy.orm import Session, selectinload

from api.models import Entity, Relationship, RelationStatus, RelationType


def list_entities(session: Session, name: str | None = None) -> list[Entity]:
    q = session.query(Entity)
    if name:
        q = q.filter(Entity.name.ilike(f"%{name}%"))
    return q.order_by(Entity.name).all()


def query_relationships(
    session: Session,
    rel_type: RelationType | None = None,
    status: RelationStatus | None = None,
    company: str | None = None,
    min_score: float | None = None,
    max_score: float | None = None,
    valid_at: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, list[Relationship]]:
    q = session.query(Relationship).options(
        selectinload(Relationship.from_entity), selectinload(Relationship.to_entity)
    )
    if rel_type:
        q = q.filter(Relationship.type == rel_type)
    if status:
        q = q.filter(Relationship.status == status)
    if company:
        from sqlalchemy import or_
        from sqlalchemy.orm import aliased

        FromE, ToE = aliased(Entity), aliased(Entity)
        q = q.join(FromE, Relationship.from_entity_id == FromE.id) \
             .join(ToE, Relationship.to_entity_id == ToE.id) \
             .filter(or_(FromE.name.ilike(f"%{company}%"), ToE.name.ilike(f"%{company}%")))
    if min_score is not None:
        q = q.filter(Relationship.relevance_score >= min_score)
    if max_score is not None:
        q = q.filter(Relationship.relevance_score <= max_score)
    if valid_at:
        # 某时点仍有效的关系：起始不晚于该时点，且未终止或终止晚于该时点
        q = q.filter(
            (Relationship.valid_from.is_(None)) | (Relationship.valid_from <= valid_at),
            (Relationship.valid_to.is_(None)) | (Relationship.valid_to >= valid_at),
        )
    total = q.count()
    items = (
        q.order_by(Relationship.relevance_score.desc().nulls_last(), Relationship.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def get_relationship_detail(session: Session, rel_id: int) -> Relationship | None:
    return (
        session.query(Relationship)
        .options(
            selectinload(Relationship.from_entity),
            selectinload(Relationship.to_entity),
            selectinload(Relationship.evidences),
        )
        .filter_by(id=rel_id)
        .one_or_none()
    )


def build_graph(session: Session, center: str | None = None) -> tuple[list[Entity], list[Relationship]]:
    """关系图数据。指定 center 时只取与该实体直接相连的关系。"""
    q = session.query(Relationship).options(
        selectinload(Relationship.from_entity), selectinload(Relationship.to_entity)
    )
    if center:
        entity = session.query(Entity).filter(Entity.name.ilike(center)).one_or_none()
        if entity is None:
            return [], []
        q = q.filter(
            (Relationship.from_entity_id == entity.id) | (Relationship.to_entity_id == entity.id)
        )
    rels = q.all()
    entity_ids = {r.from_entity_id for r in rels} | {r.to_entity_id for r in rels}
    entities = session.query(Entity).filter(Entity.id.in_(entity_ids)).all() if entity_ids else []
    return entities, rels
