from unittest import TestCase

import transaction
from pyramid import testing
from pyramid.paster import get_appsettings

from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.domain.view import DomainView
from email_mgmt_app.models import get_engine, get_session_factory, get_tm_session


class TestDomainView(TestCase):
    def setUp(self):
        settings = get_appsettings("../../../../testing.ini")
        engine = get_engine(settings)
        Base.metadata.create_all(engine)

        session_factory = get_session_factory(engine)

        dbsession = get_tm_session(session_factory, transaction.manager)

        request = testing.DummyRequest
        self.config = testing.setUp(request=request)
        request.dbsession = dbsession
        self.view = DomainView(request, id=1)

    def test1(self):
        out = self.view()
        pass

    def tearDown(self):
        testing.tearDown()




