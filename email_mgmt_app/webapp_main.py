import logging
import os

from jinja2 import TemplateNotFound, Environment, select_autoescape, FileSystemLoader
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from pyramid.renderers import get_renderer
from pyramid_jinja2 import IJinja2Environment
from pyramid_ldap3 import groupfinder
from zope.component import getGlobalSiteManager

from db_dump.info import ProcessStruct
from exceptions import InvalidMode
from impl import MapperWrapper, NamespaceStore
from interfaces import IMapperInfo
from interfaces import INamespaceStore
from myapp_config import config_process_struct, load_process_struct

logger = logging.getLogger(__name__)

VALID_MODES = ('development', 'production')


def wsgi_app(global_config, **settings):
    """
    The main functionf or our pyramid application.
    :param global_config:
    :param settings:
    :return: A WSGI application.
    """
    mode = 'mode' in settings and settings['mode'] or VALID_MODES[1]
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

    config = Configurator(package="email_mgmt_app",
                          registry=global_reg, settings=settings, root_factory=".root:get_root")
    config.include('.myapp_config')
    if use_global_reg:
        config.setup_registry(settings=settings, root_factory='root.get_root')


    jinja2_loader_template_path = settings['email_mgmt_app.jinja2_loader_template_path'].split(':')
    env = Environment(loader=FileSystemLoader(jinja2_loader_template_path),
                      autoescape=select_autoescape(default=False))
    config.registry.registerUtility(env, IJinja2Environment, 'app_env')

    # exceptionresponse_view=ExceptionView)#lambda x,y: Response(str(x), content_type="text/plain"))

    config.include('.model.email_mgmt')
    process = load_process_struct()  # type: ProcessStruct
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, mapper.local_table.key)

    # we can include viewderiver here because we haven't created all of our views yet
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


def on_new_request(event):
    logger.debug("Resetting namespaces")
    registry = event.request.registry
    registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
    registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
    registry.registerUtility(NamespaceStore('global'), INamespaceStore, 'global')


def on_application_created(event):
    pass


def on_before_render(event):
    logger.debug("on_before_render: event=%s", event)
    val = event.rendering_val
    val['request'] = event['request']
    logger.debug("VAL=%s", val)


def on_context_found(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription
    :param event: the event
    :return:
    """
    request = event.request  # type: Request
    context = request.context  # type: Resource
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
