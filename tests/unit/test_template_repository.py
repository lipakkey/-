from core.text.template_repository import TemplateRepository


def test_template_repository_loads_default_template():
    repo = TemplateRepository()
    tpl = repo.get("tee")
    assert "克罗" in tpl.title or tpl.title
    assert tpl.body
