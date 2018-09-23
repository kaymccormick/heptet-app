from impl import MapperWrapper


def test_mapperwrapper_init(mapper_info_mock):
    mapper_wrapper = MapperWrapper(mapper_info_mock)
    assert mapper_wrapper
    assert mapper_info_mock is mapper_wrapper.get_one_mapper_info()

    assert 0, mapper_wrapper.key