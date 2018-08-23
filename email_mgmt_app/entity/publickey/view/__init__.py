from pyramid.request import Request
from email_mgmt_app.util import munge_dict
from ....entity.model.email_mgmt import PublicKey
from email_mgmt_app.res import ResourceManager, ResourceRegistration


def includeme(config):
    registration = ResourceRegistration('PublicKey',
                                        title='Public Keys',
                                        # view=PublicKeyView,
                                        entity_type=PublicKey)
    mgr = ResourceManager(config, registration)
    config.add_resource_manager(mgr)



#@view_config(route_name='pubkeys', renderer='templates/pubkeys.jinja2')
def pubkeys_view(request: Request) -> dict:
    d = {}
    return munge_dict(request, d)
