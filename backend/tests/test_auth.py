from app import create_app


def test_health_endpoint():
    client = create_app(connect_database=False).test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["success"] is True