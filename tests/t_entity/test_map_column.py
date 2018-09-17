import sys

from email_mgmt_app.entity import _map_column


def test_map_column(my_form_context, my_column_info):
    x = _map_column(my_form_context, my_column_info)
    print(x, file=sys.stderr)

# def test_map_column()
