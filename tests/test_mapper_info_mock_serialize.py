from db_dump import MapperSchema


def test_mapper_info_mock_serialize_1(mapper_info_mock):
    schema = MapperSchema()
    data = schema.dump(mapper_info_mock)
    #i = schema.load(data)
    print(repr(data))

