"""数据源定义：每个源声明 id、URL、publisher 与用途说明。"""
from dataclasses import dataclass

NVDA_CIK = "0001045810"


@dataclass(frozen=True)
class Source:
    id: str
    url: str
    publisher: str
    note: str


SOURCES = [
    Source(
        id="sec_submissions",
        url=f"https://data.sec.gov/submissions/CIK{NVDA_CIK}.json",
        publisher="SEC EDGAR",
        note="NVIDIA 申报文件索引（10-K/10-Q/8-K 列表）",
    ),
    # 10-K 全文 URL 由 submissions 索引动态解析（见 run.py），不在此硬编码
]
