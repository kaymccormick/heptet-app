import json
import logging
import os
import sys
from pathlib import Path

from marshmallow import ValidationError
from sqlalchemy import Column, String
from sqlalchemy.exc import InvalidRequestError

from db_dump import get_process_schema
from db_dump.info import ProcessStruct
from email_mgmt_app import ResourceManager
from entity import EntityFormView
from impl import MapperWrapper

from interfaces import IProcess, IEntryPoint, IMapperInfo
from pyramid.config import Configurator
from pyramid.path import DottedNameResolver
from zope.component import adapter
from zope.interface import implementer, Interface

from manager import OperationArgument
from myapp_config import logger

logger = logging.getLogger(__name__)


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


class AssetManager:
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
    def __init__(self, context, ep) -> None:
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

        fname = ep.get_output_filename()
        assert fname
        logger.critical("generating output file %s", fname)

        data = {'filename': fname,
                'vars': dict(js_imports=js_imports,

                            js_stmts=js_stmts,
                             ready_stmts=ready_stmts)}


        with open(fname, 'w') as f:
            content = ep.get_template().render(
                **data['vars']
            )
            f.write(str(content))
            f.close()


def includeme(config: Configurator):
    def do_action():
        config.registry.registerSubscriptionAdapter(GenerateEntryPointProcess)

    config.action(None, do_action)


def config_process_struct(config, process):
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

        manager.operation(name='form', view=EntityFormView,
                          args=[OperationArgument.SubpathArgument('action', String, default='create')])

        config.add_resource_manager(manager)


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