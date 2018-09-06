from email_mgmt_app.res import EntityResource, Resource


class EntityNamePredicate():

    def __init__(self, val, config) -> None:
        self._val = val
        self._config = config

    def text(self):
        return 'entity_name = %s' % (self._val)

    phash = text

    def __call__(self, context, request):
        if isinstance(context, EntityResource) and context.entity_name == self._val:
            return True
        return False


class EntityTypePredicate():
    def __init__(self, val, config) -> None:
        self._val = val
        self._config = config

    def text(self):
        return 'entity_type = %s' % (repr(self._val))

    phash = text

    def __call__(self, context, request):
        if context.entity_type is None:
            return False
        if isinstance(context, Resource) and issubclass(context.entity_type, self._val):
            return True
        return False
