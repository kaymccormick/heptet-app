import json
import os
import logging

from db_dump.info import ProcessStruct
from marshmallow import ValidationError

from db_dump.schema import get_process_schema
from pyramid_ldap3 import groupfinder
from sqlalchemy import String

from email_mgmt_app.predicate import EntityTypePredicate
from email_mgmt_app.entity import EntityFormView
from email_mgmt_app.interfaces import IMapperInfo, IHtmlIdStore
from email_mgmt_app.impl import MapperWrapper, HtmlIdStore, IdStore
from email_mgmt_app.interfaces import INamespaceStore
from jinja2 import TemplateNotFound, Environment, PackageLoader, select_autoescape
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from email_mgmt_app.registry import AppSubRegistry
from email_mgmt_app.root import RootFactory
from email_mgmt_app.res import RootResource, ResourceManager, OperationArgument, IRootResource
from pyramid.interfaces import IRootFactory
from pyramid.renderers import get_renderer
from pyramid_jinja2 import IJinja2Environment

logger = logging.getLogger(__name__)


def config_process_struct(config, process):
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, wrapper.key)
        node_name = mapper.local_table.key
        manager = ResourceManager(config, wrapper.key, node_name=node_name)

        # we add only a single operation because we're dumb and lazy
        manager.operation(name='form', view=EntityFormView,
           args=[OperationArgument.SubpathArgument('action', String, default='create')])
        config.add_resource_manager(manager)





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

    # we changed the root factory to an instance of our factory, which maybe would help??
    config = Configurator(settings=settings, root_factory=RootFactory())
                          #exceptionresponse_view=ExceptionView)#lambda x,y: Response(str(x), content_type="text/plain"))

    process = load_process_struct() # type: ProcessStruct
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, mapper.local_table.key)

    # FIXME this needs to go away
    config.registry.email_mgmt_app = AppSubRegistry(process)

    config.include('.model.email_mgmt')
    config.include('.entrypoint')
    config.include('.res')

    resource = RootResource({}, '')
    config.registry.registerUtility(resource, IRootResource)

    # we can include viewderiver here because we haven't created all of our views yet
    config.include('.viewderiver')
    config.add_view_predicate('entity_type', EntityTypePredicate)

    # this adds all our views, and other stuff
    config_process_struct(config, process)

    jinja2_loader_package = settings['email_mgmt_app.jinja2_loader_package']
    jinja2_loader_template_path = settings['email_mgmt_app.jinja2_loader_template_path']
    env = Environment(loader=PackageLoader(jinja2_loader_package, jinja2_loader_template_path),
                      autoescape=select_autoescape(default=False))

    config.registry.registerUtility(env, IJinja2Environment, 'app_env')

    config.include('pyramid_jinja2')
    config.commit()

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)



#    config.add_view_predicate('entity_name', EntityNamePredicate)

    config.include('.view')

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

    store = HtmlIdStore()
    config.registry.registerUtility(store, IHtmlIdStore)
    config.registry.registerUtility(IdStore('form_name'), INamespaceStore, 'form_name')
    config.registry.registerUtility(IdStore('namespace'), INamespaceStore, 'namespace')
    return config.make_wsgi_app()


def load_process_struct():
    email_db_json = ''
    with open('email_db.json', 'r') as f:
        email_db_json = ''.join(f.readlines())
    process_schema = get_process_schema()
    process = None  # type: ProcessStruct

    # logger.debug("json for db is %s", email_db_json)
    try:
        process = process_schema.load(json.loads(email_db_json))
        logger.debug("process = %s", repr(process))
    except ValidationError as ve:
        # todo better error handling
        for k, v in ve.messages.items():
            logger.critical("input error in %s: %s", k, v)
        raise ve
    return process


def on_new_request(event):
    registry = event.request.registry
    registry.registerUtility(HtmlIdStore(), IHtmlIdStore)
    registry.registerUtility(IdStore('form_name'), INamespaceStore, 'form_name')
    registry.registerUtility(IdStore('namespace'), INamespaceStore, 'namespace')


def on_application_created(event):
    pass


def on_before_render(event):
    logger.debug("on_before_render: event=%s", event)
    val = event.rendering_val
    val['request'] = event['request']
    logger.debug("VAL=%s", val)


def set_renderer(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription
    :param event: the event
    :return:
    """
    request = event.request # type: Request
    context = request.context # type: Resource
    logger.debug("context is %s", context)

    if isinstance(context, Exception):
        return

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


# def load_alchemy_json(config):
#     """
#
#     :param config:
#     :return:
#     """
#     alchemy = None
#     try:
#         with open('alchemy.json', 'r') as f:
#             lines = f.readlines()
#             s="\n".join(lines)
#             alchemy = json.loads(s)
#             #alchemy = AlchemyInfo.from_json(s)
#             f.close()
#     except FileNotFoundError:
#         pass
#     except:
#         raise
#     assert alchemy
#
#     # dont want to propogate this way
#     if False:
#         config.registry.email_mgmt_app.alchemy = alchemy
#     return alchemy