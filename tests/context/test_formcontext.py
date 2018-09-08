def test_(my_form_context):
    x = my_form_context
    assert x.generator_context is not None
    assert x.template_vars is not None
    assert x.root_namespace is not None
    assert x.template_env is not None
    assert x.form is not None


