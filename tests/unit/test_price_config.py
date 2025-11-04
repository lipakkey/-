from core.config.models import PriceConfig


def test_price_config_random_tail_deterministic():
    cfg = PriceConfig(base_yuan=200, random_tail=True, tail_candidates=(11, 22, 33))
    tails = [cfg.derive_price(seed=i) for i in range(3)]
    assert tails == [200.11, 200.22, 200.33]


def test_price_config_wrapping_seed():
    cfg = PriceConfig(base_yuan=150, random_tail=True, tail_candidates=(5, 15))
    assert cfg.derive_price(seed=0) == 150.05
    assert cfg.derive_price(seed=2) == 150.15


def test_price_config_fixed_when_disabled():
    cfg = PriceConfig(base_yuan=180.99, random_tail=False)
    assert cfg.derive_price(seed=100) == 180.99
