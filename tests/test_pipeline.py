"""M2 管道边界用例测试（T2.6）。

覆盖三类边界：schema 校验拒绝坏数据、未注册实体进 unresolved、fixture 本身合法。
"""
import json

import pytest
from pydantic import ValidationError

from pipeline.extract.schema import ExtractedRelationship
from pipeline.resolve.run import ENTITY_REGISTRY, build_alias_index

FIXTURE_PATH = "pipeline/extract/fixtures/nvda_10k_extract.json"


def make_rel(**overrides) -> dict:
    base = {
        "from_entity": "TSMC",
        "to_entity": "NVIDIA",
        "type": "supplier",
        "source_id": "nvda_10k_latest",
        "excerpt": "excerpt",
        "locator": "10-K Item 1",
        "confidence": 0.9,
    }
    base.update(overrides)
    return base


# --- schema 边界 ---

def test_excerpt_over_400_chars_rejected():
    with pytest.raises(ValidationError):
        ExtractedRelationship(**make_rel(excerpt="x" * 401))


def test_confidence_out_of_range_rejected():
    with pytest.raises(ValidationError):
        ExtractedRelationship(**make_rel(confidence=1.5))


def test_unknown_relation_type_rejected():
    with pytest.raises(ValidationError):
        ExtractedRelationship(**make_rel(type="subsidiary"))


# --- 实体消歧边界 ---

def test_alias_matching_is_case_insensitive():
    index = build_alias_index()
    assert index["tsmc"] == "TSMC"
    assert index["台积电"] == "TSMC"
    assert index["nvidia corporation"] == "NVIDIA"


def test_unknown_entity_not_in_registry():
    index = build_alias_index()
    assert index.get("some unknown corp") is None


# --- fixture 质量门 ---

def test_fixture_passes_schema_and_registry():
    drafts = json.loads(open(FIXTURE_PATH).read())
    index = build_alias_index()
    assert drafts, "fixture 不应为空"
    for d in drafts:
        ExtractedRelationship(**d)  # schema 校验
        assert index.get(d["from_entity"].lower()), f"未注册实体: {d['from_entity']}"
        assert index.get(d["to_entity"].lower()), f"未注册实体: {d['to_entity']}"
