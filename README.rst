heptet-app
==========

.. image:: https://heptet.us/jenkins/buildStatus/icon?job=heptet-app

This repository represents a python package 'heptet-app' (hetpet_app) that
can be used as the basis for Pyramid application development.

To use this a basis for an application, use the corresponding cookiecutter.

The cookiecutter is available at:

	https://github.com/kaymccormick/heptet-app-cookiecutter.git

To use it, install the 'cookiecutter' package via pip install:

	$ pip install cookiecutter

	$ cookiecutter https://github.com/kaymccormick/heptet-app-cookiecutter.git

What it provides
----------------

All the functionality I could separate and make to work on its own. There is
a fair amount of leftover code that hasn't yet been removed - much of this
will be modularized. For instance, I hope to not retain the 'lxml' dependency
in this core module.

* Tight integration between webpack and pyramid configuration.
* Api for registering new "entry points" (a la webpack)
* Custom webpack plugin!
* End-to-end template integration with jinja2 and hooks
  for generating javascript to be included in static module
  bundling
* Location-aware resources for use in the Pyramid traversal process.
* Resource factory enabling fine-grained use of context predicate in view definitions.

The usual caveats apply - this is pre-release code and should not be confused with production-quality code. For demonstration purposes only. Use at your own risk.


References
==========

[1] _README from cookiecutter: https://github.com/kaymccormick/heptet-app-cookiecutter/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/README.txt
