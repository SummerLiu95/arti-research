"""review：人工复核 + 入库。

流程：读取 resolve 产物 → 逐条展示草稿 → 人工确认（默认全部需确认）→
确认的关系连同证据（关联快照 meta）写入数据库。

运行：.venv/bin/python -m pipeline.review.run            # 交互式逐条确认
     .venv/bin/python -m pipeline.review.run --approve-all  # 已复核过 drafts 后批量入库
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from api.db import get_session_factory
from api.models import Entity, Evidence, Relationship, RelationStatus, RelationType

RESOLVE_OUT = Path(__file__).resolve().parent.parent / "resolve" / "out" / "resolved.json"
SNAPSHOT_ROOT = Path(__file__).resolve().parent.parent / "snapshots"


def load_snapshot_meta(source_id: str) -> dict | None:
    """取最新快照目录中该 source 的 meta（URL、publisher、retrieved_at）。"""
    dates = sorted(p for p in SNAPSHOT_ROOT.iterdir() if p.is_dir())
    for d in reversed(dates):
        meta_path = d / f"{source_id}.meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            meta["snapshot_path"] = str(meta_path.parent / f"{source_id}.html")
            return meta
    return None


def get_or_create_entity(session, name: str) -> Entity:
    from pipeline.resolve.run import ENTITY_REGISTRY

    e = session.query(Entity).filter_by(name=name).one_or_none()
    if e is None:
        aliases, ticker, is_listed = ENTITY_REGISTRY.get(name, ([], None, False))
        e = Entity(name=name, aliases=aliases, ticker=ticker, is_listed=is_listed)
        session.add(e)
        session.flush()
    return e


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve-all", action="store_true", help="跳过逐条确认（草稿已人工复核过）")
    args = parser.parse_args()

    data = json.loads(RESOLVE_OUT.read_text())
    drafts = data["resolved"]
    if not drafts:
        print("没有待复核的关系")
        return

    session = get_session_factory()()
    approved = 0
    try:
        for i, d in enumerate(drafts, 1):
            print(f"\n[{i}/{len(drafts)}] {d['from_entity']} --{d['type']}--> {d['to_entity']}"
                  f" (status={d['status']}, confidence={d['confidence']})")
            print(f"  摘录: {d['excerpt'][:120]}...")
            print(f"  定位: {d['locator']}")
            if not args.approve_all:
                if input("  确认入库? [y/N] ").strip().lower() != "y":
                    continue

            meta = load_snapshot_meta(d["source_id"])
            from_id = get_or_create_entity(session, d["from_entity"]).id
            to_id = get_or_create_entity(session, d["to_entity"]).id
            rel = (
                session.query(Relationship)
                .filter_by(from_entity_id=from_id, to_entity_id=to_id, type=RelationType(d["type"]))
                .one_or_none()
            )
            if rel is None:
                rel = Relationship(
                    from_entity_id=from_id,
                    to_entity_id=to_id,
                    type=RelationType(d["type"]),
                    status=RelationStatus(d["status"]),
                    notes=d.get("note"),
                )
                session.add(rel)
                session.flush()
            else:
                # 幂等：已存在的关系更新状态与备注，仅在摘录不同时追加证据
                rel.status = RelationStatus(d["status"])
                if d.get("note"):
                    rel.notes = d["note"]
                if any(ev.excerpt == d["excerpt"] for ev in rel.evidences):
                    print("  -> 已存在且证据相同，跳过")
                    continue
            session.add(Evidence(
                relationship_id=rel.id,
                source_url=meta["url"] if meta else "unknown",
                publisher=meta["publisher"] if meta else "unknown",
                retrieved_at=datetime.fromisoformat(meta["retrieved_at"]) if meta else datetime.now(timezone.utc),
                locator=d["locator"],
                excerpt=d["excerpt"],
                snapshot_path=meta.get("snapshot_path") if meta else None,
                access_note="SEC EDGAR 公开文件",
            ))
            approved += 1

        session.commit()
        print(f"\nreview 完成：入库 {approved}/{len(drafts)} 条关系")
    finally:
        session.close()


if __name__ == "__main__":
    main()
