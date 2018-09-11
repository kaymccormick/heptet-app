def test_generate(entity_form_view_entry_point_generator):
    entity_form_view_entry_point_generator.generate()


def test_form_representation(entity_form_view_entry_point_generator):
    r = entity_form_view_entry_point_generator.form_representation()

