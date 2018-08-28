import logging

logger = logging.getLogger(__name__)

def view_decorator(view_callable):
    def decorator(context, request):
        try:
            result = view_callable(context, request)
            logger.debug("decorator result = %s", repr(result))
        except Exception as ex:
            logger.critical("view_callable raised exception! %s", ex)
            raise(ex)


        return result

    return decorator