import logging
import sys

from email_mgmt_app.interfaces import ISqlAlchemySession, IResource
from email_mgmt_app.model.meta import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, configure_mappers, backref
from email_mgmt_app.sqlalchemy_integration import get_tm_session, get_session_factory, get_engine
from zope.component import IFactory
from zope.component.factory import Factory
from zope.interface import implementer

logger = logging.getLogger(__name__)
mappers = {}

print("In model.email_mgmt", file=sys.stderr)


# marker class for objects which are "association tables"
class AssociationTableMixin(object):
    pass


# class ApplicationUser(Mixin, Base):
#     __tablename__ = 'appuser'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)

# class MyBase(Base):
#     pass


@implementer(IResource)
class Mixin(object):
    """
    Standard mixin for application.
    """

    @property
    def display_name(self):
        return self.name


class Entity(Mixin, Base):
    __tablename__ = 'app_entity'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Property(Mixin, Base):
    __tablename__ = 'app_property'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type_id = Column(Integer, ForeignKey('app_type.id'))
    type = relationship('AppType', backref='types')


class AppType(Mixin, Base):
    __tablename__ = 'app_type'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class PublicKey(Mixin, Base):
    "Public key for encryption"
    __tablename__ = 'public_key'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('person.id'))
    owner = relationship('Person', backref='keys')
    public_key_text = Column(String)
    info = {'hide': True}


class File(Mixin, Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('person.id'))
    owner = relationship('Person', backref='files')
    data = Column(LargeBinary)
    info = {'hide': True}


class FileUpload(Mixin, Base):
    __tablename__ = 'file_upload'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('person.id'))
    owner = relationship('Person', backref='file_uploads')
    data = Column(LargeBinary)
    info = {'hide': True}


class OrganizationRole(Mixin, AssociationTableMixin, Base):
    __tablename__ = 'organization_role'
    id = Column(Integer, primary_key=True)

    organization_id = Column(Integer, ForeignKey('organization.id'))
    role_id = Column(Integer, ForeignKey('role.id'))

    role_persons = relationship('OrgRolePerson', back_populates='organization_role')
    organization = relationship('Organization', back_populates='roles')
    role = relationship('Role', back_populates='organization_roles')

    info = {'hide': True}

    @property
    def display_name(self):
        return "%s, %s" % (self.role.name, self.organization.name)


class OrgRolePerson(AssociationTableMixin, Mixin, Base):
    __tablename__ = 'organization_role_person'

    organization_role_id = Column(Integer, ForeignKey('organization_role.id'), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), primary_key=True)

    person = relationship('Person', back_populates='organization_roles')
    organization_role = relationship('OrganizationRole', back_populates='role_persons')

    info = {'hide': True}

    @property
    def display_name(self):
        return self.organization_role.display_name + ': ' + self.person.display_name


class Organization(Mixin, Base):
    "An organization."
    __tablename__ = 'organization'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('organization.id'))
    name = Column(String, doc="The name of the organization.")
    children = relationship("Organization",
                            backref=backref('parent', remote_side=[id], doc="Parent organization if any."))
    roles = relationship('OrganizationRole', back_populates='organization')

    def __repr__(self):
        return "Organization[%s]: %s" % (self.id, self.name)


class Role(Mixin, Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    organization_roles = relationship('OrganizationRole', back_populates='role')


class Address(Mixin, Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address_line_1 = Column(String)
    address_line_2 = Column(String)
    address_line_3 = Column(String)
    city = Column(String)
    state_or_region = Column(String)
    postcode = Column(String)
    country = Column(String)


def entity_embed(*args, **kwargs):
    def embed():
        pass

    return embed


class Person(Mixin, Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    home_address_id = Column(Integer, ForeignKey('address.id'))
    work_address_id = Column(Integer, ForeignKey('address.id'))
    mailing_address_id = Column(Integer, ForeignKey('address.id'))
    home_address = relationship('Address', uselist=False, foreign_keys=[home_address_id], info={'embed': True})
    work_address = relationship('Address', uselist=False, foreign_keys=[work_address_id])
    mailing_address = relationship('Address', uselist=False, foreign_keys=[mailing_address_id])
    organization_roles = relationship('OrgRolePerson', back_populates='person')


class Recipient(Mixin, Base):
    __tablename__ = 'recipient'
    id = Column(Integer, primary_key=True)
    info = {'hide': True}


class Domain(Mixin, Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String, doc="Domain name.")

    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', backref='domains', doc="Associated organization.")

    info = {'hide': True}


class ServiceEntry(Mixin, Base):
    __tablename__ = 'service_entry'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    port_num = Column(Integer)
    protocol_name = Column(String)
    weight = Column(Float, default=0)
    description = Column(String, default="")
    info = {'hide': True}


class Host(Mixin, Base):
    "A host specified by its fully qualified domain name."
    __tablename__ = 'host'

    id = Column(Integer, primary_key=True)

    name = Column(String, doc="The fully qualified domain name (FQDN).")
    domain_id = Column(Integer, ForeignKey('domain.id'))
    domain = relationship('Domain', backref='hosts', doc="The associated domain.")


class EmailAddress(Mixin, Base):
    __tablename__ = 'email_address'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    host_id = Column(Integer, ForeignKey('host.id'))
    host = relationship('Host', backref='email_addresses')


configure_mappers()


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('email_mgmt_app.models')``.

    """

    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    if 'sqlalchemy.url' not in settings:
        logging.warning("sqlalchemy.url not in settings!")

    session_factory = get_session_factory(get_engine(settings))
    factory = Factory(session_factory, 'sqlalchemy_session', 'sqlalchemy_session', ISqlAlchemySession)
    config.registry.registerUtility(factory, IFactory, 'sqlalchemy_session')
    # config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    #
    # EP-5: config.registry.email_mgmt_app.dbsession = lambda r: get_tm_session(session_factory, r.tm),
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(r.registry.getUtility(IFactory, 'sqlalchemy_session'), r.tm),
        'dbsession',
        reify=True
    )
