from __future__ import annotations

import logging
from typing import Mapping, AnyStr, Tuple

import pytest
from lxml import html

from db_dump.info import RelationshipInfo
from heptet_app.entity import FormRelationshipMapper
from heptet_app.tvars import TemplateVar, StringTemplateVar, MutableSequenceTemplateVar, MappingTemplateVar, TemplateVars

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
def make_form_relationship_mapper():
    def _make_form_relationship_mapper(relationship_select):
        return FormRelationshipMapper(relationship_select)

    return _make_form_relationship_mapper


@pytest.fixture
def my_form_relationship_mapper(make_form_relationship_mapper,
                                my_relationship_select):
    return make_form_relationship_mapper(my_relationship_select)


@pytest.mark.integration
def test_map_relationship(make_form_context, my_form_relationship_mapper, jinja2_env, my_relationship_info, form_mock, mapper_info_real,
                          monkeypatch_html):
    form_context = make_form_context(template_env=jinja2_env, form=form_mock, mapper_info=mapper_info_real)
    fm = form_context
    # lame we have to initialize this here
    fm.extra['suppress_cols'] = {}
    logger.critical("%s", repr(fm))
    t = my_form_relationship_mapper
    form_context.current_element = my_relationship_info
    the_html = t.map_relationship(form_context)
#    root = html.fromstring(the_html)
    logger.critical("%s", the_html)

