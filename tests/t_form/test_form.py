from email_mgmt_app.form import Form


def test_form_1(root_namespace_store):
    f = Form('test', root_namespace_store, None, True, {})
    form_html = f.as_html()
    assert 0, form_html


def test_form_2(root_namespace_store):
    f = Form()
    form_html = f.as_html()
    assert 0, form_html


def test_form_3(root_namespace_store):
    f = Form()
    