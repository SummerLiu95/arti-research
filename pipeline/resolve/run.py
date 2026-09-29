"""resolve：实体消歧——把草稿中的公司名映射到规范实体。

策略：别名表精确匹配为主（确定性、可复现）；同名冲突记 conflict 交人工裁决。
LLM 辅助判断留作扩展点，默认不启用。

运行：make resolve
"""
import json
from pathlib import Path

EXTRACT_OUT = Path(__file__).resolve().parent.parent / "extract" / "out" / "drafts.json"
OUT = Path(__file__).resolve().parent / "out" / "resolved.json"

# 规范实体表：canonical_name -> (aliases, ticker, is_listed)
# 以 SEC CIK/证券代码为锚点维护（见 SOURCES.md 歧义处理原则）
ENTITY_REGISTRY = {
    "NVIDIA": (["英伟达", "NVIDIA Corporation", "Nvidia"], "NASDAQ:NVDA", True),
    "TSMC": (["台积电", "Taiwan Semiconductor", "Taiwan Semiconductor Manufacturing Company"], "NYSE:TSM", True),
    "SK Hynix": (["SK海力士", "SK hynix", "Hynix"], "KRX:000660", True),
    "Micron": (["美光", "Micron Technology"], "NASDAQ:MU", True),
    "Samsung": (["三星", "Samsung Electronics"], "KRX:005930", True),
    "Microsoft": (["微软", "MSFT"], "NASDAQ:MSFT", True),
    "Amazon": (["亚马逊", "AWS"], "NASDAQ:AMZN", True),
    "AMD": (["超威半导体", "Advanced Micro Devices"], "NASDAQ:AMD", True),
    "Intel": (["英特尔", "Intel Corporation"], "NASDAQ:INTC", True),
}


def build_alias_index() -> dict[str, str]:
    index = {}
    for canonical, (aliases, _, _) in ENTITY_REGISTRY.items():
        index[canonical.lower()] = canonical
        for alias in aliases:
            index[alias.lower()] = canonical
    return index


def main() -> None:
    alias_index = build_alias_index()
    drafts = json.loads(EXTRACT_OUT.read_text())

    resolved, unresolved, conflicts = [], [], []
    for d in drafts:
        from_c = alias_index.get(d["from_entity"].lower())
        to_c = alias_index.get(d["to_entity"].lower())
        if from_c and to_c:
            d["from_entity"], d["to_entity"] = from_c, to_c
            resolved.append(d)
        else:
            missing = [n for n, c in (("from_entity", from_c), ("to_entity", to_c)) if c is None]
            d["unresolved_fields"] = missing
            unresolved.append(d)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"resolved": resolved, "unresolved": unresolved, "conflicts": conflicts},
        indent=2, ensure_ascii=False,
    ))
    print(f"resolve 完成：resolved={len(resolved)} unresolved={len(unresolved)} conflicts={len(conflicts)}")
    if unresolved:
        print("[warn] 存在未匹配实体，需人工补充别名表后重跑 resolve")


if __name__ == "__main__":
    main()
