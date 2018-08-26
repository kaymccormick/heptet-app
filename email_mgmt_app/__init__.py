import logging
import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, NewRequest
from pyramid.renderers import get_renderer
from pyramid.request import Request

from email_mgmt_app.predicate import EntityTypePredicate
from email_mgmt_app.registry import AppSubRegistry
from email_mgmt_app.res import Resource, RootResource, ResourceManager
from email_mgmt_app.root import RootFactory
from email_mgmt_app.security import groupfinder
from email_mgmt_app.util import munge_dict
from jinja2.exceptions import TemplateNotFound

def on_new_request(event):
    pass

def set_renderer(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription
    :param event: the event
    :return:
    """
    request = event.request # type: Request
    context = request.context # type: Resource
    if context.entity_type:
        # sets incorrect template
        def try_template(template_name):
            try:
                logging.debug("trying template %s", template_name)
                get_renderer(template_name).template_loader().render({})
                return True
            except TemplateNotFound as ex:
                return False

        renderer = "templates/%s/%s.jinja2" % (context.entity_type.__name__.lower(),
                                               request.view_name.lower())

        if not try_template(renderer):
            renderer = "templates/entity/%s.jinja2" % request.view_name.lower()

        logging.debug("selecting %s for %s", renderer, request.path_info)

        request.override_renderer = renderer
        return True


def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'pidfile' in settings.keys():
        f = open(settings['pidfile'], 'w')
        f.write("%d" % os.getpid())
        f.close()

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include('.viewderiver')

#    config.add_view_predicate('entity_name', EntityNamePredicate)
    config.add_view_predicate('entity_type', EntityTypePredicate)

    config.registry.email_mgmt_app = AppSubRegistry()
    config.include('pyramid_jinja2')
    config.include('.events')
    config.commit()

    def _munge_view(request):
        resp = request.wrapped_response
        return munge_dict(request, resp)

    config.add_view(_munge_view, '_munge_view')

    # should this be in another spot!?
    config.registry.email_mgmt_app_resources = \
        RootResource({}, ResourceManager(config, name='', title='', node_name=''))

    config.include('.res')


    config.include('.exceptions')
    config.include('.entity.model.email_mgmt')

    # we commit here prior to including .db since I dont know how to order config
    config.commit()

    from email_mgmt_app.templates.entity.field import Template
    t = Template()

    config.include('.templates.entity.field')

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

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)
    config.add_subscriber(set_renderer, ContextFound)
    config.add_subscriber(on_new_request, NewRequest)
    config.commit()

    config.registry['email_mgmt_app_resources'] = None

    # THIS MAY BE AGAINST PYRAMID PATTERNS
    RootFactory.populate_resources(config)

    return config.make_wsgi_app()
