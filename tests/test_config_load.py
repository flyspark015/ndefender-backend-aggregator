from ndefender_backend_aggregator.config import get_config


def test_default_config_loads():
    config = get_config()
    assert config.system_controller.base_url.startswith("http")
    assert config.auth.api_key_required is True
    assert config.features.enable_remoteid is True
