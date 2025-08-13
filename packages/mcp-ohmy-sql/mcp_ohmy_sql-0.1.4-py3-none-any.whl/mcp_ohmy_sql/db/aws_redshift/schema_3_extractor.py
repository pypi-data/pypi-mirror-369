# -*- coding: utf-8 -*-

"""
Reference:

- https://docs.aws.amazon.com/redshift/latest/dg/c_Supported_data_types.html
- https://docs.aws.amazon.com/redshift/latest/dg/r_PG_TABLE_DEF.html
"""

import typing as T
from pydantic import BaseModel, Field

from enum_mate.api import BetterStrEnum
from ...lazy_import import sa, redshift_connector

from ...constants import ObjectTypeEnum, LLMTypeEnum
from ...utils import match
from ...aws.aws_redshift.api import Session, T_CONN_OR_ENGINE

from .sql import SqlEnum
from .schema_1_model import (
    ColumnInfo,
    TableInfo,
    SchemaInfo,
    DatabaseInfo,
)

try:
    from rich import print as rprint
except ImportError:  # pragma: no cover
    pass


class RedshiftDataTypeEnum(BetterStrEnum):
    """ """

    # Numeric Types
    smallint = "smallint"
    integer = "integer"
    bigint = "bigint"
    real = "real"
    double_precision = "double precision"
    numeric = "numeric"
    decimal = "decimal"
    # Character Types
    character = "character"
    character_varying = "character varying"
    char = "char"
    varchar = "varchar"
    text = "text"
    # Date/Time Types
    date = "date"
    time_without_time_zone = "time without time zone"
    time_with_time_zone = "time with time zone"
    timestamp_without_time_zone = "timestamp without time zone"
    timestamp_with_time_zone = "timestamp with time zone"
    interval_year_to_month = "interval year to month"
    interval_day_to_second = "interval day to second"
    # Boolean Type
    boolean = "boolean"
    # Advanced/Special Types
    super = "super"
    hllsketch = "hllsketch"
    varbyte = "varbyte"
    geometry = "geometry"
    geography = "geography"


REDSHIFT_TYPE_TO_LLM_TYPE_MAPPING = {
    # Numeric Types
    RedshiftDataTypeEnum.smallint.value: LLMTypeEnum.INT,
    RedshiftDataTypeEnum.integer.value: LLMTypeEnum.INT,
    RedshiftDataTypeEnum.bigint.value: LLMTypeEnum.INT,
    RedshiftDataTypeEnum.real.value: LLMTypeEnum.FLOAT,
    RedshiftDataTypeEnum.double_precision.value: LLMTypeEnum.FLOAT,
    RedshiftDataTypeEnum.numeric.value: LLMTypeEnum.FLOAT,
    RedshiftDataTypeEnum.decimal.value: LLMTypeEnum.FLOAT,
    # Character Types
    RedshiftDataTypeEnum.character.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.character_varying.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.char.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.varchar.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.text.value: LLMTypeEnum.STR,
    # Date/Time Types
    RedshiftDataTypeEnum.date.value: LLMTypeEnum.DATE,
    RedshiftDataTypeEnum.time_without_time_zone.value: LLMTypeEnum.TIME,
    RedshiftDataTypeEnum.time_with_time_zone.value: LLMTypeEnum.TIME,
    RedshiftDataTypeEnum.timestamp_without_time_zone.value: LLMTypeEnum.TS,
    RedshiftDataTypeEnum.timestamp_with_time_zone.value: LLMTypeEnum.TS,
    RedshiftDataTypeEnum.interval_year_to_month.value: LLMTypeEnum.DT,
    RedshiftDataTypeEnum.interval_day_to_second.value: LLMTypeEnum.DT,
    # Boolean Type
    RedshiftDataTypeEnum.boolean.value: LLMTypeEnum.BOOL,
    # Advanced/Special Types
    RedshiftDataTypeEnum.super.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.hllsketch.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.varbyte.value: LLMTypeEnum.BLOB,
    RedshiftDataTypeEnum.geometry.value: LLMTypeEnum.STR,
    RedshiftDataTypeEnum.geography.value: LLMTypeEnum.STR,
}


def redshift_type_to_llm_type(rs_type: str) -> LLMTypeEnum:
    """
    Convert redshift type simplified type representations suitable
    for LLM consumption.

    :param rs_type: A redshift type

    :returns: A new llm type name
    """
    if RedshiftDataTypeEnum.is_valid_value(rs_type):
        llm_type_name = REDSHIFT_TYPE_TO_LLM_TYPE_MAPPING[
            RedshiftDataTypeEnum.get_by_value(rs_type)
        ]
    else:
        llm_type_name = None
        for redshift_data_type in RedshiftDataTypeEnum:
            if rs_type.startswith(redshift_data_type.value):
                llm_type_name = REDSHIFT_TYPE_TO_LLM_TYPE_MAPPING[
                    redshift_data_type.value
                ]
                break
        if llm_type_name is None:
            raise ValueError(f"Unsupported Redshift type: {rs_type}")
    return llm_type_name


class SchemaTableFilter(BaseModel):
    schema_name: str = Field()
    include: list[str] = Field()
    exclude: list[str] = Field()


def _fetch_data(
    conn_or_engine: T_CONN_OR_ENGINE,
) -> T.Tuple[list[tuple], list[tuple], list[tuple]]:
    if isinstance(conn_or_engine, redshift_connector.Connection):
        with Session(conn_or_engine) as cursor:
            column_rows = cursor.execute(SqlEnum.column_info_sql).fetchall()
            table_rows = cursor.execute(SqlEnum.table_info_sql).fetchall()
            schema_rows = cursor.execute(SqlEnum.schema_info_sql).fetchall()
            return column_rows, table_rows, schema_rows
    elif isinstance(conn_or_engine, sa.Engine):
        with conn_or_engine.connect() as conn:
            column_rows = conn.execute(sa.text(SqlEnum.column_info_sql)).fetchall()
            column_rows = [tuple(row) for row in column_rows]

            table_rows = conn.execute(sa.text(SqlEnum.table_info_sql)).fetchall()
            table_rows = [tuple(row) for row in table_rows]

            schema_rows = conn.execute(sa.text(SqlEnum.schema_info_sql)).fetchall()
            schema_rows = [tuple(row) for row in schema_rows]
            return column_rows, table_rows, schema_rows
    else:  # pragma: no cover
        raise TypeError(
            "conn_or_engine must be either a redshift_connector.Connection or a sqlalchemy.Engine"
        )


def new_database_info(
    conn_or_engine: T_CONN_OR_ENGINE,
    db_name: str,
    schema_table_filter_list: T.Optional[list[SchemaTableFilter]] = None,
) -> DatabaseInfo:
    if schema_table_filter_list is None:
        schema_table_filter_list = list()
    schema_table_filter_mapping: dict[str, SchemaTableFilter] = {
        schema_table_filter.schema_name: schema_table_filter
        for schema_table_filter in schema_table_filter_list
    }

    column_rows, table_rows, schema_rows = _fetch_data(conn_or_engine)

    column_tuple_mapping: dict[str, dict[str, list[tuple]]] = {}
    for row in column_rows:
        schema_name = row[0]
        column_tuple_mapping.setdefault(schema_name, {})
        table_name = row[1]
        try:
            column_tuple_mapping[schema_name][table_name].append(row)
        except KeyError:
            column_tuple_mapping[schema_name][table_name] = [row]

    table_tuple_mapping: dict[str, list[tuple]] = {}
    table_name_set: set[str] = set()
    for row in table_rows:
        schema_name = row[0]
        table_name = row[1]
        try:
            table_tuple_mapping[schema_name].append(row)
        except KeyError:
            table_tuple_mapping[schema_name] = [row]
        table_name_set.add(table_name)

    schemas = list()
    for row in schema_rows:
        schema_name, schema_description = row[0], row[1]
        if schema_name in schema_table_filter_mapping:
            schema_table_filter = schema_table_filter_mapping[schema_name]
            include = schema_table_filter.include
            exclude = schema_table_filter.exclude
        else:
            include = []
            exclude = []

        tables = list()
        for table_row in table_tuple_mapping.get(schema_name, []):
            table_name = table_row[1]
            if not match(table_name, include, exclude):
                continue
            if table_name.endswith("_pkey"):
                if table_name[:-5] in table_name_set:
                    # Skip primary key tables
                    continue

            columns = list()
            for column_row in column_tuple_mapping.get(schema_name, {}).get(
                table_name, []
            ):
                column_info = ColumnInfo(
                    name=column_row[2],
                    type=column_row[3],
                    llm_type=redshift_type_to_llm_type(column_row[3]),
                    dist_key=column_row[5],
                    sort_key_position=column_row[6],
                    encoding=column_row[4],
                    notnull=column_row[7],
                )
                columns.append(column_info)
            table_info = TableInfo(
                object_type=ObjectTypeEnum.TABLE,
                name=table_name,
                dist_style=table_row[2],
                owner=table_row[3],
                columns=columns,
            )
            tables.append(table_info)

        schema_info = SchemaInfo(
            name=schema_name,
            comment=schema_description,
            tables=tables,
        )
        schemas.append(schema_info)

    database_info = DatabaseInfo(
        name=db_name,
        schemas=schemas,
    )

    return database_info
