import logging
from typing import AnyStr

from heptet_app.interfaces import *
from heptet_app.myapp_config import TEMPLATE_ENV_NAME
from jinja2 import TemplateNotFound, BaseLoader
from pyramid.config import Configurator
from pyramid.renderers import RendererHelper
from zope.component import adapter
from zope.interface import implementer
from zope.interface.registry import Components

logger = logging.getLogger(__name__)

class ComponentLoader(BaseLoader):
    def __init__(self, registry) -> None:
        self._registry = registry

    def get_source(self, environment, template):
        return super().get_source(environment, template)


@adapter(ITemplateVariable)
@implementer(ICollector)
class VariableCollector:
    def __init__(self, template_variable) -> None:
        self._variable = template_variable
        self._str = str

    def add_value(self, value):
        self._variable.get_value().append(value)

    def get_variable(self):
        return self._variable

    def get_value(self):
        return self._variable.get_value()


@implementer(ITemplateSource)
class FileTemplateSource:
    def __init__(self, env, name, renderer=None) -> None:
        self._env = env
        self._name = name
        self._renderer = renderer

    def get_name(self):
        return self._name

    def render(self, **kwargs):
        try:
            return self._env.get_template(self._name).render(**kwargs)
        except TemplateNotFound as ex:
            logger.debug("template not found: %s", ex)
            return None


@adapter(ITemplateSource)
@implementer(ITemplate)
class Template:
    def __init__(self, source) -> None:
        self._source = source

    def get_name(self):
        return self._source.get_name()

    def render(self, **kwargs):
        return self._source.render(**kwargs)

    def __str__(self):
        return "Template<%s>" % self.get_name()


@implementer(ITemplateVariable)
class TemplateVariable:
    def __init__(self, name, value=None) -> None:
        self._name = name
        self._value = value

    def get_name(self):
        return self._name

    def get_value(self):
        #        logger.debug("in get_value for %s %s", self._name, self)
        return self._value


class TemplateManager:
    def __init__(self, config: Configurator) -> None:
        self._config = config
        self._rs = {}

    def add_template(self, path: AnyStr):
        logging.debug("path = %s", path)
        self._rs[path] = RendererHelper(name=path,
                                        package='heptet_app',
                                        registry=self._config.registry)
        logging.debug("renderer = %s", self._rs[path])


def _templates(config, env):
    # templates = FileSystemLoader.list_templates(env.loader)
    # for filename in templates:
    #     source = FileTemplateSource(env, filename)
    #     logger.debug("registering filename %s", filename)
    #     config.registry.registerUtility(source, ITemplateSource, filename)
    # for filename in glob.iglob('/foobar/*.asm'):
    #     FileTemplateSource()
    #     print('/foobar/%s' % filename)
    pass


def register_components(components: Components):
    components.registerAdapter(Template, [ITemplateSource], ITemplate)
    components.registerAdapter(VariableCollector, [ITemplateVariable], ICollector)


def includeme(config: Configurator):
    config.include('pyramid_jinja2')
    # intr = config.introspectable('heptet_app',
    #                              TEMPLATE_ENV_NAME,
    #                              'template-env renderer',
    #                              'template renderer')

#    logger.critical("inclusion of template")
    config.add_jinja2_renderer(TEMPLATE_ENV_NAME, settings_prefix='jinja2.')

    # config.action(('heptet_app', 'template-env'), do_action, introspectables=(intr,), order=PHASE0_CONFIG)
