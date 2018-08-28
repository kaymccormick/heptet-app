import json
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
from jinja2.exceptions import TemplateNotFound
from email_mgmt_app.view import ExceptionView
from pyramid.response import Response

logger = logging.getLogger(__name__)

def on_new_request(event):
    pass


def on_application_created(event):
    pass

def on_before_render(event):
    val = event.rendering_val
    logger.debug("VAL=%s", val)



# this function does too much

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
                logger.debug("trying template %s", template_name)
                get_renderer(template_name).template_loader().render({})
                return True
            except TemplateNotFound as ex:
                return False
            except:
                return True

        logger.debug("Type of entity_type is %s", type(context.entity_type))
        renderer = "templates/%s/%s.jinja2" % (context.entity_type.__name__.lower(),
                                               request.view_name.lower())

        if not try_template(renderer):
            renderer = None
            if request.view_name:
                renderer = "templates/entity/%s.jinja2" % request.view_name.lower()

        if renderer:
            logger.debug("selecting %s for %s", renderer, request.path_info)
            request.override_renderer = renderer
        return True


def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder


def load_alchemy_json(config):
    """

    :param config:
    :return:
    """
    alchemy = None
    try:
        with open('alchemy.json', 'r') as f:
            lines = f.readlines()
            s="\n".join(lines)
            alchemy = json.loads(s)
            #alchemy = AlchemyInfo.from_json(s)
            f.close()
    except FileNotFoundError:
        pass
    except:
        raise
    assert alchemy

    config.registry.email_mgmt_app.alchemy = alchemy
    return alchemy



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
                          #exceptionresponse_view=ExceptionView)#lambda x,y: Response(str(x), content_type="text/plain"))
    config.registry.email_mgmt_app = AppSubRegistry()

    config.include('pyramid_jinja2')
    config.commit()

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)

    # order matters here
    config.include('.viewderiver')

#    config.add_view_predicate('entity_name', EntityNamePredicate)
    config.add_view_predicate('entity_type', EntityTypePredicate)

    # this is required to collect the list
    # of mappers
    config.include('.events')
    config.commit()

    alchemy = load_alchemy_json(config)

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
    RootFactory.populate_resources(config)

    return config.make_wsgi_app()
