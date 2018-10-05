import importlib
import logging
import os
import sys

from heptet_app import get_root
from heptet_app.exceptions import InvalidMode
from heptet_app.impl import NamespaceStore
from heptet_app.interfaces import INamespaceStore
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from zope.component import getGlobalSiteManager

DEV_MODE = 'development'
PROD_MODE = 'production'
DEFAULT_MODE = PROD_MODE
VALID_MODES = (DEV_MODE, PROD_MODE)

logger = logging.getLogger(__name__)


def wsgi_app(global_config, **settings):
    """
    WSGI application factory.
    :param global_config:
    :param settings:
    :return: A WSGI application.
    """
    mode = 'mode' in settings and settings['mode'] or DEFAULT_MODE
    if mode not in VALID_MODES:
        os.environ['APP_MODE'] = mode
        raise InvalidMode(mode, VALID_MODES)

    if 'pidfile' in settings.keys():
        f = open(settings['pidfile'], 'w')
        f.write("%d" % os.getpid())
        f.close()

    # we changed the root factory to an instance of our factory, which maybe would help??
    use_global_reg = False
    global_reg = None
    if use_global_reg:
        global_reg = getGlobalSiteManager()

    # validate settings
    config = Configurator(
        package="heptet_app",
        root_package="heptet_app",
        registry=global_reg,
        settings=settings,
        root_factory=get_root)
    config.include('.myapp_config')
    if use_global_reg:
        config.setup_registry(settings=settings, root_factory=get_root)

    # include our sql alchemy model.
    try:
        pkg = 'heptet_app.model.email_mgmt'
        pkg2 = 'model.email_mgmt'
        model_mod = None
        if pkg in sys.modules:
            model_mod = sys.modules[pkg]
        elif pkg2 in sys.modules:
            model_mod = sys.modules[pkg2]
        else:
            model_mod = importlib.import_module(pkg)
        config.include(model_mod)
    except Exception as ex:
        logger.warning(ex)

    # config.include('.viewderiver')
    # config.include('.process') fixme refactor
    config.include('.view')

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)

    config.include('.routes')

    # config.set_authentication_policy(
    #     AuthTktAuthenticationPolicy(settings['heptet_app.secret'],
    #                                 callback=groupfinder)
    # )
    # config.set_authorization_policy(
    #     ACLAuthorizationPolicy()
    # )

    config.registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
    config.registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
    return config.make_wsgi_app()


def __main__(argv):
    from waitress import serve
    from random import randint
    port = randint(1024, 65565)
    serve(wsgi_app({}, **{'sqlalchemy.url': 'sqlite:///:memory:'}), listen='127.0.0.1:%d' % port)


if __name__ == '__main__':
    exit(__main__(sys.argv))
