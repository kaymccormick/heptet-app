from __future__ import annotations

import copy
import logging
from typing import Sequence, Generic, TypeVar, Callable, Any, AnyStr, Mapping

from email_mgmt_app import EntryPointMixin
from jinja2 import Environment
from pyramid.path import DottedNameResolver
from zope.interface import implementer

from email_mgmt_app.form import Form
from email_mgmt_app.impl import NamespaceStore, TemplateEnvMixin, MixinBase
from email_mgmt_app.interfaces import IFormContext, IGeneratorContext
from email_mgmt_app.tvars import TemplateVars

TemplateEnvironment = Environment
logger = logging.getLogger(__name__)

T = TypeVar('T')


class FormContextMixin(MixinBase):
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
    def template_vars(self) -> TemplateVars:
        return self._template_vars

    @template_vars.setter
    def template_vars(self, new: TemplateVars):
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
    TemplateEnvMixin,
    TemplateVarsMixin,
    FormContextFactoryMixin,
    ContextRootNamespaceMixin,
    EntryPointMixin,
):
    # adding options here doesnt necessarily make things any clearer

    def __init__(self, entry_point, template_vars, form_context_factory: FormContextFactory,
                 root_namespace: NamespaceStore, template_env=None, **kwargs) -> None:
        super().__init__()
        # if mapper_info is not None:
        #     assert isinstance(mapper_info, MapperInfo), "%s should be MapperInfo" % mapper_info

        #        assert isinstance(template_env, Environment)
        assert isinstance(template_vars, TemplateVars), "%s should be TemplateVars, is %s" % (
            template_vars, type(template_vars))

        self._entry_point = entry_point
        self.template_env = template_env
        self.template_vars = template_vars
        self.form_context_factory = form_context_factory
        self.root_namespace = root_namespace
        for k, v in kwargs.items():
            logger.critical("%r %r", k, v)
            setattr(self, k, v)

        assert form_context_factory

    def form_context(self, **kwargs):
        form_context = self.form_context_factory(**dict(generator_context=self, template_env=self.template_env,
                                                        template_vars=self.template_vars,
                                                        root_namespace=self.root_namespace,
                                                        form_context_factory=self.form_context_factory, **kwargs))
        form_context.check_instance()
        return form_context

    @property
    def options(self):
        return self._options

    def __repr__(self):
        return 'GeneratorContext(%r, %r, %r, %r)' % (
            self._template_env, self._template_vars, self.form_context_factory, self.root_namespace)


FormContextArgs = ()

# CODE SMELL FIXME
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
            form_action: AnyStr = None,
            extra: dict = None,
    ):
        super().__init__()
        if extra is None:
            extra = {'suppress_cols': {}}
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
        self.form_action = form_action

    def check_instance(self):
        super().check_instance()
        if self.form is None:
            # FIXME this i think is now happening all the time ?
            logger.warning("form is not set, might be a bug")

    def __repr__(self):
        x = []
        for b in self.__class__.__bases__:
            x.append(b.__repr__(self))

        return self.__class__.__name__ + '/' + '/'.join(x)

    def copy(self, nest: bool = False, dup_extra: bool = False):
        # this is crappy because we keep having to update this ....
        new = copy.copy(self)
        new.namespace = None
        if nest:
            new.nest_level = new.nest_level + 1
            new.extra = dict()
        elif dup_extra:
            new.extra = copy.deepcopy(self.extra)

        return new

        # new = self.form_context_factory(generator_context=self.generator_context,
        #                                 template_env=self.template_env,
        #                                 template_vars=self.template_vars,
        #                                 root_namespace=self.root_namespace,
        #                                 namespace=None,
        #                                 form_context_factory=self.form_context_factory,
        #                                 form=self.form,
        #                                 nest_level=bool and self.nest_level + 1 or self.nest_level,
        #                                 do_modal=self.do_modal,
        #                                 builders=self.builders,
        #                                 relationship_field_mapper=self.relationship_field_mapper,
        #                                 extra=nest and dict() or dup_extra and copy.deepcopy(self.extra) or self.extra)
        # return new
