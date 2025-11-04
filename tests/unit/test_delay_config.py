import pytest

from core.config.models import DelayConfig


def test_delay_config_validates_success():
    cfg = DelayConfig(micro_delay_ms=(100, 200), macro_delay_min=(5, 20))
    cfg.validate()


def test_delay_config_invalid_micro_bounds():
    cfg = DelayConfig(micro_delay_ms=(300, 100))
    with pytest.raises(ValueError):
        cfg.validate()


def test_delay_config_invalid_macro_bounds():
    cfg = DelayConfig(macro_delay_min=(20, 10))
    with pytest.raises(ValueError):
        cfg.validate()
