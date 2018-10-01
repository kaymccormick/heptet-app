from pyramid.config import Configurator

from templates import BaseTemplate


def apptemplate(template=None):
    def wrapper_apptemplate(typ):
        typ._template = template
        return typ

    return wrapper_apptemplate


@apptemplate(template="field.jinja2")
class Template(BaseTemplate):
    pass

def includeme(config: Configurator):
    t = Template()
    assert t.template == "field.jinja2"
    pass