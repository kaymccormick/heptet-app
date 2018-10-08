from typing import Callable, AnyStr

from heptet_app import ResourceManager, EntryPoint
from heptet_app.impl import MapperWrapper

MakeEntryPoint = Callable[[ResourceManager, AnyStr, object, MapperWrapper], EntryPoint]

