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
from sqlalchemy import Column, String
from sqlalchemy.exc import InvalidRequestError
from zope.component import adapter
from zope.interface import implementer, Interface

from db_dump import get_process_schema
from db_dump.info import ProcessStruct
from email_mgmt_app import ResourceManager, EntryPoint, _add_resmgr_action, AppBase
from email_mgmt_app.context import GeneratorContext, FormContext
from email_mgmt_app.entity import EntityFormView
from email_mgmt_app.impl import MapperWrapper, NamespaceStore
from email_mgmt_app.interfaces import IProcess, IEntryPoint, IMapperInfo, IEntryPointGenerator
from email_mgmt_app.myapp_config import logger
from email_mgmt_app.operation import OperationArgument
from email_mgmt_app.tvars import TemplateVars
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


class FileType:
    def __init__(self, name, ext) -> None:
        self.name = name
        self.ext = ext

    @property
    def discriminator(self):
        return ['.' + self.ext]

    def is_element_entry(self):
        return False


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


class Asset:
    def __init__(self, disc, open=True) -> None:
        """

        :param disc: A discriminator for the asset. Used to construct the asset path. Should be a tuple of values.
        :param open:
        """
        super().__init__()


class AbstractAsset(os.PathLike, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        pass


class FileAsset(AbstractAsset):
    def __init__(self, obj, arg, mkdir=True) -> None:
        super().__init__()
        if isinstance(arg, os.PathLike):
            self._file_path = arg
        else:
            self._file_path = Path(arg)

        self._file_path.parents[0].mkdir(mode=0o755, parents=True, exist_ok=True)

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        logger.critical("opening %s", self._file_path)
        return self._file_path.open(mode, buffering, encoding, errors, newline)

    def __fspath__(self):
        return self._file_path.__fspath__()


class AbstractAssetManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_asset(self, obj: AppBase, name: AnyStr, type: FileType):
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


class VirtualAsset(AbstractAsset):

    def __init__(self, obj, arg) -> None:
        super().__init__()
        self._file = None
        self._content = None
        self._obj = obj
        self._arg = arg

    def __repr__(self):

        return 'VirtualAsset(%r, %r%s)' % (self._obj, self._arg, self._content and ', content=%r' % self._content or '')

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

    def __init__(self) -> None:
        super().__init__()
        self._io = {}
        self._asset_path = {}
        self._asset_content = {}
        self._assets = {}


    def create_asset(self, obj: AppBase, name: AnyStr, type: FileType):
        asset = VirtualAsset(obj, None)
        self._assets[obj, name] = asset
        return asset

    def get_path(self, *disc) -> os.PathLike:
        return 'virtual:'

    def get_node(self, disc):
        pass

    def select(self, *disc):
        pass

    @contextmanager
    def get(self, *disc) -> TextIOBase:
        x = ""
        self._io[disc] = StringIO()
        self._asset_path[disc] = x
        try:
            yield self._io[disc]
        finally:
            s = self._io[disc].getvalue()
            self.asset_content[disc] = s


class FileAssetManager(AbstractAssetManager):
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

    def create_asset(self, obj: AppBase, name: AnyStr, type_: FileType):
        file_asset = FileAsset(obj, Path(self._output_dir).joinpath(os.fspath(obj) + '.' + type_.ext))
        self._assets[obj, name] = file_asset
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
@implementer(IProcessContext)
class ProcessContext:
    def __init__(self, settings, template_env, asset_manager: AbstractAssetManager):
        self._settings = settings
        self._template_env = template_env
        self._asset_manager = asset_manager

    @property
    def settings(self):
        return self._settings

    @property
    def template_env(self):
        return self._template_env

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
class GenerateEntryPointProcess:
    def __init__(self, context: ProcessContext, ep: EntryPoint) -> None:
        """

        :param ep:
        """
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

        asset = self._context.asset_manager.create_asset(self._ep, None, JavaScript)
        with asset.open('w') as f:
            # FIXME embedded template filename
            content = self._context.template_env.get_template('entry_point.js.jinja2').render(
                **data
            )

            f.write(str(content))


# how do we split the responsibility between this function and "config.add_resource_manager"!?!?!

def config_process_struct(config: Configurator, process):
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        logger.debug("Registering mapper_wrapper %s", mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, wrapper.key)
        node_name = mapper.local_table.key
        manager = ResourceManager(
            mapper_key=wrapper.key,
            node_name=node_name,
            mapper_wrapper=wrapper
        )
        # fixme code smell
        entry_point = EntryPoint(wrapper.key, manager)

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


def load_process_struct(json_file=None, json_str=None) -> ProcessStruct:
    if not json_file and not json_str:
        json_file = os.path.join(os.path.dirname(__file__), "email_db.json")

    if json_file:
        with open(json_file, 'r') as f:
            json_str = ''.join(f.readlines())

    process_schema = get_process_schema()
    process = None  # type: ProcessStruct

    # logger.debug("json for db is %s", email_db_json)
    try:
        process = process_schema.load(json.loads(json_str))
        logger.debug("process = %s", repr(process))
    except InvalidRequestError as ex:
        logger.critical("Unable to load database json.")
        logger.critical(ex)
        raise ex
    except ValidationError as ve:
        # todo better error handling
        for k, v in ve.messages.items():
            logger.critical("input error in %s: %s", k, v)
        raise ve
    return process


def includeme(config: Configurator):
    def do_action():
        config.registry.registerSubscriptionAdapter(GenerateEntryPointProcess)

    # load our pre-processed info

    process = load_process_struct()  # type: ProcessStruct
    config.add_request_method(lambda r: process, 'process_struct')
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, mapper.local_table.key)

    config.include('.viewderiver')
    config.include('.entity')

    data = JsonFileData(os.path.join(os.path.dirname(__file__), "email_db.json"))
    loader = ProcessStructLoader(get_process_schema(), data)
    ps = loader()

    config_process_struct(config, process)

    config.action(None, do_action)


def get_entry_point_generator(gctx: GeneratorContext, registry=None):
    return registry.getAdapter(gctx, IEntryPointGenerator)


def process_views(registry, template_env, proc_context: ProcessContext, ep_iterable: Iterable[EntryPoint]):
    # fixme extract dependncy
    root_namespace = NamespaceStore('root')

    entry_points_data = dict(list=[])
    entry_point: EntryPoint
    for name, entry_point in ep_iterable:
        # this is random as fickle
        entry_points_data['list'].append(entry_point.key)

        # is this our most advantageous entry pint?

        #        mapper = entry_point.mapper

        gctx = GeneratorContext(
            entry_point,
            TemplateVars(),
            form_context_factory=FormContext,
            root_namespace=root_namespace,
            template_env=template_env
        )
        # FIXME use of registry.queryAdapter - is this what we want?
        # abstract this
        generator = get_entry_point_generator(gctx, registry)
        assert None is not generator

        process_view(gctx, entry_point, proc_context, registry, generator)

    # FIXME should we use asset manager for this also
    # whoops hardcoded path

    # with open('entry_points.json', 'w') as f:
    #     json.dump(entry_points_data, f)
    #     f.close()


#
# This is probably better renamed to something else.
#
def process_view(gctx, entry_point, proc_context, registry, generator):
    # abstract this away
    subscribers = registry.subscribers((proc_context, entry_point), IProcess)
    subscribers = [GenerateEntryPointProcess(proc_context, entry_point)]
    assert subscribers, "No subscribers for processing"
    for s in subscribers:
        s.process()
