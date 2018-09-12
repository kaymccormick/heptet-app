import importlib
import logging
import os
import sys

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_ldap3 import groupfinder
from zope.component import getGlobalSiteManager

from email_mgmt_app import get_root
from exceptions import InvalidMode
from impl import NamespaceStore
from interfaces import INamespaceStore

DEV_MODE = 'development'
PROD_MODE = 'production'
DEFAULT_MODE = PROD_MODE
VALID_MODES = (DEV_MODE, PROD_MODE)

logger = logging.getLogger(__name__)


def wsgi_app(global_config, **settings):
    """
    The main function or our pyramid application.
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

    config = Configurator(
        package="email_mgmt_app",
        registry=global_reg,
        settings=settings,
        root_factory=get_root)
    config.include('.myapp_config')
    if use_global_reg:
        config.setup_registry(settings=settings, root_factory=get_root)

    # we want to use the default template thingy if we can

    # include our sql alchemy model.
    pkg = 'email_mgmt_app.model.email_mgmt'
    pkg2 = 'model.email_mgmt'
    model_mod = None
    if pkg in sys.modules:
        model_mod = sys.modules[pkg]
    elif pkg2 in sys.modules:
        model_mod = sys.modules[pkg2]
    else:
        model_mod = importlib.import_module(pkg)
    config.include(model_mod)

    config.include('.process')

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)

    #    config.add_view_predicate('entity_name', EntityNamePredicate)

    config.include('.routes')
    config.include('.template')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['email_mgmt_app.secret'],
                                    callback=groupfinder)
    )
    config.set_authorization_policy(
        ACLAuthorizationPolicy()
    )

    config.registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
    config.registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
    return config.make_wsgi_app()
