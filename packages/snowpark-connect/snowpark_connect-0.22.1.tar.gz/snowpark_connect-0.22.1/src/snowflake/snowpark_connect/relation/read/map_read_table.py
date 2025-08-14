#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.errors.exceptions.base import AnalysisException

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark_connect.column_name_handler import ALREADY_QUOTED
from snowflake.snowpark_connect.config import auto_uppercase_non_column_identifiers
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.read.utils import (
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.utils.identifiers import (
    split_fully_qualified_spark_name,
)
from snowflake.snowpark_connect.utils.session import _get_current_snowpark_session
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def post_process_df(
    df: snowpark.DataFrame, plan_id: int, source_table_name: str = None
) -> DataFrameContainer:
    def _lower_or_unquote(string):
        return (
            string[1:-1].replace('""', '"')
            if ALREADY_QUOTED.match(string)
            else string.lower()
        )

    try:
        true_names = list(map(lambda x: _lower_or_unquote(x), df.columns))
        renamed_df, snowpark_column_names = rename_columns_as_snowflake_standard(
            df, plan_id
        )
        name_parts = split_fully_qualified_spark_name(source_table_name)

        # If table name is not fully qualified (only has table name, no database),
        # add current schema name to qualifiers so columns can be referenced with database prefix
        # Note: In Spark, "database" corresponds to Snowflake "schema"
        if source_table_name and len(name_parts) == 1:
            session = _get_current_snowpark_session()
            current_schema = session.get_current_schema()
            if current_schema:
                name_parts = [unquote_if_quoted(current_schema)] + name_parts

        return DataFrameContainer.create_with_column_mapping(
            dataframe=renamed_df,
            spark_column_names=true_names,
            snowpark_column_names=snowpark_column_names,
            snowpark_column_types=[f.datatype for f in df.schema.fields],
            column_qualifiers=[name_parts] * len(true_names)
            if source_table_name
            else None,
        )
    except SnowparkSQLException as e:
        # Check if this is a table/view not found error
        # Snowflake error codes: 002003 (42S02) - Object does not exist or not authorized
        if hasattr(e, "sql_error_code") and e.sql_error_code == 2003:
            raise AnalysisException(
                f"[TABLE_OR_VIEW_NOT_FOUND] The table or view cannot be found. {source_table_name}"
            ) from None  # Suppress original exception to reduce message size
        # Re-raise if it's not a table not found error
        raise


def get_table_from_name(
    table_name: str, session: snowpark.Session, plan_id: int
) -> DataFrameContainer:
    """Get table from name returning a container."""
    snowpark_name = ".".join(
        quote_name_without_upper_casing(part)
        for part in split_fully_qualified_spark_name(table_name)
    )

    if auto_uppercase_non_column_identifiers():
        snowpark_name = snowpark_name.upper()

    df = session.read.table(snowpark_name)
    return post_process_df(df, plan_id, table_name)


def get_table_from_query(
    query: str, session: snowpark.Session, plan_id: int
) -> snowpark.DataFrame:
    df = session.sql(query)
    return post_process_df(df, plan_id)


def map_read_table(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Read a table into a Snowpark DataFrame.
    """
    session: snowpark.Session = _get_current_snowpark_session()
    if rel.read.HasField("named_table"):
        table_identifier = rel.read.named_table.unparsed_identifier
    elif (
        rel.read.data_source.HasField("format")
        and rel.read.data_source.format.lower() == "iceberg"
    ):
        if len(rel.read.data_source.paths) != 1:
            raise SnowparkConnectNotImplementedError(
                f"Unexpected paths: {rel.read.data_source.paths}"
            )
        table_identifier = rel.read.data_source.paths[0]
    else:
        raise ValueError("The relation must have a table identifier.")
    return get_table_from_name(table_identifier, session, rel.common.plan_id)
