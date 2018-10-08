import sys
from unittest.mock import PropertyMock


def test_(
        my_relationship_select,
        my_form_context,
        my_relationship_info,
        make_form_context,
        make_generator_context,
        make_entry_point,
        resource_manager_mock,
        mock_relationship_info,
        form_context_mock
):
    manager = resource_manager_mock
    key = 'key1'

    entry_point = make_entry_point(manager, key)
    make_generator_context(entry_point)
    s = my_relationship_select
    my_form_context.current_element = mock_relationship_info#my_relationship_info
    # should we be using a mock here??
    fm = form_context_mock
    type(fm).current_element = PropertyMock(return_value=mock_relationship_info)
    x = s.gen_select_html(fm)
    print(x, file=sys.stderr)
