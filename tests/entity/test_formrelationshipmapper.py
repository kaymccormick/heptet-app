from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, AnyStr, Tuple, MutableSequence
from unittest.mock import MagicMock

from entity import RelationshipSelect
from ..info.test_relationship_info import *

import pytest
from db_dump.info import RelationshipInfo

from email_mgmt_app.entity import FormRelationshipMapper, TemplateVars, FormRepresentationBuilder
from tvars import TemplateVar, StringTemplateVar, MutableSequenceTemplateVar, MappingTemplateVar

import logging

logger = logging.getLogger(__name__)

TemplateVarKey = AnyStr

VarMapping = Mapping[TemplateVarKey, TemplateVar]
VarsMapping = Mapping[AnyStr, Tuple[TemplateVars, VarMapping]]
# should allow us to specify a type
_vars_mapping = dict(rando=(TemplateVars(var1=StringTemplateVar(),
                                         var2=MutableSequenceTemplateVar([]),
                                         var3=MappingTemplateVar({}))))


@pytest.fixture
def form_representation_builder(form_context):
    return FormRepresentationBuilder(form_context)


@pytest.fixture()
def vars_mapping():
    return _vars_mapping


def test_vars_mapping(vars_mapping):
    logger.critical("%s", vars_mapping)
    assert 0


@pytest.fixture
def make_relationship_info():
    def _make_relationship_info(**kwargs):
        return RelationshipInfo(**kwargs)

    return _make_relationship_info


# @pytest.fixture
# def my_relationship_info(make_relationship_info):
#     return make_relationship_info()


@pytest.fixture
def mock_relationship_info():
    mock = MagicMock('relationship_info')
    mock.mock_add_spec(RelationshipInfo())
    return mock


@pytest.fixture
def my_template_vars(make_template_vars):
    return make_template_vars(js_imports=[], js_stmts=[], ready_stmts=[])


@pytest.fixture
def my_gen_context(make_generator_context, jinja2_env, mapper_info, my_template_vars):
    return make_generator_context(jinja2_env, mapper_info, my_template_vars)


@pytest.fixture
def form_relationship_mapper(relationship_info, make_form_context, my_gen_context, root_namespace_store):
    form_context = make_form_context(my_gen_context, root_namespace_store)
    return FormRelationshipMapper(relationship_info, form_context)


@pytest.fixture
def make_form_relationship_mapper():
    def _make_form_relationship_mapper(relationship_info, form_context, relationship_select):
        return FormRelationshipMapper(relationship_info, form_context, relationship_select)

    return _make_form_relationship_mapper


@pytest.fixture
def my_form_context(make_form_context, my_gen_context, root_namespace_store):
    return make_form_context(my_gen_context, root_namespace_store)


@pytest.fixture
def my_relationship_select(my_relationship_info):
    return RelationshipSelect(my_relationship_info)


@pytest.fixture
def my_form_relationship_mapper(make_form_relationship_mapper, my_relationship_info, my_form_context,
                                my_relationship_select):
    return make_form_relationship_mapper(my_relationship_info, my_form_context, my_relationship_select)


def test_map_relationship(my_form_context, my_form_relationship_mapper):
    fm = my_form_context
    logger.critical("%s", repr(fm))
    assert 0
    t = my_form_relationship_mapper
    r = t.map_relationship()

    pass
