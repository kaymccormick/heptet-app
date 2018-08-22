import logging
import sys


def includeme(config):
    try:
        if config.registry.settings['email_mgmt_app.authsource'] == 'ldap':
            config.include('.ldap')
    except:
        logging.warning("{}", sys.exc_info()[1].message)


