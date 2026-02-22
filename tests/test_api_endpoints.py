from fastapi.testclient import TestClient

from ndefender_backend_aggregator.main import create_app

HTTP_OK = 200


def test_health_without_auth():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == HTTP_OK


def test_status_snapshot():
    client = TestClient(create_app())
    response = client.get("/api/v1/status")
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert "timestamp_ms" in payload


def test_network_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/network")
    assert response.status_code == HTTP_OK


def test_audio_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/audio")
    assert response.status_code == HTTP_OK


def test_command_endpoint_returns_result():
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/vrx/tune",
        json={"payload": {"vrx_id": 1, "freq_hz": 5740000000}},
    )
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["command"] == "SET_VRX_FREQ"
