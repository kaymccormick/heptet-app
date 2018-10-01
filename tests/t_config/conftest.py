
import pytest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from pyramid_ldap3 import groupfinder

import heptet_app
from heptet_app import myapp_config
from heptet_app import get_root
from heptet_app.impl import NamespaceStore
from heptet_app.interfaces import INamespaceStore
from heptet_app.myapp_config import on_context_found, on_before_render, on_new_request, on_application_created


@pytest.fixture
def make_wsgi_app():
    def _make_wsgi_app(global_config, model_package=None, **settings):
        """
        The main functionf or our pyramid application.
        :param global_config:
        :param settings:
        :return: A WSGI application.
        """
        config = Configurator(
            settings=settings,
            root_factory=get_root,
            package=heptet_app,
        )
        config.include(myapp_config)
        config.include(model_package)
        config.include('.process')

        renderer_pkg = 'pyramid_jinja2.renderer_factory'
        config.add_renderer(None, renderer_pkg)

        config.include('.routes')
        config.include('.viewderiver')

        config.set_authentication_policy(
            AuthTktAuthenticationPolicy(settings['heptet_app.secret'],
                                        callback=groupfinder)
        )
        config.set_authorization_policy(
            ACLAuthorizationPolicy()
        )

        config.add_subscriber(on_context_found, ContextFound)
        config.add_subscriber(on_before_render, BeforeRender)
        config.add_subscriber(on_new_request, NewRequest)
        config.add_subscriber(on_application_created, ApplicationCreated)

        config.registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
        config.registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
        return config.make_wsgi_app()

    return _make_wsgi_app
