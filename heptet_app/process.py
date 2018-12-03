import abc
import json
import logging
import os
import sys
from contextlib import contextmanager
from io import TextIOBase, StringIO
from pathlib import Path
from typing import Iterable, Tuple, Mapping, AnyStr

from pyramid.config import Configurator, PHASE3_CONFIG
from pyramid.path import DottedNameResolver
from zope.component import adapter
from zope.interface import implementer, Interface

from heptet_app import ResourceManager, EntryPoint, _add_resmgr_action, TemplateEnvironment, \
    TemplateEnvMixin, AssetEntity, OperationArgument
from heptet_app.context import GeneratorContext, FormContext

from heptet_app.impl import MapperWrapper, NamespaceStore
from heptet_app.impl import MixinBase
from heptet_app.interfaces import IProcess, IEntryPoint, IMapperInfo, IEntryPointGenerator
from heptet_app.tvars import TemplateVars

logger = logging.getLogger(__name__)



class FileType:
    def __init__(self, name, ext) -> None:
        self.name = name
        self.ext = ext


JavaScript = FileType('JavaScript', 'js')


class IProcessContext(Interface):
    pass


class BaseProcessor:
    def __init__(self, pcontext):
        """
        Base class for a processing unit.
        :param pcontext:
        """
        self._pcontext = pcontext

    @property
    def pcontext(self):
        return self._pcontext

    @pcontext.setter
    def pcontext(self, new):
        self._pcontext = new


class AbstractAsset(os.PathLike, metaclass=abc.ABCMeta):
    """
    Base abstract class for a generated asset.

    """

    @abc.abstractmethod
    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        pass


class FileAsset(AbstractAsset):
    """
    Specialization of AbstractAssset which is a file written (or to be written) to disk.
    """

    def __init__(self, obj, arg, mkdir=True) -> None:
        super().__init__()
        self._file_path = Path(arg)

        self._file_path.parents[0].mkdir(mode=0o755, parents=True, exist_ok=True)

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        logger.critical("opening %s", self._file_path)
        return self._file_path.open(mode, buffering, encoding, errors, newline)

    def __fspath__(self):
        return self._file_path.__fspath__()


class AbstractAssetManager(metaclass=abc.ABCMeta):
    """
    Abstract base class for AssetManager
    """

    def __init__(self) -> None:
        super().__init__()
        self._asset_path = None
        self._asset_content = dict()
        self._assets = dict()

    @abc.abstractmethod
    def create_asset(self, obj: AssetEntity):
        pass

    @property
    def asset_path(self) -> Mapping[Tuple, os.PathLike]:
        return self._asset_path

    @property
    def asset_content(self) -> Mapping[Tuple, AnyStr]:
        return self._asset_content

    @property
    def assets(self) -> Mapping[Tuple, AbstractAsset]:
        return self._assets

    @assets.setter
    def assets(self, new):
        self._assets = new


class VirtualAsset(AbstractAsset):
    """
    Specialization of AbstractAsset which is "virtual," i.e. not represented by a physical file.
    """

    def __init__(self, obj) -> None:
        super().__init__()
        self._file = None
        self._content = None
        self._obj = obj

    def __repr__(self):

        return 'VirtualAsset(%r%s)' % (self._obj, self._content and ', content=%r' % self._content or '')

    @contextmanager
    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        self._file = StringIO()
        try:
            yield self._file
        finally:
            self._content = self._file.getvalue()
            self._file = None

    def __fspath__(self):
        return 'virtual:' + os.fspath(self._obj)

    @property
    def content(self) -> AnyStr:
        return self._content


class VirtualAssetManager(AbstractAssetManager):
    """
    Specialization of AbstractAssetManager to manage virtual (non-physical or file-based) assets/
    """

    def __init__(self) -> None:
        super().__init__()
        self._io = {}
        self._asset_path = {}
        self._asset_content = {}
        self._assets = {}

    def create_asset(self, asset_entity: AssetEntity):
        asset = VirtualAsset(asset_entity)
        self._assets[asset_entity] = asset
        return asset

    def get_path(self, *disc) -> os.PathLike:
        return 'virtual:'

    def get_node(self, disc):
        pass

    def select(self, *disc):
        pass

    @contextmanager
    def get(self, asset_entity: AssetEntity) -> TextIOBase:
        x = ""
        self._io[asset_entity] = StringIO()
        self._asset_path[asset_entity] = x
        try:
            yield self._io[asset_entity]
        finally:
            s = self._io[asset_entity].getvalue()
            self.asset_content[asset_entity] = s


class FileAssetManager(AbstractAssetManager):
    """
    Specialization of AbstractAssetManager to manage physical assets.
    """

    def __init__(self, output_dir, mkdir=False) -> None:
        super().__init__()
        self._asset_path = {}
        p = Path(output_dir)
        if p.exists():
            if not p.is_dir():
                raise Exception("%s should be directory." % output_dir)
        elif mkdir:
            # this is messing us up
            try:
                os.mkdir(output_dir)
            except:
                logger.critical("Unable to create directory %s: %s", output_dir, sys.exc_info()[1])

        self._output_dir = output_dir
        self._assets = {}
        self._assets2 = {}

    def create_asset(self, obj: AssetEntity):
        file_asset = FileAsset(obj, obj)
        self._assets[obj] = file_asset
        return file_asset

    # def get_path(self, *disc):
    #     l = list()
    #     format_discriminator(l, *disc)
    #     p = Path(self._output_dir)
    #     p2 = p.joinpath(''.join(l))
    #     return p2

    def get_node(self, disc):
        o = self._assets3
        for elem in disc:
            if elem in o:
                o = o[elem]
            else:
                break

    # def select(self, disc):
    #     p2 = self.get_path(disc)
    #     self._assets[p2] = [list(disc)]
    #     self._assets2[disc] = p2

    def get(self, *disc):
        p2 = self.get_path(*disc)
        if not p2.parent.exists():
            p2.parent.mkdir(mode=0o0755, parents=True)

        self._assets[p2] = [list(disc)]
        self._assets2[disc] = p2
        self.asset_path[disc] = p2

        # f = p2.open('w')

        return p2.open('w')

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def assets(self):
        return self._assets


# This is confusing because it seems like it could be some other random objet
class RootNamespaceMixin(MixinBase):
    def __init__(self) -> None:
        super().__init__()
        self._root_namespace = None

    @property
    def root_namespace(self) -> NamespaceStore:
        return self._root_namespace

    @root_namespace.setter
    def root_namespace(self, new: NamespaceStore):
        self._root_namespace = new


@implementer(IProcessContext)
class ProcessContext(RootNamespaceMixin, TemplateEnvMixin):
    def __init__(self, settings, template_env: TemplateEnvironment, asset_manager: AbstractAssetManager,
                 root_namespace: NamespaceStore = None):
        super().__init__()

        self._settings = settings
        self.template_env = template_env

        self._asset_manager = asset_manager
        self._root_namespace = root_namespace

    @property
    def settings(self):
        return self._settings

    def __repr__(self):
        return 'ProcessContext)%r, %r, %r, %r)' % (
            self.settings, self.template_env, self.asset_manager, self.root_namespace)

    @property
    def asset_manager(self) -> AbstractAssetManager:
        return self._asset_manager


def setup_jsonencoder():
    def do_setup():
        old_default = json.JSONEncoder.default

        class MyEncoder(json.JSONEncoder):
            def default(self, obj):
                # logging.critical("type = %s", type(obj))
                v = None
                # This is not a mistake.
                if isinstance(obj, Column):
                    return ['Column', obj.name, obj.table.name]

                try:
                    v = old_default(self, obj)
                except:
                    logger.critical("dont know how to jsonify %s", type(obj))
                    # assert False, type(obj)
                    return str(obj)
                return v

        json.JSONEncoder.default = MyEncoder.default

    return do_setup


@adapter(IProcessContext, IEntryPoint)
@implementer(IProcess)
class GenerateEntryPointProcess(BaseProcessor):
    def __init__(self, context: ProcessContext, ep: EntryPoint) -> None:
        """

        :param ep:
        """
        super().__init__(context)
        self._ep = ep
        self._context = context

    def process(self):
        resolver = DottedNameResolver()
        ep = self._ep

        js_imports = []
        js_stmts = []
        ready_stmts = []

        # if ep.view_kwargs and 'view' in ep.view_kwargs:
        #     view_arg = ep.view_kwargs['view']
        #     logger.critical("PROCESS view_arg = %r", view_arg)
        #     view = resolver.maybe_resolve(view_arg)
        #     ep.view = view
        #
        #     # FIXME - some equiavalent of this is required for functionality

        # if generator:
        #     js_imports = generator.js_imports()
        #     if js_imports:
        #         for stmt in js_imports:
        #             logger.debug("import: %s", stmt)
        #
        #     js_stmts = generator.js_stmts()
        #     if js_stmts:
        #         for stmt in js_stmts:
        #             logger.debug("js: %s", stmt)
        #
        #     ready_stmts = generator.ready_stmts()

        # FIXME need to populate variables
        data = dict(js_imports=js_imports,
                    js_stmts=js_stmts,
                    ready_stmts=ready_stmts)

        # need to generate path

        asset = self._context.asset_manager.create_asset(self._ep)
        with asset.open('w') as f:
            # FIXME embedded template filename
            content = self._context.template_env.get_template('entry_point.js.jinja2').render(
                **data
            )

            f.write(str(content))


# how do we split the responsibility between this function and "config.add_resource_manager"!?!?!
# currently called from .includeme
def config_process_struct(config: Configurator, process):
    for mapper in process.mappers:
        # code smell, EP-19
        wrapper = MapperWrapper(mapper)
        logger.debug("Registering mapper_wrapper %s", mapper)
        # code smell - registry use. EP-20.
        config.registry.registerUtility(wrapper, IMapperInfo, wrapper.key)
        node_name = mapper.local_table.key
        # EP-19
        manager = ResourceManager(
            mapper_key=wrapper.key,
            node_name=node_name,
            mapper_wrapper=wrapper
        )
        # fixme code smell
        # EP-19
        entry_point = EntryPoint(wrapper.key, manager)

        # more code smell
        # ??
        manager.operation(name='form', view=EntityFormView,
                          args=[OperationArgument.SubpathArgument('action', String, default='create')])

        intr = config.introspectable('resource manager', manager.mapper_key, 'resource manager %s' % manager.mapper_key,
                                     'resource manager')
        config.action(('resource manager', manager.mapper_key), _add_resmgr_action, introspectables=(intr,),
                      args=(config, manager), order=PHASE3_CONFIG)


class JsonFileData:
    def __init__(self, filename):
        self._filename = filename

    def get_data(self):
        with open(self._filename, 'r') as f:
            return json.load(f)


class ProcessStructLoader:
    def __init__(self, schema: 'ProcessSchema', dataGetter):
        self._data = dataGetter
        self._schema = schema
        pass

    def __call__(self):
        data = self._schema.load(self._data.get_data())
        return data


def get_entry_point_generator(gctx: GeneratorContext, registry=None):
    return registry.getAdapter(gctx, IEntryPointGenerator)


def process_views(registry, config, proc_context: ProcessContext,
                  ep_iterable: Iterable[EntryPoint]):
    entry_point: EntryPoint
    for name, entry_point in ep_iterable:
        # this is random as fickle
        process_view(registry, config, proc_context, entry_point)


def make_generator_context(registry, entry_point, root_namespace, template_env):
    gctx = GeneratorContext(
        entry_point,
        TemplateVars(),
        form_context_factory=FormContext,
        root_namespace=root_namespace,
        template_env=template_env
    )
    return gctx
    # FIXME use of registry.queryAdapter - is this what we want?
    # abstract this
    # generator = get_entry_point_generator(gctx, registry)
    # assert None is not generator
    # return gctx, generator


#
# This is probably better renamed to something else.
#
def process_view(registry, config, proc_context: ProcessContext, entry_point: EntryPoint):
    gctx = make_generator_context(registry, entry_point, proc_context.root_namespace, proc_context.template_env)
    # abstract this away
    assert entry_point
    subscribers = registry.subscribers((proc_context, entry_point), IProcess)
    subscribers = [GenerateEntryPointProcess(proc_context, entry_point)]
    assert subscribers, "No subscribers for processing"
    for s in subscribers:
        s.process()
