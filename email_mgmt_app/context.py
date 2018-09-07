from __future__ import annotations
from zope.interface import implementer

from interfaces import IFormContext, IGeneratorContext
from form import Form
from impl import NamespaceStore


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


@implementer(IGeneratorContext)
class GeneratorContext(ContextMapperInfoMixin, ContextTemplateEnvMixin, ContextTemplateVarsMixin):
    def __init__(self, mapper_info, template_env, template_vars) -> None:
        super().__init__()
        self.mapper_info = mapper_info
        self.template_env = template_env
        self.template_vars = template_vars


@implementer(IFormContext)
class FormContext(ContextGeneratorContextMixin):
    def __init__(self, generator_context, root_namespace, nest_level: int = 0,
                 do_modal: bool = False, form: Form = None, extra: dict = None,
                 namespace: NamespaceStore = None):
        self.root_namespace = root_namespace
        self.generator_context = generator_context
        self.nest_level = nest_level
        self.do_modal = do_modal
        self.form = form
        self.extra = extra
        self.namespace = namespace
