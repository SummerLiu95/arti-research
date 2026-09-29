"""开发用种子数据：打通前后端的假数据，不代表最终研究结论。

运行：make seed
最终研究数据由 M2 管道（ingest → extract → resolve → review）产出并替换。
"""
from api.db import get_session_factory
from api.models import Entity, Evidence, Relationship, RelationStatus, RelationType

# (name, aliases, ticker, is_listed)
ENTITIES = [
    ("NVIDIA", ["英伟达", "NVIDIA Corporation"], "NASDAQ:NVDA", True),
    ("TSMC", ["台积电", "Taiwan Semiconductor"], "NYSE:TSM", True),
    ("SK Hynix", ["SK海力士"], "KRX:000660", True),
    ("Microsoft", ["微软"], "NASDAQ:MSFT", True),
    ("Amazon", ["亚马逊", "AWS"], "NASDAQ:AMZN", True),
    ("AMD", ["超威半导体"], "NASDAQ:AMD", True),
    ("Intel", ["英特尔"], "NASDAQ:INTC", True),
]

# (from, to, type, status, note) —— 方向：from → to
RELATIONSHIPS = [
    ("TSMC", "NVIDIA", RelationType.supplier, RelationStatus.confirmed, "晶圆代工（开发示例数据）"),
    ("SK Hynix", "NVIDIA", RelationType.supplier, RelationStatus.confirmed, "HBM 内存供应（开发示例数据）"),
    ("Microsoft", "NVIDIA", RelationType.customer, RelationStatus.confirmed, "Azure 采购 GPU（开发示例数据）"),
    ("Amazon", "NVIDIA", RelationType.customer, RelationStatus.confirmed, "AWS 采购 GPU（开发示例数据）"),
    ("AMD", "NVIDIA", RelationType.peer, RelationStatus.confirmed, "GPU 竞品（开发示例数据）"),
    ("Intel", "NVIDIA", RelationType.peer, RelationStatus.confirmed, "芯片竞品（开发示例数据）"),
]

EVIDENCE_TEMPLATE = {
    "publisher": "示例来源（占位）",
    "source_url": "https://example.com/placeholder",
    "access_note": "公开页面；开发占位数据，待 M2 管道替换为真实证据",
}


def main() -> None:
    session = get_session_factory()()
    try:
        entities = {}
        for name, aliases, ticker, is_listed in ENTITIES:
            e = session.query(Entity).filter_by(name=name).one_or_none()
            if e is None:
                e = Entity(name=name, aliases=aliases, ticker=ticker, is_listed=is_listed)
                session.add(e)
                session.flush()
            entities[name] = e

        for from_name, to_name, rtype, status, note in RELATIONSHIPS:
            rel = (
                session.query(Relationship)
                .filter_by(
                    from_entity_id=entities[from_name].id,
                    to_entity_id=entities[to_name].id,
                    type=rtype,
                )
                .one_or_none()
            )
            if rel is None:
                rel = Relationship(
                    from_entity_id=entities[from_name].id,
                    to_entity_id=entities[to_name].id,
                    type=rtype,
                    status=status,
                    notes=note,
                )
                session.add(rel)
                session.flush()
                session.add(
                    Evidence(
                        relationship_id=rel.id,
                        excerpt=f"占位证据摘录：{note}",
                        **EVIDENCE_TEMPLATE,
                    )
                )

        session.commit()
        n_entities = session.query(Entity).count()
        n_rels = session.query(Relationship).count()
        n_ev = session.query(Evidence).count()
        print(f"seed 完成：entity={n_entities} relationship={n_rels} evidence={n_ev}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
