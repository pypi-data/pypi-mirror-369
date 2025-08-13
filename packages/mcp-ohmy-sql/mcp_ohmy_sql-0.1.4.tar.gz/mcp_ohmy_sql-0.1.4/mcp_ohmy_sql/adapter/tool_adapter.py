# -*- coding: utf-8 -*-

import typing as T
import time
import textwrap

from ..constants import DbTypeEnum

from ..db.relational import api as relational_db
from ..db.aws_redshift import api as aws_redshift_db
from ..sa import api as sa_api
from ..aws.aws_redshift import api as aws_redshift_api

if T.TYPE_CHECKING:  # pragma: no cover
    from .adapter import Adapter


def format_query_result(
    duration: float,
    query_result_text: str,
):
    """
    Format query execution results with timing information for MCP tool output.
    """
    lines = [
        "# Execution Time",
        f"{duration:.3f} seconds",
        "",
        "# Query Result",
        query_result_text,
    ]
    return "\n".join(lines)


class ToolAdapterMixin:
    """
    MCP tools low level implementation.
    """

    def tool_list_databases(self: "Adapter") -> str:
        """
        List all configured databases with identifiers and basic information.

        Use this tool to discover available databases before exploring schemas
        or executing queries. Returns database identifiers needed for other tools.

        **Sample Output:**

        .. code-block:: typescript

            Available Databases:
            Database(
                identifier='production_db',
                db_type=postgres,
                description=Production PostgreSQL database,
                number_of_schemas=3,
                all_schemas=public,
            )
            Database(
                identifier='chinook_sqlite',
                db_type=sqlite,
                description=Sample music store database,
                number_of_schemas=1,
            )

        :returns: Formatted list of databases with identifiers, types, schema counts, and descriptions.
        """
        lines = [
            "Available Databases:",
        ]
        template = textwrap.dedent(
            """
            Database(
                identifier={identifier!r},
                db_type={db_type},
                description={description},
                number_of_schemas={number_of_schemas},
                all_schemas={all_schemas},
            )
        """
        ).strip()
        for database in self.config.databases:
            line = template.format(
                identifier=database.identifier,
                db_type=database.db_type,
                number_of_schemas=len(database.schemas),
                description=database.description or "No description",
                all_schemas=", ".join(
                    [schema.name for schema in database.schemas if schema.name]
                ),
            )
            lines.append(line)
        return "\n".join(lines)

    def tool_list_tables(
        self: "Adapter",
        database_identifier: str,
        schema_name: T.Optional[str] = None,
    ) -> str:
        """
        List tables, views, and materialized views in a database schema.

        Provides quick overview of available database objects with column counts
        and comments. Use this for discovery before getting detailed schema information.

        **Sample Output:**

        .. code-block:: typescript

            Available Tables, Views, and Materialized Views:

            - Table 'Album': 3 columns, Music album information
            - Table 'Artist': 2 columns, Recording artist details
            - Table 'Customer': 13 columns, Customer contact information
            - View 'AlbumSalesStats': 8 columns, Pre-calculated album sales metrics

        :param database_identifier: Database identifier from list_databases.
        :param schema_name: Optional schema name (uses default if None).
        :returns: List of tables/views with column counts and descriptions.
        """
        (flag, msg, database, schema) = self.get_database_and_schema_object(
            database_identifier, schema_name
        )
        if flag is False:
            return msg

        if database.db_type in [
            DbTypeEnum.SQLITE.value,
            DbTypeEnum.POSTGRESQL.value,
            DbTypeEnum.MYSQL.value,
            DbTypeEnum.MSSQL.value,
            DbTypeEnum.ORACLE.value,
        ]:
            schema_info = self.get_relational_schema_info(database, schema)
            lines = [
                "Available Tables, Views, and Materialized Views:",
            ]
            for table_info in schema_info.tables:
                line = f"- {table_info.object_type.table_type.value} {table_info.name!r}: {len(table_info.columns)} columns, {table_info.comment or 'No comment'}"
                lines.append(line)
            return "\n".join(lines)
        elif database.db_type == DbTypeEnum.AWS_REDSHIFT.value:
            database_info = self.get_aws_redshift_database_info(database)
            schema_info = database_info.schemas_mapping[schema.name]
            lines = [
                "Available Tables, Views, and Materialized Views:",
            ]
            for table_info in schema_info.tables:
                line = f"- {table_info.object_type.table_type.value} {table_info.name!r}: {len(table_info.columns)} columns, {table_info.comment or 'No comment'}"
                lines.append(line)
            return "\n".join(lines)
        else:
            raise NotImplementedError(
                f"Database type {database.db_type} is not supported."
            )

    def tool_get_all_database_details(self: "Adapter") -> str:
        """
        Get complete schema information for all configured databases.

        Returns detailed metadata for all databases, schemas, tables, columns,
        and relationships. Use this for comprehensive database discovery or when
        you need schema details across multiple databases.

        **Output Format:**

        .. code-block:: typescript

            <db_type> Database <identifier>(
              Schema <name>(
                Table <name>(
                  column:TYPE*CONSTRAINTS,
                  ...
                )
                ...
              )
              ...
            )

        **Constraints:** ``*PK`` (Primary Key), ``*FK->Table.Column`` (Foreign Key),
        ``*NN`` (Not Null), ``*UQ`` (Unique), ``*IDX`` (Indexed)

        **Sample Output:**

        .. code-block:: typescript

            sqlite Database chinook(
              Schema default(
                Table Album(
                  AlbumId:INT*PK*NN,
                  Title:STR*NN,
                  ArtistId:INT*NN*FK->Artist.ArtistId,
                )
                Table Artist(
                  ArtistId:INT*PK*NN,
                  Name:STR,
                )
              )
            )

        .. important::

            It is possible that the database connection is misconfigured or the
            database user doesn't have enough permission to get database schema,
            the response will explicitly state the error information.

        :returns: Complete schema information for all configured databases.
        """
        database_lines = []
        for database in self.config.databases:
            try:
                if database.db_type in [
                    DbTypeEnum.SQLITE.value,
                    DbTypeEnum.POSTGRESQL.value,
                    DbTypeEnum.MYSQL.value,
                    DbTypeEnum.MSSQL.value,
                    DbTypeEnum.ORACLE.value,
                ]:
                    database_info = self.get_relational_database_info(database)
                    s = relational_db.encode_database_info(database_info)
                    database_lines.append(s)
                elif database.db_type == DbTypeEnum.AWS_REDSHIFT.value:
                    database_info = self.get_aws_redshift_database_info(database)
                    s = aws_redshift_db.encode_database_info(database_info)
                    database_lines.append(s)
                else:
                    raise NotImplementedError(
                        f"Database type {database.db_type} is not supported."
                    )
            except Exception as e:
                s = f"Failed to get schema for database {database.identifier!r}, Error: {e!r}"
                database_lines.append(s)
        databases_def = "\n".join(database_lines)
        return databases_def

    def tool_get_schema_details(
        self: "Adapter",
        database_identifier: str,
        schema_name: T.Optional[str] = None,
    ) -> str:
        """
        **CRITICAL FOR SQL WRITING**: Get detailed schema for a specific database.

        **ALWAYS use this tool before writing SQL queries** to get exact table
        structures, column names, data types, and relationships for accurate SQL generation.

        **Output Format:**

        .. code-block:: typescript

            Schema <name>(
              Table <name>(
                column:TYPE*CONSTRAINTS,
                ...
              )
              View <name>(
                column:TYPE*CONSTRAINTS,
                ...
              )
              ...
            )

        **Constraints:** ``*PK`` (Primary Key), ``*FK->Table.Column`` (Foreign Key),
        ``*NN`` (Not Null), ``*UQ`` (Unique), ``*IDX`` (Indexed)

        **Sample Output:**

        .. code-block:: typescript

            Schema default(
              Table Album(
                AlbumId:INT*PK*NN,
                Title:STR*NN,
                ArtistId:INT*NN*FK->Artist.ArtistId,
              )
              Table Artist(
                ArtistId:INT*PK*NN,
                Name:STR,
              )
              View AlbumSalesStats(
                AlbumId:INT,
                AlbumTitle:STR,
                TotalRevenue:DEC,
              )
            )

        :param database_identifier: Database identifier from list_databases.
        :param schema_name: Optional schema name (uses default if None).
        :returns: Schema structure with tables, columns, types, and relationships.
        """
        (flag, msg, database, schema) = self.get_database_and_schema_object(
            database_identifier, schema_name
        )
        if flag is False:
            return msg

        if database.db_type in [
            DbTypeEnum.SQLITE.value,
            DbTypeEnum.POSTGRESQL.value,
            DbTypeEnum.MYSQL.value,
            DbTypeEnum.MSSQL.value,
            DbTypeEnum.ORACLE.value,
        ]:
            schema_info = self.get_relational_schema_info(database, schema)
            s = relational_db.encode_schema_info(schema_info)
            return s
        elif database.db_type == DbTypeEnum.AWS_REDSHIFT.value:
            database_info = self.get_aws_redshift_database_info(database)
            if schema.name in database_info.schemas_mapping:
                schema_info = database_info.schemas_mapping[schema.name]
                s = aws_redshift_db.encode_schema_info(schema_info)
                return s
            else:
                all_schema = ", ".join(
                    [name for name in database_info.schemas_mapping if name]
                )
                return f"Error: Schema '{schema.name}' not found in database '{database_identifier}', it has the following schemas: {all_schema}"
        else:
            raise NotImplementedError(
                f"Database type {database.db_type} is not supported."
            )

    def tool_execute_select_statement(
        self: "Adapter",
        database_identifier: str,
        sql: str,
        params: T.Optional[dict[str, T.Any]] = None,
    ) -> str:
        """
        Execute SELECT queries with performance timing and formatted results.

        **Read-only tool** that executes SELECT statements and returns execution time
        plus Markdown-formatted results. Use execution time (>1s = slow, >5s = needs optimization)
        to guide query performance decisions.

        **Sample Output:**

        .. code-block:: markdown

            # Execution Time
            0.045 seconds

            # Query Result
            | id | name     | email              |
            |----|----------|--------------------|
            | 1  | John Doe | john@example.com   |
            | 2  | Alice    | alice@example.com  |

        **Usage Examples:**

        .. code-block:: python

            # Simple query
            execute_select_statement("chinook_sqlite", "SELECT * FROM Album LIMIT 5")

            # Parameterized query (recommended for dynamic values)
            execute_select_statement(
                "chinook_sqlite",
                "SELECT * FROM Album WHERE ArtistId = :artist_id",
                {"artist_id": 1}
            )

        :param database_identifier: Database identifier from list_databases.
        :param sql: SELECT statement only (DDL/DML not permitted).
        :param params: Optional parameters for safe value substitution.
        :returns: Execution time and query results in Markdown table format.
        """
        start_time = time.time()
        if database_identifier not in self.config.databases_mapping:
            return (
                f"Error: Database '{database_identifier}' not found in configuration."
            )
        database = self.config.databases_mapping[database_identifier]
        if database.db_type in [
            DbTypeEnum.SQLITE.value,
            DbTypeEnum.POSTGRESQL.value,
            DbTypeEnum.MYSQL.value,
            DbTypeEnum.MSSQL.value,
            DbTypeEnum.ORACLE.value,
        ]:
            engine = database.connection.sa_engine
            query_result_text = sa_api.execute_select_query(
                engine=engine,
                query=sql,
                params=params,
            )
            duration = time.time() - start_time
            s = format_query_result(
                duration=duration,
                query_result_text=query_result_text,
            )
            return s
        elif database.db_type == DbTypeEnum.AWS_REDSHIFT.value:
            rs_conn = database.connection.rs_conn
            query_result_text = aws_redshift_api.execute_select_query(
                conn=rs_conn,
                query=sql,
                params=params,
            )
            duration = time.time() - start_time
            s = format_query_result(
                duration=duration, query_result_text=query_result_text
            )
            return s
        else:
            raise NotImplementedError(
                f"Database type {database.db_type} is not supported."
            )
