from __future__ import annotations

from typing import Mapping, AnyStr, Tuple
from unittest.mock import MagicMock, call


import pytest
from db_dump.info import RelationshipInfo

from entity import FormRelationshipMapper, TemplateVars
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



@pytest.fixture()
def vars_mapping():
    return _vars_mapping


def test_vars_mapping(vars_mapping):
    logger.critical("%s", vars_mapping)


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
def form_relationship_mapper(relationship_info, make_form_context, my_gen_context, root_namespace_store):
    form_context = make_form_context(my_gen_context, root_namespace_store)
    return FormRelationshipMapper(relationship_info, form_context)


@pytest.fixture
def make_form_relationship_mapper():
    def _make_form_relationship_mapper(relationship_info, form_context, relationship_select):
        return FormRelationshipMapper(relationship_info, form_context, relationship_select)

    return _make_form_relationship_mapper


@pytest.fixture
def my_form_relationship_mapper(make_form_relationship_mapper,
                                my_relationship_info,
                                my_form_context,
                                my_relationship_select):
    return make_form_relationship_mapper(my_relationship_info, my_form_context, my_relationship_select)




def test_map_relationship(my_form_context, my_form_relationship_mapper, jinja2_env):
    fm = my_form_context
    fm.extra['suppress_cols'] = {}
    logger.critical("%s", repr(fm))
    t = my_form_relationship_mapper
    r = t.map_relationship()
    input = r['input_html']

    jinja2_env.assert_has_calls([call.get_template('entity/rel_select.jinja2'),
                                 call.get_template('entity/field_relationship.jinja2'),
                                 ])

    assert input
    select_html = input['select_html']
    assert select_html

    logger.critical("%s", r)
    assert 0

    pass
