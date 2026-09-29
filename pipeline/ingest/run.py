"""ingest：采集公开数据源并落快照（pipeline/snapshots/<date>/）。

合规：仅访问 SEC 公开 JSON/HTML，按 SEC 政策声明 User-Agent，串行限速。
每个快照伴随 meta.json（url、publisher、retrieved_at、sha256），供证据引用。

运行：make ingest
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from pipeline.ingest.sources import SOURCES

SNAPSHOT_ROOT = Path(__file__).resolve().parent.parent / "snapshots"

# SEC 要求：声明身份与联系方式的 User-Agent；限速 ≤10 req/s（这里串行 + 1s 间隔）
HEADERS = {"User-Agent": "ArtiResearch/1.0 (research@example.com)"}
REQUEST_INTERVAL_S = 1.0


def save_snapshot(snapshot_dir: Path, source_id: str, url: str, publisher: str, content: bytes, ext: str) -> Path:
    path = snapshot_dir / f"{source_id}.{ext}"
    path.write_bytes(content)
    meta = {
        "source_id": source_id,
        "url": url,
        "publisher": publisher,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content),
    }
    (snapshot_dir / f"{source_id}.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return path


def latest_10k_url(submissions: dict) -> str | None:
    """从 submissions 索引中解析最新一份 10-K 的完整 URL。"""
    recent = submissions["filings"]["recent"]
    for form, accession, doc in zip(recent["form"], recent["accessionNumber"], recent["primaryDocument"]):
        if form == "10-K":
            acc_nodash = accession.replace("-", "")
            # Archives 路径使用无前导零的 CIK
            cik = str(int(submissions["cik"]))
            return f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"
    return None


def main() -> None:
    snapshot_dir = SNAPSHOT_ROOT / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(headers=HEADERS, timeout=30.0) as client:
        submissions = None
        for source in SOURCES:
            resp = client.get(source.url)
            resp.raise_for_status()
            path = save_snapshot(snapshot_dir, source.id, source.url, source.publisher, resp.content, "json")
            print(f"[snapshot] {source.id} -> {path} ({len(resp.content)} bytes)")
            if source.id == "sec_submissions":
                submissions = resp.json()
            time.sleep(REQUEST_INTERVAL_S)

        if submissions:
            url_10k = latest_10k_url(submissions)
            if url_10k:
                resp = client.get(url_10k)
                resp.raise_for_status()
                path = save_snapshot(snapshot_dir, "nvda_10k_latest", url_10k, "SEC EDGAR", resp.content, "html")
                print(f"[snapshot] nvda_10k_latest -> {path} ({len(resp.content)} bytes)")
            else:
                print("[warn] 未在 submissions 索引中找到 10-K")

    print(f"ingest 完成，快照目录：{snapshot_dir}")


if __name__ == "__main__":
    main()
