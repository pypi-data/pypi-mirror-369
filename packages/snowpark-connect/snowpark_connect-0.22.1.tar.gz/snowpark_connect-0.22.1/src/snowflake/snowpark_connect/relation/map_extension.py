#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import cloudpickle as pkl
import pyspark.sql.connect.proto.expressions_pb2 as expression_proto
import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.errors.exceptions.base import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
import snowflake.snowpark.types as snowpark_types
import snowflake.snowpark_connect.proto.snowflake_relation_ext_pb2 as snowflake_proto
from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import (
    ColumnNameMap,
    make_column_names_snowpark_compatible,
)
from snowflake.snowpark_connect.config import get_boolean_session_config_param
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.expression.map_expression import map_expression
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_sql_aggregate_function_count,
    push_outer_dataframe,
    set_current_grouping_columns,
)
from snowflake.snowpark_connect.utils.identifiers import (
    split_fully_qualified_spark_name,
)
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_extension(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    The Extension relation type contains any extensions we use for adding new
    functionality to Spark Connect.

    The extension will require new protobuf messages to be defined in the
    snowflake_connect_server/proto directory.
    """
    extension = snowflake_proto.Extension()
    rel.extension.Unpack(extension)
    match extension.WhichOneof("op"):
        case "rdd_map":
            rdd_map = extension.rdd_map
            result = map_relation(rdd_map.input)
            input_df = result.dataframe

            column_name = "_RDD_"
            if len(input_df.columns) > 1:
                input_df = input_df.select(
                    snowpark_fn.array_construct(*input_df.columns).as_(column_name)
                )
                input_type = snowpark_types.ArrayType(snowpark_types.IntegerType())
                return_type = snowpark_types.ArrayType(snowpark_types.IntegerType())
            else:
                input_df = input_df.rename(input_df.columns[0], column_name)
                input_type = snowpark_types.VariantType()
                return_type = snowpark_types.VariantType()
            func = snowpark_fn.udf(
                pkl.loads(rdd_map.func),
                return_type=return_type,
                input_types=[input_type],
                name="my_udf",
                replace=True,
            )
            result = input_df.select(func(column_name).as_(column_name))
            return DataFrameContainer.create_with_column_mapping(
                dataframe=result,
                spark_column_names=[column_name],
                snowpark_column_names=[column_name],
                snowpark_column_types=[return_type],
            )
        case "subquery_column_aliases":
            subquery_aliases = extension.subquery_column_aliases
            rel.extension.Unpack(subquery_aliases)
            result = map_relation(subquery_aliases.input)
            input_df = result.dataframe
            snowpark_col_names = result.column_map.get_snowpark_columns()
            if len(subquery_aliases.aliases) != len(snowpark_col_names):
                raise AnalysisException(
                    "Number of column aliases does not match number of columns. "
                    f"Number of column aliases: {len(subquery_aliases.aliases)}; "
                    f"number of columns: {len(snowpark_col_names)}."
                )
            return DataFrameContainer.create_with_column_mapping(
                dataframe=input_df,
                spark_column_names=subquery_aliases.aliases,
                snowpark_column_names=snowpark_col_names,
                column_qualifiers=result.column_map.get_qualifiers(),
            )
        case "lateral_join":
            lateral_join = extension.lateral_join
            left_result = map_relation(lateral_join.left)
            left_df = left_result.dataframe

            udtf_info = get_udtf_project(lateral_join.right)
            if udtf_info:
                return handle_lateral_join_with_udtf(
                    left_result, lateral_join.right, udtf_info
                )

            left_queries = left_df.queries["queries"]
            if len(left_queries) != 1:
                raise SnowparkConnectNotImplementedError(
                    f"Unexpected number of queries: {len(left_queries)}"
                )
            left_query = left_queries[0]
            with push_outer_dataframe(left_result):
                right_result = map_relation(lateral_join.right)
                right_df = right_result.dataframe
            right_queries = right_df.queries["queries"]
            if len(right_queries) != 1:
                raise SnowparkConnectNotImplementedError(
                    f"Unexpected number of queries: {len(right_queries)}"
                )
            right_query = right_queries[0]
            input_df_sql = f"WITH __left AS ({left_query}) SELECT * FROM __left INNER JOIN LATERAL ({right_query})"
            session = snowpark.Session.get_active_session()
            input_df = session.sql(input_df_sql)
            return DataFrameContainer.create_with_column_mapping(
                dataframe=input_df,
                spark_column_names=left_result.column_map.get_spark_columns()
                + right_result.column_map.get_spark_columns(),
                snowpark_column_names=left_result.column_map.get_snowpark_columns()
                + right_result.column_map.get_snowpark_columns(),
                column_qualifiers=left_result.column_map.get_qualifiers()
                + right_result.column_map.get_qualifiers(),
            )

        case "udtf_with_table_arguments":
            return handle_udtf_with_table_arguments(extension.udtf_with_table_arguments)
        case "aggregate":
            return map_aggregate(extension.aggregate, rel.common.plan_id)
        case other:
            raise SnowparkConnectNotImplementedError(f"Unexpected extension {other}")


def get_udtf_project(relation: relation_proto.Relation) -> bool:
    """
    Extract UDTF information from a relation if it's a project containing a UDTF call.

    Returns:
        tuple[udtf_obj, udtf_spark_output_names] if UDTF found, None otherwise
    """
    if relation.WhichOneof("rel_type") == "project":
        expressions = relation.project.expressions
        if (
            len(expressions) == 1
            and expressions[0].WhichOneof("expr_type") == "unresolved_function"
        ):
            session = snowpark.Session.get_active_session()
            func = expressions[0].unresolved_function
            udtf_name_lower = func.function_name.lower()
            if udtf_name_lower in session._udtfs:
                return session._udtfs[udtf_name_lower]

    return None


def handle_udtf_with_table_arguments(
    udtf_info: snowflake_proto.UDTFWithTableArguments,
) -> snowpark.DataFrame:
    """
    Handle UDTF with one or more table arguments using Snowpark's join_table_function.
    For multiple table arguments, this creates a Cartesian product of all input tables.
    """
    session = snowpark.Session.get_active_session()
    udtf_name_lower = udtf_info.function_name.lower()
    if udtf_name_lower not in session._udtfs:
        raise ValueError(f"UDTF '{udtf_info.function_name}' not found.")
    _udtf_obj, udtf_spark_output_names = session._udtfs[udtf_name_lower]

    table_containers = []
    for table_arg_info in udtf_info.table_arguments:
        result = map_relation(table_arg_info.table_argument)
        table_containers.append((result, table_arg_info.table_argument_idx))

    if len(table_containers) == 1:
        base_df = table_containers[0][0].dataframe
    else:
        if not get_boolean_session_config_param(
            "spark.sql.tvf.allowMultipleTableArguments.enabled"
        ):
            raise AnalysisException(
                "[TABLE_VALUED_FUNCTION_TOO_MANY_TABLE_ARGUMENTS] Multiple table arguments are not enabled. "
                "Please set `spark.sql.tvf.allowMultipleTableArguments.enabled` to `true`"
            )

        base_df = table_containers[0][0].dataframe
        first_table_col_count = len(base_df.columns)

        for table_container, _ in table_containers[1:]:
            base_df = base_df.cross_join(table_container.dataframe)

        # Ensure deterministic ordering to match Spark's Cartesian product behavior
        # For two tables A and B, Spark produces: for each B row, iterate through A rows
        # Sort order: B columns first (outer loop), then A columns (inner loop)
        all_columns = base_df.columns
        first_table_cols = all_columns[:first_table_col_count]
        subsequent_table_cols = all_columns[first_table_col_count:]

        base_df = base_df.sort(*(subsequent_table_cols + first_table_cols))

    scalar_args = []
    typer = ExpressionTyper.dummy_typer(session)
    empty_column_map = ColumnNameMap([], [], None)
    for arg_proto in udtf_info.arguments:
        # UDTF when used with table arguments, the arguments can only be scalar arguments like integer, literals etc. or Table arguments.
        # Using map_expression with dummy typer to resolve the scalar arguments.
        _, typed_column = map_expression(arg_proto, empty_column_map, typer)
        scalar_args.append(typed_column.col)

    table_arg_variants = []
    for table_container, table_arg_idx in table_containers:
        table_columns = table_container.column_map.get_snowpark_columns()
        spark_columns = table_container.column_map.get_spark_columns()

        # Create a structure that supports both positional and named access
        # Format: {"__fields__": ["col1", "col2"], "__values__": [val1, val2]}
        # This allows UDTFs to access table arguments both ways: a[0] and a["col1"]
        fields_array = snowpark_fn.array_construct(
            *[snowpark_fn.lit(col) for col in spark_columns]
        )
        values_array = snowpark_fn.array_construct(
            *[snowpark_fn.col(col) for col in table_columns]
        )

        table_arg_variant = snowpark_fn.to_variant(
            snowpark_fn.object_construct(
                snowpark_fn.lit("__fields__"),
                fields_array,
                snowpark_fn.lit("__values__"),
                values_array,
            )
        )
        table_arg_variants.append((table_arg_variant, table_arg_idx))

    scalar_args_variant = [snowpark_fn.to_variant(arg) for arg in scalar_args]

    all_args = scalar_args_variant.copy()
    for table_arg_variant, table_arg_idx in sorted(
        table_arg_variants, key=lambda x: x[1]
    ):
        all_args.insert(table_arg_idx, table_arg_variant)

    udtf_func = snowpark_fn.table_function(_udtf_obj.name)
    result_df = base_df.join_table_function(udtf_func(*all_args))

    # Return only the UDTF output columns
    original_column_count = len(base_df.columns)
    udtf_output_columns = result_df.columns[original_column_count:]

    final_df = result_df.select(*udtf_output_columns)

    return DataFrameContainer.create_with_column_mapping(
        dataframe=final_df,
        spark_column_names=udtf_spark_output_names,
        snowpark_column_names=udtf_output_columns,
    )


def handle_lateral_join_with_udtf(
    left_result: DataFrameContainer,
    udtf_relation: relation_proto.Relation,
    udtf_info: tuple[snowpark.udtf.UserDefinedTableFunction, list],
) -> snowpark.DataFrame:
    """
    Handle lateral join with UDTF on the right side using join_table_function.
    """
    session = snowpark.Session.get_active_session()

    project = udtf_relation.project
    udtf_func = project.expressions[0].unresolved_function
    _udtf_obj, udtf_spark_output_names = udtf_info

    typer = ExpressionTyper.dummy_typer(session)
    left_column_map = left_result.column_map
    left_df = left_result.dataframe
    table_func = snowpark_fn.table_function(_udtf_obj.name)
    udtf_args = [
        map_expression(arg_proto, left_column_map, typer)[1].col
        for arg_proto in udtf_func.arguments
    ]
    udtf_args_variant = [snowpark_fn.to_variant(arg) for arg in udtf_args]
    result_df = left_df.join_table_function(table_func(*udtf_args_variant))

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result_df,
        spark_column_names=left_result.column_map.get_spark_columns()
        + udtf_spark_output_names,
        snowpark_column_names=result_df.columns,
        column_qualifiers=left_result.column_map.get_qualifiers()
        + [[]] * len(udtf_spark_output_names),
    )


def map_aggregate(
    aggregate: snowflake_proto.Aggregate, plan_id: int
) -> snowpark.DataFrame:
    input_container = map_relation(aggregate.input)
    input_df: snowpark.DataFrame = input_container.dataframe

    # Detect the "GROUP BY ALL" case:
    # - it's a plain GROUP BY (not ROLLUP, CUBE, etc.)
    # - it's grouped by a single identifier named "ALL"
    # - there is no existing column named "ALL"
    is_group_by_all = False
    if (
        aggregate.group_type == snowflake_proto.Aggregate.GROUP_TYPE_GROUPBY
        and len(aggregate.grouping_expressions) == 1
    ):
        parsed_col_name = split_fully_qualified_spark_name(
            aggregate.grouping_expressions[0].unresolved_attribute.unparsed_identifier
        )
        if (
            len(parsed_col_name) == 1
            and parsed_col_name[0].lower() == "all"
            and input_container.column_map.get_snowpark_column_name_from_spark_column_name(
                parsed_col_name[0], allow_non_exists=True
            )
            is None
        ):
            is_group_by_all = True

    # First, map all groupings and aggregations.
    # In case of GROUP BY ALL, groupings are a subset of the aggregations.

    typer = ExpressionTyper(input_df)

    def _map_column(exp: expression_proto.Expression) -> tuple[str, TypedColumn]:
        new_names, snowpark_column = map_expression(
            exp, input_container.column_map, typer
        )
        if len(new_names) != 1:
            raise SnowparkConnectNotImplementedError(
                "Multi-column aggregate expressions are not supported"
            )
        return new_names[0], snowpark_column

    raw_groupings: list[tuple[str, TypedColumn]] = []
    raw_aggregations: list[tuple[str, TypedColumn]] = []

    agg_count = get_sql_aggregate_function_count()
    for exp in aggregate.aggregate_expressions:
        col = _map_column(exp)
        raw_aggregations.append(col)

        if is_group_by_all:
            new_agg_count = get_sql_aggregate_function_count()
            if new_agg_count == agg_count:
                raw_groupings.append(col)
            else:
                agg_count = new_agg_count

    if not is_group_by_all:
        raw_groupings = [_map_column(exp) for exp in aggregate.grouping_expressions]

    # Set the current grouping columns in context for grouping_id() function
    grouping_spark_columns = [spark_name for spark_name, _ in raw_groupings]
    set_current_grouping_columns(grouping_spark_columns)

    # Now create column name lists and assign aliases.
    # In case of GROUP BY ALL, even though groupings are a subset of aggregations,
    # they will have their own aliases so we can drop them later.

    spark_columns: list[str] = []
    snowpark_columns: list[str] = []
    snowpark_column_types: list[snowpark_types.DataType] = []

    def _add_column(spark_name: str, snowpark_column: TypedColumn) -> snowpark.Column:
        alias = make_column_names_snowpark_compatible(
            [spark_name], plan_id, len(spark_columns)
        )[0]

        spark_columns.append(spark_name)
        snowpark_columns.append(alias)
        snowpark_column_types.append(snowpark_column.typ)

        return snowpark_column.col.alias(alias)

    groupings = [_add_column(name, col) for name, col in raw_groupings]
    aggregations = [_add_column(name, col) for name, col in raw_aggregations]

    match aggregate.group_type:
        case snowflake_proto.Aggregate.GROUP_TYPE_GROUPBY:
            result = input_df.group_by(groupings)
        case snowflake_proto.Aggregate.GROUP_TYPE_ROLLUP:
            result = input_df.rollup(groupings)
        case snowflake_proto.Aggregate.GROUP_TYPE_CUBE:
            result = input_df.cube(groupings)
        case snowflake_proto.Aggregate.GROUP_TYPE_GROUPING_SETS:
            # TODO: What do we do about groupings?
            sets = (
                [
                    map_expression(exp, input_container.column_map, typer)[1].col
                    for exp in grouping_sets.grouping_set
                ]
                for grouping_sets in aggregate.grouping_sets
            )
            result = input_df.group_by_grouping_sets(snowpark.GroupingSets(*sets))
        case other:
            raise SnowparkConnectNotImplementedError(
                f"Unsupported GROUP BY type: {other}"
            )

    result = result.agg(*aggregations)

    if aggregate.group_type == snowflake_proto.Aggregate.GROUP_TYPE_GROUPING_SETS:
        # Immediately drop extra columns. Unlike other GROUP BY operations,
        # grouping sets don't allow ORDER BY with columns that aren't in the aggregate list.
        result = result.select(result.columns[-len(spark_columns) :])

    # Build a parent column map that includes groupings.
    result_container = DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=spark_columns,
        snowpark_column_names=snowpark_columns,
        snowpark_column_types=snowpark_column_types,
    )

    # Drop the groupings.
    grouping_count = len(groupings)

    return DataFrameContainer.create_with_column_mapping(
        result.drop(snowpark_columns[:grouping_count]),
        spark_columns[grouping_count:],
        snowpark_columns[grouping_count:],
        snowpark_column_types[grouping_count:],
        parent_column_name_map=result_container.column_map,
    )
