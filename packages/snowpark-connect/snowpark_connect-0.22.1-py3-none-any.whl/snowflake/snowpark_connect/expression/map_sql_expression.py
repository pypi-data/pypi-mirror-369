#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import re
from contextvars import ContextVar
from functools import cache

import jpype
import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
import pyspark.sql.connect.proto.types_pb2 as types_proto
from google.protobuf.any_pb2 import Any
from pyspark.errors.exceptions.base import AnalysisException

import snowflake.snowpark_connect.proto.snowflake_expression_ext_pb2 as snowflake_proto
from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_sql_named_arg,
    get_sql_plan,
    get_sql_pos_arg,
    push_evaluating_sql_scope,
    push_sql_scope,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

from .typer import ExpressionTyper

DECIMAL_RE = re.compile(r"decimal\((\d+), *(\d+)\)")

_window_specs = ContextVar[dict[str, any]]("_window_specs", default={})


@cache
def sql_parser():
    return jpype.JClass("org.apache.spark.sql.execution.SparkSqlParser")()


@cache
def _as_java_list():
    return jpype.JClass("scala.collection.JavaConverters").seqAsJavaList


def as_java_list(obj):
    return _as_java_list()(obj)


@cache
def _as_java_map():
    return jpype.JClass("scala.collection.JavaConverters").mapAsJavaMap


def as_java_map(obj):
    return _as_java_map()(obj)


def as_scala_seq(input):
    inputList = as_java_list(input)
    return (
        jpype.JClass("scala.collection.JavaConverters")
        .asScalaIteratorConverter(inputList.iterator())
        .asScala()
        .toSeq()
    )


def map_sql_expr(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[list[str], TypedColumn]:
    """
    Map Spark SQL to a Snowpark expression.
    """
    from snowflake.snowpark_connect.expression.map_expression import map_expression

    sql = exp.expression_string.expression
    logical_plan = sql_parser().parseExpression(sql)

    with push_sql_scope():
        proto = map_logical_plan_expression(logical_plan)

    with push_evaluating_sql_scope():
        return map_expression(proto, column_mapping, typer)


SPARK_OP_TO_PROTO = {
    "Add": "+",
    "Subtract": "-",
    "Multiply": "*",
    "Divide": "/",
    "IntegralDivide": "div",
    "Remainder": "%",
    "Subtract": "-",
    "UnaryMinus": "unary_minus",
    "UnaryPositive": "positive",
    "LessThan": "<",
    "GreaterThan": ">",
    "LessThanOrEqual": "<=",
    "GreaterThanOrEqual": ">=",
    "EqualTo": "==",
    "EqualNullSafe": "<=>",
    "BitwiseAnd": "&",
    "BitwiseOr": "|",
    "BitwiseXor": "^",
    "BitwiseNot": "~",
    "Not": "not",
    "And": "and",
    "Or": "or",
    "Concat": "concat",
    "In": "in",
    "IsNull": "isnull",
    "IsNotNull": "isnotnull",
    "PercentileCont": "percentile_cont",
    "PercentileDisc": "percentiledisc",
    "Lower": "lower",
    "Overlay": "overlay",
}

SPARK_SORT_DIRECTION_TO_PROTO = {
    "Ascending": expressions_proto.Expression.SortOrder.SORT_DIRECTION_ASCENDING,
    "Descending": expressions_proto.Expression.SortOrder.SORT_DIRECTION_DESCENDING,
}

SPARK_SORT_NULL_ORDERING_TO_PROTO = {
    "NullsFirst": expressions_proto.Expression.SortOrder.SORT_NULLS_FIRST,
    "NullsLast": expressions_proto.Expression.SortOrder.SORT_NULLS_LAST,
}

SPARK_FRAME_TYPE_TO_PROTO = {
    "RowFrame": expressions_proto.Expression.Window.WindowFrame.FRAME_TYPE_ROW,
    "RangeFrame": expressions_proto.Expression.Window.WindowFrame.FRAME_TYPE_RANGE,
}

SPARK_STRING_TRIM_FUNCS = {
    "StringTrim": "trim",
    "StringTrimLeft": "ltrim",
    "StringTrimRight": "rtrim",
}


def escape_spark_quoted(name: str) -> str:
    double_ticks = name.replace("`", "``")
    return f"`{double_ticks}`"


def map_frame_boundary(
    exp: jpype.JObject,
) -> expressions_proto.Expression.Window.WindowFrame.FrameBoundary:
    match str(exp.nodeName()):
        case "UnboundedPreceding$" | "UnboundedFollowing$":
            return expressions_proto.Expression.Window.WindowFrame.FrameBoundary(
                unbounded=True,
            )
        case "CurrentRow$":
            return expressions_proto.Expression.Window.WindowFrame.FrameBoundary(
                current_row=True,
            )
        case _:
            return expressions_proto.Expression.Window.WindowFrame.FrameBoundary(
                value=map_logical_plan_expression(exp)
            )


def apply_filter_clause(
    func_name: str,
    args: list[expressions_proto.Expression],
    exp: jpype.JObject,
    is_distinct: bool = False,
) -> expressions_proto.Expression:
    """Apply FILTER clause transformation if present, otherwise return normal function call."""
    if hasattr(exp, "filter"):
        filter_opt = exp.filter()
        if filter_opt.isDefined():
            # FILTER clause found - translate to CASE WHEN
            # This is the standard SQL transformation:
            # sum(value) FILTER (WHERE condition) → sum(CASE WHEN condition THEN value ELSE NULL END)
            filter_condition = map_logical_plan_expression(filter_opt.get())

            # Wrap each argument with CASE WHEN filter_condition THEN arg ELSE NULL END
            args = [
                expressions_proto.Expression(
                    unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                        function_name="when",
                        arguments=[filter_condition, arg],
                    )
                )
                for arg in args
            ]

    return expressions_proto.Expression(
        unresolved_function=expressions_proto.Expression.UnresolvedFunction(
            function_name=func_name,
            arguments=args,
            is_distinct=is_distinct,
        )
    )


def map_logical_plan_expression(exp: jpype.JObject) -> expressions_proto.Expression:
    from snowflake.snowpark_connect.expression.map_expression import (
        map_single_column_expression,
    )
    from snowflake.snowpark_connect.relation.map_sql import map_logical_plan_relation

    class_name = str(exp.getClass().getSimpleName())
    match class_name:
        case "AggregateExpression":
            func_name = as_java_list(exp.children())[0].nodeName()
            args = [
                map_logical_plan_expression(e)
                for e in as_java_list(as_java_list(exp.children())[0].children())
            ]
            proto = apply_filter_clause(func_name, args, exp)
        case "Alias":
            proto = expressions_proto.Expression(
                alias=expressions_proto.Expression.Alias(
                    expr=map_logical_plan_expression(exp.child()),
                    name=[str(exp.name())],
                )
            )
        case "CaseWhen":
            # exp has a .branches() method that gives us conditions and results
            # in a more structured format - however, we would need to flatten them, anyway,
            # so just use .children()
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name="when",
                    arguments=[
                        map_logical_plan_expression(e)
                        for e in as_java_list(exp.children())
                    ],
                )
            )
        case "Cast":
            proto = expressions_proto.Expression(
                cast=expressions_proto.Expression.Cast(
                    expr=map_logical_plan_expression(exp.child()),
                    type=None,
                    type_str=str(exp.dataType().simpleString()),
                )
            )
        case "Coalesce":
            arguments = [
                map_logical_plan_expression(e) for e in as_java_list(exp.children())
            ]

            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name="coalesce",
                    arguments=arguments,
                )
            )
        case "CreateNamedStruct":
            arg_exprs = [
                arg
                for k_v in zip(
                    as_java_list(exp.nameExprs()), as_java_list(exp.valExprs())
                )
                for arg in k_v
            ]
            struct_args = [
                map_logical_plan_expression(e)
                for e in arg_exprs
                if e.prettyName() != "NamePlaceholder"
            ]
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name="named_struct",
                    arguments=struct_args,
                )
            )
        case "Exists":
            rel_proto = map_logical_plan_relation(exp.plan())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.ExpExtension(
                    subquery_expression=snowflake_proto.SubqueryExpression(
                        input=rel_proto,
                        subquery_type=snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_EXISTS,
                    )
                )
            )
            proto = expressions_proto.Expression(extension=any_proto)
        case "ExpressionWithUnresolvedIdentifier":
            plan_id = None
            identifierExpr = map_logical_plan_expression(exp.identifierExpr())
            session = snowpark.Session.get_active_session()
            m = ColumnNameMap([], [], None)
            expr = map_single_column_expression(
                identifierExpr, m, ExpressionTyper.dummy_typer(session)
            )
            value = session.range(1).select(expr[1].col).collect()[0][0]

            proto = expressions_proto.Expression(
                unresolved_attribute=expressions_proto.Expression.UnresolvedAttribute(
                    unparsed_identifier=str(value),
                    plan_id=plan_id,
                ),
            )
            # TODO: support identifier referencing unresolved function
        case "InSubquery":
            rel_proto = map_logical_plan_relation(exp.query().plan())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.ExpExtension(
                    subquery_expression=snowflake_proto.SubqueryExpression(
                        input=rel_proto,
                        subquery_type=snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_IN,
                        in_subquery_values=[
                            map_logical_plan_expression(value)
                            for value in as_java_list(exp.values())
                        ],
                    )
                )
            )
            proto = expressions_proto.Expression(extension=any_proto)
        case "LambdaFunction":
            arguments = [
                map_logical_plan_expression(arg).unresolved_named_lambda_variable
                for arg in as_java_list(exp.arguments())
            ]
            proto = expressions_proto.Expression(
                lambda_function=expressions_proto.Expression.LambdaFunction(
                    function=map_logical_plan_expression(exp.function()),
                    arguments=arguments,
                )
            )
        case "Like" | "ILike" | "RLike":
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name=class_name.lower(),
                    arguments=[
                        map_logical_plan_expression(e)
                        for e in as_java_list(exp.children())
                    ],
                )
            )
        case "LikeAny" | "NotLikeAny" | "LikeAll" | "NotLikeAll":
            patterns = as_java_list(exp.patterns())
            arguments = [
                map_logical_plan_expression(e) for e in as_java_list(exp.children())
            ]
            arguments += [map_logical_plan_expression(e) for e in patterns]
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name=class_name.lower(),
                    arguments=arguments,
                )
            )
        case "Literal":
            type_name = str(exp.dataType().typeName())
            type_value = exp.value()

            if type_name == "string":
                type_value = str(type_value)
            elif type_name == "void":
                type_name = "null"
                type_value = types_proto.DataType()
            elif type_name == "binary":
                type_value = bytes(type_value)
            elif type_name.startswith("interval "):
                type_name = "day_time_interval"  # TODO
            elif m := DECIMAL_RE.fullmatch(type_name):
                type_name = "decimal"
                type_value = expressions_proto.Expression.Literal.Decimal(
                    value=str(type_value),
                    precision=int(m.group(1)),
                    scale=int(m.group(2)),
                )

            proto = expressions_proto.Expression(
                literal=expressions_proto.Expression.Literal(
                    **{
                        type_name: type_value,
                    }
                )
            )
        case "MultiAlias":
            proto = expressions_proto.Expression(
                alias=expressions_proto.Expression.Alias(
                    expr=map_logical_plan_expression(exp.child()),
                    name=as_java_list(exp.names()),
                )
            )
        case "NamedArgumentExpression":
            name = str(exp.key())
            value = map_logical_plan_expression(exp.child())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.ExpExtension(
                    named_argument=snowflake_proto.NamedArgumentExpression(
                        key=name,
                        value=value,
                    )
                )
            )
            proto = expressions_proto.Expression(extension=any_proto)
        case "NamedParameter":
            name = str(exp.name())
            value = get_sql_named_arg(name)
            if not value.HasField("literal_type"):
                raise AnalysisException(f"Found an unbound parameter {name!r}")
            proto = expressions_proto.Expression(literal=value)
        case "NamePlaceholder$":
            # This is a placeholder for an expression name to be resolved later.
            raise SnowparkConnectNotImplementedError(
                "NamePlaceholder is not supported in SQL expressions."
            )
        case "PosParameter":
            pos = exp.pos()
            try:
                value = get_sql_pos_arg(pos)
            except KeyError:
                raise AnalysisException(f"Found an unbound parameter at position {pos}")
            proto = expressions_proto.Expression(literal=value)
        case "ScalarSubquery":
            rel_proto = map_logical_plan_relation(exp.plan())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.ExpExtension(
                    subquery_expression=snowflake_proto.SubqueryExpression(
                        input=rel_proto,
                        subquery_type=snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_SCALAR,
                    )
                )
            )
            proto = expressions_proto.Expression(extension=any_proto)
        case "SortOrder":
            direction = SPARK_SORT_DIRECTION_TO_PROTO[str(exp.direction())]
            null_ordering = SPARK_SORT_NULL_ORDERING_TO_PROTO[str(exp.nullOrdering())]
            proto = expressions_proto.Expression(
                sort_order=expressions_proto.Expression.SortOrder(
                    child=map_logical_plan_expression(exp.child()),
                    direction=direction,
                    null_ordering=null_ordering,
                )
            )
        case op if (func_name := SPARK_STRING_TRIM_FUNCS.get(op)):
            args = [exp.srcStr()]
            if not exp.trimStr().isEmpty():
                args.append(exp.trimStr().get())
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name=func_name,
                    arguments=[map_logical_plan_expression(arg) for arg in args],
                )
            )
        case "StringLocate":
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name="position",
                    arguments=[
                        map_logical_plan_expression(exp.substr()),
                        map_logical_plan_expression(exp.str()),
                        map_logical_plan_expression(exp.start()),
                    ],
                )
            )
        case "Substring":
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name="substring",
                    arguments=[
                        map_logical_plan_expression(exp.str()),
                        map_logical_plan_expression(exp.pos()),
                        map_logical_plan_expression(exp.len()),
                    ],
                )
            )
        case "TimestampAdd" | "TimestampDiff":
            func = "timestamp_add" if class_name == "TimestampAdd" else "timestamp_diff"
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name=func,
                    arguments=[
                        expressions_proto.Expression(
                            literal=expressions_proto.Expression.Literal(
                                string=str(exp.unit())
                            )
                        )
                    ]
                    + [
                        map_logical_plan_expression(e)
                        for e in as_java_list(exp.children())
                    ],
                )
            )
        case "UnresolvedAlias":
            proto = map_logical_plan_expression(exp.child())
        case "UnresolvedAttribute":
            *parents, name = as_java_list(exp.nameParts())
            plan_id = None
            is_fully_qualified_name = False
            if parents:
                parent_name = ".".join(str(p) for p in parents)
                plan_id = get_sql_plan(parent_name)
                # If no plan_id exists, treat the column name as fully qualified by its parent.
                if plan_id is None:
                    # There's a difference in how Spark sql and dataframe operation passes backticks in column names.
                    # Spark sql un-escapes the backticks instead of passing the raw string. This
                    # logic is to escape backticks again to make it consistent with regular spark functions.
                    parent_chain = ".".join(escape_spark_quoted(p) for p in parents)
                    name = f"{parent_chain}.{escape_spark_quoted(name)}"
                    is_fully_qualified_name = True

            if not is_fully_qualified_name:
                # There's a difference in how Spark sql and dataframe operation passes backticks in column names.
                # Spark sql un-escapes the backticks instead of passing the raw string. This
                # logic is to escape backticks again to make it consistent with regular spark functions.
                name = escape_spark_quoted(name)

            proto = expressions_proto.Expression(
                unresolved_attribute=expressions_proto.Expression.UnresolvedAttribute(
                    unparsed_identifier=str(name),
                    plan_id=plan_id,
                ),
            )
        case "UnresolvedExtractValue":
            proto = expressions_proto.Expression(
                unresolved_extract_value=expressions_proto.Expression.UnresolvedExtractValue(
                    child=map_logical_plan_expression(exp.child()),
                    extraction=map_logical_plan_expression(exp.extraction()),
                )
            )
        case "UnresolvedFunction":
            func_name = ".".join(
                str(part) for part in as_java_list(exp.nameParts())
            ).lower()
            args = [
                map_logical_plan_expression(arg)
                for arg in as_java_list(exp.arguments())
            ]

            proto = apply_filter_clause(func_name, args, exp, exp.isDistinct())
        case "UnresolvedNamedLambdaVariable":
            proto = expressions_proto.Expression(
                unresolved_named_lambda_variable=expressions_proto.Expression.UnresolvedNamedLambdaVariable(
                    name_parts=[str(part) for part in as_java_list(exp.nameParts())],
                )
            )
        case "UnresolvedStar":
            if exp.target().isEmpty():
                proto = expressions_proto.Expression(
                    unresolved_star=expressions_proto.Expression.UnresolvedStar()
                )
            else:
                proto = expressions_proto.Expression(
                    unresolved_star=expressions_proto.Expression.UnresolvedStar(
                        unparsed_target=f"{'.'.join(as_java_list(exp.target().get()))}.*",
                    )
                )
        case "UnresolvedWindowExpression":
            window_spec_reference = exp.windowSpec().name()
            window_spec = _window_specs.get().get(window_spec_reference)
            if window_spec is not None:
                # Build Window expression
                proto = get_window_expression_proto(window_spec, exp.child())
            else:
                raise AnalysisException(
                    f"Window specification not found {window_spec_reference!r}"
                )
        case "UTF8String":
            proto = expressions_proto.Expression(
                literal=expressions_proto.Expression.Literal(
                    **{
                        "string": exp.toString(),
                    }
                )
            )
        case "WindowExpression":
            window_spec = exp.windowSpec()
            proto = get_window_expression_proto(window_spec, exp.windowFunction())
        case "FunctionTableSubqueryArgumentExpression":
            rel_proto = map_logical_plan_relation(exp.plan())
            any_proto = Any()
            any_proto.Pack(
                snowflake_proto.ExpExtension(
                    subquery_expression=snowflake_proto.SubqueryExpression(
                        input=rel_proto,
                        subquery_type=snowflake_proto.SubqueryExpression.SUBQUERY_TYPE_TABLE_ARG,
                    )
                )
            )
            proto = expressions_proto.Expression(extension=any_proto)
        case op if (proto_func := SPARK_OP_TO_PROTO.get(op)) is not None:
            proto = expressions_proto.Expression(
                unresolved_function=expressions_proto.Expression.UnresolvedFunction(
                    function_name=proto_func,
                    arguments=[
                        map_logical_plan_expression(arg)
                        for arg in as_java_list(exp.children())
                    ],
                )
            )

        case other:
            raise SnowparkConnectNotImplementedError(f"Not implemented: {other}")

    return proto


def get_window_expression_proto(
    window_spec, window_function
) -> expressions_proto.Expression:
    frame_spec = window_spec.frameSpecification()
    if frame_spec.nodeName() == "UnspecifiedFrame$":
        frame_spec_proto = None
    else:
        frame_spec_proto = expressions_proto.Expression.Window.WindowFrame(
            frame_type=SPARK_FRAME_TYPE_TO_PROTO[str(frame_spec.frameType())],
            lower=map_frame_boundary(frame_spec.lower()),
            upper=map_frame_boundary(frame_spec.upper()),
        )

    proto = expressions_proto.Expression(
        window=expressions_proto.Expression.Window(
            window_function=map_logical_plan_expression(window_function),
            partition_spec=[
                map_logical_plan_expression(e)
                for e in as_java_list(window_spec.partitionSpec())
            ],
            order_spec=[
                map_logical_plan_expression(e).sort_order
                for e in as_java_list(window_spec.orderSpec())
            ],
            frame_spec=frame_spec_proto,
        )
    )
    return proto
