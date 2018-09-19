import pytest
from email_mgmt_app.form import Form


def test_form_1(root_namespace_store):
    f = Form('test', root_namespace_store, None, True, {})
    form_html = f.as_html()


def test_form_2(root_namespace_store):
    with pytest.raises(TypeError):
        f = Form()
        form_html = f.as_html()

