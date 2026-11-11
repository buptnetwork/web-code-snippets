"""JSON 接口：列表、详情、创建，以及 404／422／409 错误响应。"""

import pytest

from tests.helpers import make_payload


def test_list(client):
    response = client.get("/questions", params={"page_size": 1})
    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == 102
    assert response.json()["total"] == 2


def test_detail(client):
    assert client.get("/questions/101").json()["tags"] == ["python", "sql"]


@pytest.mark.parametrize("url", ["/questions/0", "/questions/-1", "/questions/999"])
def test_missing_question_is_404(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert response.json()["code"] == "question_not_found"


@pytest.mark.parametrize("url", ["/questions/not-an-int", "/questions?page=0", "/questions?page_size=51"])
def test_invalid_parameters_are_422(client, url):
    assert client.get(url).status_code == 422


def test_create_returns_201_and_location(client):
    body = make_payload("接口创建并回读的教学问题", ["python", "sql"]).model_dump()
    response = client.post("/questions", json=body)
    assert response.status_code == 201
    readback = client.get(response.headers["Location"])
    assert readback.status_code == 200 and readback.json() == response.json()
    assert client.post("/questions", json=body).status_code == 409  # 同一标题再次创建


def test_client_cannot_choose_author(client):
    body = {**make_payload("带作者字段的教学问题").model_dump(), "author_id": 1}
    assert client.post("/questions", json=body).status_code == 422
