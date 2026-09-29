"""数据集导出（T6.1）：把库内关系+证据导出为交付数据集。

产物：data/relationships.json（全量嵌套）与 data/relationships.csv（扁平）
附 data/MANIFEST.json 记录数据截点与内容哈希。

运行：make export
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from api.db import get_session_factory
from api.models import Relationship

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    session = get_session_factory()()
    try:
        rels = session.query(Relationship).all()
        records = []
        for r in rels:
            records.append({
                "id": r.id,
                "from_entity": r.from_entity.name,
                "to_entity": r.to_entity.name,
                "from_ticker": r.from_entity.ticker,
                "to_ticker": r.to_entity.ticker,
                "type": str(r.type),
                "status": str(r.status),
                "relevance_score": r.relevance_score,
                "score_breakdown": r.score_breakdown,
                "valid_from": r.valid_from.isoformat() if r.valid_from else None,
                "valid_to": r.valid_to.isoformat() if r.valid_to else None,
                "notes": r.notes,
                "evidences": [
                    {
                        "source_url": ev.source_url,
                        "publisher": ev.publisher,
                        "published_at": ev.published_at.isoformat() if ev.published_at else None,
                        "retrieved_at": ev.retrieved_at.isoformat(),
                        "locator": ev.locator,
                        "excerpt": ev.excerpt,
                        "access_note": ev.access_note,
                    }
                    for ev in r.evidences
                ],
            })

        DATA_DIR.mkdir(exist_ok=True)
        json_path = DATA_DIR / "relationships.json"
        csv_path = DATA_DIR / "relationships.csv"

        payload = {
            "subject": {"name": "NVIDIA Corporation", "ticker": "NASDAQ:NVDA", "cik": "0001045810"},
            "data_cutoff": datetime.now(timezone.utc).date().isoformat(),
            "disclaimer": "仅供技术研究，不构成投资建议",
            "relationships": records,
        }
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "from_entity", "to_entity", "from_ticker", "to_ticker",
                "type", "status", "relevance_score", "evidence_count", "notes",
            ])
            writer.writeheader()
            for r in records:
                writer.writerow({
                    **{k: r[k] for k in ("id", "from_entity", "to_entity", "from_ticker",
                                          "to_ticker", "type", "status", "relevance_score", "notes")},
                    "evidence_count": len(r["evidences"]),
                })

        digest = hashlib.sha256(json_path.read_bytes()).hexdigest()
        (DATA_DIR / "MANIFEST.json").write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_cutoff": payload["data_cutoff"],
            "relationship_count": len(records),
            "evidence_count": sum(len(r["evidences"]) for r in records),
            "relationships_json_sha256": digest,
        }, indent=2, ensure_ascii=False))
        print(f"export 完成：{len(records)} 条关系 -> {json_path}, {csv_path}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
