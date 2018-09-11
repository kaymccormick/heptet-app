from __future__ import annotations

import copy
import logging
from typing import Sequence, Generic, TypeVar, Callable, Any

from jinja2 import Environment
from pyramid.path import DottedNameResolver
from zope.interface import implementer

from db_dump.info import MapperInfo
from form import Form
from impl import NamespaceStore
from interfaces import IFormContext, IGeneratorContext
from tvars import TemplateVars

TemplateEnvironment = Environment
logger = logging.getLogger(__name__)


class MixinBase:
    def check_instance(self):
        pass


T = TypeVar('T')


class EntityTypeMixin(Generic[T], MixinBase):
    def __init__(self) -> None:
        super().__init__()
        self._entity_type = None  # type: T

    @property
    def entity_type(self) -> T:
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new: T) -> None:
        self._entity_type = new


class ContextFormContextMixin(MixinBase):
    def __init__(self):
        super().__init__()
        self._form_context = None  # type: FormContext

    @property
    def form_context(self) -> FormContext:
        return self._form_context

    @form_context.setter
    def form_context(self, new: FormContext) -> None:
        self._form_context = new

    def __repr__(self):
        return self.form_context.__repr__()

    def check_instance(self):
        super().check_instance()
        assert self.form_context


class GeneratorContextMixin(MixinBase):
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

    def check_instance(self):
        super().check_instance()
        assert self.generator_context


class TemplateVarsMixin(MixinBase):
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

    def check_instance(self):
        super().check_instance()
        assert self._template_vars is not None


class ContextMapperInfoMixin(MixinBase):
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

    def check_instance(self):
        super().check_instance()
        assert self.mapper_info


class TemplateEnvMixin(MixinBase):

    def __init__(self) -> None:
        super().__init__()
        self._template_env = None

    @property
    def template_env(self):
        return self._template_env

    @template_env.setter
    def template_env(self, new):
        self._template_env = new

    def __repr__(self):
        return self._template_env.__repr__()

    def check_instance(self):
        super().check_instance()
        assert self.template_env


class FormContextFactoryMixin(MixinBase):
    def __init__(self) -> None:
        super().__init__()
        self._form_context_factory = None  # type: FormContextFactory

    @property
    def form_context_factory(self) -> FormContextFactory:
        return self._form_context_factory

    @form_context_factory.setter
    def form_context_factory(self, new: FormContextFactory):
        self._form_context_factory = new

    def check_instance(self):
        super().check_instance()
        assert self.form_context_factory


class ContextRootNamespaceMixin(MixinBase):

    def __init__(self) -> None:
        super().__init__()
        self._root_namespace = None  # type: NamespaceStore

    @property
    def root_namespace(self) -> NamespaceStore:
        return self._root_namespace

    @root_namespace.setter
    def root_namespace(self, new: NamespaceStore) -> None:
        self._root_namespace = new

    def check_instance(self):
        super().check_instance()
        assert self.root_namespace


# our generator context shouldn't have all of this knowledge of the form stuff!

@implementer(IGeneratorContext)
class GeneratorContext(
    ContextMapperInfoMixin,
    TemplateEnvMixin,
    TemplateVarsMixin,
    FormContextFactoryMixin,
    ContextRootNamespaceMixin,
):
    def __init__(self, mapper_info, template_env, template_vars, form_context_factory: FormContextFactory,
                 root_namespace: NamespaceStore) -> None:
        super().__init__()
        if mapper_info is not None:
            assert isinstance(mapper_info, MapperInfo), "%s should be MapperInfo" % mapper_info

        #        assert isinstance(template_env, Environment)
        assert isinstance(template_vars, TemplateVars), "%s should be TemplateVars, is %s" % (template_vars, type(template_vars))
        self.mapper_info = mapper_info
        self.template_env = template_env
        self.template_vars = template_vars
        self.form_context_factory = form_context_factory
        self.root_namespace = root_namespace
        assert form_context_factory

    def form_context(self, **kwargs):
        form_context = self.form_context_factory(**dict(generator_context=self, template_env=self.template_env,
                                                        template_vars=self.template_vars,
                                                        root_namespace=self.root_namespace,
                                                        form_context_factory=self.form_context_factory, **kwargs))
        form_context.check_instance()
        return form_context

    def __repr__(self):
        return "GeneratorContext("
        x = []
        for b in self.__class__.__bases__:
            x.append(b.__repr__(self))

        return self.__class__.__name__ + '/' + '/'.join(x)


FormContextArgs = ()

FormContextFactory = Callable[[GeneratorContext,
                               TemplateEnvironment,
                               NamespaceStore, NamespaceStore, 'FormContextFactory',
                               Form, int, bool, Sequence, dict], 'FormContext']

T = TypeVar('T')


class DottedNameResolverMixin:
    def __init__(self) -> None:
        super().__init__()
        self._resolver = None  # type: DottedNameResolver

    @property
    def resolver(self) -> DottedNameResolver:
        return self._resolver

    @resolver.setter
    def resolver(self, new: DottedNameResolver) -> None:
        self._resolver = new


class CurrentElementMixin(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._current_element = None

    @property
    def current_element(self) -> T:
        return self._current_element

    @current_element.setter
    def current_element(self, new: T) -> None:
        self._current_element = new


class ContextFactoryMixin:
    def __init__(self) -> None:
        super().__init__()
        self._factory = None

    @property
    def factory(self):
        return self._factory

    @factory.setter
    def factory(self, new):
        self._factory = new


class FieldMapper(object):
    pass


RelationshipFieldMapper = Any


class RelationshipFieldMapperMixin(MixinBase):

    def __init__(self) -> None:
        super().__init__()
        self._relationship_field_mapper = None  # type: RelationshipFieldMappper

    @property
    def relationship_field_mapper(self) -> RelationshipFieldMapper:
        return self._relationship_field_mapper

    @relationship_field_mapper.setter
    def relationship_field_mapper(self, new: RelationshipFieldMapper):
        self._relationship_field_mapper = new

    def check_instance(self):
        super().check_instance()
        assert self.relationship_field_mapper, "No relationship field mapper."


# we neeed a "builder" or whatever that becomes
# FormRepresentationBuilder - I suppose it does buil!
# we need a "collection' of field mappers

@implementer(IFormContext)
class FormContext(
    GeneratorContextMixin,
    TemplateEnvMixin,
    TemplateVarsMixin,
    CurrentElementMixin,
    FormContextFactoryMixin,
    RelationshipFieldMapperMixin,
    DottedNameResolverMixin,
):
    def __init__(
            self,
            generator_context: GeneratorContext,
            template_env: TemplateEnvironment,
            template_vars: TemplateVars,
            root_namespace: NamespaceStore,
            namespace: NamespaceStore = None,
            form_context_factory=None,
            relationship_field_mapper: FieldMapper = None,
            resolver: DottedNameResolver = None,
            form: Form = None,
            nest_level: int = 0,
            do_modal: bool = False,
            builders: Sequence = None,
            extra: dict = None,
    ):
        super().__init__()
        if extra is None:
            extra = {}
        self.generator_context = generator_context
        self.template_env = template_env
        self.root_namespace = root_namespace
        self.namespace = namespace
        if form_context_factory is None:
            form_context_factory = FormContext
        self.form_context_factory = form_context_factory
        self.resolver = resolver
        self.form = form
        self.nest_level = nest_level
        self.do_modal = do_modal
        self.builders = builders
        self.extra = extra
        self.template_vars = template_vars
        self.relationship_field_mapper = relationship_field_mapper

    def check_instance(self):
        super().check_instance()

    def __repr__(self):
        x = []
        for b in self.__class__.__bases__:
            x.append(b.__repr__(self))

        return self.__class__.__name__ + '/' + '/'.join(x)

    def copy(self, nest: bool = False, dup_extra: bool = False):
        new = self.form_context_factory(generator_context=self.generator_context,
                                        template_env=self.template_env,
                                        template_vars=self.template_vars,
                                        root_namespace=self.root_namespace,
                                        namespace=None,
                                        form_context_factory=self.form_context_factory,
                                        form=self.form,
                                        nest_level=bool and self.nest_level + 1 or self.nest_level,
                                        do_modal=self.do_modal,
                                        builders=self.builders,
                                        relationship_field_mapper=self.relationship_field_mapper,
                                        extra=nest and dict() or dup_extra and copy.deepcopy(self.extra) or self.extra)
        return new
