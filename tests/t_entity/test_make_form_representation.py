import logging
import sys

import lxml
from email_mgmt_app.entity import MakeFormRepresentation, FormRelationshipMapper

logger = logging.getLogger(__name__)


def test_make_form_representation_1(make_form_context, monkeypatch_html,
                                    make_generator_context, make_entry_point, mapper_info_real,
                                    mapper_wrapper_mock, jinja2_env, element_mock):
    mapper_info = mapper_info_real
    entry_point = make_entry_point('test1', mapper=mapper_info)
    generator_context = make_generator_context(entry_point, env=jinja2_env)
    form_context = generator_context.form_context(relationship_field_mapper=FormRelationshipMapper, form_action="./")
    m = MakeFormRepresentation(form_context)
    form = m.make_form_representation()
    logger.critical("%r", type(form))
    logger.critical("%r", form.mock_calls)
    logger.critical("%r", form.element[0].mock_calls)

    print(form.as_html(), file=sys.stderr)



#
#
# def test_form_representation_parse(my_form_context):
#     form = _make_form_representation(my_form_context)
#     logger.critical("%r", form)
#     root = lxml.html.fromstring(form.as_html())
#     assert root
#     assert "Form" == root.get('data-pyclass')
