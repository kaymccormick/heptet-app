import copy

import pytest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from pyramid_ldap3 import groupfinder
from sqlalchemy.exc import InvalidRequestError

import email_mgmt_app.myapp_config
import myapp_config
from email_mgmt_app import get_root
from impl import MapperWrapper, NamespaceStore
from interfaces import IMapperInfo, INamespaceStore
from model import email_mgmt
from process import config_process_struct, load_process_struct
from myapp_config import on_new_request, on_application_created, on_before_render, on_context_found


# we need to keep this somewhat synchronized!
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
            settings=settings, root_factory=get_root,
            package=email_mgmt_app
        )
        config.include(myapp_config)
        config.include(model_package)
        config.include('.process')
        config.include('.routes')
        config.include('.template')
        renderer_pkg = 'pyramid_jinja2.renderer_factory'
        config.add_renderer(None, renderer_pkg)
        config.include('.viewderiver')
        config.commit()

        config.set_authentication_policy(
            AuthTktAuthenticationPolicy(settings['email_mgmt_app.secret'],
                                        callback=groupfinder)
        )
        config.set_authorization_policy(
            ACLAuthorizationPolicy()
        )

        config.add_subscriber(on_context_found, ContextFound)
        config.add_subscriber(on_before_render, BeforeRender)
        config.add_subscriber(on_new_request, NewRequest)
        config.add_subscriber(on_application_created, ApplicationCreated)
        config.commit()

        config.registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
        config.registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
        return config.make_wsgi_app()

    return _make_wsgi_app


# make_wsgi_app is a fixture, not our application!!
def test_my_config(make_wsgi_app, webapp_settings):
    settings = copy.copy(webapp_settings)
    settings['model_package'] = email_mgmt
    app = make_wsgi_app({}, **settings)
