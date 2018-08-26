from typing import AnyStr


class BaseTemplate:
    def __init__(self, template: AnyStr=None) -> None:
        if template is not None:
            self._template = template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, new):
        self._template = new


