import logging


def includeme(config):
    logging.warning("%s", ",".join(config.registry.settings.keys()))
    if config.registry.settings['email_mgmt_app.authsource'] == 'ldap':
        config.include('.ldap')

