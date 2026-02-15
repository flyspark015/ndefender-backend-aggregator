from fastapi.testclient import TestClient

from ndefender_backend_aggregator.config import get_config
from ndefender_backend_aggregator.main import create_app

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401


def test_health_requires_api_key():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == HTTP_UNAUTHORIZED


def test_health_with_api_key():
    config = get_config()
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/health",
        headers={"X-API-Key": config.auth.api_key, "X-Role": "viewer"},
    )
    assert response.status_code == HTTP_OK


def test_status_snapshot():
    config = get_config()
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/status",
        headers={"X-API-Key": config.auth.api_key, "X-Role": "viewer"},
    )
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert "timestamp_ms" in payload


def test_network_endpoint():
    config = get_config()
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/network",
        headers={"X-API-Key": config.auth.api_key, "X-Role": "viewer"},
    )
    assert response.status_code == HTTP_OK


def test_audio_endpoint():
    config = get_config()
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/audio",
        headers={"X-API-Key": config.auth.api_key, "X-Role": "viewer"},
    )
    assert response.status_code == HTTP_OK


def test_command_endpoint_returns_result():
    config = get_config()
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/vrx/tune",
        headers={"X-API-Key": config.auth.api_key, "X-Role": "operator"},
        json={"payload": {"vrx_id": 1, "freq_hz": 5740000000}},
    )
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["command"] == "SET_VRX_FREQ"
