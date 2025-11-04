from core.config.models import PriceConfig


def test_price_config_random_tail_deterministic():
    config = PriceConfig(base_yuan=200, random_tail=True, tail_candidates=(11, 22, 33))
    tails = [config.derive_price(seed=i) for i in range(3)]
    assert tails == [200.11, 200.22, 200.33]


def test_price_config_no_decimal():
    config = PriceConfig(base_yuan=199.9, keep_decimal=False, random_tail=False)
    assert config.derive_price() == 200
