from typing import Callable, AnyStr

from email_mgmt_app import ResourceManager, EntryPoint
from email_mgmt_app.impl import MapperWrapper

MakeEntryPoint = Callable[[ResourceManager, AnyStr, object, MapperWrapper], EntryPoint]

