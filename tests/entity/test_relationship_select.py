import sys




def test_(my_relationship_select):
    s = my_relationship_select
    x = s.gen_select_html()
    print(x, file=sys.stderr)