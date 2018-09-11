import logging

from sqlalchemy import Column

from db_dump.info import TableColumnSpecInfo

logger = logging.getLogger(__name__)

_column_map = dict()


def map_column(column: Column, map_target):
    logger.critical("%s %s", column, map_target)
    t = _column_map.get(column.table.key, None)
    if t is None:
        t = { column.key: map_target }
        _column_map[column.table.key] = t
    else:
        t[column.key] = map_target


def get_column_map(column):
    x = None
    if isinstance(column, TableColumnSpecInfo):
        x = _column_map.get(column.table, { }).get(column.column, None)


    return x

