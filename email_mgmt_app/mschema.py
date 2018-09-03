from db_dump.fields import TypeField
from marshmallow import Schema, fields


class EntryPointSchema(Schema):
    key = fields.String()
    view_kwargs = fields.Dict()
    view = TypeField()

