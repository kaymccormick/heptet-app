import logging
import sys

import lxml
from email_mgmt_app.entity import MakeFormRepresentation

logger = logging.getLogger(__name__)


def test_make_form_representation_1(my_form_context):
    m = MakeFormRepresentation(my_form_context)
    form = m.make_form_representation()
    logger.critical("%r", type(form))
    logger.critical("%r", form)
    print(form.as_html(), file=sys.stderr)

#
#
# def test_form_representation_parse(my_form_context):
#     form = _make_form_representation(my_form_context)
#     logger.critical("%r", form)
#     root = lxml.html.fromstring(form.as_html())
#     assert root
#     assert "Form" == root.get('data-pyclass')
