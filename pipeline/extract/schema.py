"""抽取产物的 Pydantic schema：LLM 输出必须满足此结构，否则丢弃。"""
from enum import Enum

from pydantic import BaseModel, Field


class RelType(str, Enum):
    supplier = "supplier"
    customer = "customer"
    partner = "partner"
    investor_or_investee = "investor_or_investee"
    peer = "peer"


class RelStatus(str, Enum):
    confirmed = "confirmed"
    inferred = "inferred"
    unknown = "unknown"


class ExtractedRelationship(BaseModel):
    """一条从公开文本中抽取的关系草稿。"""

    from_entity: str = Field(description="关系发起方公司名（如 TSMC）")
    to_entity: str = Field(description="关系指向方公司名（如 NVIDIA）")
    type: RelType
    status: RelStatus = RelStatus.inferred
    source_id: str = Field(description="快照 source_id，如 nvda_10k_latest")
    excerpt: str = Field(max_length=400, description="支持该关系的原文摘录，≤400字")
    locator: str = Field(description="证据定位：章节名或原文位置描述")
    confidence: float = Field(ge=0, le=1, description="抽取置信度 0-1")
    note: str | None = None


class ExtractionResult(BaseModel):
    relationships: list[ExtractedRelationship]
