define(`WSGI_CONFIG', `###
# wsgi server configuration
###

[server:main]
use = egg:waitress#main
listen = LISTEN_ADDR
url_prefix = /app
')dnl
define(`APP_MAIN', `[app:main]
use = egg:APP_PACKAGE
mode = APP_MODE
# do we want this the same as the pyramid paths?
APP_PACKAGE.jinja2_loader_package = APP_PACKAGE
APP_PACKAGE.jinja2_loader_template_path = templates
APP_PACKAGE.secret = 9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw
APP_PACKAGE.authsource = db
APP_PACKAGE.request_attrs = context, root, subpath, traversed, view_name, matchdict
jinja2.autoescape = false
pyramid.reload_templates = true
pyramid.debug_authorization = false
pyramid.debug_notfound = true
pyramid.debug_routematch = false
pyramid.default_locale_name = en
pyramid.includes = PYRAMID_INCLUDES

sqlalchemy.url = SQLALCHEMY_URL

retry.attempts = 3

# By default, the toolbar only appears for clients from IP addresses
# '127.0.0.1' and '::1'.
# debugtoolbar.hosts = 127.0.0.1 ::1
')dnl
define(`LOGGERS', `[loggers]
keys = LOGGER_NAMES
define(`LOGGER', `[logger_$1]define(`LOGGERS', defn(`LOGGERS')` $1'')dnl
define(`HANDLERS', `[handlers]
keys = ')dnl
define(`HANDLER', `define(`HANDLERS', `HANDLERS $1')dnl
handler = $1')dnl
define(`LEVEL', `level = $1')dnl
define(`QUALNAME', `qualname = $1')dnl
traceon(APP_MAIN)dnl
define(`LISTEN_ADDR', `0.0.0.0:6543')dnl
define(`PYRAMID_INCLUDES', `pyramid_toolbar')dnl
define(`APP_PACKAGE', `email_mgmt_app')dnl
define(`APP_MODE', `development')dnl
define(`SQLALCHEMY_URL', `postgresql://flaskuser:FcQCPDM7%%40RpRCsnO@localhost/email')dnl
APP_MAIN
WSGI_CONFIG

LOGGER(root)
HANDLER(console)
LEVEL(DEBUG)

LOGGER(db_dump)
LEVEL(WARN)
HANDLER(console)
QUALNAME(db_dump)

LOGGERS

