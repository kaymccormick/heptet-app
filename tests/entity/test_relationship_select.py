import sys


def test_(my_relationship_select, my_form_context, my_relationship_info):
    s = my_relationship_select
    my_form_context.current_element = my_relationship_info
    x = s.gen_select_html(my_form_context)
    print(x, file=sys.stderr)
