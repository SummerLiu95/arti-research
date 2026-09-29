"""API 测试：SQLite 内存库 + TestClient，覆盖关键路径与失败/边界用例。"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.db import get_session_factory
from api.main import app, get_session
from api.models import Base, Entity, Evidence, Relationship, RelationStatus, RelationType


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    session = TestSession()
    nvda = Entity(name="NVIDIA", aliases=["英伟达"], ticker="NASDAQ:NVDA", is_listed=True)
    tsmc = Entity(name="TSMC", aliases=["台积电"], ticker="NYSE:TSM", is_listed=True)
    amd = Entity(name="AMD", aliases=[], ticker="NASDAQ:AMD", is_listed=True)
    session.add_all([nvda, tsmc, amd])
    session.flush()
    r1 = Relationship(from_entity_id=tsmc.id, to_entity_id=nvda.id,
                      type=RelationType.supplier, status=RelationStatus.confirmed,
                      relevance_score=80.0, score_breakdown={"type_weight": 1.0})
    r2 = Relationship(from_entity_id=amd.id, to_entity_id=nvda.id,
                      type=RelationType.peer, status=RelationStatus.confirmed,
                      relevance_score=48.0)
    session.add_all([r1, r2])
    session.flush()
    session.add(Evidence(relationship_id=r1.id, source_url="https://example.com/10k",
                         publisher="SEC EDGAR", locator="10-K Item 1", excerpt="TSMC manufactures wafers."))
    session.commit()

    def override():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- 关键路径 ---

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_relationships(client):
    body = client.get("/relationships").json()
    assert body["total"] == 2
    assert body["items"][0]["relevance_score"] == 80.0  # 按评分降序


def test_filter_by_type(client):
    body = client.get("/relationships", params={"type": "supplier"}).json()
    assert body["total"] == 1
    assert body["items"][0]["from_entity"]["name"] == "TSMC"


def test_filter_by_min_score(client):
    body = client.get("/relationships", params={"min_score": 60}).json()
    assert body["total"] == 1


def test_filter_by_company_bidirectional(client):
    body = client.get("/relationships", params={"company": "NVIDIA"}).json()
    assert body["total"] == 2


def test_relationship_detail_with_evidence(client):
    body = client.get("/relationships/1").json()
    assert body["evidences"][0]["publisher"] == "SEC EDGAR"
    assert body["score_breakdown"]["type_weight"] == 1.0


def test_graph(client):
    body = client.get("/graph").json()
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2


def test_graph_center(client):
    body = client.get("/graph", params={"center": "TSMC"}).json()
    assert len(body["edges"]) == 1


# --- 失败/边界用例 ---

def test_relationship_404(client):
    assert client.get("/relationships/999").status_code == 404


def test_invalid_score_range_422(client):
    r = client.get("/relationships", params={"min_score": 80, "max_score": 20})
    assert r.status_code == 422


def test_invalid_type_422(client):
    assert client.get("/relationships", params={"type": "subsidiary"}).status_code == 422


def test_invalid_page_422(client):
    assert client.get("/relationships", params={"page": 0}).status_code == 422


def test_graph_unknown_center_404(client):
    assert client.get("/graph", params={"center": "NoSuchCorp"}).status_code == 404
