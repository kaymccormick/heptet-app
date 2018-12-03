import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'plaster_pastedeploy',
    'pyramid >= 1.9a',
    'pyramid_jinja2',
    'stringcase',
    'zope.component',
    'zope.interface',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

setup(
    name='heptet-app',
    version='0.45.0',
    description='Heptet App Framework',
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
    packages=find_packages(exclude=["node_modules"]),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = heptet_app.webapp_main:wsgi_app',
        ],
        'console_scripts': [
            'initialize_heptet_app_db = heptet_app.scripts.initializedb:main',
            'process_model = heptet_app.scripts.process_model:main',
            'process_views = heptet_app.process_views:main',
            'entry_points_json = heptet_app.process_views2:main',
        ],
    },
)
