import logging
import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, NewRequest, ApplicationCreated, BeforeRender
from pyramid.renderers import get_renderer
from pyramid.request import Request

from email_mgmt_app.adapter import AlchemyInfo
from email_mgmt_app.predicate import EntityTypePredicate
from email_mgmt_app.registry import AppSubRegistry
from email_mgmt_app.res import Resource, RootResource, ResourceManager
from email_mgmt_app.root import RootFactory
from email_mgmt_app.security import groupfinder
from email_mgmt_app.util import munge_dict
from jinja2.exceptions import TemplateNotFound


def on_new_request(event):
    pass


def on_application_created(event):
    pass

def on_before_render(event):
    val = event.rendering_val



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
            except:
                return True

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
    config.registry.email_mgmt_app = AppSubRegistry()

    config.include('pyramid_jinja2')
    config.commit()
    # order matters here
    config.include('.viewderiver')

#    config.add_view_predicate('entity_name', EntityNamePredicate)
    config.add_view_predicate('entity_type', EntityTypePredicate)

    config.include('.events')
    config.commit()

    alchemy = None
    try:
        with open('alchemy.json', 'r') as f:
            lines = f.readlines()
            s="\n".join(lines)
            alchemy = AlchemyInfo.from_json(s)
            f.close()
    except FileNotFoundError:
        pass
    except:
        raise
    assert alchemy

    logging.critical("a = %s", alchemy)
    config.registry.email_mgmt_app.alchemy = alchemy

    def _munge_view(request):
        resp = request.wrapped_response
        return munge_dict(request, resp)

    config.add_view(_munge_view, '_munge_view')

    # should this be in another spot!?
    config.registry.email_mgmt_app.resources = \
        RootResource({}, ResourceManager(config, name='', title='', node_name=''))

    config.include('.page')
    config.commit()

    config.include('.view')
    config.include('.res')

    config.include('.entity.model.email_mgmt')

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

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)
    config.add_subscriber(set_renderer, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_application_created, ApplicationCreated)
    config.commit()

    # THIS MAY BE AGAINST PYRAMID PATTERNS
    RootFactory.populate_resources(config)

    return config.make_wsgi_app()
