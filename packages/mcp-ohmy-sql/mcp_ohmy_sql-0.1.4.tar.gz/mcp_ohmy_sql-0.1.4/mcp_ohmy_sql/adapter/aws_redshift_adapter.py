# -*- coding: utf-8 -*-

"""
AWS Redshift adapter mixin for Redshift-specific database operations.
"""

import typing as T

from ..config.api import Database
from ..db.aws_redshift import api as aws_redshift

if T.TYPE_CHECKING:  # pragma: no cover
    from .adapter import Adapter


class AwsRedshiftAdapterMixin:
    """
    Adapter mixin for AWS Redshift operations using boto3, redshift-connector, and the db/aws_redshift module.
    """
    def get_aws_redshift_database_info(
        self: "Adapter",
        database: "Database",
    ) -> aws_redshift.DatabaseInfo:
        """
        Retrieves the database information for a specific database.

        :param database: The database object that contains the redshift connector and metadata.

        :returns: A DatabaseInfo object containing the all schema details.
        """
        database_info = aws_redshift.new_database_info(
            conn_or_engine=database.connection.sa_engine,
            db_name=database.identifier,
            schema_table_filter_list=[
                aws_redshift.SchemaTableFilter(
                    schema_name=schema.name,
                    include=schema.table_filter.include,
                    exclude=schema.table_filter.exclude,
                )
                for schema in database.schemas
            ],
        )
        return database_info
