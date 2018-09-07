from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, AnyStr, Tuple, MutableSequence
from unittest.mock import MagicMock

import pytest
from db_dump.info import RelationshipInfo

from email_mgmt_app.entity import FormRelationshipMapper, TemplateVars
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
    assert 0

@pytest.fixture
def relationship_info():
    mock = MagicMock('relationship_info')
    mock.mock_add_spec(RelationshipInfo())
    return mock


@pytest.fixture
def form_relationship_mapper(relationship_info, form_context):
    return FormRelationshipMapper(relationship_info, form_context)


def test_map_relationship(form_relationship_mapper):
    t = form_relationship_mapper
    r = t.map_relationship()

    pass
