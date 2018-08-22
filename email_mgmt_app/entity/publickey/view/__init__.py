from pyramid.request import Request
from email_mgmt_app.util import munge_dict
from ....entity.model.email_mgmt import PublicKey
from res.resource import ResourceManager, ResourceRegistration


def includeme(config):
    mgr = ResourceManager(config, PublicKey)
    config.register_resource\
        (ResourceRegistration('PublicKey',
                              title='Public Keys',
                              #view=PublicKeyView,
                              entity_type=PublicKey),
         mgr)


#@view_config(route_name='pubkeys', renderer='templates/pubkeys.jinja2')
def pubkeys_view(request: Request) -> dict:
    d = {}
    return munge_dict(request, d)
