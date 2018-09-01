import os

from pyramid_ldap3 import groupfinder

from email_mgmt_app import set_renderer, on_before_render, on_new_request, on_application_created
from email_mgmt_app.predicate import EntityTypePredicate
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from email_mgmt_app.registry import AppSubRegistry
from email_mgmt_app.root import RootFactory
from email_mgmt_app.res import RootResource, ResourceManager


def wsgi_app(global_config, **settings):
    """
    The main functionf or our pyramid application.
    :param global_config:
    :param settings:
    :return: A WSGI application.
    """
    if 'pidfile' in settings.keys():
        f = open(settings['pidfile'], 'w')
        f.write("%d" % os.getpid())
        f.close()

    config = Configurator(settings=settings, root_factory=RootFactory)
                          #exceptionresponse_view=ExceptionView)#lambda x,y: Response(str(x), content_type="text/plain"))
    config.registry.email_mgmt_app = AppSubRegistry()

    config.include('pyramid_jinja2')
    config.commit()

    RootFactory.resources = config.registry.email_mgmt_app.resources
    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)

    # order matters here
    config.include('.viewderiver')

#    config.add_view_predicate('entity_name', EntityNamePredicate)
    # does this need to be in a particular spot?
    config.add_view_predicate('entity_type', EntityTypePredicate)

    # this is required to collect the list
    # of mappers
    config.include('.events')
    config.commit()

    # test remove
    #alchemy = load_alchemy_json(config)

    # should this be in another spot!?
    # this is confusing because resourcemanager
    config.registry.email_mgmt_app.resources = \
        RootResource({}, ResourceManager(config, title='', node_name=''))

    config.include('.page')
    config.commit()

    config.include('.view')
    config.commit()

    config.include('.entity.model.email_mgmt')
    config.commit()
    config.include('.res')


    # we commit here prior to including .db since I dont know how to order config
    config.commit()

#    config.include('.templates.entity.field')
    config.include('.db')
    config.commit()

    # now static routes only
    config.include('.routes')
    config.include('.auth')
    config.include('.views')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['email_mgmt_app.secret'],
                                    callback=groupfinder)
    )
    config.set_authorization_policy(
       ACLAuthorizationPolicy()
    )

    config.add_subscriber(set_renderer, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_application_created, ApplicationCreated)
    config.commit()

    # THIS MAY BE AGAINST PYRAMID PATTERNS
    # not to mention my patterns  - all this does is :
    # RootFactory.resources = config.registry.email_mgmt_app.resources
    RootFactory.populate_resources(config)

    return config.make_wsgi_app()