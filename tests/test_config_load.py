from ndefender_backend_aggregator.config import get_config


def test_default_config_loads():
    config = get_config()
    assert config.system_controller.base_url.startswith("http")
    assert "Content-Type" in config.cors.allow_headers
    assert config.features.enable_remoteid is True
