#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import copy
import json
import typing
from contextlib import suppress
from datetime import datetime

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import unquote_if_quoted
from snowflake.snowpark.row import Row
from snowflake.snowpark.types import (
    ArrayType,
    DataType,
    DateType,
    MapType,
    NullType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.read.map_read import JsonReaderConfig
from snowflake.snowpark_connect.relation.read.utils import (
    get_spark_column_names_from_snowpark_columns,
    rename_columns_as_snowflake_standard,
)
from snowflake.snowpark_connect.type_mapping import (
    cast_to_match_snowpark_type,
    map_simple_types,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_read_json(
    rel: relation_proto.Relation,
    schema: StructType | None,
    session: snowpark.Session,
    paths: list[str],
    options: JsonReaderConfig,
) -> DataFrameContainer:
    """
    Read a JSON file into a Snowpark DataFrame.

    [JSON lines](http://jsonlines.org/) file format is supported.

    We leverage the stage that is already created in the map_read function that
    calls this.
    """

    if rel.read.is_streaming is True:
        # TODO: Structured streaming implementation.
        raise SnowparkConnectNotImplementedError(
            "Streaming is not supported for JSON files."
        )
    else:
        snowpark_options = options.convert_to_snowpark_args()
        snowpark_options["infer_schema"] = True

        rows_to_infer_schema = snowpark_options.pop("rowstoinferschema", 1000)
        dropFieldIfAllNull = snowpark_options.pop("dropfieldifallnull", False)

        reader = session.read.options(snowpark_options)

        df = reader.json(paths[0])
        if len(paths) > 1:
            # TODO: figure out if this is what Spark does.
            for p in paths[1:]:
                df = df.union_all(session.read.options(snowpark_options).json(p))

        if schema is None:
            schema = copy.deepcopy(df.schema)
            infer_row_counts = 0

            columns_with_valid_contents = set()
            for row in df.to_local_iterator():
                infer_row_counts += 1
                if (
                    rows_to_infer_schema != -1
                    and infer_row_counts > rows_to_infer_schema
                ):
                    break
                schema = merge_row_schema(
                    schema, row, columns_with_valid_contents, dropFieldIfAllNull
                )

            if dropFieldIfAllNull:
                schema.fields = [
                    sf
                    for sf in schema.fields
                    if unquote_if_quoted(sf.name) in columns_with_valid_contents
                ]

        df = construct_dataframe_by_schema(
            schema, df.to_local_iterator(), session, snowpark_options
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


def merge_json_schema(
    content: typing.Any,
    schema: StructType | None,
    dropFieldIfAllNull: bool = False,
) -> DataType:
    if content is None:
        if schema is not None:
            return schema
        return NullType()

    if isinstance(content, str):
        with suppress(json.JSONDecodeError):
            json_content = json.loads(content)
            if not isinstance(json_content, str):
                content = json_content

    if isinstance(content, dict):
        current_schema = StructType()

        existed_schema = {}
        if schema is not None and schema.type_name() == "struct":
            for sf in schema.fields:
                existed_schema[sf.name] = sf.datatype

        for k, v in content.items():
            col_name = f'"{unquote_if_quoted(k)}"'
            existed_data_type = existed_schema.get(col_name, None)
            next_level_schema = merge_json_schema(
                v, existed_data_type, dropFieldIfAllNull
            )

            if (
                existed_data_type is not None
                or not dropFieldIfAllNull
                or not isinstance(next_level_schema, NullType)
            ):
                # Drop field if it's always null
                current_schema.add(StructField(col_name, next_level_schema))
            if existed_data_type is not None:
                del existed_schema[col_name]

        for k, v in existed_schema.items():
            col_name = f'"{unquote_if_quoted(k)}"'
            current_schema.add(StructField(col_name, v))

    elif isinstance(content, list):
        # ArrayType(*) need to have element schema inside, it would be NullType() as placeholder and keep updating while enumerating
        inner_schema = NullType()
        if schema is not None and schema.type_name() == "list":
            inner_schema = schema.element_type
        if len(content) > 0:
            for v in content:
                inner_schema = merge_json_schema(v, inner_schema, dropFieldIfAllNull)
        if isinstance(inner_schema, NullType) and dropFieldIfAllNull:
            return NullType()
        current_schema = ArrayType(inner_schema)
    else:
        current_schema = map_simple_types(type(content).__name__)

    # If there's conflict , use StringType
    if (
        schema is not None
        and schema != NullType()
        and current_schema is not None
        and current_schema != NullType()
        and schema.type_name() != current_schema.type_name()
    ):
        return StringType()

    current_schema.structured = True
    return current_schema


def merge_row_schema(
    schema: StructType | None,
    row: Row,
    columns_with_valid_contents: set,
    dropFieldIfAllNull: bool = False,
) -> StructType | NullType:
    if row is None:
        if schema is not None:
            return schema
        return NullType()
    new_schema = StructType()

    for sf in schema.fields:
        col_name = unquote_if_quoted(sf.name)
        if isinstance(sf.datatype, (StructType, MapType, StringType)):
            next_level_content = row[col_name]
            if next_level_content is not None:
                with suppress(json.JSONDecodeError):
                    if isinstance(next_level_content, datetime):
                        next_level_content = str(next_level_content)
                    next_level_content = json.loads(next_level_content)
                if isinstance(next_level_content, dict):
                    sf.datatype = merge_json_schema(
                        next_level_content,
                        None
                        if not isinstance(sf.datatype, StructType)
                        else sf.datatype,
                        dropFieldIfAllNull,
                    )
                else:
                    sf.datatype = StringType()
                columns_with_valid_contents.add(col_name)

        elif isinstance(sf.datatype, ArrayType):
            content = row[col_name]
            if content is not None:
                with suppress(Exception):
                    decoded_content = json.loads(content)
                    if isinstance(decoded_content, list):
                        content = decoded_content
                if not isinstance(content, list):
                    sf.datatype = StringType()
                else:
                    for v in content:
                        if v is not None:
                            columns_with_valid_contents.add(col_name)
                        sf.datatype.element_type = merge_json_schema(
                            v,
                            sf.datatype.element_type,
                            dropFieldIfAllNull,
                        )
        elif isinstance(sf.datatype, TimestampType):
            sf.datatype = StringType()
            columns_with_valid_contents.add(col_name)
        elif row[col_name] is not None:
            columns_with_valid_contents.add(col_name)

        sf.datatype.structured = True
        new_schema.add(sf)

    return schema


def union_data_into_df(
    result_df: snowpark.DataFrame,
    data: typing.List[Row],
    schema: StructType,
    session: snowpark.Session,
) -> snowpark.DataFrame:
    current_df = session.create_dataframe(
        data=data,
        schema=schema,
    )
    if result_df is None:
        return current_df

    return result_df.union(current_df)


def construct_dataframe_by_schema(
    schema: StructType,
    rows: typing.Iterator[Row],
    session: snowpark.Session,
    snowpark_options: dict,
    batch_size: int = 1000,
) -> snowpark.DataFrame:
    result = None

    current_data = []
    for row in rows:
        current_data.append(construct_row_by_schema(row, schema, snowpark_options))
        if len(current_data) >= batch_size:
            result = union_data_into_df(
                result,
                current_data,
                schema,
                session,
            )

            current_data = []

    if len(current_data) > 0:
        result = union_data_into_df(
            result,
            current_data,
            schema,
            session,
        )

        current_data = []

    if result is None:
        raise ValueError("Dataframe cannot be empty")
    return result


def construct_row_by_schema(
    content: typing.Any, schema: DataType, snowpark_options: dict
) -> None | DataType:
    if content is None:
        return None
    elif isinstance(schema, StructType):
        result = {}
        if isinstance(content, (dict, Row)):
            for sf in schema.fields:
                col_name = unquote_if_quoted(sf.name)
                quoted_col_name = (
                    f'"{col_name}"' if isinstance(content, Row) else col_name
                )
                result[quoted_col_name] = construct_row_by_schema(
                    (content.as_dict() if isinstance(content, Row) else content).get(
                        col_name, None
                    ),
                    sf.datatype,
                    snowpark_options,
                )
        elif isinstance(content, str):
            with suppress(json.JSONDecodeError):
                decoded_content = json.loads(content)
                if isinstance(decoded_content, dict):
                    content = decoded_content
            for sf in schema.fields:
                col_name = unquote_if_quoted(sf.name)
                result[col_name] = construct_row_by_schema(
                    content.get(col_name, None), sf.datatype, snowpark_options
                )
        else:
            raise SnowparkConnectNotImplementedError(
                f"JSON construct {str(content)} to StructType failed"
            )
        return result
    elif isinstance(schema, ArrayType):
        result = []
        inner_schema = schema.element_type
        if isinstance(content, str):
            content = json.loads(content)
        for ele in content:
            result.append(construct_row_by_schema(ele, inner_schema, snowpark_options))
        return result
    elif isinstance(schema, DateType):
        return cast_to_match_snowpark_type(
            schema, content, snowpark_options.get("DATE_FORMAT")
        )

    return cast_to_match_snowpark_type(schema, content)
