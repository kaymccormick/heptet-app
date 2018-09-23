import sys

from email_mgmt_app.form import FormSelect, FormOptionElement


def test_formselect_init():
    options = [FormOptionElement("test1", "xyz")]
    select = FormSelect('test1', 'test1', options)
    print(select.as_html(), file=sys.stderr)
