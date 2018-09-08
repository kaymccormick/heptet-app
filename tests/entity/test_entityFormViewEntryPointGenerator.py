def test_generate(entity_form_view_entry_point_generator):
    entity_form_view_entry_point_generator.generate()
    entry_point = entity_form_view_entry_point_generator.entry_point
    assert entry_point.vars
    assert entity_form_view_entry_point_generator

