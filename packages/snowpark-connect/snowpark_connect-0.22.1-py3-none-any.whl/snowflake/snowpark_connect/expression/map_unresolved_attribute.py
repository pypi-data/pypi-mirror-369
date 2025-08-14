#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import re

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
from pyspark.errors.exceptions.connect import AnalysisException

import snowflake.snowpark.functions as snowpark_fn
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
)
from snowflake.snowpark.exceptions import SnowparkSQLException
from snowflake.snowpark.types import ArrayType, MapType, StructType
from snowflake.snowpark_connect.column_name_handler import ColumnNameMap
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.typed_column import TypedColumn
from snowflake.snowpark_connect.utils.context import (
    get_is_evaluating_sql,
    get_outer_dataframes,
    get_plan_id_map,
    resolve_lca_alias,
)
from snowflake.snowpark_connect.utils.identifiers import (
    split_fully_qualified_spark_name,
)

SPARK_QUOTED = re.compile("^(`.*`)$", re.DOTALL)


def map_unresolved_attribute(
    exp: expressions_proto.Expression,
    column_mapping: ColumnNameMap,
    typer: ExpressionTyper,
) -> tuple[str, TypedColumn]:
    original_attr_name = exp.unresolved_attribute.unparsed_identifier
    name_parts = split_fully_qualified_spark_name(original_attr_name)

    assert len(name_parts) > 0, f"Unable to parse input attribute: {original_attr_name}"

    attr_name = ".".join(name_parts)

    has_plan_id = exp.unresolved_attribute.HasField("plan_id")

    if has_plan_id:
        plan_id = exp.unresolved_attribute.plan_id
        target_df_container = get_plan_id_map(plan_id)
        target_df = target_df_container.dataframe
        assert (
            target_df is not None
        ), f"resolving an attribute of a unresolved dataframe {plan_id}"
        column_mapping = target_df_container.column_map
        typer = ExpressionTyper(target_df)

    def get_col(snowpark_name):
        return (
            snowpark_fn.col(snowpark_name)
            if not has_plan_id
            else target_df.col(snowpark_name)
        )

    # Check if regex column names are enabled and this is a quoted identifier
    # We need to check the original attribute name before split_fully_qualified_spark_name processes it
    if (
        get_is_evaluating_sql()
        and global_config.spark_sql_parser_quotedRegexColumnNames
        and SPARK_QUOTED.match(original_attr_name)
    ):
        # Extract regex pattern by removing backticks
        regex_pattern = original_attr_name[1:-1]  # Remove first and last backtick

        # Get all available column names from the column mapping
        available_columns = column_mapping.get_spark_columns()

        # Match the regex pattern against available columns
        matched_columns = []
        try:
            compiled_regex = re.compile(
                regex_pattern,
                re.IGNORECASE if not global_config.spark_sql_caseSensitive else 0,
            )
            for col_name in available_columns:
                if compiled_regex.fullmatch(col_name):
                    matched_columns.append(col_name)
        except re.error as e:
            raise AnalysisException(f"Invalid regex pattern '{regex_pattern}': {e}")

        if not matched_columns:
            raise AnalysisException(
                f"No columns match the regex pattern '{regex_pattern}'"
            )

        # When multiple columns match, we need to signal that this should expand to multiple columns
        # Since map_unresolved_attribute can only return one column, we'll use a special marker
        # to indicate that this is a multi-column regex expansion
        if len(matched_columns) > 1:
            # Create a special column name that indicates multi-column expansion
            # The higher-level logic will need to handle this
            multi_col_name = "__REGEX_MULTI_COL__"
            # For now, return the first column but mark it specially
            quoted_col_name = matched_columns[0]
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    quoted_col_name
                )
            )
            col = get_col(snowpark_name)
            qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_col_name)
            typed_col = TypedColumn(col, lambda: typer.type(col))
            typed_col.set_qualifiers(qualifiers)
            # Store matched columns info for later use
            typed_col._regex_matched_columns = matched_columns
            return (multi_col_name, typed_col)
        else:
            # Single column match - return that column
            quoted_col_name = matched_columns[0]
            snowpark_name = (
                column_mapping.get_snowpark_column_name_from_spark_column_name(
                    quoted_col_name
                )
            )
            col = get_col(snowpark_name)
            qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_col_name)
            typed_col = TypedColumn(col, lambda: typer.type(col))
            typed_col.set_qualifiers(qualifiers)
            return (matched_columns[0], typed_col)

    quoted_attr_name = ".".join(
        quote_name_without_upper_casing(x) for x in name_parts[:-1]
    )
    if len(name_parts) > 1:
        quoted_attr_name = f"{quoted_attr_name}.{name_parts[-1]}"
    else:
        quoted_attr_name = name_parts[0]

    snowpark_name = column_mapping.get_snowpark_column_name_from_spark_column_name(
        quoted_attr_name, allow_non_exists=True
    )
    if snowpark_name is not None:
        col = get_col(snowpark_name)
        qualifiers = column_mapping.get_qualifier_for_spark_column(quoted_attr_name)
    else:
        # this means it has to be a struct column with a field name
        snowpark_name = column_mapping.get_snowpark_column_name_from_spark_column_name(
            name_parts[0], allow_non_exists=True
        )
        if snowpark_name is None:
            for outer_df_container in get_outer_dataframes():
                snowpark_name = outer_df_container.column_map.get_snowpark_column_name_from_spark_column_name(
                    name_parts[0], allow_non_exists=True
                )
                if snowpark_name is not None:
                    break

        if snowpark_name is None:
            # Attempt LCA fallback.
            alias_tc = resolve_lca_alias(attr_name)

            if alias_tc is not None:
                # Return the TypedColumn that represents the alias.
                return (attr_name, alias_tc)

            # If qualified name not found, try to resolve as unqualified column name
            # This handles cases like "d.name" where we need to find "name" after a JOIN
            if len(name_parts) > 1:
                unqualified_name = name_parts[-1]
                snowpark_name = (
                    column_mapping.get_snowpark_column_name_from_spark_column_name(
                        unqualified_name, allow_non_exists=True
                    )
                )
                if snowpark_name is not None:
                    col = get_col(snowpark_name)
                    qualifiers = column_mapping.get_qualifier_for_spark_column(
                        unqualified_name
                    )
                    typed_col = TypedColumn(col, lambda: typer.type(col))
                    typed_col.set_qualifiers(qualifiers)
                    return (unqualified_name, typed_col)

        if snowpark_name is None:
            if has_plan_id:
                raise AnalysisException(
                    f'[RESOLVED_REFERENCE_COLUMN_NOT_FOUND] The column "{attr_name}" does not exist in the target dataframe.'
                )
            else:
                # Column does not exist. Pass in dummy column name for lazy error throwing as it could be a built-in function
                snowpark_name = attr_name

        col = get_col(snowpark_name)
        try:
            col_type = typer.type(col)[0]
        except SnowparkSQLException as e:
            if "invalid identifier" in e.raw_message:
                raise AnalysisException(
                    f'[COLUMN_NOT_FOUND] The column "{attr_name}" does not exist in the target dataframe.'
                )
            else:
                raise
        is_struct = isinstance(col_type, StructType)
        # for struct columns when accessed, spark use just the leaf field name rather than fully attributed one
        if is_struct:
            attr_name = name_parts[-1]

        path = name_parts[1:]
        if is_struct and not global_config.spark_sql_caseSensitive:
            path = _match_path_to_struct(path, col_type)

        for field_name in path:
            col = col.getItem(field_name)

        qualifiers = []

    typed_col = TypedColumn(col, lambda: typer.type(col))
    typed_col.set_qualifiers(qualifiers)
    return (name_parts[-1], typed_col)


def _match_path_to_struct(path: list[str], col_type: StructType) -> list[str]:
    """Takes a path of names and adjusts them to strictly match the field names in a StructType."""
    adjusted_path = []
    typ = col_type
    for i, name in enumerate(path):
        if isinstance(typ, StructType):
            lowercase_name = name.lower()
            for field in typ.fields:
                if field.name.lower() == lowercase_name:
                    adjusted_path.append(field.name)
                    typ = field.datatype
                    break
        elif isinstance(typ, MapType) or isinstance(typ, ArrayType):
            # For MapType and ArrayType, we can use the name as is.
            adjusted_path.append(name)
            typ = typ.value_type if isinstance(typ, MapType) else typ.element_type
        else:
            # If the type is not a struct, map, or array, we cannot access the field.
            raise AnalysisException(
                f"[INVALID_EXTRACT_BASE_FIELD_TYPE] Can't extract a value from \"{'.'.join(path[:i])}\". Need a complex type [STRUCT, ARRAY, MAP] but got \"{typ}\"."
            )
    return adjusted_path
