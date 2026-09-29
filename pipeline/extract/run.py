"""extract：从快照文本中抽取关系草稿。

两种模式：
- fixture（默认）：加载预置抽取结果，无需 LLM 凭据即可复现全流程
- llm：设置 LLM_API_KEY 后调用模型做结构化抽取（输出同样过 schema 校验）

产物：pipeline/extract/out/drafts.json（草稿，须经 resolve + 人工复核后入库）

运行：make extract            # fixture 模式
     EXTRACT_MODE=llm make extract
"""
import json
import os
from pathlib import Path

from pydantic import TypeAdapter

from pipeline.extract.schema import ExtractedRelationship, ExtractionResult

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "nvda_10k_extract.json"
OUT = HERE / "out" / "drafts.json"

LLM_PROMPT = """你是供应链关系抽取器。从以下 NVIDIA 公开披露文本中抽取公司间关系。
每条关系输出 JSON：from_entity, to_entity, type(supplier/customer/partner/investor_or_investee/peer),
status(confirmed=文本明确陈述 / inferred=合理推断), excerpt(≤400字原文摘录), locator(章节定位), confidence(0-1)。
只输出文本明确支持或可由上下文合理推断的关系；文本未点名的关系必须标 inferred。"""


def load_fixture() -> list[ExtractedRelationship]:
    adapter = TypeAdapter(list[ExtractedRelationship])
    return adapter.validate_python(json.loads(FIXTURE.read_text()))


def extract_with_llm() -> list[ExtractedRelationship]:
    """LLM 模式：structured output，产出仍须过 schema 校验。"""
    from openai import OpenAI  # 延迟导入，fixture 模式不依赖 openai 包

    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM 模式需要 LLM_API_KEY（见 .env.example）")

    snapshot_dir = HERE.parent / "snapshots"
    latest = sorted(snapshot_dir.iterdir())[-1]
    text_path = latest / "nvda_10k_latest.html"
    text = text_path.read_text(errors="ignore")[:100_000]  # 截断控制 token

    client = OpenAI(api_key=api_key)
    resp = client.beta.chat.completions.parse(
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": LLM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=ExtractionResult,
    )
    result = resp.choices[0].message.parsed
    for rel in result.relationships:
        rel.source_id = "nvda_10k_latest"
    return result.relationships


def main() -> None:
    mode = os.environ.get("EXTRACT_MODE", "fixture")
    rels = extract_with_llm() if mode == "llm" else load_fixture()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps([r.model_dump() for r in rels], indent=2, ensure_ascii=False)
    )
    print(f"extract 完成（mode={mode}）：{len(rels)} 条关系草稿 -> {OUT}")


if __name__ == "__main__":
    main()
