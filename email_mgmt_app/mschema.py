from db_dump.fields import TypeField
from marshmallow import Schema, fields


class NamespaceSchema(Schema):
    namespace = fields.Dict(keys=fields.String(), values=fields.Nested('NamespaceSchema'))


class EntryPointSchema(Schema):
    key = fields.String()
    view_kwargs = fields.Dict()
    view = TypeField()
