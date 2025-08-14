#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto

import snowflake.snowpark.functions as snowpark_fn
import snowflake.snowpark_connect.proto.snowflake_expression_ext_pb2 as snowflake_proto
from snowflake.snowpark.types import BooleanType
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import push_evaluating_sql_scope
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_extension(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], TypedColumn]:
    """
    The Extension relation type contains any extensions we use for adding new
    functionality to Spark Connect.

    The extension will require new protobuf messages to be defined in the
    snowflake_connect_server/proto directory.
    """
    extension = snowflake_proto.ExpExtension()
    exp.extension.Unpack(extension)
    match extension.WhichOneof("op"):
        case "named_argument":
            from snowflake.snowpark_connect.expression.map_expression import (
                map_expression,
            )

            named_argument = extension.named_argument
            key = named_argument.key
            value = named_argument.value

            exp_name, typed_col = map_expression(value, column_mapping, typer)
            if value.HasField("literal"):
                name = key
            elif value.HasField("unresolved_attribute"):
                name = "__" + key + "__" + exp_name[0]
            else:
                raise SnowparkConnectNotImplementedError(
                    "Named argument not supported yet for this input."
                )
            return [name], typed_col

        case "subquery_expression":
            from snowflake.snowpark_connect.expression.map_expression import (
                map_expression,
            )
            from snowflake.snowpark_connect.relation.map_relation import map_relation

            with push_evaluating_sql_scope():
                df_container = map_relation(extension.subquery_expression.input)
                df = df_container.dataframe

            queries = df.queries["queries"]
            if len(queries) != 1:
                raise SnowparkConnectNotImplementedError(
                    f"Unexpected number of queries: {len(queries)}"
                )
            query = f"({queries[0]})"

            match extension.subquery_expression.subquery_type:
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_SCALAR:
                    name = "scalarsubquery()"
                    result_exp = snowpark_fn.expr(query)
                    result_type = df.schema[0].datatype
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_EXISTS:
                    name = "exists()"
                    result_exp = snowpark_fn.expr(f"(EXISTS {query})")
                    result_type = BooleanType()
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_TABLE_ARG:
                    # TODO: Currently, map_sql.py handles this, so we never end up here.
                    raise SnowparkConnectNotImplementedError("Unexpected table arg")
                case snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_IN:
                    cols = [
                        map_expression(e, column_mapping, typer)
                        for e in extension.subquery_expression.in_subquery_values
                    ]
                    col_names_str = ", ".join(
                        col_name for col_names, _ in cols for col_name in col_names
                    )
                    # TODO: Figure out how to make a named_struct(...) here to match Spark.
                    name = f"({col_names_str}) in (listquery())"
                    result_exp = snowpark_fn.in_(
                        [col.col for _, col in cols], snowpark_fn.expr(query)
                    )
                    result_type = BooleanType()
                case other:
                    raise SnowparkConnectNotImplementedError(
                        f"Unexpected subquery type: {other}"
                    )

            return [name], TypedColumn(result_exp, lambda: [result_type])

        case other:
            raise SnowparkConnectNotImplementedError(f"Unexpected extension {other}")
