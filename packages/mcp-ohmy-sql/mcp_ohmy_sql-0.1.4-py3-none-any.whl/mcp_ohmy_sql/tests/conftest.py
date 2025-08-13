# -*- coding: utf-8 -*-

import typing as T
import os
import dataclasses

import pytest
import sqlalchemy as sa
import redshift_connector
from which_runtime.api import runtime

# ===== Top-level modules
from mcp_ohmy_sql.constants import ObjectTypeEnum, DbTypeEnum, EnvVarEnum
from mcp_ohmy_sql.paths import path_sample_config

# ===== DB modules
from mcp_ohmy_sql.db.relational.schema_1_model import (
    ForeignKeyInfo,
    ColumnInfo,
    TableInfo,
    SchemaInfo,
    DatabaseInfo,
)
from mcp_ohmy_sql.db.relational.schema_3_extractor import (
    new_foreign_key_info,
    new_column_info,
    new_table_info,
    new_schema_info,
    new_database_info,
)

# ===== Config modules
from mcp_ohmy_sql.config.define import Config

# ===== Hub modules
from mcp_ohmy_sql.adapter.adapter import Adapter

# ===== Test modules
from mcp_ohmy_sql.tests.test_config import setup_test_config

# --- Chinook modules
from mcp_ohmy_sql.tests.chinook.chinook_data_model import (
    Base,
    ChinookTableNameEnum,
    ChinookViewNameEnum,
    VIEW_NAME_AND_SELECT_STMT_MAP,
    Album,
)
from mcp_ohmy_sql.tests.setup_relational_database import (
    drop_all_tables,
    create_all_tables,
    insert_all_data,
    drop_all_views,
    create_all_views,
)

if runtime.is_local_runtime_group:
    from mcp_ohmy_sql.tests.setup_aws_redshift_database import (
        drop_all_redshift_tables,
        create_all_redshift_tables,
        insert_all_data_to_redshift,
    )
from mcp_ohmy_sql.tests.test_config import DatabaseEnum


@dataclasses.dataclass
class SaEngineObjs:
    """
    Data container for SQLAlchemy engine, metadata, and database type.
    """

    engine: sa.Engine
    metadata: sa.MetaData
    db_type: DbTypeEnum


@dataclasses.dataclass
class SaSchemaObjs:
    """
    Data container for all sqlalchemy Table, Column, and ForeignKey objects
    """

    t_album: sa.Table
    c_album_album_id: sa.Column
    c_album_title_id: sa.Column
    c_album_artist_id: sa.Column
    fk_album_artist_id: sa.ForeignKey
    t_album_sales_stats: sa.Table


@dataclasses.dataclass
class SaSchemaInfoObjs:
    """
    Data container for all sqlalchemy schema information objects.
    """

    fk_album_artist_id_info: ForeignKeyInfo
    c_album_album_id_info: ColumnInfo
    c_album_title_id_info: ColumnInfo
    c_album_artist_id_info: ColumnInfo
    t_album_info: TableInfo
    v_album_sales_stats_info: TableInfo
    schema_info: SchemaInfo
    database_info: DatabaseInfo


# ------------------------------------------------------------------------------
# In-memory SQLite database fixtures
# ------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def in_memory_sqlite_engine_objs():
    """
    Fixture to create an in-memory SQLite database engine for testing.

    This fixture sets up a new SQLite database in memory, creates the necessary tables,
    and returns the engine. The database is reset after each test function.
    """
    engine = sa.create_engine("sqlite:///:memory:")

    # create tables and views
    create_all_tables(engine=engine, metadata=Base.metadata)
    create_all_views(engine=engine, db_type=DbTypeEnum.SQLITE)

    # get the latest metadata with views
    metadata = sa.MetaData()
    metadata.reflect(engine, views=True)

    yield SaEngineObjs(
        engine=engine,
        metadata=metadata,
        db_type=DbTypeEnum.SQLITE,
    )

    # drop views and tables
    drop_all_views(engine=engine, db_type=DbTypeEnum.SQLITE)
    drop_all_tables(engine=engine, metadata=Base.metadata)
    # clear metadata
    metadata.clear()


@pytest.fixture(scope="function")
def in_memory_sqlite_sa_objects(
    in_memory_sqlite_engine_objs,
) -> SaSchemaObjs:
    """
    Fixture to extract SQLAlchemy schema objects from the in-memory SQLite database.
    """
    metadata = in_memory_sqlite_engine_objs.metadata

    t_album = metadata.tables[ChinookTableNameEnum.Album.value]

    c_album_album_id = t_album.columns[Album.AlbumId.name]
    c_album_title_id = t_album.columns[Album.Title.name]
    c_album_artist_id = t_album.columns[Album.ArtistId.name]

    fk_album_artist_id = list(c_album_artist_id.foreign_keys)[0]

    t_album_sales_stats = metadata.tables[ChinookViewNameEnum.AlbumSalesStats.value]

    return SaSchemaObjs(
        t_album=t_album,
        c_album_album_id=c_album_album_id,
        c_album_title_id=c_album_title_id,
        c_album_artist_id=c_album_artist_id,
        fk_album_artist_id=fk_album_artist_id,
        t_album_sales_stats=t_album_sales_stats,
    )


@pytest.fixture(scope="function")
def in_memory_sqlite_sa_schema_info_objects(
    in_memory_sqlite_engine_objs,
    in_memory_sqlite_sa_objects,
) -> SaSchemaInfoObjs:
    """
    Fixture to create schema information objects for the in-memory SQLite database.
    """
    engine = in_memory_sqlite_engine_objs.engine
    metadata = in_memory_sqlite_engine_objs.metadata
    sa_objs = in_memory_sqlite_sa_objects

    fk_album_artist_id_info = new_foreign_key_info(sa_objs.fk_album_artist_id)

    c_album_album_id_info = new_column_info(
        table=sa_objs.t_album,
        column=sa_objs.c_album_album_id,
    )
    c_album_title_id_info = new_column_info(
        table=sa_objs.t_album,
        column=sa_objs.c_album_title_id,
    )
    c_album_artist_id_info = new_column_info(
        table=sa_objs.t_album,
        column=sa_objs.c_album_artist_id,
    )
    t_album_info = new_table_info(
        table=sa_objs.t_album,
        object_type=ObjectTypeEnum.TABLE,
    )
    v_album_sales_stats_info = new_table_info(
        table=sa_objs.t_album_sales_stats,
        object_type=ObjectTypeEnum.VIEW,
    )

    schema_info = new_schema_info(
        engine=engine,
        metadata=metadata,
        schema_name=None,
        exclude=["PlaylistTrack", "Playlist"],
    )
    database_info = new_database_info(
        name="Chinook",
        db_type=DbTypeEnum.SQLITE,
        schemas=[schema_info],
    )
    schema_info_objs = SaSchemaInfoObjs(
        fk_album_artist_id_info=fk_album_artist_id_info,
        c_album_album_id_info=c_album_album_id_info,
        c_album_title_id_info=c_album_title_id_info,
        c_album_artist_id_info=c_album_artist_id_info,
        t_album_info=t_album_info,
        v_album_sales_stats_info=v_album_sales_stats_info,
        schema_info=schema_info,
        database_info=database_info,
    )

    return schema_info_objs


# ------------------------------------------------------------------------------
# Config and Adapter
# ------------------------------------------------------------------------------
@pytest.fixture(scope="class")
def mcp_ohmy_sql_config() -> Config:
    os.environ[EnvVarEnum.MCP_OHMY_SQL_CONFIG.name] = str(path_sample_config)
    setup_test_config()
    config = Config.load(path=path_sample_config)
    return config


@pytest.fixture(scope="class")
def mcp_ohmy_sql_adapter(mcp_ohmy_sql_config) -> Adapter:
    adapter = Adapter(
        config=mcp_ohmy_sql_config,
    )
    return adapter


@pytest.fixture(scope="class")
def sa_engine_factory():
    """ """
    created_sa_engine_objs_list: list[SaEngineObjs] = list()

    def _create_sa_engine_objs(
        engine: sa.Engine,
        db_type: DbTypeEnum,
    ) -> SaEngineObjs:
        # drop all tables and views
        drop_all_views(engine=engine, db_type=db_type)
        drop_all_tables(engine=engine, metadata=Base.metadata)
        # create tables and views
        create_all_tables(engine=engine, metadata=Base.metadata)
        create_all_views(engine=engine, db_type=db_type)
        # insert all data
        insert_all_data(engine=engine, metadata=Base.metadata)

        # get the latest metadata with views
        metadata = sa.MetaData()
        metadata.reflect(engine, views=True)

        sa_engine_objs = SaEngineObjs(
            engine=engine,
            metadata=metadata,
            db_type=db_type,
        )
        created_sa_engine_objs_list.append(sa_engine_objs)
        return sa_engine_objs

    yield _create_sa_engine_objs

    for sa_engine_objs in created_sa_engine_objs_list:
        engine = sa_engine_objs.engine
        metadata = sa_engine_objs.metadata
        db_type = sa_engine_objs.db_type

        # drop views
        drop_all_views(engine=engine, db_type=db_type)
        drop_all_tables(engine=engine, metadata=Base.metadata)

        # clear metadata
        metadata.clear()


@pytest.fixture(scope="class")
def sqlite_sa_engine_objs(
    sa_engine_factory,
) -> SaEngineObjs:
    return sa_engine_factory(
        engine=DatabaseEnum.chinook_sqlite.connection.sa_engine,
        db_type=DbTypeEnum.SQLITE,
    )


@pytest.fixture(scope="class")
def postgres_sa_engine_objs(
    sa_engine_factory,
) -> SaEngineObjs:
    return sa_engine_factory(
        engine=DatabaseEnum.chinook_postgres.connection.sa_engine,
        db_type=DbTypeEnum.POSTGRESQL,
    )


# ------------------------------------------------------------------------------
# AWS Redshift fixtures
# ------------------------------------------------------------------------------
@pytest.fixture(scope="class")
def rs_conn() -> "redshift_connector.Connection":
    """
    Create Redshift Connection and prepare the database with all tables, views,
    and data for testing.
    """
    conn = DatabaseEnum.chinook_redshift.connection.rs_conn
    return conn


@pytest.fixture(scope="class")
def rs_engine() -> "sa.Engine":
    """
    Create Redshift Connection and prepare the database with all tables, views,
    and data for testing.
    """
    engine = DatabaseEnum.chinook_redshift.connection.sa_engine
    return engine


@pytest.fixture(scope="class")
def rs_tables(
    rs_conn,
    rs_engine,
):
    """
    Create all Redshift tables for testing.
    This fixture is used to prepare the database with tables for testing.
    """
    # conn_or_engine = rs_conn
    conn_or_engine = rs_engine
    drop_all_redshift_tables(conn_or_engine)
    create_all_redshift_tables(conn_or_engine)


@pytest.fixture(scope="class")
def rs_data(
    rs_conn,
    rs_engine,
    rs_tables,
) -> None:
    """
    Insert all data into the Redshift database.
    This fixture is used to prepare the database with data for testing.
    """
    # insert_all_data_to_redshift(rs_conn)
    insert_all_data_to_redshift(rs_engine)
