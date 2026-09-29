"""核心数据模型：entity / relationship / evidence。

设计要点（见 docs/ARCHITECTURE.md §5）：
- relationship 1─N evidence，证据不可变，指向快照原文 + locator
- 关系状态区分 confirmed（已确认事实）/ inferred（合理推断）/ unknown
- relevance_score 0–100 由评分引擎写入，score_breakdown 存因子明细（可解释）
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship as orm_relationship


class Base(DeclarativeBase):
    pass


class RelationType(str, enum.Enum):
    supplier = "supplier"
    customer = "customer"
    partner = "partner"
    investor_or_investee = "investor_or_investee"
    peer = "peer"


class RelationStatus(str, enum.Enum):
    confirmed = "confirmed"  # 已确认事实
    inferred = "inferred"    # 合理推断
    unknown = "unknown"      # 未知


class Entity(Base):
    """公司实体。"""

    __tablename__ = "entity"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    aliases: Mapped[list] = mapped_column(JSONB, default=list)  # 别名，用于消歧
    ticker: Mapped[str | None] = mapped_column(String(32), index=True)  # 证券标识，如 NASDAQ:NVDA
    is_listed: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    outgoing: Mapped[list["Relationship"]] = orm_relationship(
        back_populates="from_entity", foreign_keys="Relationship.from_entity_id"
    )
    incoming: Mapped[list["Relationship"]] = orm_relationship(
        back_populates="to_entity", foreign_keys="Relationship.to_entity_id"
    )


class Relationship(Base):
    """实体间关系。方向：from_entity → to_entity（如 TSMC --supplier--> NVIDIA）。"""

    __tablename__ = "relationship"
    __table_args__ = (
        UniqueConstraint("from_entity_id", "to_entity_id", "type", name="uq_relationship"),
        CheckConstraint("relevance_score BETWEEN 0 AND 100", name="ck_score_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    from_entity_id: Mapped[int] = mapped_column(ForeignKey("entity.id"), index=True)
    to_entity_id: Mapped[int] = mapped_column(ForeignKey("entity.id"), index=True)
    type: Mapped[RelationType] = mapped_column(String(32), index=True)
    status: Mapped[RelationStatus] = mapped_column(String(16), default=RelationStatus.confirmed)
    relevance_score: Mapped[float | None] = mapped_column()  # 0–100，评分引擎写入
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)  # 评分因子明细
    valid_from: Mapped[datetime | None] = mapped_column()  # 时效：关系起始
    valid_to: Mapped[datetime | None] = mapped_column()    # 时效：关系终止（None=仍有效）
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    from_entity: Mapped[Entity] = orm_relationship(foreign_keys=[from_entity_id], back_populates="outgoing")
    to_entity: Mapped[Entity] = orm_relationship(foreign_keys=[to_entity_id], back_populates="incoming")
    evidences: Mapped[list["Evidence"]] = orm_relationship(back_populates="relationship", cascade="all, delete-orphan")


class Evidence(Base):
    """证据：一条关系可挂多条，指向快照原文与定位。"""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    relationship_id: Mapped[int] = mapped_column(ForeignKey("relationship.id"), index=True)
    source_url: Mapped[str] = mapped_column(Text)
    publisher: Mapped[str] = mapped_column(String(255))
    published_at: Mapped[datetime | None] = mapped_column()  # 发布时间
    retrieved_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))  # 获取时间
    locator: Mapped[str | None] = mapped_column(Text)  # 证据定位（页码/段落/原文片段）
    excerpt: Mapped[str | None] = mapped_column(Text)  # 原文摘录（≤400 字）
    snapshot_path: Mapped[str | None] = mapped_column(Text)  # pipeline/snapshots/ 下的快照引用
    access_note: Mapped[str | None] = mapped_column(Text)  # 访问/许可限制说明

    relationship: Mapped[Relationship] = orm_relationship(back_populates="evidences")
