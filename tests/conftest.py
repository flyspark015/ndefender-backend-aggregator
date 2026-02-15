import sys
from pathlib import Path

import pytest

from ndefender_backend_aggregator import config as config_module

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture(autouse=True)
def _reset_config_cache():
    config_module.get_config.cache_clear()
    yield
    config_module.get_config.cache_clear()
