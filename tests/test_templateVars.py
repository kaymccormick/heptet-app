from tvars import TemplateVars

import logging

logger = logging.getLogger(__name__)


def test_template_vars():
    template_vars = TemplateVars()
    template_vars['x'] = "hello"
    x = template_vars['x']
    assert template_vars['x'] == "hello"
    template_vars['y'] = {'hello': 'birdy'}
    assert template_vars['y']['hello'] == 'birdy'
    template_vars['y']['x'] = 'test'
    logger.critical("%s", template_vars['y'])
    template_vars['zz'] = []
    template_vars['zx'] = object()
    logger.critical("%s <%s>", template_vars['zz'], type(template_vars['zz']))
