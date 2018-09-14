import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from pyramid.config import Configurator, PHASE3_CONFIG
from pyramid.path import DottedNameResolver
from pyramid.request import Request
from sqlalchemy import Column, String
from sqlalchemy.exc import InvalidRequestError
from zope.component import adapter
from zope.interface import implementer, Interface

from context import GeneratorContext, FormContext
from db_dump import get_process_schema
from db_dump.info import ProcessStruct
from email_mgmt_app import ResourceManager, EntryPoint, _add_resmgr_action, get_root
from entity import EntityFormView
from impl import MapperWrapper, NamespaceStore
from interfaces import IProcess, IEntryPoint, IMapperInfo, IEntryPointGenerator
from manager import OperationArgument
from marshmallow import ValidationError
from myapp_config import logger

from test.util import get_request
from tvars import TemplateVars
from util import format_discriminator

logger = logging.getLogger(__name__)


class FileType:

    def __init__(self, name, ext) -> None:
        self.name = name
        self.ext = ext

    @property
    def discriminator(self):
        return ['.' + self.ext]


JavaScript = FileType('JavaScript', 'js')


class IProcessContext(Interface):
    pass


@implementer(IProcessContext)
class ProcessContext:
    def __init__(self, settings, template_env, asset_manager):
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
    def asset_manager(self):
        return self._asset_manager


class BaseProcessor:
    def __init__(self, pcontext):
        """
        Base class for a processing unit.
        :param pcontext:
        """
        self._pcontex = pcontext

    @property
    def pcontext(self):
        return self._pcontex

    @pcontext.setter
    def pcontext(self, new):
        self._pcontex = new


class Asset:
    def __init__(self, disc, open=True) -> None:
        """

        :param disc: A discriminator for the asset. Used to construct the asset path. Should be a tuple of values.
        :param open:
        """
        super().__init__()


class AssetManager:
    def get(self, disc):

        l = list()
        format_discriminator(l, *disc)
        p = Path(self._output_dir)
        p2 = p.joinpath(''.join(l))
        if not p2.parent.exists():
            p2.parent.mkdir(mode=0o0755, parents=True)

        return open(p2, 'w')
    def __init__(self, output_dir, mkdir=False) -> None:
        super().__init__()
        p = Path(output_dir)
        if p.exists():
            if not p.is_dir():
                raise Exception("%s should be directory." % output_dir)
        else:
            # this is messing us up
            try:
                os.mkdir(output_dir)
            except:
                logger.critical("Unable to create directory %s: %s", output_dir, sys.exc_info()[1])

        self._output_dir = output_dir

    @property
    def output_dir(self):
        return self._output_dir


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

        if ep.view_kwargs and 'view' in ep.view_kwargs:
            view_arg = ep.view_kwargs['view']
            logger.critical("PROCESS view_arg = %r", view_arg)
            view = resolver.maybe_resolve(view_arg)
            ep.view = view

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

        data = dict(js_imports=js_imports,
                    js_stmts=js_stmts,
                    ready_stmts=ready_stmts)

        with self._context.asset_manager.get((self._ep, JavaScript)) as f:
            content = self._context.template_env.get_template('entry_point.js.jinja2').render(
                **data
            )
            f.write(content)
            f.close()

        # with open(fname, 'w') as f:
        #     content = ep.get_template().render(
        #         **data['vars']
        #     )
        #     f.write(content)
        #     f.close()
        #


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
        entry_point = EntryPoint(manager, wrapper.key, None, None, None, None, None, wrapper,
                                 )

        manager.operation(name='form', view=EntityFormView,
                          args=[OperationArgument.SubpathArgument('action', String, default='create')])

        intr = config.introspectable('resource manager', manager.mapper_key, 'resource manager %s' % manager.mapper_key,
                                     'resource manager')
        config.action(('resource manager', manager.mapper_key), _add_resmgr_action, introspectables=(intr,),
                      args=(config, manager), order=PHASE3_CONFIG)


def load_process_struct() -> ProcessStruct:
    relpath = os.path.join(os.path.dirname(__file__), "email_db.json")
    logger.critical("%s", __file__)
    email_db_json = ''
    # we need to find this?
    with open(relpath, 'r') as f:
        email_db_json = ''.join(f.readlines())
    process_schema = get_process_schema()
    process = None  # type: ProcessStruct

    # logger.debug("json for db is %s", email_db_json)
    try:
        process = process_schema.load(json.loads(email_db_json))
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
    config_process_struct(config, process)

    config.action(None, do_action)


def process_views(registry, template_env, asset_mgr, proc_context, ep_iterable: Iterable[EntryPoint], request):


    root = get_root(request)
    assert root is not None

    @dataclass
    class MyEvent:
        request: Request = field(default_factory=lambda: request)

    event = MyEvent()
    #on_new_request(event)

    root_namespace = NamespaceStore('root')
    entry_points_data = dict(list=[])
    entry_point: EntryPoint
    for name, entry_point in ep_iterable:
        entry_points_data['list'].append(entry_point.key)

        # What can we set us up with?
        gctx = GeneratorContext(entry_point.mapper_wrapper.get_one_mapper_info(), TemplateVars(), form_context_factory=FormContext, root_namespace=root_namespace,
                                template_env=template_env)
        generator = registry.queryAdapter(gctx, IEntryPointGenerator)
        assert None is not generator
        entry_point.generator = generator

        entry_point.generator.generate()
        subscribers = registry.subscribers((proc_context, entry_point), IProcess)
        subscribers = [GenerateEntryPointProcess(proc_context, entry_point)]
        assert subscribers, "No subscribers for processing"
        for s in subscribers:

            result = s.process()
            if result:
                logger.debug("result = %s", result)

    with open('entry_points.json', 'w') as f:
        json.dump(entry_points_data, f)
        f.close()
