from jinja2 import Environment


class AppSubRegistry:
    def __init__(self) -> None:
        self._mappers = {}
        self._jinja2_env = None
        self._json_renderer = None
        self._dbsession = None
        self._views = []
        self._resources = None
        self._entry_points = {}

    @property
    def mappers(self) -> dict:
        return self._mappers

    @property
    def jinja2_env(self) -> Environment:
        return self._jinja2_env

    @jinja2_env.setter
    def jinja2_env(self, new) -> None:
        self._jinja2_env = new

    @property
    def json_renderer(self):
        return self._json_renderer

    @json_renderer.setter
    def json_renderer(self, new):
        self._json_renderer = new

    @property
    def dbsession(self):
        return self._dbsession

    @dbsession.setter
    def dbsession(self, new):
        self._dbsession = new

    @property
    def views(self):
        return self._views

    @views.setter
    def views(self, new):
        self._views = new

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new):
        self._resources = new

    @property
    def entry_points(self):
        return self._entry_points

    @entry_points.setter
    def entry_points(self, new):
        self._entry_points = new
