import os
import re
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from email_mgmt_app.entity.model.email_mgmt import Domain, ServiceEntry, Organization, Person, Role, OrgPerson, \
    OrganizationRole
from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.model.email_mgmt import get_engine, get_session_factory, get_tm_session


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        f = open("services")
        re_compile = re.compile("[ \t]*([^ \t#]*)[ \t]*([0-9]+)/(tcp|udp)")
        while True:
            s = f.readline()
            if s == "":
                break
            m = re_compile.search(s)
            if m is None:
                print(s)
                continue

            name = m.group(1)

            port = int(m.group(2))
            proto = m.group(3)
            sv = ServiceEntry()
            sv.name = name
            sv.port_num = port
            sv.protocol_name = proto
            dbsession.add(sv)


        r = Role()
        r.name = "Support"
        dbsession.add(r)

        p = Person()
        p.name = 'Kay McCormick'

        d = Domain()
        d.name = "test.domain"
        o = Organization()
        o.name = "Heptet Global"
        o2 = Organization()
        o2.parent = o
        o2.name = "Heptet North America"

        d.organization = o2

        org_person = OrgPerson()
        org_person.person = p
        o2.persons.append(org_person)

        role = Role()
        role.name = 'CEO'
        org_role = OrganizationRole()
        org_role.role = role
        o2.roles.append(org_role)

        dbsession.add(d)
