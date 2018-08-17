import logging
import re

from lxml import etree
import lxml.html
from webtest import TestApp
import transaction
import lxml

import email_mgmt_app
from email_mgmt_app.entity.model.email_mgmt import get_tm_session
from email_mgmt_app.entity.model.email_mgmt import get_session_factory
from email_mgmt_app.entity.model.email_mgmt import get_engine

javascript_contenttypes = ['application/javascript', 'text/plain']

def init_database(engine, session):
    from email_mgmt_app.entity.model.meta import Base
    Base.metadata.create_all(engine)

settings = { 'sqlalchemy.url': 'postgresql://flaskuser:FcQCPDM7%40RpRCsnO@localhost/email',
             'email_mgmt_app.secret': '9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw',
             'email_mgmt_app.authsource': 'db'}

packed_assets = ['./node_modules/bootstrap/dist/css/bootstrap.min.css', './node_modules/bootstrap/dist/js/bootstrap.js', './node_modules/css-loader/index.js!./node_modules/bootstrap/dist/css/bootstrap.min.css', './node_modules/css-loader/lib/css-base.js', './node_modules/jquery/dist/jquery.js', './node_modules/popper.js/dist/esm/popper.js', './node_modules/raw-loader/index.js!./node_modules/jquery/dist/jquery.slim.min.js', './node_modules/script-loader/addScript.js', './node_modules/script-loader/index.js!./node_modules/jquery/dist/jquery.slim.min.js', './node_modules/style-loader/lib/addStyles.js', './node_modules/style-loader/lib/urls.js', './node_modules/webpack/buildin/global.js', './src/index.prod.js']

app = TestApp(email_mgmt_app.main(None, **settings))

engine = get_engine(settings)
session_factory = get_session_factory(engine)

session = get_tm_session(session_factory, transaction.manager)

init_database(engine, session)
resp = app.get('/')
assert resp.status_int == 200
assert resp.content_type == 'text/html'
assert resp.content_length > 0
root = lxml.html.document_fromstring(resp.text)

logging.warning("%s", type(root))
scripts = root.xpath("//script")
srcs = []
for script in scripts:
    print(script.keys())
    if 'src' in script.attrib:
        scriptsrc = script.get('src')
        srcs.append(scriptsrc)

for src in srcs:
    print(src)
    srcresp = app.request(src)
    assert srcresp.content_type in javascript_contenttypes, ("%s" % srcresp.content_type)
    text = srcresp.text
    all = re.findall(r'^/\*\*\*/ "(.*)":$', text, re.MULTILINE)
    #print(*all, sep='\n')

for link in root.iterlinks():
    print(link[2])