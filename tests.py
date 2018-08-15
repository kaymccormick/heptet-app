import unittest
import transaction

from email_mgmt_app.entity.domain.view import DomainView
from email_mgmt_app.entity.model.email_mgmt import Domain
from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'

        })
        ## I moved this!
        self.config.include('email_mgmt_app.models')
        settings = self.config.get_settings()

        from email_mgmt_app.models import get_tm_session
        from email_mgmt_app.models import get_session_factory
        from email_mgmt_app.models import get_engine

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from email_mgmt_app.entity.model.meta import Base
        from email_mgmt_app.entity.domain.view import DomainView
#        from email_mgmt_app.entity.model.email_mgmt import Domain
        Base.metadata.create_all(self.engine)

        domain = Domain()
        domain.name = "testdomain.com";
        self.session.add(domain)

    def tearDown(self):
        from email_mgmt_app.entity.model.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        # from .models import MyModel
        #
        # model = MyModel(name='one', value=55)
        #self.session.add(model)

    def test_passing_view(self):
        view = DomainView(None, dummy_request(self.session))
        d = view.__call__()
        print(repr(d))
        pass
        # from .views.default import my_view
        # info = my_view(dummy_request(self.session))
        # self.assertEqual(info['one'].name, 'one')
        # self.assertEqual(info['project'], 'Pyramid Scaffold')


class TestMyViewFailureCondition(BaseTest):
    def test_failing_view(self):
        pass
        # from .views.default import my_view
        # info = my_view(dummy_request(self.session))
        # self.assertEqual(info.status_int, 500)
