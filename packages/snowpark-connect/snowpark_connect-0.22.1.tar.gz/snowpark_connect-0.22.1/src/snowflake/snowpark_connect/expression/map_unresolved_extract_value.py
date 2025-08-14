#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto

import snowflake.snowpark.functions as snowpark_fn
from snowflake.snowpark.types import ArrayType, MapType, StructType, _IntegralType
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn


def _check_if_array_type(
    child_typed_column: TypedColumn, extract_typed_column: TypedColumn
):
    extract_typed_column_type = extract_typed_column.types
    container_type = child_typed_column.types
    return (
        len(extract_typed_column_type) == 1
        and isinstance(extract_typed_column_type[0], ArrayType)
        and len(container_type) == 1
        and isinstance(container_type[0], _IntegralType)
    )


def map_unresolved_extract_value(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[str, TypedColumn]:
    from snowflake.snowpark_connect.expression.map_expression import (
        map_single_column_expression,
    )

    child_name, child_typed_column = map_single_column_expression(
        exp.unresolved_extract_value.child, column_mapping, typer
    )
    extract_name, extract_typed_column = map_single_column_expression(
        exp.unresolved_extract_value.extraction,
        column_mapping,
        typer,
    )
    spark_function_name = (
        f"{child_name}.{extract_name}"
        if isinstance(child_typed_column.typ, StructType)
        else f"{child_name}[{extract_name}]"
    )
    # Spark respects "spark.sql.caseSensitive" for struct fields
    # map keys are compared as-is
    if global_config.spark_sql_caseSensitive or isinstance(
        child_typed_column.typ, MapType
    ):
        extract_fn = snowpark_fn.get
    else:
        extract_fn = snowpark_fn.get_ignore_case
    # Set index to a dummy value before we use it later in the ansi mode check.
    index = snowpark_fn.lit(1)
    if _check_if_array_type(extract_typed_column, child_typed_column):
        # Set all non-valid array indices to NULL.
        # This is done because both conditions of a CASE WHEN statement are executed regardless of if the condition is true or not.
        # Getting a negative index in Snowflake throws an error; thus, we convert all non-valid array indices to NULL before getting the index.
        index = snowpark_fn.when(
            (snowpark_fn.array_size(child_typed_column.col) > extract_typed_column.col)
            & (extract_typed_column.col >= 0),
            extract_typed_column.col,
        ).otherwise(snowpark_fn.lit(None))
        result_exp = snowpark_fn.when(index.isNull(), snowpark_fn.lit(None)).otherwise(
            snowpark_fn.get(child_typed_column.col, index)
        )
    else:
        result_exp = extract_fn(child_typed_column.col, extract_typed_column.col)

    spark_sql_ansi_enabled = global_config.spark_sql_ansi_enabled

    if spark_sql_ansi_enabled and _check_if_array_type(
        extract_typed_column, child_typed_column
    ):
        result_exp = snowpark_fn.when(
            index.isNull(),
            child_typed_column.col.getItem("[snowpark_connect::INVALID_ARRAY_INDEX]"),
        ).otherwise(result_exp)

    return spark_function_name, TypedColumn(result_exp, lambda: typer.type(result_exp))
