from __future__ import annotations

import logging
import textwrap

from zope.interface import implementer

from email_mgmt_app.interfaces import IFormContext, IGeneratorContext
from email_mgmt_app.form import Form
from email_mgmt_app.impl import NamespaceStore

logger = logging.getLogger(__name__)


class ContextGeneratorContextMixin:

    def __init__(self) -> None:
        super().__init__()
        self._generator_context = None

    @property
    def generator_context(self) -> GeneratorContext:
        return self._generator_context

    @generator_context.setter
    def generator_context(self, new):
        self._generator_context = new

    def __repr__(self):
        return self._generator_context.__repr__()


class ContextTemplateVarsMixin:
    def __init__(self) -> None:
        super().__init__()
        self._template_vars = None

    @property
    def template_vars(self):
        return self._template_vars

    @template_vars.setter
    def template_vars(self, new):
        self._template_vars = new

    def __repr__(self):
        return self._template_vars.__repr__()


class ContextMapperInfoMixin:
    def __init__(self) -> None:
        super().__init__()
        self._mapper_info = None

    @property
    def mapper_info(self):
        return self._mapper_info

    @mapper_info.setter
    def mapper_info(self, new):
        self._mapper_info = new

    def __repr__(self):
        return self._mapper_info.__repr__()


class ContextTemplateEnvMixin:

    def __init__(self) -> None:
        super().__init__()
        self._template_env = None

    @property
    def template_env(self):
        return self._template_env

    @template_env.setter
    def template_env(self, new):
        return self._template_env

    def __repr__(self):
        return self._template_env.__repr__()


@implementer(IGeneratorContext)
class GeneratorContext(ContextMapperInfoMixin, ContextTemplateEnvMixin, ContextTemplateVarsMixin):
    def __init__(self, mapper_info, template_env, template_vars) -> None:
        super().__init__()
        self.mapper_info = mapper_info
        self.template_env = template_env
        self.template_vars = template_vars

    def __repr__(self):
        x = []
        for b in self.__class__.__bases__:
            x.append(b.__repr__(self))

        return self.__class__.__name__ + '/' + '/'.join(x)


@implementer(IFormContext)
class FormContext(ContextGeneratorContextMixin, ContextTemplateEnvMixin, ContextTemplateVarsMixin):
    def __init__(self, generator_context: GeneratorContext, template_env, root_namespace: NamespaceStore,
                 nest_level: int = 0,
                 do_modal: bool = False, form: Form = None, extra: dict = None,
                 namespace: NamespaceStore = None):
        super().__init__()
        self.root_namespace = root_namespace
        self.template_env = template_env
        self.generator_context = generator_context
        self.template_vars = generator_context.template_vars
        self.nest_level = nest_level
        self.do_modal = do_modal
        self.form = form
        self.extra = extra
        self.namespace = namespace

    def __repr__(self):
        x = []
        for b in self.__class__.__bases__:
            x.append(b.__repr__(self))

        return self.__class__.__name__ + '/' + '/'.join(x)