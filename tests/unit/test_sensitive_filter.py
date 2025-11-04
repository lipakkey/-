from core.config.models import SensitiveDictionary
from core.text.sensitive import SensitiveFilter


def test_sensitive_filter_replacement():
    dictionary = SensitiveDictionary(
        sensitive_words=("违禁",),
        brand_alias_mapping={"AMIRI": "克罗"},
    )
    filter_ = SensitiveFilter(dictionary)
    result = filter_.apply("AMIRI 违禁 描述")

    assert result.text == "克罗 ✂️ 描述"
    assert set(result.hits) == {"AMIRI", "违禁"}
