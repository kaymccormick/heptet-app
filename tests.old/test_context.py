from heptet_app.context import FormContextMixin


def test_formcontextmixin():
    class A(FormContextMixin):
        pass
    a = A()
    r = repr(a)
