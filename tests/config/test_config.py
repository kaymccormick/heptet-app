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
from impl import MapperWrapper, NamespaceStore
from interfaces import IMapperInfo, INamespaceStore
from myapp_config import load_process_struct, config_process_struct
from root import RootFactory
from webapp_main import on_context_found, on_before_render, on_new_request, on_application_created


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
            settings=settings, root_factory=RootFactory(),
            package=email_mgmt_app.myapp_config
        )
        config.include(email_mgmt_app)
        config.include(myapp_config)

        # # I wish we could do away this is
        # jinja2_loader_template_path = settings['email_mgmt_app.jinja2_loader_template_path'].split(':')
        # env = Environment(loader=FileSystemLoader(jinja2_loader_template_path),
        #                   autoescape=select_autoescape(default=False))
        # config.registry.registerUtility(env, IJinja2Environment, 'app_env')

        # exceptionresponse_view=ExceptionView)#lambda x,y: Response(str(x), content_type="text/plain"))

        config.include(model_package)
        process = load_process_struct()  # type: ProcessStruct
        for mapper in process.mappers:
            wrapper = MapperWrapper(mapper)
            config.registry.registerUtility(wrapper, IMapperInfo, mapper.local_table.key)

        # we can include viewderiver here because we haven't created all of our views yet
        # view derivers mut be included prior to view registration ?
        config.include('.viewderiver')
        # we no longer need a custom predicate!
        # config.add_view_predicate('entity_type', EntityTypePredicate)
        config.include('.entity')
        # this adds all our views, and other stuff
        config_process_struct(config, process)

        config.include('pyramid_jinja2')
        config.commit()

        renderer_pkg = 'pyramid_jinja2.renderer_factory'
        config.add_renderer(None, renderer_pkg)

        #    config.add_view_predicate('entity_name', EntityNamePredicate)

        config.include('.view')

        # now static routes only
        config.include('.routes')
        #    config.include('.auth')
        config.include('.views')
        config.include('.template')
        config.include('.process')

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
    settings['model_package'] = '.model.email_mgmt'
    app = make_wsgi_app({}, **settings)
