#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import copy

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.dataframe_reader import DataFrameReader
from snowflake.snowpark.types import StringType, StructField, StructType
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.read.map_read import CsvReaderConfig
from snowflake.snowpark_connect.relation.read.utils import (
    get_spark_column_names_from_snowpark_columns,
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_read_csv(
    rel: relation_proto.Relation,
    schema: snowpark.types.StructType | None,
    session: snowpark.Session,
    paths: list[str],
    options: CsvReaderConfig,
) -> DataFrameContainer:
    """
    Read a CSV file into a Snowpark DataFrame.

    We leverage the stage that is already created in the map_read function that
    calls this.
    """

    if rel.read.is_streaming is True:
        # TODO: Structured streaming implementation.
        raise SnowparkConnectNotImplementedError(
            "Streaming is not supported for CSV files."
        )
    else:
        snowpark_options = options.convert_to_snowpark_args()
        raw_options = rel.read.data_source.options
        if schema is None or (
            snowpark_options.get("PARSE_HEADER", False)
            and raw_options.get("enforceSchema", "True").lower() == "false"
        ):  # Schema has to equals to header's format
            reader = session.read.options(snowpark_options)
        else:
            reader = session.read.options(snowpark_options).schema(schema)
        df = read_data(
            reader,
            schema,
            session,
            paths[0],
            snowpark_options,
            raw_options,
        )
        if len(paths) > 1:
            # TODO: figure out if this is what Spark does.
            for p in paths[1:]:
                df = df.union_all(reader.csv(p))

        if schema is None:
            df = df.select(
                [snowpark_fn.col(c).cast("STRING").alias(c) for c in df.schema.names]
            )

        spark_column_names = get_spark_column_names_from_snowpark_columns(df.columns)

        renamed_df, snowpark_column_names = rename_columns_as_snowflake_standard(
            df, rel.common.plan_id
        )
        return DataFrameContainer.create_with_column_mapping(
            dataframe=renamed_df,
            spark_column_names=spark_column_names,
            snowpark_column_names=snowpark_column_names,
            snowpark_column_types=[f.datatype for f in df.schema.fields],
        )


def get_header_names(
    session: snowpark.Session,
    path: list[str],
    snowpark_options: dict,
) -> list[str]:
    snowpark_options_no_header = copy.copy(snowpark_options)
    snowpark_options_no_header["PARSE_HEADER"] = False

    header_df = session.read.options(snowpark_options_no_header).csv(path).limit(1)
    header_data = header_df.collect()[0]
    return [
        f'"{header_data[i]}"'
        for i in range(len(header_df.schema.fields))
        if header_data[i] is not None
    ]


def read_data(
    reader: DataFrameReader,
    schema: snowpark.types.StructType | None,
    session: snowpark.Session,
    path: list[str],
    snowpark_options: dict,
    raw_options: dict,
) -> snowpark.DataFrame:
    df = reader.csv(path)
    filename = path.strip("/").split("/")[-1]
    if schema is not None:
        if len(schema.fields) != len(df.schema.fields):
            raise Exception(f"csv load from {filename} failed.")
        if raw_options.get("enforceSchema", "True").lower() == "false":
            for i in range(len(schema.fields)):
                if (
                    schema.fields[i].name != df.schema.fields[i].name
                    and f'"{schema.fields[i].name}"' != df.schema.fields[i].name
                ):
                    raise Exception("CSV header does not conform to the schema")
        return df

    headers = get_header_names(session, path, snowpark_options)

    # Handle mismatch in column count between header and data
    if (
        len(df.schema.fields) == 1
        and df.schema.fields[0].name.upper() == "C1"
        and snowpark_options.get("PARSE_HEADER") is True
        and len(headers) != len(df.schema.fields)
    ):
        df = (
            session.read.options(snowpark_options)
            .schema(StructType([StructField(h, StringType(), True) for h in headers]))
            .csv(path)
        )
    elif snowpark_options.get("PARSE_HEADER") is False and len(headers) != len(
        df.schema.fields
    ):
        return df.select([df.schema.fields[i].name for i in range(len(headers))])

    return df
