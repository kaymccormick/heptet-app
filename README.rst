heptet-app
==========

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

There is no reason for anyone to use this module in its current state,
except me.

References
==========

[1] _README from cookiecutter: https://github.com/kaymccormick/heptet-app-cookiecutter/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/README.txt
