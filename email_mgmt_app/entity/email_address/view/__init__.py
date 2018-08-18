from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import Host, EmailAddress
from pyramid.request import Request
from pyramid.view import view_config
from email_mgmt_app.util import munge_dict
from ....entity import EntityView
from ....resource import ResourceRegistration, ResourceManager


class EmailAddressView(EntityView[EmailAddress]):
    pass


def includeme(config: Configurator):
    mgr = ResourceManager(config, EmailAddress)
    config.register_resource\
        (ResourceRegistration('EmailAddress', view=EmailAddressView, entity_type=EmailAddress, title='Email Addresses'),
         mgr)
    mgr.operation('view', ".EmailAddressView", renderer='templates/email_address/email_address.jinja2')

#@view_config(route_name='email_form', renderer='templates/email_address/email_form.jinja2')
def email_form_view(request: Request) -> dict:
    d = {'hosts': request.dbsession.query(Host).all()}
    return munge_dict(request, d)

#@view_config(route_name='email_create', renderer='templates/email_address/email_create.jinja2')
def email_create_view(request: Request) -> dict:
    d = {}
    # create e-mail entry
    email = EmailAddress()
    email.name = request.POST['local_part']
    email.host_id = request.POST['host_id']
    request.dbsession.add(email)
    request.dbsession.flush()
    d['email'] = email
    return munge_dict(request, d)

