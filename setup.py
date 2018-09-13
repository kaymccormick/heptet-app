import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'plaster_pastedeploy',
    'pyramid >= 1.9a',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_retry',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'pyramid_ldap3',
    'lxml',
    'bcrypt', 'stringcase',
    'kazoo'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

setup(
    name='email_mgmt_app',
    version='0.4',
    description='Pyramid Scaffold',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Kay McCormick',
    author_email='kay@kaymccormick.com',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = email_mgmt_app.webapp_main:wsgi_app',
        ],
        'console_scripts': [
            'initialize_email_mgmt_app_db = email_mgmt_app.scripts.initializedb:main',
            'process_model = email_mgmt_app.scripts.process_model:main',
            'process_views = email_mgmt_app.process_views:main',
        ],
    },
)
