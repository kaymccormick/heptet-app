import json
import os

from marshmallow import ValidationError


def load_process_struct(json_file=None, json_str=None) -> 'ProcessStruct':
    if not json_file and not json_str:
        json_file = os.path.join(os.path.dirname(__file__), "heptet_db.json")

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

    try:
        process = load_process_struct()  # type: ProcessStruct
    except:
        logger.warning("unable to blah")
        return

    config.add_request_method(lambda r: process, 'process_struct')
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, mapper.local_table.key)

    config.include('.viewderiver')
    config.include('.entity')

    data = JsonFileData(os.path.join(os.path.dirname(__file__), "heptet_db.json"))
    loader = ProcessStructLoader(get_process_schema(), data)
    ps = loader()

    config_process_struct(config, process)

    config.action(None, do_action)
