# -*- coding: utf-8 -*-

"""
mcp_ohmy_sql Configuration System

This module defines the configuration system for the mcp_ohmy_sql MCP server, providing
a flexible JSON-based configuration that supports multiple databases and schemas.

The configuration system is built on Pydantic models for validation and type safety,
ensuring robust configuration handling for production deployments.
"""

import typing as T
import json
from pathlib import Path
from functools import cached_property

from pydantic import BaseModel, Field, field_validator

from ..constants import DbTypeEnum
from ..lazy_import import sa


class Settings(BaseModel):
    """
    Global settings for the MCP server.

    This class is currently empty but reserved for future global configuration
    options such as query timeout limits, result size limits, logging levels,
    and other server-wide settings.

    Example:

        In JSON configuration::

            {
                "settings": {}
            }
    """

    # enable_cache_for_schema: bool = Field(default=False)
    # cache_for_schema_expires: int = Field(default=3600)
    # enable_cache_for_query: bool = Field(default=False)
    # cache_for_query_expires: int = Field(default=600)


class TableFilter(BaseModel):
    """
    Table filtering configuration for database schemas.

    Provides include/exclude patterns to control which tables are accessible
    through the MCP server. Supports wildcards for flexible filtering.

    :param include: List of table names or patterns to include. If empty, includes
        all tables not in exclude list. Supports wildcards with '*'.
    :param exclude: List of table names or patterns to exclude. Supports wildcards
        with '*'. Applied after include filtering.

    **Examples**:
        Include specific tables only::

            {
                "include": ["users", "orders", "products"],
                "exclude": []
            }

        Exclude system and temporary tables::

            {
                "include": [],
                "exclude": ["pg_*", "information_schema", "tmp_*", "_backup_*"]
            }

        Mixed filtering::

            {
                "include": ["sales_*", "customer_*"],
                "exclude": ["*_temp", "*_staging"]
            }

    .. note::

        When both include and exclude are specified, tables must be in the
        include list AND not in the exclude list to be accessible.
    """

    include: list[str] = Field(
        default_factory=list,
        description="List of table names or patterns to include (supports wildcards)",
    )
    exclude: list[str] = Field(
        default_factory=list,
        description="List of table names or patterns to exclude (supports wildcards)",
    )


class Schema(BaseModel):
    """
    Database schema configuration.

    Defines a specific schema within a database and its table filtering rules.
    Each database can have multiple schemas, allowing fine-grained control over
    which parts of the database are accessible.


    :param name: Schema name. If None, uses the database's default schema.
        Some databases (like SQLite) don't have explicit schemas.
    :param table_filter: :class:`TableFilter` rules for this schema.

    **Examples**:
        Default schema with filtering::

            {
                "table_filter": {
                    "exclude": ["_migrations", "temp_*"]
                }
            }

        Named schema with specific tables::

            {
                "name": "reporting",
                "table_filter": {
                    "include": ["sales_summary", "customer_metrics"],
                    "exclude": []
                }
            }

        Multiple schemas for different purposes::

            [
                {
                    "name": "public",
                    "table_filter": {"exclude": ["audit_*"]}
                },
                {
                    "name": "analytics",
                    "table_filter": {"include": ["fact_*", "dim_*"]}
                }
            ]
    """

    name: T.Optional[str] = Field(
        default=None, description="Schema name. If None, uses database default schema"
    )
    table_filter: TableFilter = Field(
        default_factory=TableFilter, description="Table filtering rules for this schema"
    )


from .sqlalchemy import SqlalchemyConnection
from .aws_redshift import AWSRedshiftConnection

T_CONNECTION = T.Union[
    SqlalchemyConnection,
    AWSRedshiftConnection,
]


class Database(BaseModel):
    """
    Database configuration definition.

    Represents a single database connection with its schemas and access rules.
    Each database must have a unique identifier and can contain multiple schemas
    with different filtering rules.

    :param identifier: Unique identifier for this database. Used in MCP tools to
        reference specific databases. Must be unique across all databases
        in the configuration.
    :param description: Human-readable description of the database purpose or contents.
        Useful for documentation and understanding the database role.
    :param db_type: Database type identifier (e.g., 'sqlite', 'postgres', 'mysql',
        'aws_redshift'). Must match a valid :class:`~mcp_ohmy_sql.constants.DbTypeEnum` value.
    :param connection: Database connection configuration. The specific type depends
        on the database type (
        :class:`~mcp_ohmy_sql.config.sqlalchemy.SqlalchemyConnection`,
        :class:`~mcp_ohmy_sql.config.aws_redshift.AWSRedshiftConnection`,
        etc.).
    :param schemas: List of :class:`Schema` configurations for this database. Each schema can
        have its own table filtering rules.

    **Examples**:
        SQLite database::

            {
                "identifier": "app_db",
                "description": "Main application database",
                "db_type": "sqlite",
                "connection": {
                    ...
                },
                "schemas": [
                    {
                        "name": null,
                        "table_filter": {
                            "exclude": ["migrations", "temp_*"]
                        }
                    }
                ]
            }

    .. note::

        The connection field uses Pydantic's
        `discriminator feature <https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions>`_
        to automatically select the appropriate connection type based on
        the "type" field in the connection configuration.
    """

    identifier: str = Field(description="Unique identifier for this database")
    description: str = Field(
        default="", description="Human-readable description of the database"
    )
    db_type: str = Field(description="Database type (must match DbTypeEnum values)")
    connection: T_CONNECTION = Field(
        discriminator="type", description="Database connection configuration"
    )
    schemas: list[Schema] = Field(
        description="List of schema configurations for this database"
    )

    @field_validator("db_type", mode="after")
    @classmethod
    def check_name(cls, value: str) -> str:  # pragma: no cover
        """
        Validate the db_type field.
        """
        if DbTypeEnum.is_valid_value(value) is False:
            raise ValueError(f"{value} is not a valid value of {DbTypeEnum}")
        return value

    @property
    def db_type_enum(self) -> DbTypeEnum:
        """
        Get the database type as an :class:`~mcp_ohmy_sql.constants.DbTypeEnum`.
        """
        return DbTypeEnum.get_by_value(self.db_type)

    @cached_property
    def schemas_mapping(self) -> dict[str, Schema]:
        """
        Create a mapping of schema names to Schema objects.
        """
        mapping = {schema.name: schema for schema in self.schemas}
        if len(mapping) != len(self.schemas):
            raise ValueError(
                "Duplicate schema names found in database configuration! "
                "Each schema name must be unique."
            )
        return mapping

    @cached_property
    def sa_metadata(self) -> "sa.MetaData":
        """
        Create SQLAlchemy metadata for this database.
        """
        metadata = sa.MetaData()
        for schema in self.schemas:
            metadata.reflect(
                self.connection.sa_engine,
                schema=schema.name,
                views=True,
            )
        return metadata


class Config(BaseModel):
    """
    Root configuration object for the mcp_ohmy_sql MCP server.

    This is the main configuration class that contains all settings, database
    connections, and server configuration. It provides methods for loading
    and validating configuration from JSON files.

    :param version: Configuration schema version. Currently must be "0.1.1".
        Used for backward compatibility and migration handling.
    :param settings: Global server :class:`Settings`. For features like query timeouts,
        result limits, etc.
    :param databases: List of :class:`Database` configurations. Each database must have
        a unique identifier and can contain multiple schemas.

    **Configuration File Structure**:
        The JSON configuration file should follow this structure::

            {
                "version": "0.1.1",
                "settings": {...},
                "databases": [
                    {
                        "identifier": "my first database",
                        ...
                    }
                    {
                        "identifier": "my second database",
                        ...
                    }
                ]
            }

    **Usage**:
        Load from environment variable::

            import os
            from pathlib import Path

            config_path = Path(os.environ["MCP_OHMY_SQL_CONFIG"])
            config = Config.load(config_path)

        Access databases::

            # Get all databases
            for db in config.databases:
                print(f"Database: {db.identifier}")

            # Get specific database
            db = config.databases_mapping["my_db"]

            # Get database schemas
            for schema in db.schemas:
                print(f"Schema: {schema.name}")

    **Validation**:
        The configuration is validated when loaded using Pydantic. Common
        validation errors include:

        - Missing required fields (version, databases)
        - Invalid version number
        - Duplicate database identifiers
        - Invalid database types
        - Invalid connection configurations

    **Environment Loading**:
        The typical usage pattern is to load configuration from an environment
        variable that points to the JSON configuration file::

            export MCP_OHMY_SQL_CONFIG=/path/to/config.json

        This allows different configurations for different environments
        (development, staging, production) without code changes.

    **Troubleshooting**:
        Common configuration issues:

        1. **File not found**: Check MCP_OHMY_SQL_CONFIG environment variable
        2. **JSON syntax errors**: Validate JSON with a JSON linter
        3. **Validation errors**: Check field names and types match the schema
        4. **Connection errors**: Verify database URLs and credentials
        5. **Permission errors**: Ensure file is readable by the process
    """

    version: str = Field(description="Configuration schema version (currently '0.1.1')")
    settings: Settings = Field(
        default_factory=Settings, description="Global server settings"
    )
    databases: list[Database] = Field(description="List of database configurations")

    @classmethod
    def load(cls, path: Path) -> "Config":
        """
        Load configuration from a JSON file.

        Reads and parses a JSON configuration file, validates it against the
        configuration schema, and returns a Config object. Provides detailed
        error messages for common configuration problems.

        :paaram path: Path to the JSON configuration file. Must be readable by
            the current process.

        :returns: :class:`Config` Validated configuration object ready for use.

        :raises: If file cannot be read, JSON is invalid, or validation
            fails. Error messages include specific details about the
            failure to help with troubleshooting.

        This method performs three validation steps:

        1. File system access (can read the file)
        2. JSON parsing (valid JSON syntax)
        3. Schema validation (matches expected structure and types)
        """
        try:
            s = path.read_text()
        except Exception as e:  # pragma: no cover
            raise Exception(
                f"Failed to read configuration content from {path}! Error: {e!r}"
            )

        try:
            dct = json.loads(s)
        except Exception as e:  # pragma: no cover
            raise Exception(
                f"Failed to load configuration from {path}! Check your JSON content! Error: {e!r}"
            )

        try:
            config = cls(**dct)
        except Exception as e:  # pragma: no cover
            raise Exception(
                f"Configuration Validation failed! Check your JSON content! Error: {e!r}"
            )

        return config

    @cached_property
    def databases_mapping(self) -> dict[str, Database]:
        """
        Create a mapping of database identifiers to Database objects.
        """
        mapping = {db.identifier: db for db in self.databases}
        if len(mapping) != len(self.databases):
            raise ValueError(
                "Duplicate database identifiers found in configuration! "
                "Each database identifier must be unique."
            )
        return mapping
