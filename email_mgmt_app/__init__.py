import json
import logging

from pyramid.renderers import get_renderer
from pyramid.request import Request

from email_mgmt_app.res import Resource
from jinja2.exceptions import TemplateNotFound

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

# this ought to be relocated
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

    # dont want to propogate this way
    if False:
        config.registry.email_mgmt_app.alchemy = alchemy
    return alchemy



