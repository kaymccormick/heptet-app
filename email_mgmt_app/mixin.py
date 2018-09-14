from email_mgmt_app import EntryPoint


class EntryPointMixin:
    def __init__(self) -> None:
        super().__init__()
        self._entry_point = None  # type: EntryPoint

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @entry_point.setter
    def entry_point(self, new: EntryPoint):
        self._entry_point = new