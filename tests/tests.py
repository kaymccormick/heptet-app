import logging
import unittest
import transaction

import webapp_main
from pyramid.interfaces import IRootFactory
from pyramid.request import Request

from email_mgmt_app.root import RootFactory
from email_mgmt_app.res import RootResource, ResourceManager
from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

def real_request(dbsession):
    return Request(dbsession=dbsession)

class BaseTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)

        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:',
            'email_mgmt_app.secret': '9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw',
            'email_mgmt_app.authsource': 'db',
            'email_mgmt_app.request_attrs': 'context, root, subpath, traversed, view_name, matchdict, virtual_root, virtual_root_path, exception, exc_info, authenticated_userid, unauthenticated_userid, effective_principals',
        })

        settings = self.config.get_settings()
        self.settings = settings

        from sqlalchemy_integration import get_tm_session
        from sqlalchemy_integration import get_session_factory
        from sqlalchemy_integration import get_engine

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from model.meta import Base
        Base.metadata.create_all(self.engine)


    def tearDown(self):
        from model.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class BaseAppTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:',
            'email_mgmt_app.secret': '9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw',
            'email_mgmt_app.authsource': 'db',
            'email_mgmt_app.request_attrs': 'context, root, subpath, traversed, view_name, matchdict, virtual_root, virtual_root_path, exception, exc_info, authenticated_userid, unauthenticated_userid, effective_principals',
        })

        self.config.registry.email_mgmt_app.resources = \
            RootResource({}, ResourceManager(self.config, name='', title='', node_name=''))

        RootFactory.populate_resources(self.config)

        settings = self.config.get_settings()
        self.settings = settings


    def tearDown(self):
        testing.tearDown()
        transaction.abort()


class TestConfigSuccessCondition(BaseAppTest):
    def setUp(self):
        super(TestConfigSuccessCondition, self).setUp()
        logging.info("settings = %s", repr(self.settings))
        self.app = webapp_main.main(None, ** self.settings)


    def test_root_factory(self):
        root_factory = self.app.registry.queryUtility(IRootFactory)
        assert root_factory
        assert issubclass(root_factory, RootFactory), "%s is not subclass of type %s" % (repr(root_factory), repr(RootFactory.__module__ + '.' + RootFactory.__name__))
        logging.debug("root_factory = %s", root_factory)
        root = root_factory(dummy_request(None))

        assert root.__name__ == ''
        assert root.__parent__ is None

        for (x, y) in root.items():
            logging.debug("%s: %s", x, repr(y))
            assert '__parent__' in dir(y) and y.__parent__ == root, "No parent for %s" % (repr(y))
            assert y.__name__ == x

        pass



class TestMyViewFailureCondition(BaseTest):
    def test_failing_view(self):
        pass
        # from email_mgmt_app.views.default import my_view
        # info = my_view(dummy_request(self.session))
        # self.assertEqual(info.status_int, 500)



class TestViewSuccessCondition(BaseTest):
    def setUp(self):
        super().setUp()
        self.init_database()

        # from email_mgmt_app.models import MyModel
        #
        # model = MyModel(name='one', value=55)
        #self.session.add(model)

    def test_passing_view(self):
        pass


class TestViewFailureCondition(BaseTest):
    def test_failing_view(self):
        pass
