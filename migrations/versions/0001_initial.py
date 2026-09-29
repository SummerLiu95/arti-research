"""initial schema: entity / relationship / evidence

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aliases", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("ticker", sa.String(32), nullable=True),
        sa.Column("is_listed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_entity_name", "entity", ["name"], unique=True)
    op.create_index("ix_entity_ticker", "entity", ["ticker"])

    op.create_table(
        "relationship",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_entity_id", sa.Integer(), sa.ForeignKey("entity.id"), nullable=False),
        sa.Column("to_entity_id", sa.Integer(), sa.ForeignKey("entity.id"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="confirmed"),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("from_entity_id", "to_entity_id", "type", name="uq_relationship"),
        sa.CheckConstraint("relevance_score BETWEEN 0 AND 100", name="ck_score_range"),
    )
    op.create_index("ix_relationship_from", "relationship", ["from_entity_id"])
    op.create_index("ix_relationship_to", "relationship", ["to_entity_id"])
    op.create_index("ix_relationship_type", "relationship", ["type"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("relationship_id", sa.Integer(), sa.ForeignKey("relationship.id"), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("publisher", sa.String(255), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("locator", sa.Text(), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("snapshot_path", sa.Text(), nullable=True),
        sa.Column("access_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_evidence_relationship", "evidence", ["relationship_id"])


def downgrade() -> None:
    op.drop_table("evidence")
    op.drop_table("relationship")
    op.drop_table("entity")
