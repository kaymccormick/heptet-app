from typing import AnyStr

from sqlalchemy import Integer
from sqlalchemy.sql.type_api import TypeEngine


class AppType:
    def __init__(self, sqlalchemy_type: TypeEngine=None, input_type: AnyStr='text') -> None:
        super().__init__()
        self._sqlalchemy_type = sqlalchemy_type
        self._input_type = input_type

    @property
    def sqlalchemy_type(self):
        return self._sqlalchemy_type

    @property
    def input_type(self):
        return self._input_type


class Integer(AppType):
    def __init__(self, sqlalchemy_type: TypeEngine = Integer) -> None:
        super().__init__(sqlalchemy_type)
