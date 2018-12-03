from marshmallow import Schema, fields


class EntryPointSchema(Schema):
    key = fields.String()
    fspath = fields.Function(lambda ep: ep.__fspath__())
    manager = fields.Nested("ResourceManagerSchema")
    content = fields.String()


class AssetManagerSchema(Schema):
    asset_content = fields.Dict()


class ResourceManagerSchema(Schema):
    mapper_key = fields.String()
    title = fields.String()
    # entity_type = TypeField()
    node_name = fields.String()
    pass


class ResourceSchema(Schema):
    # type = TypeField(attribute='__class__')
    manager = fields.Nested(ResourceManagerSchema)
    name = fields.String(attribute='__name__')  # function=lambda x: x.__name__)
    parent = fields.Nested('self', attribute='__parent__', only=[])  # functiona=lambda x: x.__parent__)
    data = fields.Dict(attribute='_data',
                       keys=fields.String(), values=fields.Nested('ResourceSchema'))
    url = fields.Url(function=lambda x: x.url())